"""
Custom exceptions for FraudGuard package.
"""


class FraudGuardError(Exception):
    """Base exception class for all FraudGuard errors."""
    pass


class ConfigurationError(FraudGuardError):
    """Raised when there's an error in configuration."""
    pass


class FeatureExtractionError(FraudGuardError):
    """Raised when feature extraction fails."""
    pass


class ModelError(FraudGuardError):
    """Raised when there's an error with model training or prediction."""
    pass


class ValidationError(FraudGuardError):
    """Raised when data validation fails."""
    pass


class DeploymentError(FraudGuardError):
    """Raised when deployment operations fail."""
    pass


class DataError(FraudGuardError):
    """Raised when there's an issue with input data."""
    pass
