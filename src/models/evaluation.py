import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.metrics import MeanAbsoluteError, MeanSquaredError
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging
import os
import json
from typing import Dict, List, Tuple, Any, Optional, Callable
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.patches import Patch
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def evaluate_model(
    model,
    X_val: np.ndarray,
    y_val: np.ndarray,
    threshold: float = 0.5,
    feature_idx: int = 0
) -> Dict[str, Any]:
    """
    Evaluate a pathogen spread prediction model on validation data.
    
    Args:
        model: The PathogenSpreadModel to evaluate
        X_val: Validation input data
        y_val: Validation ground truth
        threshold: Threshold for binary classification metrics
        feature_idx: Feature index to evaluate (typically 0 for pathogen concentration)
        
    Returns:
        Dictionary containing evaluation metrics
    """
    logger.info("Evaluating model performance...")
    
    # Make predictions
    y_pred = model.predict(X_val)
    
    # Extract the feature of interest (typically pathogen concentration)
    y_val_feature = y_val[:, :, :, feature_idx]
    y_pred_feature = y_pred[:, :, :, feature_idx]
    
    # Flatten arrays for easier metric calculation
    y_val_flat = y_val_feature.flatten()
    y_pred_flat = y_pred_feature.flatten()
    
    # Calculate regression metrics
    mae = mean_absolute_error(y_val_flat, y_pred_flat)
    mse = mean_squared_error(y_val_flat, y_pred_flat)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_val_flat, y_pred_flat)
    
    # Calculate binary classification metrics (for infected vs. non-infected)
    y_val_binary = (y_val_flat > threshold).astype(int)
    y_pred_binary = (y_pred_flat > threshold).astype(int)
    
    # True positives, false positives, true negatives, false negatives
    tp = np.sum((y_val_binary == 1) & (y_pred_binary == 1))
    fp = np.sum((y_val_binary == 0) & (y_pred_binary == 1))
    tn = np.sum((y_val_binary == 0) & (y_pred_binary == 0))
    fn = np.sum((y_val_binary == 1) & (y_pred_binary == 0))
    
    # Calculate precision, recall, F1 score
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    
    # Calculate IoU (Intersection over Union) for affected areas
    iou = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0
    
    # Calculate metrics per sample
    sample_metrics = []
    for i in range(len(y_val)):
        sample_val = y_val[i, :, :, feature_idx]
        sample_pred = y_pred[i, :, :, feature_idx]
        
        sample_val_binary = (sample_val > threshold).astype(int)
        sample_pred_binary = (sample_pred > threshold).astype(int)
        
        sample_tp = np.sum((sample_val_binary == 1) & (sample_pred_binary == 1))
        sample_fp = np.sum((sample_val_binary == 0) & (sample_pred_binary == 1))
        sample_fn = np.sum((sample_val_binary == 1) & (sample_pred_binary == 0))
        
        sample_iou = sample_tp / (sample_tp + sample_fp + sample_fn) if (sample_tp + sample_fp + sample_fn) > 0 else 0
        sample_mae = mean_absolute_error(sample_val.flatten(), sample_pred.flatten())
        
        sample_metrics.append({
            'iou': float(sample_iou),
            'mae': float(sample_mae)
        })
    
    # Calculate spread error metrics
    # This measures how well the model predicts the extent of spread
    spread_areas_val = np.sum(y_val_binary)
    spread_areas_pred = np.sum(y_pred_binary)
    spread_area_error = abs(spread_areas_val - spread_areas_pred) / max(spread_areas_val, 1)
    
    # Return all metrics as a dictionary
    metrics = {
        'mae': float(mae),
        'mse': float(mse),
        'rmse': float(rmse),
        'r2': float(r2),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1),
        'accuracy': float(accuracy),
        'iou': float(iou),
        'spread_area_error': float(spread_area_error),
        'sample_metrics': sample_metrics,
        'threshold': threshold
    }
    
    logger.info(f"Evaluation metrics: MAE={mae:.4f}, RMSE={rmse:.4f}, IoU={iou:.4f}, F1={f1:.4f}")
    
    return metrics


