import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.layers import LSTM, Dense, Input, Dropout, Conv2D, MaxPooling2D, Flatten, Reshape, TimeDistributed
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import h5py
import os
import pickle
import json
import logging
from typing import Tuple, List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class PathogenSpreadModel:
    """
    LSTM-based model for predicting pathogen spread patterns over time and space.
    """
    
    def __init__(
        self,
        spatial_dim: int = 32,
        time_steps: int = 7,
        features: int = 5,
        lstm_units: int = 64,
        learning_rate: float = 0.001,
        dropout_rate: float = 0.2,
        model_path: Optional[str] = None
    ):
        """
        Initialize the model.
        
        Args:
            spatial_dim: Spatial dimension for the grid (square)
            time_steps: Number of time steps to consider for prediction
            features: Number of features per grid cell
            lstm_units: Number of LSTM units
            learning_rate: Learning rate for Adam optimizer
            dropout_rate: Dropout rate for regularization
            model_path: Path to a saved model to load
        """
        self.spatial_dim = spatial_dim
        self.time_steps = time_steps
        self.features = features
        self.lstm_units = lstm_units
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        
        # Initialize model
        if model_path and os.path.exists(model_path):
            logger.info(f"Loading model from {model_path}")
            self.model = load_model(model_path)
        else:
            logger.info("Creating new pathogen

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model, Model
from tensorflow.keras.layers import LSTM, Dense, Input, Dropout, Conv2D, MaxPooling2D, Flatten, Reshape, TimeDistributed
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import h5py
import os
import pickle
import json
import logging
from typing import Tuple, List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class PathogenSpreadModel:
    """
    LSTM-based model for predicting pathogen spread patterns over time and space.
    """
    
    def __init__(
        self,
        spatial_dim: int = 32,
        time_steps: int = 7,
        features: int = 5,
        lstm_units: int = 64,
        learning_rate: float = 0.001,
        dropout_rate: float = 0.2,
        model_path: Optional[str] = None
    ):
        """
        Initialize the model.
        
        Args:
            spatial_dim: Spatial dimension for the grid (square)
            time_steps: Number of time steps to consider for prediction
            features: Number of features per grid cell
            lstm_units: Number of LSTM units
            learning_rate: Learning rate for Adam optimizer
            dropout_rate: Dropout rate for regularization
            model_path: Path to a saved model to load
        """
        self.spatial_dim = spatial_dim
        self.time_steps = time_steps
        self.features = features
        self.lstm_units = lstm_units
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        
        # Initialize model
        if model_path and os.path.exists(model_path):
            logger.info(f"Loading model from {model_path}")
            self.model = load_model(model_path)
        else:
            logger.info("Creating new pathogen spread model")
            self.model = self._build_model()
        
        # Compile model
        self.model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss='mean_squared_error',
            metrics=['mae']
        )
    
    def _build_model(self) -> Model:
        """
        Build the LSTM model architecture.
        
        Returns:
            Compiled TensorFlow model
        """
        # Input shape for sequence of spatial grids with features
        input_shape = (self.time_steps, self.spatial_dim, self.spatial_dim, self.features)
        
        # Create a sequential model
        model = Sequential([
            # Use TimeDistributed to apply the same CNN to each time step
            TimeDistributed(
                Conv2D(32, (3, 3), activation='relu', padding='same'),
                input_shape=input_shape
            ),
            TimeDistributed(MaxPooling2D((2, 2))),
            TimeDistributed(Conv2D(64, (3, 3), activation='relu', padding='same')),
            TimeDistributed(MaxPooling2D((2, 2))),
            
            # Reshape for LSTM input
            TimeDistributed(Flatten()),
            
            # LSTM layers for temporal patterns
            LSTM(self.lstm_units, return_sequences=True),
            Dropout(self.dropout_rate),
            LSTM(self.lstm_units),
            Dropout(self.dropout_rate),
            
            # Dense layers to predict the output grid
            Dense(256, activation='relu'),
            Dense(self.spatial_dim * self.spatial_dim * self.features, activation='linear'),
            
            # Reshape back to grid format
            Reshape((self.spatial_dim, self.spatial_dim, self.features))
        ])
        
        logger.info(f"Model architecture created with input shape {input_shape}")
        model.summary(print_fn=logger.info)
        
        return model
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        epochs: int = 50,
        batch_size: int = 16,
        patience: int = 5,
        save_path: Optional[str] = None
    ) -> Dict[str, List[float]]:
        """
        Train the model.
        
        Args:
            X_train: Training input data (time_steps, spatial_dim, spatial_dim, features)
            y_train: Training target data (spatial_dim, spatial_dim, features)
            X_val: Validation input data
            y_val: Validation target data
            epochs: Number of training epochs
            batch_size: Batch size for training
            patience: Patience for early stopping
            save_path: Path to save the trained model
            
        Returns:
            Dictionary with training history
        """
        # Configure callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=patience,
                restore_best_weights=True
            )
        ]
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            callbacks.append(
                ModelCheckpoint(
                    save_path,
                    monitor='val_loss',
                    save_best_only=True,
                    verbose=1
                )
            )
        
        # Train the model
        logger.info(f"Training model with {X_train.shape[0]} samples for {epochs} epochs")
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=2
        )
        
        # Save the trained model if path is provided and no ModelCheckpoint was used
        if save_path and not any(isinstance(cb, ModelCheckpoint) for cb in callbacks):
            self.save_model(save_path)
        
        return {key: history.history[key] for key in history.history.keys()}
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions with the model.
        
        Args:
            X: Input data of shape (batch_size, time_steps, spatial_dim, spatial_dim, features)
            
        Returns:
            Predicted spread patterns of shape (batch_size, spatial_dim, spatial_dim, features)
        """
        logger.info(f"Making predictions with input of shape {X.shape}")
        return self.model.predict(X)
    
    def predict_spread(
        self,
        initial_state: np.ndarray,
        time_steps: int,
        weather_sequence: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Predict the spread of a pathogen over time.
        
        Args:
            initial_state: Initial state of the system (spatial_dim, spatial_dim, features)
            time_steps: Number of time steps to predict forward
            weather_sequence: Optional sequence of weather conditions for each future time step
            
        Returns:
            Predicted spread over time (time_steps, spatial_dim, spatial_dim, features)
        """
        # Initialize the prediction sequence with the initial state
        current_sequence = np.zeros((1, self.time_steps, self.spatial_dim, self.spatial_dim, self.features))
        current_sequence[0, -1] = initial_state  # Set the last time step to the initial state
        
        # Generate predictions for each future time step
        predictions = []
        
        for i in range(time_steps):
            # Make a prediction for the next time step
            next_step = self.model.predict(current_sequence)
            predictions.append(next_step[0])  # Store prediction
            
            # Update the sequence by shifting and adding the new prediction
            current_sequence[0, :-1] = current_sequence[0, 1:]
            current_sequence[0, -1] = next_step[0]
            
            # If weather sequence is provided, incorporate it
            if weather_sequence is not None and i < len(weather_sequence):
                # Assuming the last feature channels are for weather
                current_sequence[0, -1, :, :, -weather_sequence.shape[-1]:] = weather_sequence[i]
        
        return np.array(predictions)
    
    def generate_probability_heatmap(
        self,
        spread_predictions: np.ndarray,
        threshold: float = 0.5,
        feature_idx: int = 0
    ) -> np.ndarray:
        """
        Generate a probability heatmap from spread predictions.
        
        Args:
            spread_predictions: Model predictions (time_steps, spatial_dim, spatial_dim, features)
            threshold: Threshold for binary classification
            feature_idx: Index of the feature to use for the heatmap
            
        Returns:
            Probability heatmap (spatial_dim, spatial_dim)
        """
        # Extract the specified feature from predictions
        feature_predictions = spread_predictions[:, :, :, feature_idx]
        
        # Calculate probability based on prediction values
        # Assuming values are between 0 and 1 (or apply sigmoid if needed)
        probabilities = np.maximum(0, np.minimum(1, feature_predictions))
        
        # Aggregate probabilities over time (e.g., maximum probability at each point)
        max_probability = np.max(probabilities, axis=0)
        
        return max_probability
    
    def plot_heatmap(
        self,
        heatmap: np.ndarray,
        title: str = "Spread Probability Heatmap",
        save_path: Optional[str] = None
    ) -> None:
        """
        Plot a probability heatmap.
        
        Args:
            heatmap: Probability heatmap (spatial_dim, spatial_dim)
            title: Title for the plot
            save_path: Path to save the plot
        """
        plt.figure(figsize=(10, 8))
        plt.imshow(heatmap, cmap='inferno', interpolation='nearest')
        plt.colorbar(label='Probability')
        plt.title(title)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Heatmap saved to {save_path}")
        
        plt.close()
    
    def save_model(self, save_path: str) -> None:
        """
        Save the model to disk.
        
        Args:
            save_path: Path to save the model
        """
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        self.model.save(save_path)
        
        # Save metadata alongside the model
        metadata = {
            'spatial_dim': self.spatial_dim,
            'time_steps': self.time_steps,
            'features': self.features,
            'lstm_units': self.lstm_units,
            'learning_rate': self.learning_rate,
            'dropout_rate': self.dropout_rate
        }
        
        metadata_path = os.path.join(os.path.dirname(save_path), 
                                    os.path.basename(save_path).split('.')[0] + '_metadata.json')
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        logger.info(f"Model saved to {save_path} with metadata at {metadata_path}")
    
    @classmethod
    def load_model(cls, model_path: str) -> 'PathogenSpreadModel':
        """
        Load a model from disk.
        
        Args:
            model_path: Path to the saved model
            
        Returns:
            Loaded PathogenSpreadModel instance
        """
        # Load metadata if available
        metadata_path = os.path.join(os.path.dirname(model_path), 
                                    os.path.basename(model_path).split('.')[0] + '_metadata.json')
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Create a new instance with the saved metadata
            instance = cls(
                spatial_dim=metadata['spatial_dim'],
                time_steps=metadata['time_steps'],
                features=metadata['features'],
                lstm_units=metadata['lstm_units'],
                learning_rate=metadata['learning_rate'],
                dropout_rate=metadata['dropout_rate'],
                model_path=model_path
            )
        else:
            # Create with default parameters
            logger.warning(f"No metadata found for model at {model_path}, using default parameters")
            instance = cls(model_path=model_path)
        
        return instance


