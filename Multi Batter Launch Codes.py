# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 09:02:37 2024

@author: benja
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 16:09:48 2024

@author: benja
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Data Loading and Cleaning
df = pd.read_csv('batting_data.csv')
df['launch_angle'] = pd.to_numeric(df['launch_angle'])
df['batter'] = df['batter'].astype('Int64')  # Ensure batter IDs are integers

# 2. Overlapping Binning
bin_width = 10
bin_starts = range(-60, 91)  # Start bins from -60 to 90
bin_ends = [start + bin_width for start in bin_starts]

# Create bin labels for reference
bin_labels = [f"{start}-{end}" for start, end in zip(bin_starts, bin_ends)]

# Create a dictionary to hold bin data
bin_data = {}
for start, end, label in zip(bin_starts, bin_ends, bin_labels):
    bin_data[label] = df['launch_angle'].between(start, end, inclusive='both')

# Create a DataFrame from the bin data and concatenate
df_bins = pd.DataFrame(bin_data)
df = pd.concat([df, df_bins], axis=1)

# Get unique batter IDs
batters = df['batter'].unique()

# 3. Prompt for Number of Players and Batter IDs
while True:
    try:
        num_players = int(input("Enter the number of players to graph (1-3): "))
        if 1 <= num_players <= 3:
            break
        else:
            print("Invalid number of players. Please enter 1, 2, or 3.")
    except ValueError:
        print("Invalid input. Please enter a number.")

selected_batters = []
for i in range(num_players):
    while True:
        try:
            batter_id = int(input(f"Enter batter ID {i + 1}: "))
            if batter_id in batters:
                selected_batters.append(batter_id)
                break
            else:
                print("Invalid batter ID. Please try again.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

# 4. Calculate and Plot for Each Batter
plt.figure(figsize=(10, 6))
all_squared_up_rates = []  # Collect squared-up rates for all batters for y-axis scaling

for batter in selected_batters:
    # Filter data for selected batter
    batter_df = df[df['batter'] == batter]

    # 5. Calculate Squared-Up Rates for Launch Angles within +/- 10 degrees
    launch_angles = np.arange(-60, 91)
    squared_up_rates = []
    total_events = []
    for angle in launch_angles:
        filtered_events = batter_df[
            batter_df['launch_angle'].between(angle - 10, angle + 10, inclusive='both')
        ]
        total = len(filtered_events)
        squared_up = filtered_events['squared_up'].sum()
        squared_up_rate = squared_up / total if total >= 20 else np.nan
        squared_up_rates.append(squared_up_rate)
        total_events.append(total)
    all_squared_up_rates.extend(squared_up_rates)

    # 6. Prepare Data for Graphing
    data = pd.DataFrame(
        {
            'launch_angle': launch_angles,
            'squared_up_rate': squared_up_rates,
            'total_events': total_events,
        }
    )
    
    # Plotting for each batter
    plt.plot(data['launch_angle'], data['squared_up_rate'] * 100, marker='o', label=batter)

# 7. Prompt for Y-Axis Scale
while True:
    print("\nSelect y-axis scale:")
    print("1. 0% to 100%")
    print("2. Minimum to Maximum Squared-Up Rate")
    print("3. Custom (Enter Minimum and Maximum Separated by a Space)")

    choice = input("Enter your choice (1, 2, or 3): ")
    if choice == '1':
        y_min = 0
        y_max = 100
        break
    elif choice == '2':
        y_min = np.nanmin(all_squared_up_rates) * 100
        y_max = np.nanmax(all_squared_up_rates) * 100
        break
    elif choice == '3':
        try:
            y_min, y_max = map(float, input("Enter min and max values (e.g., 10 50): ").split())
            break
        except ValueError:
            print("Invalid input. Please enter two numbers separated by a space.")
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

# 8. Plot Settings and Display
plt.title(f'Squared-Up Rate vs. Launch Angle for Batters: {", ".join(map(str, selected_batters))}')
plt.xlabel('Launch Angle (degrees)')
plt.ylabel('Squared-Up Rate (%)')
plt.ylim([y_min, y_max])
plt.grid(axis='y')
plt.legend()


plt.show()