def plot_evaluation_metrics(metrics: Dict[str, Any], save_path: Optional[str] = None) -> None:
    """
    Plot evaluation metrics for the model.
    
    Args:
        metrics: Dictionary of evaluation metrics
        save_path: Path to save the plot
    """
    # Create a figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot regression metrics
    axes[0, 0].bar(['MAE', 'RMSE'], [metrics['mae'], metrics['rmse']], color=['#1f77b4', '#ff7f0e'])
    axes[0, 0].set_title('Regression Metrics')
    axes[0, 0].set_ylabel('Error')
    axes[0, 0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot R² score
    axes[0, 1].bar(['R²'], [metrics['r2']], color=['#2ca02c'])
    axes[0, 1].set_title('R² Score')
    axes[0, 1].set_ylim(0, 1)
    axes[0, 1].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot classification metrics
    axes[1, 0].bar(['Precision', 'Recall', 'F1', 'Accuracy'], 
                  [metrics['precision'], metrics['recall'], metrics['f1'], metrics['accuracy']],
                  color=['#d62728', '#9467bd', '#8c564b', '#e377c2'])
    axes[1, 0].set_title('Classification Metrics')
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot IoU and area error
    axes[1, 1].bar(['IoU', '1 - Area Error'], 
                  [metrics['iou'], 1 - metrics['spread_area_error']],
                  color=['#7f7f7f', '#bcbd22'])
    axes[1, 1].set_title('Spatial Accuracy')
    axes[1, 1].set_ylim(0, 1)
    axes[1, 1].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add overall title
    plt.suptitle('Model Evaluation Metrics', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
    
    # Save the plot if a path is provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Evaluation metrics plot saved to {save_path}")
    
    plt.close()


def visualize_predictions(
    model,
    X_samples: np.ndarray,
    y_true: np.ndarray,
    sample_indices: List[int],
    feature_idx: int = 0,
    save_dir: Optional[str] = None
) -> None:
    """
    Visualize predictions against ground truth for selected samples.
    
    Args:
        model: The PathogenSpreadModel
        X_samples: Input sequences
        y_true: Ground truth targets
        sample_indices: Indices of samples to visualize
        feature_idx: Feature index to visualize
        save_dir: Directory to save visualizations
    """
    # Create save directory if needed
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    for i, sample_idx in enumerate(sample_indices):
        if sample_idx >= len(X_samples):
            logger.warning(f"Sample index {sample_idx} out of range")
            continue
        
        # Get the input sequence and ground truth
        X_sequence = X_samples[sample_idx:sample_idx+1]
        y_ground_truth = y_true[sample_idx]
        
        # Make prediction
        y_pred = model.predict(X_sequence)[0]
        
        # Create a figure to show comparison
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Plot the last input frame
        last_input = X_sequence[0, -1, :, :, feature_idx]
        im0 = axes[0].imshow(last_input, cmap='viridis', vmin=0, vmax=1)
        axes[0].set_title("Last Input")
        axes[0].axis('off')
        fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)
        
        # Plot the ground truth
        im1 = axes[1].imshow(y_ground_truth[:, :, feature_idx], cmap='viridis', vmin=0, vmax=1)
        axes[1].set_title("Ground Truth")
        axes[1].axis('off')
        fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
        
        # Plot the prediction
        im2 = axes[2].imshow(y_pred[:, :, feature_idx], cmap='viridis', vmin=0, vmax=1)
        axes[2].set_title("Prediction")
        axes[2].axis('off')
        fig.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)
        
        plt.suptitle(f"Sample {sample_idx}", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
        
        # Save the visualization
        if save_dir:
            save_path = os.path.join(save_dir, f"prediction_sample_{sample_idx}.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Prediction visualization saved to {save_path}")
        
        plt.close()


def calculate_error_map(y_true: np.ndarray, y_pred: np.ndarray, feature_idx: int = 0) -> np.ndarray:
    """
    Calculate an error map showing the difference between prediction and ground truth.
    
    Args:
        y_true: Ground truth data
        y_pred: Predicted data
        feature_idx: Feature index to analyze
        
    Returns:
        Error map as a numpy array
    """
    # Extract the feature of interest
    y_true_feature = y_true[:, :, feature_idx]
    y_pred_feature = y_pred[:, :, feature_idx]
    
    # Calculate absolute error
    error_map = np.abs(y_true_feature - y_pred_feature)
    
    return error_map


def plot_error_heatmap(
    error_map: np.ndarray,
    title: str = "Prediction Error Heatmap",
    save_path: Optional[str] = None
) -> None:
    """
    Plot a heatmap of prediction errors.
    
    Args:
        error_map: Error map as a numpy array
        title: Title for the plot
        save_path: Path to save the visualization
    """
    plt.figure(figsize=(10, 8))
    im = plt.imshow(error_map, cmap='hot', interpolation='nearest')
    plt.colorbar(im, label='Absolute Error')
    plt.title(title)
    plt.axis('off')
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Error heatmap saved to {save_path}")
    
    plt.close()


def evaluate_on_showcase(
    model,
    showcase_data: Dict[str, np.ndarray],
    time_steps: int = 7,
    save_dir: Optional[str] = None
) -> Dict[str, Dict[str, float]]:
    """
    Evaluate model performance on showcase examples of different threat types.
    
    Args:
        model: The PathogenSpreadModel
        showcase_data: Dictionary mapping threat types to sequences
        time_steps: Number of time steps to use for input
        save_dir: Directory to save visualizations
        
    Returns:
        Dictionary of evaluation metrics for each threat type
    """
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    results = {}
    
    for threat_type, sequence in showcase_data.items():
        logger.info(f"Evaluating on {threat_type} showcase")
        
        # Split into input and target
        X = sequence[:time_steps].reshape(1, time_steps, *sequence.shape[1:])
        y_true = sequence[time_steps].reshape(1, *sequence.shape[1:])
        
        # Make prediction
        y_pred = model.predict(X)
        
        # Calculate metrics
        metrics = evaluate_model(model, X, y_true)
        results[threat_type] = metrics
        
        # Visualize the results
        if save_dir:
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Plot the last input frame
            im0 = axes[0].imshow(X[0, -1, :, :, 0], cmap='viridis', vmin=0, vmax=1)
            axes[0].set_title("Last Input")
            axes[0].axis('off')
            fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)
            
            # Plot the ground truth
            im1 = axes[1].imshow(y_true[0, :, :, 0], cmap='viridis', vmin=0, vmax=1)
            axes[1].set_title("Ground Truth")
            axes[1].axis('off')
            fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
            
            # Plot the prediction
            im2 = axes[2].imshow(y_pred[0, :, :, 0], cmap='viridis', vmin=0, vmax=1)
            axes[2].set_title("Prediction")
            axes[2].axis('off')
            fig.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)
            
            plt.suptitle(f"{threat_type} Spread Prediction", fontsize=16)
            plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
            
            save_path = os.path.join(save_dir, f"{threat_type.lower()}_prediction.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            # Also plot error heatmap
            error_map = calculate_error_map(y_true[0], y_pred[0])
            plot_error_heatmap(
                error_map,
                title=f"{threat_type} Prediction Error",
                save_path=os.path.join(save_dir, f"{threat_type.lower()}_error.png")
            )
            
            plt.close()
    
    return results


if __name__ == "__main__":
    import argparse
    from src.models.data_generator import generate_showcase_dataset
    
    parser = argparse.ArgumentParser(description="Evaluate a pathogen spread prediction model")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the trained model")
    parser.add_argument("--output_dir", type=str, default="./evaluation", help="Directory to save evaluation results")
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load the model
    from src.models.spread_prediction import PathogenSpreadModel
    model = PathogenSpreadModel.load_model(args.model_path)
    
    # Generate showcase data
    showcase_data = generate_showcase_dataset()
    
    # Evaluate on showcase data
    results = evaluate_on_showcase(
        model=model,
        showcase_data=showcase_data,
        save_dir=args.output_dir
    )
    
    # Save results to JSON
    results_path = os.path.join(args.output_dir, "showcase_results.json")
    with open(results_path, 'w') as f:
        # Convert numpy types to Python types for JSON serialization
        json_results = {}
        for threat_type, metrics in results.items():
            json_results[threat_type] = {k: float(v) if isinstance(v, np.number) else v 
                                        for k, v in metrics.items() 
                                        if k != 'sample_metrics'}
        
        json.dump(json_results, f, indent=4)
    
    logger.info(f"Evaluation results saved to {results_path}")

