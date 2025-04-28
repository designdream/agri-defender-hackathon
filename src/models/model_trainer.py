#!/usr/bin/env python3
"""
Model trainer script for the AgriDefender pathogen spread prediction model.
This script trains an LSTM-based model to predict the spread of biological threats in crops.
"""

import os
import sys
import argparse
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Add project root to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.spread_prediction import PathogenSpreadModel
from src.models.data_generator import generate_synthetic_dataset, generate_showcase_dataset
from src.models.evaluation import evaluate_model, plot_evaluation_metrics, visualize_predictions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def setup_training_dirs(output_dir: str) -> Dict[str, str]:
    """
    Set up directories for training outputs.
    
    Args:
        output_dir: Base directory for training outputs
        
    Returns:
        Dictionary of directory paths
    """
    # Generate timestamp for unique run identification
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(output_dir, f"run_{timestamp}")
    
    # Create subdirectories
    dirs = {
        "run": run_dir,
        "models": os.path.join(run_dir, "models"),
        "plots": os.path.join(run_dir, "plots"),
        "evaluation": os.path.join(run_dir, "evaluation"),
        "logs": os.path.join(run_dir, "logs")
    }
    
    # Create all directories
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")
    
    return dirs


def generate_training_data(
    args: argparse.Namespace,
    data_dir: Optional[str] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate or load training data.
    
    Args:
        args: Command-line arguments
        data_dir: Directory to save generated data
        
    Returns:
        Tuple of (X_train, y_train, X_val, y_val)
    """
    logger.info("Generating training data...")
    
    # Generate synthetic dataset
    threat_types = args.threat_types.split(",") if args.threat_types else None
    
    X, y = generate_synthetic_dataset(
        dataset_size=args.dataset_size,
        spatial_dim=args.spatial_dim,
        time_steps=args.time_steps,
        features=args.features,
        threat_types=threat_types
    )
    
    # Split into training and validation sets
    val_size = int(len(X) * args.val_split)
    train_size = len(X) - val_size
    
    # Shuffle the data
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    X_train, X_val = X[:train_size], X[train_size:]
    y_train, y_val = y[:train_size], y[train_size:]
    
    logger.info(f"Training set: {X_train.shape}, Validation set: {X_val.shape}")
    
    # Save the data if a directory is provided
    if data_dir:
        np.save(os.path.join(data_dir, "X_train.npy"), X_train)
        np.save(os.path.join(data_dir, "y_train.npy"), y_train)
        np.save(os.path.join(data_dir, "X_val.npy"), X_val)
        np.save(os.path.join(data_dir, "y_val.npy"), y_val)
        logger.info(f"Saved training data to {data_dir}")
    
    return X_train, y_train, X_val, y_val


def train_model(args: argparse.Namespace, dirs: Dict[str, str]) -> PathogenSpreadModel:
    """
    Train the pathogen spread prediction model.
    
    Args:
        args: Command-line arguments
        dirs: Directory paths for outputs
        
    Returns:
        Trained PathogenSpreadModel
    """
    # Generate or load training data
    X_train, y_train, X_val, y_val = generate_training_data(
        args,
        data_dir=os.path.join(dirs["run"], "data") if args.save_data else None
    )
    
    # Configure TensorFlow for performance
    if args.mixed_precision:
        policy = tf.keras.mixed_precision.Policy('mixed_float16')
        tf.keras.mixed_precision.set_global_policy(policy)
        logger.info("Using mixed precision training")
    
    # Set memory growth for GPUs if available
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            logger.info(f"Using {len(gpus)} GPU(s) for training")
        except RuntimeError as e:
            logger.warning(f"Error setting GPU memory growth: {e}")
    
    # Create and train the model
    logger.info("Creating and training the model...")
    
    model = PathogenSpreadModel(
        spatial_dim=args.spatial_dim,
        time_steps=args.time_steps,
        features=args.features,
        lstm_units=args.lstm_units,
        learning_rate=args.learning_rate,
        dropout_rate=args.dropout_rate
    )
    
    # Create model save path
    model_save_path = os.path.join(dirs["models"], "spread_model.h5")
    
    # Train the model
    history = model.train(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        epochs=args.epochs,
        batch_size=args.batch_size,
        patience=args.patience,
        save_path=model_save_path
    )
    
    # Plot training history
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(history['loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.title('Loss During Training')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history['mae'], label='Train MAE')
    plt.plot(history['val_mae'], label='Val MAE')
    plt.title('Mean Absolute Error During Training')
    plt.xlabel('Epoch')
    plt.ylabel('MAE')
    plt.legend()
    
    history_plot_path = os.path.join(dirs["plots"], "training_history.png")
    plt.tight_layout()
    plt.savefig(history_plot_path)
    logger.info(f"Saved training history plot to {history_plot_path}")
    
    # Save training history as JSON
    history_json_path = os.path.join(dirs["logs"], "training_history.json")
    with open(history_json_path, 'w') as f:
        json.dump({k: [float(v) for v in vals] for k, vals in history.items()}, f, indent=4)
    
    logger.info(f"Saved training history to {history_json_path}")
    logger.info(f"Model trained and saved to {model_save_path}")
    
    return model


def evaluate_trained_model(
    model: PathogenSpreadModel,
    args: argparse.Namespace,
    dirs: Dict[str, str]
) -> Dict[str, Any]:
    """
    Evaluate the trained model.
    
    Args:
        model: Trained PathogenSpreadModel
        args: Command-line arguments
        dirs: Directory paths for outputs
        
    Returns:
        Evaluation metrics
    """
    logger.info("Evaluating the trained model...")
    
    # Generate a small validation set if not already done
    if args.quick_eval:
        logger.info("Generating a small validation set for quick evaluation")
        threat_types = args.threat_types.split(",") if args.threat_types else None
        
        X_val, y_val = generate_synthetic_dataset(
            dataset_size=50,  # Small dataset for quick evaluation
            spatial_dim=args.spatial_dim,
            time_steps=args.time_steps,
            features=args.features,
            threat_types=threat_types
        )
    else:
        # Use the larger validation set from the training data
        _, _, X_val, y_val = generate_training_data(args)
    
    # Evaluate the model
    metrics = evaluate_model(model, X_val, y_val)
    
    # Plot evaluation metrics
    metrics_plot_path = os.path.join(dirs["evaluation"], "metrics.png")
    plot_evaluation_metrics(metrics, save_path=metrics_plot_path)
    
    # Visualize some predictions
    sample_indices = np.random.choice(len(X_val), min(5, len(X_val)), replace=False)
    visualize_predictions(
        model=model,
        X_samples=X_val,
        y_true=y_val,
        sample_indices=sample_indices,
        save_dir=os.path.join(dirs["evaluation"], "prediction_samples")
    )
    
    # Generate showcase examples
    if args.generate_showcase:
        logger.info("Generating showcase examples")
        showcase_data = generate_showcase_dataset()
        
        # Evaluate on showcase data
        from src.models.evaluation import evaluate_on_showcase
        showcase_results = evaluate_on_showcase(
            model=model,
            showcase_data=showcase_data,
            time_steps=args.time_steps,
            save_dir=os.path.join(dirs["evaluation"], "showcase")
        )
        
        # Save showcase results
        showcase_results_path = os.path.join(dirs["evaluation"], "showcase_results.json")
        with open(showcase_results_path, 'w') as f:
            json_results = {}
            for threat_type, threat_metrics in showcase_results.items():
                json_results[threat_type] = {k: float(v) if isinstance(v, np.number) else v 
                                          for k, v in threat_metrics.items() 
                                          if k != 'sample_metrics'}
            
            json.dump(json_results, f, indent=4)
        
        logger.info(f"Saved showcase evaluation results to {showcase_results_path}")
    
    # Save evaluation metrics
    metrics_json_path = os.path.join(dirs["evaluation"], "metrics.json")
    with open(metrics_json_path, 'w') as f:
        # Remove sample_metrics which may contain numpy arrays
        metrics_copy = {k: v for k, v in metrics.items() if k != 'sample_metrics'}
        json.dump(metrics_copy, f, indent=4)
    
    logger.info(f"Saved evaluation metrics to {metrics_json_path}")
    
    return metrics


def save_training_config(args: argparse.Namespace, dirs: Dict[str, str]) -> None:
    """
    Save the training configuration.
    
    Args:
        args: Command-line arguments
        dirs: Directory paths for outputs
    """
    # Convert args to dictionary
    config = vars(args)
    
    # Save configuration
    config_path = os.path.join(dirs["logs"], "training_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    logger.info(f"Saved training configuration to {config_path}")


def main():
    """Main function to run the training pipeline."""
    parser = argparse.ArgumentParser(description="Train a pathogen spread prediction model")
    
    # Data parameters
    parser.add_argument("--dataset-size", type=int, default=1000, help="Number of samples to generate")
    parser.add_argument("--spatial-dim", type=int, default=32, help="Spatial dimension of the grid")
    parser.add_argument("--time-steps", type=int, default=7, help="Number of time steps in the input sequence")
    parser.add_argument("--features", type=int, default=5, help="Number of features per grid cell")
    parser.add_argument("--threat-types", type=str, default=None, help="Comma-separated list of threat types")
    parser.add_argument("--val-split", type=float, default=0.2, help="Validation set split ratio")
    parser.add_argument("--save-data", action="store_true", help="Save generated training data")
    
    # Model parameters
    parser.add_argument("--lstm-units", type=int, default=64, help="Number of LSTM units")
    parser.add_argument("--dropout-rate", type=float, default=0.2, help="Dropout rate")
    
    # Training parameters
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size for training")
    parser.add_argument("--epochs", type=int, default=50, help="Maximum number of epochs")
    parser.add_argument("--patience", type=int, default=5, help="Patience for early stopping")
    parser.add_argument("--learning-rate", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--mixed-precision", action="store_true", help="Use mixed precision training")
    
    # Evaluation parameters
    parser.add_argument("--quick-eval", action="store_true", help="Perform a quick evaluation on a small dataset")
    parser.add_argument("--generate-showcase", action="store_true", help="Generate showcase examples")
    
    # Output parameters
    parser.add_argument("--output-dir", type=str, default="./outputs", help="Output directory")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up directories
    dirs = setup_training_dirs(args.output_dir)
    
    # Save training configuration
    save_training_config(args, dirs)
    
    try:
        # Train the model
        model = train_model(args, dirs)
        
        # Evaluate the model
        metrics = evaluate_trained_model(model, args, dirs)
        
        logger.info(f"Training and evaluation completed successfully!")
        logger.info(f"Model saved to {os.path.join(dirs['models'], 'spread_model.h5')}")
        logger.info(f"All outputs saved to {dirs['run']

import os
import argparse
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import json
import logging
from datetime import datetime
from typing import Tuple, Dict, Any, Optional

from src.models.spread_prediction import PathogenSpreadModel
from src.models.data_generator import generate_synthetic_dataset
from src.models.evaluation import evaluate_model, plot_evaluation_metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def train_model(
    spatial_dim: int = 32,
    time_steps: int = 7,
    features: int = 5,
    lstm_units: int = 64,
    learning_rate: float = 0.001,
    batch_size: int = 16,
    epochs: int = 50,
    patience: int = 5,
    dataset_size: int = 1000,
    val_split: float = 0.2,
    model_dir: str = './models',
    plot_dir: str = './plots',
    threat_types: Optional[list] = None
) -> Tuple[PathogenSpreadModel, Dict[str, Any]]:
    """
    Train a pathogen spread prediction model.
    
    Args:
        spatial_dim: Spatial dimension for the grid (square)
        time_steps: Number of time steps to consider for prediction
        features: Number of features per grid cell
        lstm_units: Number of LSTM units
        learning_rate: Learning rate for Adam optimizer
        batch_size: Batch size for training
        epochs: Number of training epochs
        patience: Patience for early stopping
        dataset_size: Number of samples to generate
        val_split: Validation split ratio
        model_dir: Directory to save the model
        plot_dir: Directory to save the plots
        threat_types: List of threat types to generate data for
        
    Returns:
        Tuple of (trained model, evaluation metrics)
    """
    # Create directories if they don't exist
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)
    
    logger.info(f"Generating synthetic dataset with {dataset_size} samples")
    
    # Generate synthetic dataset
    if threat_types is None:
        threat_types = ['FUNGAL', 'BACTERIAL', 'VIRAL', 'PEST']
        
    X, y = generate_synthetic_dataset(
        dataset_size=dataset_size,
        spatial_dim=spatial_dim,
        time_steps=time_steps,
        features=features,
        threat_types=threat_types
    )
    
    # Split into training and validation sets
    split_idx = int(len(X) * (1 - val_split))
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    logger.info(f"Training set: {X_train.shape}, Validation set: {X_val.shape}")
    
    # Initialize the model
    model = PathogenSpreadModel(
        spatial_dim=spatial_dim,
        time_steps=time_steps,
        features=features,
        lstm_units=lstm_units,
        learning_rate=learning_rate
    )
    
    # Generate a timestamp for model versioning
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_name = f"spread_model_{timestamp}"
    
    # Train the model
    model_path = os.path.join(model_dir, f"{model_name}.h5")
    
    logger.info(f"Starting model training for {epochs} epochs")
    history = model.train(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        epochs=epochs,
        batch_size=batch_size,
        patience=patience,
        save_path=model_path
    )
    
    # Plot training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history['loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.title('Loss During Training')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history['mae'], label='Train MAE')
    plt.plot(history['val_mae'], label='Val MAE')
    plt.title('Mean Absolute Error During Training')
    plt.xlabel('Epoch')
    plt.ylabel('MAE')
    plt.legend()
    
    history_plot_path = os.path.join(plot_dir, f"{model_name}_history.png")
    plt.tight_layout()
    plt.savefig(history_plot_path)
    plt.close()
    
    logger.info(f"Training history plot saved to {history_plot_path}")
    
    # Evaluate the model
    logger.info("Evaluating model performance")
    eval_metrics = evaluate_model(model, X_val, y_val)
    
    # Plot evaluation metrics
    eval_plot_path = os.path.join(plot_dir, f"{model_name}_evaluation.png")
    plot_evaluation_metrics(eval_metrics, eval_plot_path)
    
    # Save evaluation metrics
    metrics_path = os.path.join(model_dir, f"{model_name}_metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(eval_metrics, f, indent=4)
    
    logger.info(f"Model trained and saved to {model_path}")
    logger.info(f"Evaluation metrics saved to {metrics_path}")
    
    return model, eval_metrics


def generate_example_prediction(
    model: PathogenSpreadModel,
    initial_state: Optional[np.ndarray] = None,
    time_steps: int = 7,
    plot_dir: str = './plots'
) -> None:
    """
    Generate an example prediction and visualize it.
    
    Args:
        model: Trained PathogenSpreadModel
        initial_state: Initial state (if None, a random state will be generated)
        time_steps: Number of time steps to predict forward
        plot_dir: Directory to save the plots
    """
    # Generate a random initial state if none provided
    if initial_state is None:
        from src.models.data_generator import generate_initial_state
        initial_state = generate_initial_state(
            spatial_dim=model.spatial_dim,
            features=model.features,
            concentration=0.8,
            random_seed=42
        )
    
    # Make predictions
    predictions = model.predict_spread(
        initial_state=initial_state,
        time_steps=time_steps
    )
    
    # Generate a timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate and save heatmap
    heatmap = model.generate_probability_heatmap(predictions)
    heatmap_path = os.path.join(plot_dir, f"heatmap_{timestamp}.png")
    model.plot_heatmap(heatmap, save_path=heatmap_path)
    
    # Plot the sequence of predictions
    plt.figure(figsize=(15, 8))
    
    # Plot the initial state
    plt.subplot(2, 4, 1)
    plt.imshow(initial_state[:, :, 0], cmap='viridis')
    plt.title("Initial State")
    plt.colorbar()
    
    # Plot predictions at different time steps
    for i in range(min(6, time_steps)):
        plt.subplot(2, 4, i + 2)
        plt.imshow(predictions[i, :, :, 0], cmap='viridis')
        plt.title(f"t+{i+1}")
        plt.colorbar()
    
    # Save the sequence plot
    sequence_path = os.path.join(plot_dir, f"sequence_{timestamp}.png")
    plt.tight_layout()
    plt.savefig(sequence_path)
    plt.close()
    
    logger.info(f"Example prediction sequence saved to {sequence_path}")
    logger.info(f"Probability heatmap saved to {heatmap_path}")


def main():
    """Command line interface for training a model."""
    parser = argparse.ArgumentParser(description='Train a pathogen spread prediction model')
    
    parser.add_argument('--spatial-dim', type=int, default=32, help='Spatial dimension for the grid')
    parser.add_argument('--time-steps', type=int, default=7, help='Number of time steps to consider')
    parser.add_argument('--features', type=int, default=5, help='Number of features per grid cell')
    parser.add_argument('--lstm-units', type=int, default=64, help='Number of LSTM units')
    parser.add_argument('--learning-rate', type=float, default=0.001, help='Learning rate')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size for training')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
    parser.add_argument('--patience', type=int, default=5, help='Patience for early stopping')
    parser.add_argument('--dataset-size', type=int, default=1000, help='Number of samples to generate')
    parser.add_argument('--val-split', type=float, default=0.2, help='Validation split ratio')
    parser.add_argument('--model-dir', type=str, default='./models', help='Directory to save the model')
    parser.add_argument('--plot-dir', type=str, default='./plots', help='Directory to save the plots')
    
    args = parser.parse_args()
    
    # Train the model
    model, metrics = train_model(
        spatial_dim=args.spatial_dim,
        time_steps=args.time_steps,
        features=args.features,
        lstm_units=args.lstm_units,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        epochs=args.epochs,
        patience=args.patience,
        dataset_size=args.dataset_size,
        val_split=args.val_split,
        model_dir=args.model_dir,
        plot_dir=args.plot_dir
    )
    
    # Generate example prediction
    generate_example_prediction(
        model=model,
        time_steps=10,
        plot_dir=args.plot_dir
    )
    
    logger.info("Training and evaluation complete!")


if __name__ == "__main__":
    main()

