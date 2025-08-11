from __future__ import annotations

from typing import Iterator, List, Union, overload

import numpy as np

from pymoors.typing import OneDArray, TwoDArray


class Individual:
    def __init__(
        self,
        *,
        genes: OneDArray,
        fitness: OneDArray,
        rank: int | None = None,
        survival_score: float | None = None,
        constraints: OneDArray | None = None,
    ):
        self.genes = genes
        self.fitness = fitness
        self.rank = rank
        self.constraints = constraints
        self.survival_score = survival_score

    @property
    def is_best(self) -> bool:
        if self.rank is not None:
            return self.rank == 0
        return True

    @property
    def is_feasible(self) -> bool:
        if self.constraints is None:
            return True
        return bool(np.all(np.array(self.constraints) <= 0))


class Population:
    def __init__(
        self,
        *,
        genes: TwoDArray,
        fitness: TwoDArray,
        rank: OneDArray | None = None,
        survival_score: OneDArray | None = None,
        constraints: TwoDArray | None = None,
    ):
        if len(genes) != len(fitness):
            raise ValueError("genes and fitness arrays must have the same lenght")
        if constraints is not None and len(constraints) != len(genes):
            raise ValueError("constraints must have the same length as genes")
        if rank is not None and len(rank) != len(genes):
            raise ValueError("rank must have the same length as genes")
        if survival_score is not None and len(survival_score) != len(genes):
            raise ValueError("survival_score must have the same length as genes")

        self.genes = genes
        self.fitness = fitness
        self.rank = rank
        self.survival_score = survival_score
        self.constraints = constraints
        # Set private attribute for whose individuals with rank = 0
        self._best = None
        self._best_as_population = None

    @overload
    def __getitem__(self, index: int) -> Individual: ...

    @overload
    def __getitem__(self, index: slice) -> List[Individual]: ...

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[Individual, List[Individual]]:
        if isinstance(index, int):
            return Individual(
                genes=self.genes[index],
                fitness=self.fitness[index],
                rank=int(self.rank[index]) if self.rank is not None else None,
                survival_score=float(self.survival_score[index])
                if self.survival_score is not None
                else None,
                constraints=self.constraints[index]
                if self.constraints is not None
                else None,
            )
        if isinstance(index, slice):
            return [
                Individual(
                    genes=self.genes[i],
                    fitness=self.fitness[i],
                    rank=int(self.rank[i]) if self.rank is not None else None,
                    survival_score=float(self.survival_score[i])
                    if self.survival_score is not None
                    else None,
                    constraints=self.constraints[i]
                    if self.constraints is not None
                    else None,
                )
                for i in range(*index.indices(len(self.genes)))
            ]
        raise TypeError(f"indices must be integers or slices, not {type(index)}")

    def __iter__(self) -> Iterator[Individual]:
        for i in range(len(self.genes)):
            yield self[i]

    def __len__(self) -> int:
        return len(self.genes)

    @property
    def best(self) -> List[Individual]:
        if self._best is None:
            if self.rank is None:
                self._best = [i for i in self]
            else:
                self._best = [i for i in self if i.is_best]
        return self._best

    @property
    def best_as_population(self) -> Population:
        if self._best_as_population is None:
            if self.rank is None:
                self._best_as_population = self
            else:
                # Create a boolean mask where rank == 0
                mask = self.rank == 0
                best_genes = self.genes[mask]
                best_fitness = self.fitness[mask]
                best_rank = self.rank[mask]
                best_survival_score = (
                    self.survival_score[mask]
                    if self.survival_score is not None
                    else None
                )
                best_constraints = (
                    self.constraints[mask] if self.constraints is not None else None
                )

                self._best_as_population = Population(
                    genes=best_genes,
                    fitness=best_fitness,
                    rank=best_rank,
                    survival_score=best_survival_score,
                    constraints=best_constraints,
                )
        return self._best_as_population
