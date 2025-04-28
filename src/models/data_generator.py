import numpy as np
import matplotlib.pyplot as plt
import logging
from typing import Tuple, List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Dictionary of spread behaviors for different threat types
SPREAD_BEHAVIORS = {
    'FUNGAL': {
        'spread_rate': 0.2,  # How quickly it spreads
        'pattern': 'radial',  # Spread pattern
        'weather_influence': 0.7,  # How much weather affects it
        'intensity_decay': 0.1  # How quickly intensity falls off
    },
    'BACTERIAL': {
        'spread_rate': 0.15,
        'pattern': 'radial',
        'weather_influence': 0.5,
        'intensity_decay': 0.2
    },
    'VIRAL': {
        'spread_rate': 0.25,
        'pattern': 'jump',  # Can jump to distant locations
        'weather_influence': 0.3,
        'intensity_decay': 0.05
    },
    'PEST': {
        'spread_rate': 0.3,
        'pattern': 'directional',  # Tends to move in specific directions
        'weather_influence': 0.6,
        'intensity_decay': 0.15
    }
}

def generate_initial_state(
    spatial_dim: int = 32, 
    features: int = 5, 
    concentration: float = 0.5,
    num_points: int = 1,
    random_seed: Optional[int] = None
) -> np.ndarray:
    """
    Generate an initial state for a pathogen spread simulation.
    
    Args:
        spatial_dim: Dimension of the spatial grid (square)
        features: Number of features per grid cell
        concentration: Concentration of the initial infection (0-1)
        num_points: Number of initial infection points
        random_seed: Random seed for reproducibility
        
    Returns:
        Initial state as numpy array of shape (spatial_dim, spatial_dim, features)
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Initialize an empty grid
    state = np.zeros((spatial_dim, spatial_dim, features))
    
    # Feature 0 represents pathogen concentration
    # Generate random points for initial infections
    for _ in range(num_points):
        x = np.random.randint(0, spatial_dim)
        y = np.random.randint(0, spatial_dim)
        
        # Set initial concentration
        intensity = concentration * (0.8 + 0.4 * np.random.random())  # Some randomness
        state[x, y, 0] = intensity
        
        # Create some diffusion around the point
        radius = int(3 + 3 * np.random.random())  # Random radius between 3-6
        for i in range(max(0, x-radius), min(spatial_dim, x+radius+1)):
            for j in range(max(0, y-radius), min(spatial_dim, y+radius+1)):
                # Calculate distance from center
                dist = np.sqrt((i-x)**2 + (j-y)**2)
                if dist <= radius:
                    # Intensity decreases with distance
                    state[i, j, 0] = max(state[i, j, 0], intensity * (1 - dist/radius))
    
    # Features 1-4 can represent environmental factors
    # Features 1-4 can represent environmental factors
    # Feature 1: Temperature (normalized between 0-1)
    state[:, :, 1] = 0.2 + 0.6 * np.random.random()  # Base temperature
    # Add some spatial variation
    for i in range(5):
        x = np.random.randint(0, spatial_dim)
        y = np.random.randint(0, spatial_dim)
        radius = int(spatial_dim * 0.3 * np.random.random())
        for i in range(max(0, x-radius), min(spatial_dim, x+radius+1)):
            for j in range(max(0, y-radius), min(spatial_dim, y+radius+1)):
                dist = np.sqrt((i-x)**2 + (j-y)**2)
                if dist <= radius:
                    # Temperature variation
                    state[i, j, 1] += 0.1 * (1 - dist/radius) * (2 * np.random.random() - 1)
    
    # Feature 2: Humidity (normalized between 0-1)
    state[:, :, 2] = 0.3 + 0.4 * np.random.random()  # Base humidity
    # Add some spatial variation - humidity often correlates with topography
    for i in range(4):
        x = np.random.randint(0, spatial_dim)
        y = np.random.randint(0, spatial_dim)
        radius = int(spatial_dim * 0.4 * np.random.random())
        for i in range(max(0, x-radius), min(spatial_dim, x+radius+1)):
            for j in range(max(0, y-radius), min(spatial_dim, y+radius+1)):
                dist = np.sqrt((i-x)**2 + (j-y)**2)
                if dist <= radius:
                    state[i, j, 2] += 0.15 * (1 - dist/radius) * np.random.random()
    
    # Feature 3: Wind direction (0-1 normalized to 0-360 degrees)
    wind_direction = np.random.random()  # Predominant wind direction
    state[:, :, 3] = wind_direction
    
    # Feature 4: Wind speed (normalized between 0-1)
    state[:, :, 4] = 0.1 + 0.4 * np.random.random()  # Base wind speed
    # Add spatial variation to wind speed
    for i in range(3):
        x = np.random.randint(0, spatial_dim)
        y = np.random.randint(0, spatial_dim)
        radius = int(spatial_dim * 0.25 * np.random.random())
        for i in range(max(0, x-radius), min(spatial_dim, x+radius+1)):
            for j in range(max(0, y-radius), min(spatial_dim, y+radius+1)):
                dist = np.sqrt((i-x)**2 + (j-y)**2)
                if dist <= radius:
                    state[i, j, 4] += 0.1 * (1 - dist/radius) * np.random.random()
    
    # Ensure all values are within [0, 1]
    state = np.clip(state, 0, 1)
    
    return state


def simulate_spread(
    initial_state: np.ndarray,
    time_steps: int,
    threat_type: str = 'FUNGAL',
    random_seed: Optional[int] = None
) -> np.ndarray:
    """
    Simulate the spread of a pathogen over time.
    
    Args:
        initial_state: Initial state (spatial_dim, spatial_dim, features)
        time_steps: Number of time steps to simulate
        threat_type: Type of biological threat to simulate
        random_seed: Random seed for reproducibility
        
    Returns:
        Sequence of states over time (time_steps, spatial_dim, spatial_dim, features)
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    spatial_dim, _, features = initial_state.shape
    
    # Get spread behavior parameters for this threat type
    behavior = SPREAD_BEHAVIORS.get(threat_type, SPREAD_BEHAVIORS['FUNGAL'])
    
    # Initialize the sequence with the initial state
    sequence = np.zeros((time_steps, spatial_dim, spatial_dim, features))
    sequence[0] = initial_state.copy()
    
    # Simulation constants
    spread_rate = behavior['spread_rate']
    weather_influence = behavior['weather_influence']
    intensity_decay = behavior['intensity_decay']
    pattern = behavior['pattern']
    
    # Simulate for each time step
    for t in range(1, time_steps):
        curr_state = sequence[t-1].copy()
        next_state = curr_state.copy()
        
        # Extract environmental factors
        temperature = curr_state[:, :, 1]
        humidity = curr_state[:, :, 2]
        wind_direction = curr_state[:, :, 3] * 2 * np.pi  # Convert to radians
        wind_speed = curr_state[:, :, 4]
        
        # Calculate environmental favorability for spread (0-1)
        # Different pathogens prefer different conditions
        if threat_type == 'FUNGAL':
            favorability = 0.5 + 0.5 * humidity - 0.3 * np.abs(temperature - 0.6)
        elif threat_type == 'BACTERIAL':
            favorability = 0.3 + 0.4 * humidity + 0.3 * temperature
        elif threat_type == 'VIRAL':
            favorability = 0.4 + 0.3 * wind_speed + 0.2 * temperature
        elif threat_type == 'PEST':
            favorability = 0.2 + 0.4 * temperature - 0.2 * wind_speed + 0.2 * humidity
        else:
            favorability = 0.5 * np.ones_like(temperature)
        
        favorability = np.clip(favorability, 0, 1)
        
        # Pathogen concentration in current state
        concentration = curr_state[:, :, 0]
        
        # Calculate spread based on pattern
        if pattern == 'radial':
            # Radial spread (typical for fungi and bacteria)
            for i in range(spatial_dim):
                for j in range(spatial_dim):
                    if concentration[i, j] > 0.01:
                        spread_radius = int(1 + 3 * spread_rate * favorability[i, j])
                        for ni in range(max(0, i-spread_radius), min(spatial_dim, i+spread_radius+1)):
                            for nj in range(max(0, j-spread_radius), min(spatial_dim, j+spread_radius+1)):
                                dist = np.sqrt((ni-i)**2 + (nj-j)**2)
                                if dist <= spread_radius:
                                    spread_factor = concentration[i, j] * (1 - dist/spread_radius) * spread_rate * favorability[i, j]
                                    next_state[ni, nj, 0] = max(next_state[ni, nj, 0], next_state[ni, nj, 0] + spread_factor)
        
        elif pattern == 'directional':
            # Directional spread (following wind)
            for i in range(spatial_dim):
                for j in range(spatial_dim):
                    if concentration[i, j] > 0.01:
                        # Get wind vector
                        wind_dx = wind_speed[i, j] * np.cos(wind_direction[i, j])
                        wind_dy = wind_speed[i, j] * np.sin(wind_direction[i, j])
                        
                        # Scale by spread rate and favorability
                        spread_distance = int(1 + 4 * spread_rate * favorability[i, j])
                        
                        # Calculate spread direction and intensity
                        for distance in range(1, spread_distance + 1):
                            # Position affected by wind
                            wind_factor = weather_influence * wind_speed[i, j]
                            ni = int(i + distance * wind_dx * wind_factor)
                            nj = int(j + distance * wind_dy * wind_factor)
                            
                            # Also spread a bit in random directions (less strongly)
                            for _ in range(3):
                                random_angle = np.random.random() * 2 * np.pi
                                random_dx = np.cos(random_angle)
                                random_dy = np.sin(random_angle)
                                random_dist = 1 + int(2 * np.random.random())
                                ri = int(i + random_dist * random_dx)
                                rj = int(j + random_dist * random_dy)
                                
                                if 0 <= ri < spatial_dim and 0 <= rj < spatial_dim:
                                    random_factor = concentration[i, j] * 0.3 * spread_rate * favorability[i, j] / (1 + random_dist)
                                    next_state[ri, rj, 0] = max(next_state[ri, rj, 0], next_state[ri, rj, 0] + random_factor)
                            
                            # Apply wind-driven spread
                            if 0 <= ni < spatial_dim and 0 <= nj < spatial_dim:
                                spread_factor = concentration[i, j] * spread_rate * favorability[i, j] / (1 + 0.5 * distance)
                                next_state[ni, nj, 0] = max(next_state[ni, nj, 0], next_state[ni, nj, 0] + spread_factor)
        
        elif pattern == 'jump':
            # Jump spread (can spread to distant locations, typical for viruses or pests)
            for i in range(spatial_dim):
                for j in range(spatial_dim):
                    if concentration[i, j] > 0.1:  # Only significant concentrations can jump
                        # Regular short-distance spread
                        spread_radius = int(1 + 2 * spread_rate * favorability[i, j])
                        for ni in range(max(0, i-spread_radius), min(spatial_dim, i+spread_radius+1)):
                            for nj in range(max(0, j-spread_radius), min(spatial_dim, j+spread_radius+1)):
                                dist = np.sqrt((ni-i)**2 + (nj-j)**2)
                                if dist <= spread_radius:
                                    spread_factor = concentration[i, j] * (1 - dist/spread_radius) * spread_rate * favorability[i, j]
                                    next_state[ni, nj, 0] = max(next_state[ni, nj, 0], next_state[ni, nj, 0] + spread_factor)
                        
                        # Occasional long-distance jumps
                        if np.random.random() < 0.1 * concentration[i, j]:
                            jump_distance = int(5 + 10 * np.random.random())  # Long jump
                            jump_angle = np.random.random() * 2 * np.pi
                            
                            # Wind influence on jump direction
                            jump_angle = (1 - weather_influence) * jump_angle + weather_influence * wind_direction[i, j]
                            
                            # Calculate jump landing point
                            ni = int(i + jump_distance * np.cos(jump_angle))
                            nj = int(j + jump_distance * np.sin(jump_angle))
                            
                            if 0 <= ni < spatial_dim and 0 <= nj < spatial_dim:
                                # Create a new infection point
                                jump_intensity = concentration[i, j] * 0.3 * (0.7 + 0.6 * np.random.random())
                                next_state[ni, nj, 0] += jump_intensity
                                
                                # Create some diffusion around the jump point
                                small_radius = 2
                                for li in range(max(0, ni-small_radius), min(spatial_dim, ni+small_radius+1)):
                                    for lj in range(max(0, nj-small_radius), min(spatial_dim, nj+small_radius+1)):
                                        dist = np.sqrt((li-ni)**2 + (lj-nj)**2)
                                        if dist <= small_radius:
                                            spread_factor = jump_intensity * (1 - dist/small_radius) * 0.7
                                            next_state[li, lj, 0] = max(next_state[li, lj, 0], next_state[li, lj, 0] + spread_factor)
        
        # Apply natural decay
        next_state[:, :, 0] *= (1 - intensity_decay * (1 - favorability))
        
        # Update environmental factors slightly for the next time step
        # Temperature change
        next_state[:, :, 1] += 0.02 * (2 * np.random.random((spatial_dim, spatial_dim)) - 1)
        # Humidity change
        next_state[:, :, 2] += 0.03 * (2 * np.random.random((spatial_dim, spatial_dim)) - 1)
        # Wind direction change (slight)
        next_state[:, :, 3] += 0.05 * (2 * np.random.random((spatial_dim, spatial_dim)) - 1)
        # Wind speed change
        next_state[:, :, 4] += 0.04 * (2 * np.random.random((spatial_dim, spatial_dim)) - 1)
        
        # Ensure all values are within [0, 1]
        next_state = np.clip(next_state, 0, 1)
        
        # Store the next state
        sequence[t] = next_state
    
    return sequence


