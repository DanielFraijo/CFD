import os
import pandas as pd
import plotly.graph_objects as go

# Get list of subdirectories
subdirs = [d for d in os.listdir() if os.path.isdir(d)]

# Read CSV files and handle duplicates by averaging over 'x'
data = {}
for subdir in subdirs:
    csv_file = os.path.join(subdir, "surface.csv")
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            if 'x' in df.columns:
                # Group by 'x' and take mean to handle duplicates
                df = df.groupby('x').mean().reset_index()
                data[subdir] = df
            else:
                print(f"Warning: 'x' column missing in {csv_file}. Skipping file.")
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")

# Check if data was loaded and get available variables
if not data:
    print("No data found. Exiting.")
    exit()

first_df = data[next(iter(data))]
variables = [col for col in first_df.columns if col != 'x']
if not variables:
    print("No variables found to plot. Exiting.")
    exit()

# Define variable labels for y-axis (customize as needed)
var_labels = {
    "Heat_Flux": "Heat Flux (W/m²)",
    "Temperature_tr": "Temperature (K)",
    "Pressure": "Pressure (Pa)",
    # Add more mappings as required
}

# Initialize Plotly figure
fig = go.Figure()

# Add traces for each variable and subdirectory
for var_idx, variable in enumerate(variables):
    for sub_idx, subdir in enumerate(subdirs):
        if variable in data[subdir].columns:
            # Make first variable’s traces visible initially
            visible = True if var_idx == 0 else False
            fig.add_trace(
                go.Scatter(
                    x=data[subdir]['x'],
                    y=data[subdir][variable],
                    name=subdir.replace("wedge_", ""),  # Shorten legend labels
                    mode='lines',
                    line=dict(width=2),  # Thicker lines for visibility
                    visible=visible
                )
            )

# Create dropdown buttons to toggle variables
buttons = []
total_traces = len(subdirs) * len(variables)
for var_idx, variable in enumerate(variables):
    visible_list = [False] * total_traces
    start_idx = var_idx * len(subdirs)
    end_idx = start_idx + len(subdirs)
    for i in range(start_idx, end_idx):
        visible_list[i] = True
    button = dict(
        label=variable,
        method='update',
        args=[
            {'visible': visible_list},
            {
                'title': f'{variable} Comparison Across Simulations',
                'yaxis.title': var_labels.get(variable, variable)
            }
        ]
    )
    buttons.append(button)

# Customize layout for a professional, polished appearance
fig.update_layout(
    # Title settings
    title={
        'text': f"{variables[0]} Comparison Across Simulations",
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=16, family="Arial, sans-serif")
    },
    # Axis titles
    xaxis_title="x (m)",
    yaxis_title=var_labels.get(variables[0], variables[0]),
    # Remove range slider
    xaxis_rangeslider_visible=False,
    # Legend title
    legend_title="Simulation",
    # Use a clean, white template
    template="plotly_white",
    # Global font settings
    font=dict(family="Arial, sans-serif", size=12, color="black"),
    # X-axis customization
    xaxis=dict(
        tickformat=".3f",  # 3 decimal places
        nticks=20,  # Control tick density
        gridcolor='lightgray',  # Subtle gridlines
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,  # Boxed axes
        title_font=dict(size=14),
        tickfont=dict(size=12),
        title_standoff=20  # Add space between title and ticks
    ),
    # Y-axis customization
    yaxis=dict(
        tickformat=".2e",  # Scientific notation with 2 decimal places
        nticks=15,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
        title_font=dict(size=14),
        tickfont=dict(size=12),
        title_standoff=20  # Add space between title and ticks
    ),
    # Legend positioned outside the plot, interactive but not draggable
    legend=dict(
        x=1.02,
        y=1.0,
        xanchor='left',
        yanchor='top',
        bgcolor='rgba(255,255,255,0)',  # Transparent background
        borderwidth=0,  # No border for smoother look
        font=dict(size=12, family="Arial, sans-serif")
    ),
    # Adjust margins to accommodate the legend
    margin=dict(l=50, r=150, t=50, b=50),
    # Dropdown menu for variable selection
    updatemenus=[
        dict(
            buttons=buttons,
            direction='down',
            showactive=True,
            x=0.17,
            xanchor='left',
            y=1.15,
            yanchor='top',
            font=dict(family="Arial, sans-serif", size=12, color="black")
        )
    ]
)

# Save the interactive plot as HTML without the Plotly logo
fig.write_html("interactive_plot.html", config={'displaylogo': False}, include_plotlyjs='cdn')
print("Interactive plot saved as 'interactive_plot.html'")
