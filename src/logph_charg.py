# ---- plot verschiedene Temperaturen ---------
import matplotlib.pyplot as plt
import numpy as np
from fluprodia import FluidPropertyDiagram

# List of ambient temperatures you want to simulate
ambient_temperatures = [5, 10, 15, 20, 25]  # Modify this list as needed

# Create a figure and axis for plotting log(p)-h diagram
fig, ax = plt.subplots(1, figsize=(20, 10))

# Initialize the fluid property diagram
diagram = FluidPropertyDiagram('NH3')
diagram.set_unit_system(T='°C', p='bar', h='kJ/kg')

# Define isolines for the diagram
isolines = {
    'Q': np.linspace(0, 1, 2),
    'p': np.array([1, 2, 5, 10, 20, 50, 100, 300]),
    'v': np.array([]),
    'h': np.arange(500, 3501, 500)
}
diagram.set_isolines(**isolines)
diagram.calc_isolines()

# Draw isolines on the log(p)-h diagram
diagram.draw_isolines(fig, ax, 'logph', x_min=0, x_max=3000, y_min=0.5, y_max=2e2)

# Adjust the font size of the isoline labels
for text in ax.texts:
    text.set_fontsize(10)

# Colors for different ambient temperatures
colors = plt.cm.viridis(np.linspace(0, 1, len(ambient_temperatures)))

# Iterate over each ambient temperature
for idx, temp in enumerate(ambient_temperatures):
    # Run your heat pump simulation for the current temperature
    # Replace this with your actual simulation code to get 'nw' based on temperature
    nw = Network(p_unit='bar', T_unit='C', h_unit='kJ / kg')
    network, cd, cp, hx1, hx2 = create_connections(network=nw, charging_mode=True, temp=temp)
    # For example: nw.run(ambient_temperature=temp)

    # Store the model result in a dictionary
    result_dict = {}
    result_dict.update(
        {cp.label: cp.get_plotting_data()[1] for cp in network.comps['object']
         if cp.get_plotting_data() is not None})

    # Calculate individual isolines for T-s diagram
    for key, data in result_dict.items():
        result_dict[key]['datapoints'] = diagram.calc_individual_isoline(**data)

    # Plot the data for the current ambient temperature
    for key in result_dict.keys():
        datapoints = result_dict[key]['datapoints']
        ax.plot(datapoints['h'], datapoints['p'], color=colors[idx], linewidth=2)
        ax.scatter(datapoints['h'][0], datapoints['p'][0], color=colors[idx])
        
    # Add label only once for each temperature
    if idx == 0 or (idx > 0 and temp != ambient_temperatures[idx - 1]):
        ax.plot([], [], color=colors[idx], label=f'Temp: {temp}°C, COP = {round(abs(cd.Q.val+hx1.Q.val+hx2.Q.val) / cp.P.val, 2)}') # COP = {round(abs(hp_condenser.Q.val) / hp_compressor.P.val, 2)}
        
# Set labels and title for the log-p h diagram
ax.set_xlabel('Enthalpy, h in kJ/kg', fontsize=16)
ax.set_ylabel('Pressure, p in bar', fontsize=16)
ax.set_title('log-p h Diagram of charging Phase', fontsize=20)

# Create a legend for the temperature curves
ax.legend(title='Ambient Temperature', fontsize=12)

# Set font size for the x-axis and y-axis ticks
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
plt.tight_layout()
plt.show()

fig.savefig('logph.png')
