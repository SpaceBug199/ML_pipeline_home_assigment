# model_executor.py
import pandas as pd
from typing import Dict, List, Any, Tuple
import logging
from utility.model_loader import ModelLoader

class ModelExecutor:
    """Handles model inference execution logic."""
    
    @staticmethod
    def execute_inference(data: Dict[str, Any]) -> Tuple[int, float]:
        """Execute model inference on the provided user data.
        
        Args:
            data: Dictionary containing user tax data with fields:
                age, income, employment_type, marital_status, time_spent_on_platform,
                number_of_sessions, fields_filled_percentage, previous_year_filing,
                device_type, referral_source
                
        Returns:
            A tuple containing (prediction, confidence_score)
            
        Raises:
            ValueError: If required fields are missing or in incorrect format
            RuntimeError: If model execution fails
        """
        try:
            model = ModelLoader()._model
            if model is None:
                raise RuntimeError("Model not loaded")

            # Get raw data DataFrame
            input_df = ModelExecutor._preprocess_data(data)
            logging.info(f"Preprocessed data: {input_df.info()}")
            
            # Let pipeline handle all transformations
            logging.info (f"model = {model}")
            
            prediction_proba = model.predict(input_df)[0]
            prediction = int(prediction_proba[1] >= 0.5)
            confidence = float(prediction_proba[1] if prediction == 1 else prediction_proba[0])
            
            return prediction, confidence
            
        except Exception as e:
            logging.error(f"Inference execution error: {str(e)}")
            raise RuntimeError(f"Failed to execute inference: {str(e)}")
    
    @staticmethod
    def _preprocess_data(data: Dict[str, Any]) -> List[float]:
        """Preprocess raw input data into model-ready features.
        
        Args:
            data: Raw input data dictionary
            
        Returns:
            List of preprocessed features in the correct order for model input
        """
        """Validate data and return DataFrame with raw categorical values."""
       
        required_fields = [
            'age', 'income', 'employment_type', 'marital_status', 
            'time_spent_on_platform', 'number_of_sessions', 
            'fields_filled_percentage', 'previous_year_filing', 
            'device_type', 'referral_source'
        ]
        
        # Validation checks (keep existing)
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        logging.info(f"Data received for inference: {data}")
        
        # Create DataFrame with original string values
        return pd.DataFrame([{
            'employment_type': data['employment_type'].lower(),
            'marital_status': data['marital_status'].lower(),
            'device_type': data['device_type'].lower(),
            'referral_source': data['referral_source'].lower(),
            'age': float(data['age']),
            'income': float(data['income']),
            'time_spent_on_platform': float(data['time_spent_on_platform']),
            'number_of_sessions': float(data['number_of_sessions']),
            'fields_filled_percentage': float(data['fields_filled_percentage']),
            'previous_year_filing': float(data['previous_year_filing'])
        }])
                
        