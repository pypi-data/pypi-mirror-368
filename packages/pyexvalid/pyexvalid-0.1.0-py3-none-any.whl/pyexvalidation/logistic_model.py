from typing import Dict
import numpy as np
import pandas as pd


class LogisticModel:
    """
    A class that represents a logistic regression model.

    This class stores the model's coefficients, intercept, and outcome variable name, and can be used for probability predictions.
    """

    def __init__(
        self, intercept: float, coefs_dict: Dict[str, float], outcome: str = "outcome"
    ) -> None:
        """
        Initialize the LogisticModel.

        Parameters:
            intercept (float): The model's intercept (constant term).
            coefs_dict (Dict[str, float]): A dictionary mapping predictor names to their coefficients.
            outcome (str): The name of the outcome variable.
        """
        if not isinstance(coefs_dict, dict):
            raise TypeError("coefs_dict must be a dictionary.")
        if not isinstance(outcome, str):
            raise TypeError("outcome must be a string.")
        if not isinstance(intercept, (int, float)):
            raise TypeError("intercept must be a numeric value.")

        self.coefficients = coefs_dict
        self.outcome_name = outcome
        self.intercept = intercept
        self.predictors = list(self.coefficients.keys())

    def __str__(self) -> str:
        """
        Return a string representation of the logistic regression model.
        """
        # Use " + " to connect all "coefficient * variable_name" pairs
        parts = [f"{coef:.4f} * {name}" for name, coef in self.coefficients.items()]
        equation = " + ".join(parts)
        # Replace "+ -" with "- " for negative coefficients
        equation = equation.replace("+ -", "- ")
        return f"log-odds({self.outcome_name}) = {self.intercept:.4f} + {equation}"

    def calculate_log_odds(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate the log-odds for the given data.

        Parameters:
            data (pd.DataFrame): A DataFrame containing the predictor variables.

        Returns:
            pd.Series: A Series containing the log-odds for each observation.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame.")

        log_odds = (
            data[self.predictors].dot(pd.Series(self.coefficients)) + self.intercept
        )
        return pd.Series(log_odds)

    def calculate_probability(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate the predicted probabilities for the given data.

        Parameters:
            data (pd.DataFrame): A DataFrame containing the predictor variables.

        Returns:
            pd.Series: A Series containing the predicted probabilities for each observation.
        """
        log_odds = self.calculate_log_odds(data)
        probabilities = 1 / (1 + np.exp(-log_odds))

        return pd.Series(probabilities)

    def predict_all(self, data: pd.DataFrame, keep_data: bool = False) -> pd.DataFrame:
        """
        Predict the outcome for the given data.

        Parameters:
            data (pd.DataFrame): A DataFrame containing the predictor variables.

        Returns:
            pd.DataFrame: A DataFrame with the predicted probabilities and the outcome variable.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame.")

        linear_predictors = self.calculate_log_odds(data)
        probabilities = self.calculate_probability(data)

        # Create a DataFrame to hold the results
        df = pd.DataFrame(index=data.index)
        # Add the outcome variable if it exists in the data
        df.loc[:, "outcome"] = (
            data[self.outcome_name] if self.outcome_name in data.columns else None
        )
        df.loc[:, "linear_predictor"] = linear_predictors
        df.loc[:, "probabilities"] = probabilities

        if keep_data:
            df = pd.concat([df, data], axis=1)

        return df
