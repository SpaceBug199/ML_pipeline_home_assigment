import os
import pickle
import tempfile
from typing import Any, Optional, BinaryIO, Tuple
import logging
import shutil

class ModelLoader:
    """Singleton class responsible for loading and providing access to ML models with rollback support."""
    
    _instance = None
    _model = None
    _previous_model = None
    _model_binary_backup = None
    
    def __new__(cls) -> 'ModelLoader':
        """Ensures single instance of ModelLoader exists."""
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def load_model_from_file(self, model_path: str) -> bool:
        """Loads model from a local file path with backup of previous model.
        
        Args:
            model_path: Path to the pickled model file.
            
        Returns:
            True if model loaded successfully, False otherwise.
        """
        if not os.path.exists(model_path):
            logging.error(f"Model file not found at: {model_path}")
            return False
            
        try:
            # Backup current model before loading new one
            self._backup_current_model()
            
            with open(model_path, 'rb') as model_file:
                ModelLoader._model = pickle.load(model_file)
                logging.info(f"model type = {ModelLoader._model}")
                
            # Create binary backup of the new model
            with open(model_path, 'rb') as model_file:
                ModelLoader._model_binary_backup = model_file.read()
                
            logging.info(f"Model successfully loaded from {model_path}")
            return True
        except (pickle.PickleError, IOError) as e:
            logging.error(f"Failed to load model: {e}")
            self._restore_previous_model()
            return False
    
    def load_model_from_binary(self, binary_data: BinaryIO) -> bool:
        """Loads model directly from binary data with backup of previous model.
        
        Args:
            binary_data: Binary file-like object containing the pickled model.
            
        Returns:
            True if model loaded successfully, False otherwise.
        """
        try:
            # Store current position to rewind later
            current_position = binary_data.tell()
            
            # Backup current model before loading new one
            self._backup_current_model()
            
            # Load the new model
            binary_data.seek(current_position)
            ModelLoader._model = pickle.load(binary_data)
            
            # Create binary backup of the new model
            binary_data.seek(current_position)
            ModelLoader._model_binary_backup = binary_data.read()
            
            logging.info("Model successfully loaded from binary data")
            return True
        except (pickle.PickleError, IOError) as e:
            logging.error(f"Failed to load model from binary data: {e}")
            self._restore_previous_model()
            return False
    
    def _backup_current_model(self) -> None:
        """Backs up the currently loaded model before replacing it."""
        ModelLoader._previous_model = ModelLoader._model
    
    def _restore_previous_model(self) -> None:
        """Restores the previous model in case of failure."""
        ModelLoader._model = ModelLoader._previous_model
        logging.info("Restored previous model due to loading failure")
    
    def rollback_model(self) -> bool:
        """Explicitly rolls back to the previous model version.
        
        Returns:
            True if rollback successful, False otherwise.
        """
        if ModelLoader._previous_model is None:
            logging.error("No previous model available for rollback")
            return False
        
        ModelLoader._model = ModelLoader._previous_model
        logging.info("Successfully rolled back to previous model")
        return True
    
    @property
    def model(self) -> Optional[Any]:
        """Provides access to the loaded model.
        
        Returns:
            The loaded model or None if model hasn't been loaded.
        """
        if ModelLoader._model is None:
            logging.warning("Attempted to access model before loading")
        return ModelLoader._model
    
    def persist_model(self, file_path: str) -> bool:
        """Persists the current model to disk.
        
        Args:
            file_path: Path where the model should be saved.
            
        Returns:
            True if successfully persisted, False otherwise.
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                pickle.dump(ModelLoader._model, f)
            logging.info(f"Model successfully persisted to {file_path}")
            return True
        except (IOError, OSError) as e:
            logging.error(f"Failed to persist model: {e}")
            return False