def convert_to_geojson(
    heatmap: np.ndarray,
    origin_lat: float,
    origin_lon: float,
    cell_size_deg: float = 0.01
) -> Dict[str, Any]:
    """
    Convert a probability heatmap to GeoJSON format.
    
    Args:
        heatmap: Probability heatmap (spatial_dim, spatial_dim)
        origin_lat: Latitude of the origin point (bottom-left)
        origin_lon: Longitude of the origin point (bottom-left)
        cell_size_deg: Size of each cell in degrees
        
    Returns:
        GeoJSON object
    """
    features = []
    
    # Get the dimensions of the heatmap
    rows, cols = heatmap.shape
    
    # Create a feature for each cell with probability > 0
    for i in range(rows):
        for j in range(cols):
            prob = heatmap[i, j]
            if prob > 0:
                # Calculate the coordinates of the cell
                min_lon = origin_lon + j * cell_size_deg
                min_lat = origin_lat + i * cell_size_deg
                max_lon = min_lon + cell_size_deg
                max_lat = min_lat + cell_size_deg
                
                # Create a polygon for the cell
                polygon = {
                    "type": "Polygon",
                    "coordinates": [[
                        [min_lon, min_lat],
                        [max_lon, min_lat],
                        [max_lon, max_lat],
                        [min_lon, max_lat],
                        [min_lon, min_lat]
                    ]]
                }
                
                # Create a feature with the polygon and probability
                feature = {
                    "type": "Feature",
                    "geometry": polygon,
                    "properties": {
                        "probability": float(prob),
                        "row": i,
                        "col": j
                    }
                }
                
                features.append(feature)
    
    # Create a FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return geojson

