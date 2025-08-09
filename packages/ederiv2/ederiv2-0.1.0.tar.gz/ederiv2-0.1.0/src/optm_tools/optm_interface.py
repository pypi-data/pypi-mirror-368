from abc import ABC, abstractmethod

class OptimizationStrategyAbstract(ABC):
    """
    Abstract base class for optimization strategies.
    """

    @abstractmethod
    def optimize(self, objective_func, initial_guess, **kwargs):
        """
        Perform optimization.

        Args:
            objective_func (callable): The objective function to minimize or maximize.
            initial_guess (Any): Initial guess for the optimizer.
            **kwargs: Additional parameters for the optimizer.

        Returns:
            result (Any): The result of the optimization.
        """
        pass


class Optimizer:
    """
    Optimizer class that uses a given optimization strategy.
    """

    def __init__(self, strategy: OptimizationStrategyAbstract):
        self._strategy = strategy

    @property
    def strategy(self) -> OptimizationStrategyAbstract:
        """
        Get the current optimization strategy.

        Returns:
            OptimizationStrategyAbstract: The current optimization strategy.
        """
        if not isinstance(self._strategy, OptimizationStrategyAbstract):
            raise TypeError("Current strategy is not a valid OptimizationStrategyAbstract instance.")
        return self._strategy

    def set_strategy(self, strategy: OptimizationStrategyAbstract):
        """
        Set a new optimization strategy.

        Args:
            strategy (OptimizationStrategy): The new optimization strategy to use.
        """
        self._strategy = strategy

    def optimize(self, objective_func, initial_guess, **kwargs):
        """
        Optimize the objective function using the provided strategy.

        Args:
            objective_func (callable): The objective function to minimize or maximize.
            initial_guess (Any): Initial guess for the optimizer.
            **kwargs: Additional parameters for the optimizer.

        Returns:
            result (Any): The result of the optimization.
        """
        return self._strategy.optimize(objective_func, initial_guess, **kwargs)