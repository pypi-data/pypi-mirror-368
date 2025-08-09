import numpy as np
from typing import Any, Dict, List, Tuple, Callable
from src.optm_tools.strategies.optm_interface import OptimizationStrategyAbstract

class GeneticAlgorithm(OptimizationStrategyAbstract):
    def __init__(
        self,
        param_space: Dict[str, Tuple[Any, Any]],
        population_size: int = 20,
        generations: int = 30,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        random_state: int = None
    ):
        self._param_space = param_space
        self._population_size = population_size
        self._generations = generations
        self._crossover_rate = crossover_rate
        self._mutation_rate = mutation_rate
        self._random_state = random_state or np.random.randint(0, 10000)
        self._rng = np.random.default_rng(self._random_state)

    def _sample_individual(self) -> Dict[str, Any]:
        individual = {}
        for param, (low, high) in self._param_space.items():
            if isinstance(low, int) and isinstance(high, int):
                individual[param] = self._rng.integers(low, high + 1)
            else:
                individual[param] = self._rng.uniform(low, high)
        return individual

    def _initialize_population(self) -> List[Dict[str, Any]]:
        return [self._sample_individual() for _ in range(self._population_size)]

    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Dict[str, Any]:
        child = {}
        for key in self._param_space:
            child[key] = parent1[key] if self._rng.random() < 0.5 else parent2[key]
        return child

    def _mutate(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        mutant = individual.copy()
        for key, (low, high) in self._param_space.items():
            if self._rng.random() < self._mutation_rate:
                if isinstance(low, int) and isinstance(high, int):
                    mutant[key] = self._rng.integers(low, high + 1)
                else:
                    mutant[key] = self._rng.uniform(low, high)
        return mutant

    def optimize(
        self,
        objective_func: Callable[[Dict[str, Any]], float],
        maximize: bool = False
    ) -> Tuple[Dict[str, Any], float]:
        population = self._initialize_population()
        best_individual = None
        best_score = -np.inf if maximize else np.inf

        for gen in range(self._generations):
            scores = [objective_func(ind) for ind in population]
            if maximize:
                gen_best_idx = int(np.argmax(scores))
                if scores[gen_best_idx] > best_score:
                    best_score = scores[gen_best_idx]
                    best_individual = population[gen_best_idx]
            else:
                gen_best_idx = int(np.argmin(scores))
                if scores[gen_best_idx] < best_score:
                    best_score = scores[gen_best_idx]
                    best_individual = population[gen_best_idx]

            # Selection (tournament)
            selected = []
            for _ in range(self._population_size):
                i, j = self._rng.integers(0, self._population_size, 2)
                if (maximize and scores[i] > scores[j]) or (not maximize and scores[i] < scores[j]):
                    selected.append(population[i])
                else:
                    selected.append(population[j])

            # Crossover and mutation
            next_population = []
            while len(next_population) < self._population_size:
                if self._rng.random() < self._crossover_rate:
                    p1, p2 = self._rng.choice(selected, 2, replace=False)
                    child = self._crossover(p1, p2)
                else:
                    child = self._rng.choice(selected)
                child = self._mutate(child)
                next_population.append(child)
            population = next_population

        return best_individual, best_score