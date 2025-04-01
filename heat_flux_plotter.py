import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def process_simulation_directories(base_path, x_variable='index', output_filename='grid_convergence'):
    """
    Process all wedge simulation directories and plot heat flux data
    
    Parameters:
    base_path: str - Base directory path
    x_variable: str - Variable to use for x-axis ('index' or column name)
    output_filename: str - Base name for output files
    """
    plt.figure(figsize=(12, 8))
    data_summary = {}
    
    for dir_name in sorted(os.listdir(base_path)):  # Sorted for consistent ordering
        dir_path = os.path.join(base_path, dir_name)
        
        if (os.path.isdir(dir_path) and 
            dir_name.startswith('wedge_r') and 
            'surface.csv' in os.listdir(dir_path)):
            
            try:
                csv_path = os.path.join(dir_path, 'surface.csv')
                df = pd.read_csv(csv_path)
                
                if 'Heat_Flux' in df.columns:
                    # Choose x-axis data
                    if x_variable == 'index' or x_variable not in df.columns:
                        x_data = df.index
                        x_label = 'Surface Point Index'
                    else:
                        x_data = df[x_variable]
                        x_label = x_variable
                    
                    # Store data for summary
                    data_summary[dir_name] = {
                        'mean_heat_flux': np.mean(df['Heat_Flux']),
                        'max_heat_flux': np.max(df['Heat_Flux']),
                        'points': len(df)
                    }
                    
                    plt.plot(x_data, df['Heat_Flux'], 
                            label=dir_name, 
                            alpha=0.7)
                    
            except Exception as e:
                print(f"Error processing {dir_name}: {str(e)}")
                continue
    
    # Plot customization
    plt.xlabel(x_label)
    plt.ylabel('Heat Flux (W/m²)')
    plt.title('Grid Convergence Study - Heat Flux Distribution')
    plt.legend(title='Grid Configurations (rx_ay_z)', 
              bbox_to_anchor=(1.05, 1), 
              loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Save plot
    plt.tight_layout()
    plot_path = os.path.join(base_path, f'{output_filename}.png')
    plt.savefig(plot_path, bbox_inches='tight', dpi=300)
    
    # Save summary data
    summary_df = pd.DataFrame(data_summary).T
    summary_path = os.path.join(base_path, f'{output_filename}_summary.csv')
    summary_df.to_csv(summary_path)
    
    print(f"Plot saved as: {plot_path}")
    print(f"Summary data saved as: {summary_path}")
    plt.show()

def main():
    base_path = os.getcwd()
    # Example: use 'x' coordinate if available in your CSV
    process_simulation_directories(base_path, x_variable='index')
    
if __name__ == "__main__":
    main()
