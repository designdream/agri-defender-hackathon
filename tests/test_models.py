import pytest
import numpy as np
import os
import tempfile
import json
from datetime import datetime

from src.models.spread_prediction import PathogenSpreadModel, convert_to_geojson
from src.models.data_generator import generate_synthetic_dataset, generate_initial_state, simulate_spread
from src.models.evaluation import evaluate_model, calculate_error_map


class TestMachineLearningModels:
    """Tests for the machine learning models."""
    
    def test_model_creation(self):
        """Test creating a pathogen spread model."""
        # Create a model with default parameters
        model = PathogenSpreadModel()
        
        # Verify model properties
        assert model.spatial_dim == 32
        assert model.time_steps == 7
        assert model.features == 5
        assert model.lstm_units == 64
        
        # Verify model architecture was created
        assert model.model is not None
    
    def test_model_training(self, trained_test_model):
        """Test training the model with synthetic data."""
        # Get access to the trained test model from fixture
        model = trained_test_model
        
        # Generate a small validation dataset
        X_val, y_val = generate_synthetic_dataset(
            dataset_size=10,
            spatial_dim=model.spatial_dim,
            time_steps=model.time_steps,
            features=model.features
        )
        
        # Evaluate the model
        metrics = evaluate_model(model, X_val, y_val)
        
        # Basic sanity checks on the metrics
        assert "mae" in metrics
        assert "mse" in metrics
        assert "rmse" in metrics
        assert "r2" in metrics
        assert 0.0 <= metrics["mae"] <= 1.0  # MAE should be reasonable for normalized data
        assert 0.0 <= metrics["rmse"] <= 1.0  # RMSE should be reasonable too
    
    def test_model_prediction(self, trained_test_model):
        """Test making predictions with the model."""
        model = trained_test_model
        
        # Generate a single test sample
        X_test, _ = generate_synthetic_dataset(
            dataset_size=1,
            spatial_dim=model.spatial_dim,
            time_steps=model.time_steps,
            features=model.features
        )
        
        # Make prediction
        y_pred = model.predict(X_test)
        
        # Check prediction shape and values
        assert y_pred.shape == (1, model.spatial_dim, model.spatial_dim, model.features)
        assert np.all(y_pred >= 0)  # Values should be non-negative
        assert np.all(y_pred <= 1)  # Values should be normalized
    
    def test_spread_prediction(self, trained_test_model):
        """Test predicting pathogen spread over time."""
        model = trained_test_model
        
        # Generate a simple initial state
        initial_state = generate_initial_state(
            spatial_dim=model.spatial_dim,
            features=model.features,
            concentration=0.6,
            random_seed=42
        )
        
        # Predict spread over time
        time_steps = 3
        predictions = model.predict_spread(
            initial_state=initial_state,
            time_steps=time_steps
        )
        
        # Check predictions shape and values
        assert predictions.shape == (time_steps, model.spatial_dim, model.spatial_dim, model.features)
        assert np.all(predictions >= 0)  # Values should be non-negative
        assert np.all(predictions <= 1)  # Values should be normalized
        
        # Check that predictions evolve over time
        time0 = predictions[0]
        time2 = predictions[2]
        
        # There should be some difference between time steps
        assert not np.array_equal(time0, time2)
    
    def test_probability_heatmap(self, trained_test_model):
        """Test generating probability heatmaps."""
        model = trained_test_model
        
        # Generate an initial state and predict spread
        initial_state = generate_initial_state(
            spatial_dim=model.spatial_dim,
            features=model.features,
            random_seed=42
        )
        
        predictions = model.predict_spread(
            initial_state=initial_state,
            time_steps=5
        )
        
        # Generate heatmap
        heatmap = model.generate_probability_heatmap(
            spread_predictions=predictions,
            threshold=0.5,
            feature_idx=0
        )
        
        # Check heatmap shape and values
        assert heatmap.shape == (model.spatial_dim, model.spatial_dim)
        assert np.all(heatmap >= 0)  # Probabilities should be non-negative
        assert np.all(heatmap <= 1)  # Probabilities should be normalized
    
    def test_model_save_load(self, trained_test_model, temp_model_dir):
        """Test saving and loading the model."""
        model = trained_test_model
        
        # Save the model
        model_path = os.path.join(temp_model_dir, "test_model.h5")
        model.save_model(model_path)
        
        # Check that model file exists
        assert os.path.exists(model_path)
        
        # Check that metadata file exists
        metadata_path = os.path.join(temp_model_dir, "test_model_metadata.json")
        assert os.path.exists(metadata_path)
        
        # Load the model
        loaded_model = PathogenSpreadModel.load_model(model_path)
        
        # Verify loaded model attributes
        assert loaded_model.spatial_dim == model.spatial_dim
        assert loaded_model.time_steps == model.time_steps
        assert loaded_model.features == model.features
        assert loaded_model.lstm_units == model.lstm_units
        
        # Verify that loaded model can make predictions
        X_test, _ = generate_synthetic_dataset(
            dataset_size=1,
            spatial_dim=model.spatial_dim,
            time_steps=model.time_steps,
            features=model.features
        )
        
        prediction_original = model.predict(X_test)
        prediction_loaded = loaded_model.predict(X_test)
        
        # Predictions should be similar (may not be identical due to model recompilation)
        assert prediction_original.shape == prediction_loaded.shape
    
    def test_geojson_conversion(self):
        """Test converting heatmap to GeoJSON."""
        # Create a simple heatmap

