from __future__ import annotations

import abc
import asyncio
import random
from typing import Any

import torch
from datasets import Dataset as HFDataset
from datasets import DatasetDict, concatenate_datasets
from torch.utils.data import DataLoader, RandomSampler

from actors.environments.types import EnvironmentOutput


class Environment(abc.ABC):
    def __init__(
        self,
        train_data: HFDataset | DatasetDict | None = None,
        eval_data: (
            HFDataset | DatasetDict | dict[str, HFDataset | DatasetDict] | None
        ) = None,
    ) -> None:
        self.train_data = (
            self._normalise_hf_splits(train_data) if train_data is not None else None
        )

        if eval_data is not None:
            if isinstance(eval_data, dict):
                self.eval_datasets = {
                    name: self._normalise_hf_splits(data)
                    for name, data in eval_data.items()
                }
            else:
                self.eval_datasets = {"eval": self._normalise_hf_splits(eval_data)}
        else:
            self.eval_datasets = {}

        self._data_state = {"epoch": 0, "step_in_epoch": 0, "current_generator_seed": 0}
        self._rng = torch.Generator()
        self._dataloader = None

    @staticmethod
    def _normalise_hf_splits(
        data: HFDataset | DatasetDict,
    ):
        if isinstance(data, DatasetDict):
            return data.get("train", next(iter(data.values())))
        return data

    def _build_dataloader(self, batch_size: int):
        """Create a DataLoader with the current RNG seed & generator state."""
        if self.train_data is None:
            return

        self._rng.manual_seed(self._data_state["current_generator_seed"])
        sampler = RandomSampler(self.train_data, generator=self._rng)

        def collate_fn(batch):
            if not batch:
                return {}
            keys = batch[0].keys()
            return {k: [d[k] for d in batch] for k in keys}

        self._dataloader = DataLoader(
            self.train_data,
            batch_size=batch_size,
            sampler=sampler,
            collate_fn=collate_fn,
            drop_last=True,
        )

    def get_dataloader(self, batch_size: int):
        """Get the current dataloader, building it if necessary."""
        if self._dataloader is None:
            self._build_dataloader(batch_size)
        return self._dataloader

    def get_data_state(self):
        """Get the current data state for checkpointing."""
        return self._data_state.copy()

    def set_data_state(self, state: dict[str, Any], batch_size: int):
        """Set data state for resuming."""
        self._data_state = state.copy()
        if "rng_state" in state:
            self._rng.set_state(state["rng_state"])
        self._build_dataloader(batch_size)

    def get_rng_state(self):
        """Get RNG state for checkpointing."""
        return self._rng.get_state()

    def set_rng_state(self, state):
        """Set RNG state for resuming."""
        self._rng.set_state(state)

    def skip_to_step(self, target_step: int, batch_size: int):
        """Skip ahead to a specific step by advancing the data state."""
        if self.train_data is None:
            return

        # We need to build the dataloader first to know steps per epoch
        if self._dataloader is None:
            self._build_dataloader(batch_size)

        steps_per_epoch = len(self._dataloader)
        target_epoch = target_step // steps_per_epoch
        target_step_in_epoch = target_step % steps_per_epoch

        self._data_state.update(
            epoch=target_epoch,
            step_in_epoch=target_step_in_epoch,
            current_generator_seed=self._data_state["current_generator_seed"]
            + target_epoch,
        )
        self._build_dataloader(batch_size)

    def advance_epoch(self, batch_size: int):
        """Advance to the next epoch."""
        self._data_state.update(
            epoch=self._data_state["epoch"] + 1,
            step_in_epoch=0,
            current_generator_seed=self._data_state["current_generator_seed"] + 1,
        )
        self._build_dataloader(batch_size)

    def advance_step(self):
        """Advance to the next step within the current epoch."""
        self._data_state["step_in_epoch"] += 1

    def batches_left(self, batch_size: int) -> int:
        """Return the number of batches left in the current epoch."""
        if self._dataloader is None:
            self._build_dataloader(batch_size)
        if self.train_data is None:
            return 0

        steps_per_epoch = len(self._dataloader)
        current_step = self._data_state["step_in_epoch"]
        return max(0, steps_per_epoch - current_step)

    def get_next_batch(self, batch_size: int) -> dict[str, list[Any]] | None:
        """Get the next batch from the dataloader, handling edge cases."""
        if self.train_data is None:
            return None

        # Build dataloader if needed
        if self._dataloader is None or self._data_state["step_in_epoch"] == 0:
            self._build_dataloader(batch_size)

        dataloader_iter = iter(self._dataloader)

        # Skip to current position
        for _ in range(self._data_state["step_in_epoch"]):
            try:
                next(dataloader_iter)
            except StopIteration:
                return None

        # Get the next batch
        try:
            batch = next(dataloader_iter)
            self.advance_step()
            return batch
        except StopIteration:
            # Automatically advance to next epoch when we run out of batches
            self._data_state.update(
                epoch=self._data_state["epoch"] + 1,
                step_in_epoch=0,
                current_generator_seed=self._data_state["current_generator_seed"] + 1,
            )
            self._build_dataloader(batch_size)

            # Try to get batch from new epoch
            try:
                dataloader_iter = iter(self._dataloader)
                batch = next(dataloader_iter)
                self.advance_step()
                return batch
            except StopIteration:
                return None

    def expand_batch_for_groups(
        self, batch: dict[str, list[Any]], group_size: int
    ) -> dict[str, list[Any]]:
        """
        Expand a batch by duplicating each item group_size times.

        Also adds identifier for the group to each item.
        """
        if not isinstance(batch, dict):
            raise ValueError("batch must be a dictionary")

        expanded = {}

        for k, v in batch.items():
            if isinstance(v, list):
                expanded[k] = [item for item in v for _ in range(group_size)]
            else:
                expanded[k] = v

        return expanded

    def split_batch_in_parts(
        self, batch: dict[str, list[Any]], number_of_parts: int
    ) -> list[dict[str, list[Any]]]:
        """Split a batch into a specified number of parts."""
        if not isinstance(batch, dict):
            raise ValueError("batch must be a dictionary")

        if number_of_parts <= 0:
            raise ValueError("number_of_parts must be greater than 0")

        part_size = len(next(iter(batch.values()))) // number_of_parts
        if part_size == 0:
            return [batch] * number_of_parts

        parts = []
        for i in range(number_of_parts):
            part = {k: v[i * part_size : (i + 1) * part_size] for k, v in batch.items()}
            parts.append(part)

        return parts

    def __call__(
        self, batch_size: int, group_size: int = 1, accelerator=None
    ) -> EnvironmentOutput | None:
        """
        Get a batch from the data and run generation.

        Args:
            batch_size: Number of problems to include in batch
            group_size: Number of generations/base rollouts per problem

        Returns:
            EnvironmentOutput
        """
        # Get the next batch from data
        raw_batch = self.get_next_batch(batch_size)
        if raw_batch is None:
            raise StopIteration("No more batches available")

        expanded_batch = self.expand_batch_for_groups(raw_batch, group_size)
        group_ids = [i // group_size for i in range(batch_size * group_size)]
        # Expand batch for groups
        if accelerator is not None:
            expanded_batch = self.split_batch_in_parts(
                expanded_batch, accelerator.num_processes // torch.cuda.device_count()
            )
            expanded_batch = expanded_batch[
                accelerator.process_index // torch.cuda.device_count()
            ]
        # Run generation
        env_output: EnvironmentOutput = None
        if accelerator.is_local_main_process:
            env_output = asyncio.run(self.generate(expanded_batch))

        # We gather.
        env_outputs = accelerator.gather_for_metrics([env_output])
        env_outputs = [eo for eo in env_outputs if eo is not None]
        env_out_combined: EnvironmentOutput = EnvironmentOutput.combine_and_group(
            env_outputs,
            group_ids,
            [{k: v[i] for k, v in raw_batch.items()} for i in range(batch_size)],
        )

        return env_out_combined

    def eval(
        self,
        group_size: int = 1,
        accelerator=None,
    ) -> dict[str, EnvironmentOutput]:
        """
        Evaluate all registered evaluation splits with the same distributed
        pattern used in `__call__`.

        Args:
            group_size: number of generations per prompt
            accelerator: `accelerate.Accelerator` (may be None for single-GPU)

        Returns:
            {split_name: grouped EnvironmentOutput}
        """
        if not self.eval_datasets:
            return {}

        results: dict[str, EnvironmentOutput] = {}

        for split_name, ds in self.eval_datasets.items():
            # build a full batch from the whole eval dataset
            eval_batch = {k: ds[:][k] for k in ds.column_names}
            expanded = self.expand_batch_for_groups(eval_batch, group_size)
            group_ids = [
                i // group_size for i in range(len(expanded[next(iter(expanded))]))
            ]
            if accelerator is not None:
                parts = accelerator.num_processes // torch.cuda.device_count()
                expanded = self.split_batch_in_parts(expanded, parts)
                expanded = expanded[
                    accelerator.process_index // torch.cuda.device_count()
                ]

            env_out: EnvironmentOutput | None = None
            if accelerator is None or accelerator.is_local_main_process:
                env_out = asyncio.run(self.generate(expanded))

            # gather outputs from all ranks
            if accelerator is not None:
                gathered = accelerator.gather_for_metrics([env_out])
                gathered = [eo for eo in gathered if eo is not None]
            else:
                gathered = [env_out]

            # merge + group
            env_out_combined: EnvironmentOutput = EnvironmentOutput.combine_and_group(
                gathered,
                group_ids,
                [
                    {k: v[i] for k, v in eval_batch.items()}
                    for i in range(len(eval_batch[next(iter(eval_batch))]))
                ],
            )

            results[split_name] = env_out_combined

        return results

    @abc.abstractmethod
    async def generate(self, batch) -> EnvironmentOutput:
        """
        Generate outputs for a batch of inputs.

        Args:
            batch: Dictionary mapping column names to lists of values

        Returns:
            EnvironmentOutput containing actor outputs
        """

    # ═════════════════════════════════════════════════════════════════════════════
    # Combining multiple environments
    # ═════════════════════════════════════════════════════════════════════════════

    def __add__(self, other: Environment) -> Environment:
        if not isinstance(other, Environment):
            raise TypeError

        class CombinedEnvironment(Environment):
            def __init__(
                self, env1: Environment, env2: Environment, seed: int | None = None
            ):
                self.env1 = env1
                self.env2 = env2
                self.keys_for_env1 = (
                    set(env1.train_data.column_names) if env1.train_data else set()
                )
                self.keys_for_env2 = (
                    set(env2.train_data.column_names) if env2.train_data else set()
                )
                self.all_keys = self.keys_for_env1 | self.keys_for_env2
                self.random_column_name = f"_GROUP_{random.randint(0, 10**10)}"
                if env1.train_data is not None:
                    env1.train_data = env1.train_data.add_column(
                        self.random_column_name, ["env1"] * len(env1.train_data)
                    )
                if env2.train_data is not None:
                    env2.train_data = env2.train_data.add_column(
                        self.random_column_name, ["env2"] * len(env2.train_data)
                    )
                train_data = None
                if env1.train_data is not None and env2.train_data is not None:
                    train_data = concatenate_datasets(
                        [env1.train_data, env2.train_data]
                    )
                    train_data = (
                        train_data.shuffle(seed=seed)
                        if seed is not None
                        else train_data.shuffle()
                    )
                elif env1.train_data is not None:
                    train_data = env1.train_data
                elif env2.train_data is not None:
                    train_data = env2.train_data
                eval_datasets = {}
                for name, data in env1.eval_datasets.items():
                    if name in env2.eval_datasets:
                        eval_datasets[f"{name}_env1"] = data
                        eval_datasets[f"{name}_env2"] = env2.eval_datasets[name]
                        # We add the column.
                        eval_datasets[f"{name}_env2"] = data.add_column(
                            self.random_column_name, ["env1"] * len(data)
                        )
                        eval_datasets[f"{name}_env2"] = env2.eval_datasets[
                            name
                        ].add_column(
                            self.random_column_name,
                            ["env2"] * len(env2.eval_datasets[name]),
                        )
                    else:
                        eval_datasets[name] = data
                        eval_datasets[name] = data.add_column(
                            self.random_column_name, ["env1"] * len(data)
                        )
                    # We add the column.
                for name, data in env2.eval_datasets.items():
                    if name not in eval_datasets:
                        eval_datasets[name] = data
                        eval_datasets[name] = data.add_column(
                            self.random_column_name, ["env2"] * len(data)
                        )
                super().__init__(train_data=train_data, eval_data=eval_datasets)

            async def generate(self, batch: dict[str, Any]) -> EnvironmentOutput:
                ids_of_env1 = [
                    i
                    for i, v in enumerate(batch[self.random_column_name])
                    if v == "env1"
                ]
                ids_of_env2 = [
                    i
                    for i, v in enumerate(batch[self.random_column_name])
                    if v == "env2"
                ]
                batch_env1 = {
                    k: [v[i] for i in ids_of_env1]
                    for k, v in batch.items()
                    if k in self.keys_for_env1
                }
                batch_env2 = {
                    k: [v[i] for i in ids_of_env2]
                    for k, v in batch.items()
                    if k in self.keys_for_env2
                }
                env_output1 = (
                    await self.env1.generate(batch_env1) if ids_of_env1 else None
                )
                env_output2 = (
                    await self.env2.generate(batch_env2) if ids_of_env2 else None
                )
                combined = EnvironmentOutput()

                def _merge(eo: EnvironmentOutput, id_map: list[int], prefix: str):
                    for sub_idx, pb in enumerate(eo.outputs):
                        tgt_idx = id_map[sub_idx]
                        for actor_name, groups in pb.items():
                            for group_name, ao in groups.items():
                                new_group = f"{prefix}/{group_name}"
                                for i in range(len(ao.input_ids)):
                                    combined.add_entry(
                                        problem_idx=tgt_idx,
                                        actor_name=actor_name,
                                        group_name=new_group,
                                        input_ids=ao.input_ids[i],
                                        attention_mask=ao.attention_mask[i]
                                        if ao.attention_mask
                                        else None,
                                        rewards=ao.rewards[i],
                                        reward_components={
                                            k: v[i]
                                            for k, v in ao.reward_components.items()
                                        },
                                        ended_in_eos=ao.ended_in_eos[i]
                                        if ao.ended_in_eos
                                        else None,
                                        metadata=ao.metadata,
                                    )

                if env_output1:
                    _merge(env_output1, ids_of_env1, "env1")
                if env_output2:
                    _merge(env_output2, ids_of_env2, "env2")
                return combined

        return CombinedEnvironment(self, other)
