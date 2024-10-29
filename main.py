import random
import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global variable to store balance histories for multiple simulations
saved_graphs = {}  # Dictionary to store saved graphs
selected_graph = None  # Track the currently selected graph

# Function to validate that the odds add up to 100%
def validate_odds(outcomes):
    total_odds = sum([outcome[1] for outcome in outcomes])
    if round(total_odds, 2) != 1:
        raise ValueError("The odds do not add up to 100%. Please adjust the odds.")

# Function to run the simulation
def simulate_betting(start_balance, wager, outcomes, betnums, allow_broke):
    balance = start_balance
    balance_history = [balance]
    
    # Validate that odds sum to 100%
    validate_odds(outcomes)
    
    # Extract values and odds for random.choices
    values = [outcome[0] for outcome in outcomes]
    odds = [outcome[1] for outcome in outcomes]
    
    # Simulate bets
    for i in range(betnums):
        if allow_broke and balance <= 0:
            break  # End simulation if broke and "Allow Broke" is checked

        balance -= wager
        result = random.choices(values, odds)[0]
        balance += result
        balance_history.append(balance)

    return balance_history

# Function to plot balance over time
def plot_balance_over_time(balance_histories):
    ax.clear()  # Clear the current axes
    for i, balance_history in enumerate(balance_histories):
        ax.plot(balance_history, label="Simulation {}".format(i + 1))
    
    ax.set_xlabel("Number of Bets")
    ax.set_ylabel("Balance")
    ax.set_title("Balance Change Over Time")
    ax.legend()
    ax.grid(True)

    # Dynamic scaling to ensure the center is 0
    max_balance = max(max(balance_history) for balance_history in balance_histories)
    min_balance = min(min(balance_history) for balance_history in balance_histories)
    ax.set_ylim(min(min_balance, 0) - 100, max(max_balance, 0) + 100)  # Extend the limits for better visualization
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')  # Add a horizontal line at y=0
    canvas.draw()  # Update the canvas

# Function to run simulation from GUI inputs and append to the selected graph
def run_simulation():
    try:
        if selected_graph is None:
            messagebox.showerror("Selection Error", "Please select a graph to append to.")
            return

        start_balance = int(start_balance_entry.get())
        wager = int(wager_entry.get())
        betnums = int(betnums_entry.get())
        
        # Gather outcomes from input fields
        outcomes = []
        for outcome_frame in outcome_frames:
            reward = int(outcome_frame['reward'].get())
            prob = float(outcome_frame['prob'].get())
            outcomes.append([reward, prob])

        # Run the simulation
        allow_broke = allow_broke_var.get()  # Check the "Allow Broke" checkbox state
        balance_history = simulate_betting(start_balance, wager, outcomes, betnums, allow_broke)

        # Append to the selected graph
        saved_graphs[selected_graph].append(balance_history)  # Append new history to the selected graph
        save_graph(selected_graph)  # Save the graph to a file
        plot_balance_over_time(saved_graphs[selected_graph])  # Update plot with the new graph data

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

# Function to create a new graph
def create_new_graph():
    new_graph_name = simpledialog.askstring("Graph Name", "Enter a name for the new graph:")
    if new_graph_name and new_graph_name not in saved_graphs:
        saved_graphs[new_graph_name] = []  # Initialize a new graph with an empty list
        save_graph(new_graph_name)  # Save the new graph to a file
        update_sidebar()  # Update the sidebar with the new graph

# Function to save a graph to a file
def save_graph(graph_name):
    # Create a directory if it does not exist
    if not os.path.exists('graphs'):
        os.makedirs('graphs')
    
    # Save the graph's balance histories to a JSON file
    with open(os.path.join('graphs', f'{graph_name}.json'), 'w') as f:
        json.dump(saved_graphs[graph_name], f)

