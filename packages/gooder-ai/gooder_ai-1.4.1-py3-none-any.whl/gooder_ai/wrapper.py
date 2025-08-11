from abc import ABC, abstractmethod


# Abstract base class
class ModelWrapper(ABC):
    @abstractmethod
    def predict_proba(self, x):
        """
        Predict class probabilities for the input data.
        Args:
            x (array-like): Input features for which to predict probabilities.
        Returns:
            array-like: Predicted probabilities for each class.
        Example:
            >>> class MyModel(ModelWrapper):
            ...     def predict_proba(self, x):
            ...         # Implement prediction logic here
            ...         return [[0.2, 0.8], [0.6, 0.4]]
        """
        pass

    @property
    @abstractmethod
    def classes_(self):
        """
        Returns the class labels for the model.
        Expected return type: list or numpy.array of class labels.
        """
        pass
