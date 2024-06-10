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

# 2. Get unique batter IDs and their corresponding names
batters = df['batter'].unique()
batter_name_map = dict(zip(df['batter'], df['Name']))  # Create a dictionary to map IDs to names

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
all_data = pd.DataFrame()  # Initialize DataFrame to store data
all_squared_up_rates = []  # Collect squared-up rates for all batters for y-axis scaling

for batter in selected_batters:
    # Filter data for selected batter
    batter_df = df[df['batter'] == batter].copy()  

    # 5. Calculate Squared-Up Rates for Launch Angles within +/- 10 degrees
    launch_angles = np.arange(-60, 91, 2)
    squared_up_rates = []
    total_events = []
    obs_percentages = []  # New list to store observation percentages
    for angle in launch_angles:
        filtered_events = batter_df[
            batter_df['launch_angle'].between(angle - 10, angle + 10, inclusive='both')
        ]
        total = len(filtered_events)
        squared_up = filtered_events['squared_up'].sum()
       
        squared_up_rate = squared_up / total if total > 20 else np.nan
        # Calculate percentage of observations for this angle
        obs_percentage = (total / len(batter_df)) * 100 

        squared_up_rates.append(squared_up_rate)
        total_events.append(total)
        obs_percentages.append(obs_percentage)  # Add to the list

    # 6. Prepare Data for Graphing
    data = pd.DataFrame({
        'launch_angle': launch_angles,
        'squared_up_rate': squared_up_rates,
        'total_events': total_events,
        'obs_percentage': obs_percentages,  # Include observation percentage
        'batter': batter_name_map[batter]  # Use batter name from the dictionary
    })
    all_data = pd.concat([all_data, data])

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
        y_min = all_data['squared_up_rate'].min() * 100
        y_max = all_data['squared_up_rate'].max() * 100
        break
    elif choice == '3':
        try:
            y_min, y_max = map(float, input("Enter min and max values (e.g., 10 50): ").split())
            break
        except ValueError:
            print("Invalid input. Please enter two numbers separated by a space.")
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

# 8. Plotting (with Y-Axis Scale and Marker Size)
plt.figure(figsize=(10, 6))

# Define custom colors for each batter
colors = ['#50ae26', '#74b4fa', '#ce2431']

for i, batter in enumerate(selected_batters):
    batter_name = batter_name_map[batter]
    batter_data = all_data[all_data['batter'] == batter_name]

    # Plotting with marker size based on observation percentage
    plt.scatter(
        batter_data['launch_angle'],
        batter_data['squared_up_rate'] * 100,
        s=batter_data['obs_percentage'] * 6,  # Scale marker size by percentage
        label=batter_name,  # Use batter name for the label
        color=colors[i],#Assign colors from above
        alpha=0.9  # Add some transparency to markers
    )

plt.title(f'Squared-Up Rate vs. Launch Angle for Batters: {", ".join(map(str, [batter_name_map[b] for b in selected_batters]))}')
plt.xlabel('Launch Angle (degrees)')
plt.ylabel('Squared-Up Rate (%)')
plt.ylim([y_min, y_max])
plt.grid(axis='y')
plt.legend(loc='lower right')

plt.show()