def generate_synthetic_dataset(
    dataset_size: int,
    spatial_dim: int = 32,
    time_steps: int = 7,
    features: int = 5,
    threat_types: Optional[List[str]] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a synthetic dataset for training the spread prediction model.
    
    Args:
        dataset_size: Number of samples to generate
        spatial_dim: Spatial dimension for the grid
        time_steps: Number of time steps in each sequence
        features: Number of features per grid cell
        threat_types: List of threat types to include
        
    Returns:
        Tuple of (X, y) where:
            X: Input sequences of shape (dataset_size, time_steps, spatial_dim, spatial_dim, features)
            y: Target outputs of shape (dataset_size, spatial_dim, spatial_dim, features)
    """
    logger.info(f"Generating synthetic dataset with {dataset_size} samples")
    
    # Set default threat types if not provided
    if threat_types is None:
        threat_types = ['FUNGAL', 'BACTERIAL', 'VIRAL', 'PEST']
    
    # Initialize arrays for input sequences and targets
    X = np.zeros((dataset_size, time_steps, spatial_dim, spatial_dim, features))
    y = np.zeros((dataset_size, spatial_dim, spatial_dim, features))
    
    for i in range(dataset_size):
        # Pick a random threat type
        threat_type = np.random.choice(threat_types)
        
        # Generate initial state
        concentration = 0.3 + 0.6 * np.random.random()  # Random initial concentration
        num_points = np.random.randint(1, 4)  # Random number of initial infection points
        initial_state = generate_initial_state(
            spatial_dim=spatial_dim,
            features=features,
            concentration=concentration,
            num_points=num_points,
            random_seed=None  # Use different seeds for diversity
        )
        
        # Simulate spread
        total_steps = time_steps + 1  # We need time_steps for input and 1 for target
        sequence = simulate_spread(
            initial_state=initial_state,
            time_steps=total_steps,
            threat_type=threat_type,
            random_seed=None
        )
        
        # Input sequence is all but the last step
        X[i] = sequence[:time_steps]
        
        # Target is the last step
        y[i] = sequence[-1]
        
        # Log progress
        if (i + 1) % 100 == 0 or i == dataset_size - 1:
            logger.info(f"Generated {i + 1}/{dataset_size} samples")
    
    return X, y


def visualize_spread_sequence(
    sequence: np.ndarray,
    feature_idx: int = 0,
    title: str = "Pathogen Spread Sequence",
    save_path: Optional[str] = None
) -> None:
    """
    Visualize a spread sequence over time.
    
    Args:
        sequence: Sequence of states (time_steps, spatial_dim, spatial_dim, features)
        feature_idx: Index of the feature to visualize
        title: Title for the plot
        save_path: Path to save the visualization
    """
    time_steps, spatial_dim, _, _ = sequence.shape
    
    # Create a figure with subplots for each time step
    fig, axes = plt.subplots(1, time_steps, figsize=(time_steps * 3, 3))
    
    # If there's only one time step, axes is not an array
    if time_steps == 1:
        axes = [axes]
    
    # Plot each time step
    for t in range(time_steps):
        state = sequence[t, :, :, feature_idx]
        im = axes[t].imshow(state, cmap='inferno', vmin=0, vmax=1)
        axes[t].set_title(f"t={t}")
        axes[t].axis('off')
    
    # Add a colorbar
    fig.subplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.88, 0.15, 0.03, 0.7])
    fig.colorbar(im, cax=cbar_ax)
    
    # Set the overall title
    fig.suptitle(title, fontsize=16)
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.close()


def generate_showcase_dataset() -> Dict[str, np.ndarray]:
    """
    Generate a showcase dataset with one example of each threat type.
    
    Returns:
        Dictionary mapping threat types to sequences
    """
    threat_types = ['FUNGAL', 'BACTERIAL', 'VIRAL', 'PEST']
    spatial_dim = 32
    time_steps = 8
    features = 5
    
    showcase = {}
    
    for threat_type in threat_types:
        logger.info(f"Generating showcase for {threat_type}")
        
        # Create a consistent initial state
        initial_state = generate_initial_state(
            spatial_dim=spatial_dim,
            features=features,
            concentration=0.7,
            num_points=1,
            random_seed=42
        )
        
        # Simulate spread for this threat type
        sequence = simulate_spread(
            initial_state=initial_state,
            time_steps=time_steps,
            threat_type=threat_type,
            random_seed=42
        )
        
        showcase[threat_type] = sequence
    
    return showcase


# If run directly, generate and visualize some example data
if __name__ == "__main__":
    import os
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate synthetic pathogen spread data")
    parser.add_argument("--output_dir", type=str, default="./data", help="Directory to save output")
    parser.add_argument("--visualize", action="store_true", help="Generate visualizations")
    args = parser.parse_args()
    
    # Create output directories
    os.makedirs(args.output_dir, exist_ok=True)
    if args.visualize:
        vis_dir = os.path.join(args.output_dir, "visualizations")
        os.makedirs(vis_dir, exist_ok=True)
    
    # Generate showcase dataset
    showcase = generate_showcase_dataset()
    
    # Save and visualize
    for threat_type, sequence in showcase.items():
        # Save the sequence
        np.save(os.path.join(args.output_dir, f"{threat_type.lower()}_sequence.npy"), sequence)
        
        if args.visualize:
            # Visualize pathogen concentration over time
            visualize_spread_sequence(
                sequence=sequence,
                feature_idx=0,  # Pathogen concentration
                title=f"{threat_type} Spread Over Time",
                save_path=os.path.join(vis_dir, f"{threat_type.lower()}_sequence.png")
            )
    
    logger.info(f"Showcase dataset generated and saved to {args.output_dir}")
    
    # Generate a small training dataset as an example
    X, y = generate_synthetic_dataset(
        dataset_size=100,
        spatial_dim=32,
        time_steps=7,
        features=5
    )
    
    # Save the training dataset
    np.save(os.path.join(args.output_dir, "train_X.npy"), X)
    np.save(os.path.join(args.output_dir, "train_y.npy"), y)
    
    logger.info(f"Training dataset generated and saved to {args.output_dir}")
