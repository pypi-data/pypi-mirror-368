"""Model evaluation and performance assessment utilities.

This module provides comprehensive model evaluation tools including
cross-validation, hyperparameter tuning, performance metrics, and
model comparison utilities.
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar, Optional, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    roc_curve,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Import custom exceptions
from ..utils.exceptions import ModelTrainingError

# Configure logging
logger = logging.getLogger(__name__)

# Type aliases for better readability
ArrayLike = Union[np.ndarray, pd.Series]
DataFrame = pd.DataFrame
Series = pd.Series


class ModelTrainer:
    """Handles model training, hyperparameter tuning, and evaluation."""

    DEFAULT_BASE_MODELS: ClassVar[dict[str, BaseEstimator]] = {
        "rf": RandomForestClassifier(random_state=42),
        "svm": SVC(probability=True, random_state=42),
        "lr": LogisticRegression(random_state=42, max_iter=10000),
    }

    DEFAULT_SCORING: ClassVar[dict[str, str]] = {
        "roc_auc": "roc_auc",
        "precision": make_scorer(precision_score, zero_division=0),
        "recall": make_scorer(recall_score, zero_division=0),
        "accuracy": "accuracy",
        "f1": make_scorer(f1_score, zero_division=0),
    }

    MODEL_NAME_MAP: ClassVar[dict[str, str]] = {
        "Random Forest": "rf",
        "SVM": "svm",
        "Logistic Regression": "lr",
    }

    @staticmethod
    def create_cv_splits(
        X: DataFrame,
        y: Series,
        n_splits: int = 3,
        random_state: int = 42,
    ) -> list[tuple[np.ndarray, np.ndarray]]:
        """
        Create cross-validation splits using stratified k-fold.

        Args:
            X: Feature matrix
            y: Target variable
            n_splits: Number of CV folds
            random_state: Random state for reproducibility

        Returns:
            List of (train_indices, test_indices) tuples

        Raises:
            ValueError: If there's only one class in the target variable
        """
        # Check if there's only one class
        if len(y.unique()) < 2:
            raise ValueError("The least populated class in y has only 1 member, which is less than n_splits=3.")

        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        return list(cv.split(X, y))

    @staticmethod
    def tune_model_parameters(
        X: DataFrame,
        y: Series,
        model_type: str,
        cv_splits: list[tuple[np.ndarray, np.ndarray]],
        random_state: int = 42,
        params: Optional[dict[str, Any]] = None,
    ) -> tuple[Pipeline, dict[str, Any], dict[str, Any], int, float]:
        """
        Tune model hyperparameters using randomized search.

        Args:
            X: Feature matrix
            y: Target variable
            model_type: Type of model ('rf', 'svm', 'lr')
            cv_splits: Cross-validation splits
            random_state: Random state for reproducibility
            params: Dictionary containing model parameters

        Returns:
            Tuple of (best_estimator, best_params, cv_results, best_index, best_score)
        """
        if params is None:
            params = {}

        base_models = params.get("base_models", ModelTrainer.DEFAULT_BASE_MODELS)
        scoring = params.get("scoring", ModelTrainer.DEFAULT_SCORING)

        if model_type not in base_models:
            raise ModelTrainingError(f"Model type '{model_type}' not supported")

        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model", base_models[model_type]),
        ])

        param_grid = params.get("param_grids", {}).get(model_type, {})
        pipeline_param_grid = {f"model__{key}": value for key, value in param_grid.items()}

        random_search_params = params.get(
            "random_search_params",
            {
                "n_iter": 20,
                "n_jobs": -1,
                "verbose": 0,
                "refit": "roc_auc",  # Specify which metric to use for refitting
                "return_train_score": True,  # Return training scores for analysis
            },
        )

        # Remove scoring from random_search_params to avoid duplicate parameter
        random_search_params_clean = {k: v for k, v in random_search_params.items() if k != "scoring"}

        random_search = RandomizedSearchCV(
            pipeline,
            pipeline_param_grid,
            cv=cv_splits,
            scoring=scoring,
            random_state=random_state,
            **random_search_params_clean,
        )

        random_search.fit(X, y)

        return (
            random_search.best_estimator_,
            random_search.best_params_,
            random_search.cv_results_,
            int(random_search.best_index_),
            random_search.best_score_,
        )

    @staticmethod
    def _extract_fold_metrics(
        model_cv_results: dict[str, Any],
        best_idx: int,
        fold_idx: int,
    ) -> dict[str, float]:
        """Extract metrics for a specific fold."""
        return {
            "accuracy": model_cv_results[f"split{fold_idx}_test_accuracy"][best_idx],
            "precision": model_cv_results[f"split{fold_idx}_test_precision"][best_idx],
            "recall": model_cv_results[f"split{fold_idx}_test_recall"][best_idx],
            "f1": model_cv_results[f"split{fold_idx}_test_f1"][best_idx],
            "roc_auc": model_cv_results[f"split{fold_idx}_test_roc_auc"][best_idx],
        }

    @staticmethod
    def _calculate_optimal_threshold(y_true: Series, y_prob: np.ndarray) -> float:
        """Calculate optimal classification threshold using ROC curve."""
        fpr, tpr, thresholds = roc_curve(y_true, y_prob[:, 1])
        j_scores = tpr - fpr
        j_best_idx = j_scores.argmax()
        return float(thresholds[j_best_idx])

    @staticmethod
    def _create_model_metrics(
        model_name: str,
        best_score: float,
        model_cv_results: dict[str, Any],
        best_idx: int,
        best_params: dict[str, Any],
        features: list[str],
        model: Pipeline,
    ) -> dict[str, Any]:
        """Create comprehensive metrics dictionary for a model."""
        metrics = {
            "Model": model_name,
            "Best AUC Score": f"{best_score:.3f}",
            "Accuracy": (
                f"{model_cv_results['mean_test_accuracy'][best_idx]:.3f} ± "
                f"{model_cv_results['std_test_accuracy'][best_idx]:.3f}"
            ),
            "Precision": (
                f"{model_cv_results['mean_test_precision'][best_idx]:.3f} ± "
                f"{model_cv_results['std_test_precision'][best_idx]:.3f}"
            ),
            "Recall": (
                f"{model_cv_results['mean_test_recall'][best_idx]:.3f} ± "
                f"{model_cv_results['std_test_recall'][best_idx]:.3f}"
            ),
            "F1 Score": (
                f"{model_cv_results['mean_test_f1'][best_idx]:.3f} ± {model_cv_results['std_test_f1'][best_idx]:.3f}"
            ),
            "ROC AUC": (
                f"{model_cv_results['mean_test_roc_auc'][best_idx]:.3f} ± "
                f"{model_cv_results['std_test_roc_auc'][best_idx]:.3f}"
            ),
            "Train-Test AUC": f"{model_cv_results.get('mean_train_roc_auc', [0])[best_idx] - model_cv_results['mean_test_roc_auc'][best_idx]:.3f}",
            "Best Parameters": best_params,
        }

        # Add feature importances for Random Forest
        if model_name == "Random Forest":
            feature_imp = pd.DataFrame({
                "feature": features,
                "importance": model.named_steps["model"].feature_importances_,
            }).sort_values("importance", ascending=False)
            metrics["Feature Importances"] = feature_imp  # type: ignore[assignment]
        return metrics

    @staticmethod
    def train_evaluate_models(
        X: DataFrame,
        y: Series,
        features: list[str],
        models_to_evaluate: Optional[list[str]] = None,
        params: Optional[dict[str, Any]] = None,
        n_splits: int = 3,
        random_state: int = 42,
    ) -> dict[str, Any]:
        """
        Train and evaluate multiple models with cross-validation.

        Args:
            X: Feature matrix
            y: Target variable
            features: List of feature names to use
            models_to_evaluate: List of model names to evaluate
            params: Model parameters dictionary
            n_splits: Number of CV folds
            random_state: Random state for reproducibility

        Returns:
            Dictionary containing training results and model information
        """
        if models_to_evaluate is None:
            models_to_evaluate = ["Random Forest", "SVM", "Logistic Regression"]

        if params is None:
            params = {}

        X_selected = X[features]
        cv_splits = ModelTrainer.create_cv_splits(X_selected, y, n_splits, random_state)

        models = {}
        best_params = {}
        cv_results = {}
        best_idxs = {}
        best_scores = {}

        for model_name in models_to_evaluate:
            if model_name not in ModelTrainer.MODEL_NAME_MAP:
                raise ModelTrainingError(f"Model {model_name} not supported")

            logger.info(f"Tuning {model_name}...")

            try:
                model, params_result, cv_result, best_idx, best_score = ModelTrainer.tune_model_parameters(
                    X_selected,
                    y,
                    ModelTrainer.MODEL_NAME_MAP[model_name],
                    cv_splits,
                    random_state,
                    params=params,
                )
                models[model_name] = model
                best_params[model_name] = params_result
                cv_results[model_name] = cv_result
                best_idxs[model_name] = best_idx
                best_scores[model_name] = best_score
            except Exception:
                logger.exception("Failed to train %s", model_name)
                continue

        results = []
        fold_data: dict[str, list[dict[str, Any]]] = {}
        best_fold_metrics: Optional[dict[str, float]] = None
        best_fold_idx: Optional[int] = None

        for name, model in models.items():
            model_cv_results = cv_results[name]
            best_idx = best_idxs[name]

            metrics = ModelTrainer._create_model_metrics(
                name, best_scores[name], model_cv_results, best_idx, best_params[name], features, model
            )

            fold_predictions = []
            for i, (_train_idx, test_idx) in enumerate(cv_splits):
                y_true = y.iloc[test_idx]
                y_prob = model.predict_proba(X_selected.iloc[test_idx])

                best_threshold = ModelTrainer._calculate_optimal_threshold(y_true, y_prob)
                y_pred = (y_prob[:, 1] >= best_threshold).astype(int)

                fold_metrics = ModelTrainer._extract_fold_metrics(model_cv_results, best_idx, i)

                if best_fold_metrics is None or fold_metrics["roc_auc"] > best_fold_metrics["roc_auc"]:
                    best_fold_idx = i
                    best_fold_metrics = fold_metrics

                fold_data_dict = {
                    "y_true": y_true,
                    "y_prob": y_prob,
                    "y_pred": y_pred,
                    "metrics": fold_metrics,
                    "estimator": model,
                    "fold_idx": i,
                    "threshold": best_threshold,
                }

                fold_predictions.append(fold_data_dict)

            fold_data[name] = fold_predictions
            results.append(metrics)

        results_df = pd.DataFrame(results)
        best_model = "Logistic Regression"  # Default best model

        return {
            "model_results": results_df,
            "fitted_models": models,
            "best_params": best_params,
            "fold_data": fold_data,
            "best_model": best_model,
            "best_fold_idx": best_fold_idx,
        }

    @staticmethod
    def analyze_best_models(fold_data: dict[str, list[dict[str, Any]]], fold_idx: int = 0) -> dict[str, dict[str, Any]]:
        """
        Analyze performance of best models for a specific fold.

        Args:
            fold_data: Dictionary containing fold predictions for each model
            fold_idx: Index of the fold to analyze

        Returns:
            Dictionary containing detailed analysis results for each model
        """
        detailed_results = {}

        for model_name, folds in fold_data.items():
            if fold_idx >= len(folds):
                logger.warning(f"Fold {fold_idx} not available for {model_name}")
                continue

            fold = folds[fold_idx]
            y_true = fold["y_true"]
            y_pred = fold["y_pred"]

            try:
                report = classification_report(y_true, y_pred, output_dict=True)

                detailed_results[model_name] = {
                    "Classification Report": pd.DataFrame(report).transpose(),
                    "Confusion Matrix": confusion_matrix(y_true, y_pred),
                }
            except Exception:
                logger.exception("Failed to analyze %s", model_name)
                continue

        return detailed_results

    @staticmethod
    def run_modeling(
        data: DataFrame,
        features: list[str],
        target_class: str = "Lung Cancer",
        class_column: str = "class_final",
        models: Optional[list[str]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> tuple[dict[str, dict[str, Any]], dict[str, Any], str]:
        """
        Main function for running complete modeling pipeline.

        Args:
            data: Input data containing features and class labels
            features: List of feature names to use
            target_class: Target class to predict
            class_column: Name of the column containing class labels
            models: List of model names to evaluate
            params: Model parameters dictionary

        Returns:
            Tuple of (detailed_results, training_results, best_model_name)
        """
        if class_column not in data.columns:
            raise ModelTrainingError(f"Class column '{class_column}' not found in data")

        if not features:
            raise ModelTrainingError("No features provided")

        missing_features = [f for f in features if f not in data.columns]
        if missing_features:
            raise ModelTrainingError(f"Missing features: {missing_features}")

        X = data.drop([class_column], axis=1)
        y = (data[class_column] == target_class).astype(int)

        if y.sum() == 0 or y.sum() == len(y):
            raise ModelTrainingError(f"Target class '{target_class}' not found or all samples have same class")

        # Train and evaluate models with parameter tuning
        results = ModelTrainer.train_evaluate_models(X, y, features, models_to_evaluate=models, params=params)

        # Print comprehensive results
        logger.info("\\nModel Performance Metrics:")
        logger.info(results["model_results"])

        best_model = results["best_model"]

        # Analyze best models
        logger.info("\\nDetailed Analysis of Best Models:")

        detailed_results = ModelTrainer.analyze_best_models(results["fold_data"], fold_idx=results["best_fold_idx"])

        return detailed_results, results, best_model