# Function to load a graph from a file
def load_graph(graph_name):
    global selected_graph
    selected_graph = graph_name  # Set the selected graph

    # Load saved graph history from file
    try:
        with open(os.path.join('graphs', f'{graph_name}.json'), 'r') as f:
            saved_graphs[graph_name] = json.load(f)  # Load the balance histories
        plot_balance_over_time(saved_graphs[graph_name])  # Plot loaded graph
    except FileNotFoundError:
        messagebox.showerror("File Error", f"Graph file {graph_name}.json not found.")

# Function to update the sidebar with saved graphs
def update_sidebar():
    for widget in sidebar_frame.winfo_children():
        widget.destroy()  # Clear the sidebar
    for graph_name in saved_graphs.keys():
        btn = tk.Button(sidebar_frame, text=graph_name, command=lambda name=graph_name: load_graph(name))
        btn.pack(fill=tk.X)  # Fill the button in the sidebar

# Function to add a new outcome input row
def add_outcome():
    frame = tk.Frame(outcome_container)
    tk.Label(frame, text="Reward/Penalty:").pack(side=tk.LEFT)
    reward_entry = tk.Entry(frame, width=5)
    reward_entry.pack(side=tk.LEFT)

    tk.Label(frame, text="Probability:").pack(side=tk.LEFT)
    prob_entry = tk.Entry(frame, width=5)
    prob_entry.pack(side=tk.LEFT)

    remove_button = tk.Button(frame, text="Remove", command=lambda: remove_outcome(frame))
    remove_button.pack(side=tk.LEFT)

    frame.pack(anchor="w")
    
    outcome_frames.append({"frame": frame, "reward": reward_entry, "prob": prob_entry})

# Function to remove an outcome input row
def remove_outcome(frame):
    # Find and remove the correct outcome frame dictionary from outcome_frames
    for outcome_frame in outcome_frames:
        if outcome_frame["frame"] == frame:
            outcome_frames.remove(outcome_frame)
            break
    frame.destroy()

# Create the main window
root = tk.Tk()
root.title("Betting Simulation")

# Starting balance input
tk.Label(root, text="Starting Balance:").pack(anchor="w")
start_balance_entry = tk.Entry(root)
start_balance_entry.pack(anchor="w")
start_balance_entry.insert(0, "100")

# Wager input
tk.Label(root, text="Wager:").pack(anchor="w")
wager_entry = tk.Entry(root)
wager_entry.pack(anchor="w")
wager_entry.insert(0, "5")

# Number of bets input
tk.Label(root, text="Number of Bets:").pack(anchor="w")
betnums_entry = tk.Entry(root)
betnums_entry.pack(anchor="w")
betnums_entry.insert(0, "100")

# Outcome inputs
tk.Label(root, text="Outcomes:").pack(anchor="w")
outcome_container = tk.Frame(root)
outcome_container.pack(anchor="w")

outcome_frames = []  # List to store outcome input frames
add_outcome()  # Add initial outcome

add_outcome_button = tk.Button(root, text="Add Outcome", command=add_outcome)
add_outcome_button.pack(anchor="w")

# Checkbox to allow broke
allow_broke_var = tk.BooleanVar()
allow_broke_check = tk.Checkbutton(root, text="Allow Broke", variable=allow_broke_var)
allow_broke_check.pack(anchor="w")

# New graph button
new_graph_button = tk.Button(root, text="New Graph", command=create_new_graph)
new_graph_button.pack(anchor="w")

# Run simulation button
run_button = tk.Button(root, text="Run Simulation", command=run_simulation)
run_button.pack(anchor="w")

# Create a frame for the sidebar
sidebar_frame = tk.Frame(root)
sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y)

# Create a figure for the graph
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)  # Add a subplot to the figure
canvas = FigureCanvasTkAgg(fig, master=root)  # Create a canvas to hold the figure
canvas_widget = canvas.get_tk_widget()  # Get the Tkinter widget for the canvas
canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Pack the canvas into the main window

update_sidebar()  # Load existing graphs into the sidebar

# Start the main event loop
root.mainloop()
