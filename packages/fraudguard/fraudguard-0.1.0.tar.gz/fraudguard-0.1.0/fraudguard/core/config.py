"""
Configuration management for FraudGuard.
"""

import os
import yaml
from typing import Any, Dict, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FraudGuardConfig:
    """
    Central configuration management for FraudGuard.
    
    Handles loading configuration from files, environment variables,
    and programmatic settings.
    """
    
    DEFAULT_CONFIG = {
        'models': {
            'xgboost': {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            },
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 2,
                'min_samples_leaf': 1,
                'random_state': 42
            }
        },
        'features': {
            'transaction': {
                'amount_bins': [0, 10, 50, 100, 500, 1000, float('inf')],
                'merchant_categories': True,
                'time_features': True
            },
            'behavioral': {
                'lookback_days': 30,
                'velocity_windows': [1, 7, 30],
                'aggregation_functions': ['mean', 'std', 'count']
            }
        },
        'pipeline': {
            'handle_imbalance': True,
            'sampling_strategy': 'auto',
            'cross_validation_folds': 5,
            'test_size': 0.2,
            'random_state': 42
        },
        'deployment': {
            'api_host': '0.0.0.0',
            'api_port': 8000,
            'batch_size': 1000,
            'max_workers': 4
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file:
            self.load_from_file(config_file)
        
        self.load_from_env()
        
    def load_from_file(self, config_file: Union[str, Path]):
        """Load configuration from YAML file."""
        config_path = Path(config_file)
        
        if not config_path.exists():
            logger.warning(f"Configuration file {config_path} not found")
            return
            
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    self._merge_config(self.config, file_config)
                    logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration file: {e}")
            
    def load_from_env(self):
        """Load configuration from environment variables."""
        env_mapping = {
            'FRAUDGUARD_MODEL_TYPE': ('pipeline', 'model_type'),
            'FRAUDGUARD_API_HOST': ('deployment', 'api_host'),
            'FRAUDGUARD_API_PORT': ('deployment', 'api_port'),
            'FRAUDGUARD_LOG_LEVEL': ('logging', 'level'),
            'FRAUDGUARD_RANDOM_STATE': ('pipeline', 'random_state')
        }
        
        for env_var, (section, key) in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                if section not in self.config:
                    self.config[section] = {}
                
                # Convert to appropriate type
                if key in ['api_port', 'random_state', 'n_estimators', 'max_depth']:
                    value = int(value)
                elif key in ['learning_rate', 'subsample', 'test_size']:
                    value = float(value)
                elif key in ['handle_imbalance']:
                    value = value.lower() == 'true'
                    
                self.config[section][key] = value
                logger.debug(f"Set {section}.{key} = {value} from environment")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value (e.g., 'models.xgboost.n_estimators')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value
            value: Value to set
        """
        keys = key_path.split('.')
        config_dict = self.config
        
        for key in keys[:-1]:
            if key not in config_dict:
                config_dict[key] = {}
            config_dict = config_dict[key]
            
        config_dict[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self.config.copy()
    
    def _merge_config(self, base_config: Dict, new_config: Dict):
        """Recursively merge configuration dictionaries."""
        for key, value in new_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(base_config[key], value)
            else:
                base_config[key] = value


# Global configuration instance
config = FraudGuardConfig()
