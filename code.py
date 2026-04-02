import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

def simulate_cloud_network(grid_size, num_tasks):
    """
    Simulates a server network using SOC principles (BTW Sandpile mechanics).
    grid_size: Dimension of the 2D server grid (L x L)
    num_tasks: Number of random tasks to inject over time
    """
    # Initialize network grid (0 tasks on all servers)
    grid = np.zeros((grid_size, grid_size), dtype=int)
    avalanche_sizes = []
    
    # Capacity threshold before a server offloads to its 4 neighbors
    threshold = 4 

    print(f"Simulating network of {grid_size}x{grid_size} servers...")
    
    for step in range(num_tasks):
        # NOISE: A random task arrives at a random server
        x, y = np.random.randint(0, grid_size, 2)
        grid[x, y] += 1
        
        # Check if the task causes an overload (avalanche condition)
        if grid[x, y] >= threshold:
            current_avalanche_size = 0
            # Queue of servers to evaluate for shedding
            unstable_servers = [(x, y)]
            
            while unstable_servers:
                tx, ty = unstable_servers.pop(0)
                
                # If server is still overloaded, shed load
                if grid[tx, ty] >= threshold:
                    # Offload 4 tasks (one to each neighbor)
                    grid[tx, ty] -= threshold
                    current_avalanche_size += 1
                    
                    # CONNECTIVITY: Distribute to neighbors (Up, Down, Left, Right)
                    neighbors = [(tx-1, ty), (tx+1, ty), (tx, ty-1), (tx, ty+1)]
                    for nx, ny in neighbors:
                        # Check network boundaries (tasks lost to external networks at edges)
                        if 0 <= nx < grid_size and 0 <= ny < grid_size:
                            grid[nx, ny] += 1
                            if grid[nx, ny] >= threshold and (nx, ny) not in unstable_servers:
                                unstable_servers.append((nx, ny))
            
            # Record the size of the cascade
            if current_avalanche_size > 0:
                avalanche_sizes.append(current_avalanche_size)
                
    return avalanche_sizes

# --- Execution and Analysis ---
if __name__ == "__main__":
    GRID_SIZE = 50       # 50x50 server grid
    NUM_TASKS = 100000   # 100,000 tasks injected
    
    # Run simulation
    avalanches = simulate_cloud_network(GRID_SIZE, NUM_TASKS)
    
    # Analyze frequency distribution
    size_counts = Counter(avalanches)
    sizes = np.array(list(size_counts.keys()))
    frequencies = np.array(list(size_counts.values()))
    
    # Plotting the Power Law Distribution (Log-Log Scale)
    plt.figure(figsize=(8, 6))
    plt.scatter(sizes, frequencies, c='blue', alpha=0.6, edgecolors='none', marker='o')
    plt.xscale('log')
    plt.yscale('log')
    plt.title('Avalanche Frequency Distribution in Server Network', fontsize=14)
    plt.xlabel('Avalanche Size ($s$)', fontsize=12)
    plt.ylabel('Frequency ($P(s)$)', fontsize=12)
    plt.grid(True, which="both", ls="--", alpha=0.4)
    
    # Save plot for the LaTeX report
    plt.savefig('avalanche_distribution.png', dpi=300)
    print("Simulation complete. Plot saved as 'avalanche_distribution.png'.")
    plt.show()