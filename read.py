import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import math

def read_and_parse_dat(file_path):
    """
    Read and parse a .dat file, returning a DataFrame with all columns.
    Assumes data section starts with a header containing 'Inner_Iter'.
    """
    data = []
    columns = None
    in_data_section = False
    line_number = 0

    with open(file_path, 'r') as f:
        for line in f:
            line_number += 1
            stripped_line = line.strip()

            if 'Inner_Iter' in stripped_line and not in_data_section:
                columns = [col.strip() for col in stripped_line.split('|') if col.strip()]
                print(f"Line {line_number} - Header found: {columns}")
                in_data_section = True
                next(f, None)  # Skip separator line
                continue

            if in_data_section:
                if not stripped_line or stripped_line.startswith('+'):
                    continue

                values = [val.strip() for val in stripped_line.split('|') if val.strip()]
                if len(values) != len(columns):
                    print(f"Line {line_number} - Skipped: Expected {len(columns)} values, got {len(values)}")
                    continue

                try:
                    parsed_values = [int(values[0])] + [float(val) for val in values[1:]]
                    data.append(parsed_values)
                except ValueError as e:
                    print(f"Line {line_number} - Skipped: Invalid data - {e}")
                    continue

    if columns is None:
        raise ValueError("Header with 'Inner_Iter' not found.")
    if not data:
        raise ValueError("No valid data found after the header.")
    return pd.DataFrame(data, columns=columns)

def plot_data(df, log_scale=False):
    """
    Create a single figure with subplots in a grid layout, prioritizing 2 rows where possible.
    Each subplot has a line with a different color.
    """
    columns_to_plot = [col for col in df.columns if col != 'Inner_Iter']
    if not columns_to_plot:
        print("No columns to plot. The file may only contain 'Inner_Iter'.")
        sys.exit(1)

    print(f"Plotting the following columns: {columns_to_plot}")
    
    n_plots = len(columns_to_plot)
    
    # Determine grid dimensions, aiming for 2 rows where possible
    if n_plots <= 2:
        n_rows = 1
        max_cols = n_plots
    else:
        n_rows = 2
        max_cols = math.ceil(n_plots / 2)  # Enough columns to fit all plots in 2 rows

    # Create subplots with shared x-axis
    fig, axes = plt.subplots(n_rows, max_cols, figsize=(5 * max_cols, 4 * n_rows), sharex=True)
    
    # Handle case where axes is not a 2D array (e.g., 1 row)
    if n_rows == 1:
        axes = [axes] if n_plots == 1 else axes
    axes = axes.flatten()  # Flatten to 1D array for easy indexing
    
    # Get color cycle for unique colors
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    # Plot each column
    for i, col in enumerate(columns_to_plot):
        ax = axes[i]
        ax.plot(df['Inner_Iter'], df[col], color=colors[i % len(colors)], label=col)
        if log_scale:
            ax.set_yscale('log')
        ax.set_ylabel(col)
        ax.set_title(f'{col} vs Inner_Iter')
        ax.legend()
        ax.grid(True)

    # Set x-label on bottom row axes
    if n_rows == 1:
        bottom_axes = axes
    else:
        bottom_axes = axes[(n_rows - 1) * max_cols : n_rows * max_cols]
    for ax in bottom_axes:
        if ax in fig.axes:  # Ensure axis hasn’t been deleted
            ax.set_xlabel('Inner_Iter')

    # Remove unused subplots
    for j in range(i + 1, n_rows * max_cols):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()

# Parse command-line arguments
default_file = 'screen.dat'
file_path = sys.argv[1] if len(sys.argv) > 1 else default_file
log_scale = '--log' in sys.argv[2:]

# Check if file exists
if not os.path.isfile(file_path):
    print(f"Error: '{file_path}' not found.")
    sys.exit(1)

# Process file and generate plots
try:
    print(f"Reading file: {file_path}")
    df = read_and_parse_dat(file_path)
    print("First 5 rows of data:")
    print(df.head())
    plot_data(df, log_scale=log_scale)
except Exception as e:
    print(f"Error processing file: {e}")
    sys.exit(1)