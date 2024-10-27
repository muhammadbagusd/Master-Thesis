# ----- Brayton  cycle ---------------
# ------------ Brayton -------- 
from tespy.components import (Compressor, Condenser ,SimpleHeatExchanger, 
                              HeatExchanger, Pump, Turbine, Valve, CycleCloser, Source, Sink)
from tespy.connections import Connection, Bus
from tespy.networks import Network

br = Network(fluids=['Water', 'Nitrogen', 'Methanol'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# Heat Pump Cycle Components (Charging)
br_compressor = Compressor('Compressor')
br_hotHX = HeatExchanger('Heat Exchanger Hot Storage')  # Transfers heat to hot storage
br_coldHX = HeatExchanger('Heat Exchanger Cold Storage')  # Transfers heat to hot storage
br_HX_A = SimpleHeatExchanger('Simple Heat Exchanger A')
br_HX_B = SimpleHeatExchanger('Simple Heat Exchanger B')
br_closer = CycleCloser('HP Cycle Closer')  # Closes the heat pump loop
br_turbine = Turbine('Turbine')
br_regenerator = HeatExchanger('Regenerator')

# Hot Storage Tank charge
br_hot_sto_charge_so = Source('Hot storage tank charge Source')
br_hot_sto_charge_si = Sink('Hot storage tank charge Sink')

# Hot Storage Tank discharge
br_hot_sto_discharge_so = Source('Hot storage tank discharge Source')
br_hot_sto_discharge_si = Sink('Hot storage tank discharge Sink')

# Cold Storage Tank charge
br_cold_sto_charge_so = Source('cold storage tank Source')
br_cold_sto_charge_si = Sink('cold storage tank Sink')

# Brayton Cycle Charge Case Connections (Closed Loop with CycleCloser)
br_c1 = Connection(br_closer, 'out1', br_compressor, 'in1', label='1')
br_c2 = Connection(br_compressor, 'out1', br_hotHX, 'in1', label='2')
br_c3 = Connection(br_hotHX, 'out1', br_regenerator, 'in1', label='3')
br_c7 = Connection(br_regenerator, 'out1', br_HX_A, 'in1', label='7')
br_c4 = Connection(br_HX_A, 'out1', br_turbine, 'in1', label='4')
br_c5 = Connection(br_turbine, 'out1', br_coldHX, 'in1', label='5')
br_c8 = Connection(br_coldHX, 'out1', br_HX_B, 'in1', label='8')
br_c6 = Connection(br_HX_B, 'out1', br_regenerator, 'in2', label='6')
br_c9 = Connection(br_regenerator, 'out2', br_closer, 'in1', label='9')

br.add_conns(br_c1, br_c2, br_c3, br_c4, br_c5, br_c6, br_c7, br_c8, br_c9)

# Ambient Connection
br_c11 = Connection(br_cold_sto_charge_so, 'out1', br_coldHX, 'in2', label='cold in')
br_c12 = Connection(br_coldHX, 'out2', br_cold_sto_charge_si, 'in1', label='cold out')

# charge case connection
br_c13_1 = Connection(br_hot_sto_charge_so, 'out1', br_hotHX, 'in2', label='hot in')
br_c14_1 = Connection(br_hotHX, 'out2', br_hot_sto_charge_si, 'in1', label='hot out')

# discharge case connection
# br_c13_2 = Connection(br_hot_sto_discharge_so, 'out1', br_hotHX, 'in2')
# br_c14_2 = Connection(br_hotHX, 'out2', br_hot_sto_discharge_si, 'in1')

br.add_conns(br_c11, br_c12, br_c13_1, br_c14_1)

# set parameter brayton cycle components
br_compressor.set_attr(eta_s=0.98)
br_hotHX.set_attr(pr1=1, pr2=0.98)
br_coldHX.set_attr(pr1=0.98, pr2=1)
br_HX_A.set_attr(pr=0.98)
br_HX_B.set_attr(pr=0.98)
br_turbine.set_attr(eta_s=0.9)
br_regenerator.set_attr(pr1=1, pr2=0.98)

# set parameter connections
br_c8.set_attr(m=19, T=17, p=25, fluid={'Nitrogen': 1})
br_c2.set_attr(T=587)
br_c5.set_attr(T=-73)
br_c3.set_attr(T=287)
br_c7.set_attr(T=37)
br_c4.set_attr(p=105)
br_c12.set_attr(m=10, T=20, p=25, fluid={'Water': 1})
br_c13_1.set_attr(x=0)
br_c14_1.set_attr(m=10, p=10, fluid={'Methanol': 1})
# ---------- Generator -------------
generator = Bus("generator")
generator.add_comps(
    {"comp": br_turbine, "char": 0.98, "base": "component"},
    {"comp": br_compressor, "char": 0.98, "base": "bus"},
    # {"comp": rc_pump_sto, "char": 0.98, "base": "bus"},
)
br.add_busses(generator)

br.solve(mode='design')
br.print_results()
#----- plotting -----------
# Adding feature to plot the T-s Diagram using fluprodia library
# Importing necessary library
import matplotlib.pyplot as plt
import numpy as np
from fluprodia import FluidPropertyDiagram

# Initial Setup
diagram = FluidPropertyDiagram('Nitrogen')
diagram.set_unit_system(T='°C', p='bar', h='kJ/kg')

# Storing the model result in the dictionary
result_dict = {}
result_dict.update(
    {cp.label: cp.get_plotting_data()[1] for cp in br.comps['object']
     if cp.get_plotting_data() is not None})

# Iterate over the results obtained from TESPy simulation
for key, data in result_dict.items():
    # Calculate individual isolines for T-s diagram
    result_dict[key]['datapoints'] = diagram.calc_individual_isoline(**data)

# Create a figure and axis for plotting T-s diagram
fig, ax = plt.subplots(1, figsize=(20, 10))
isolines = {
    'Q': np.linspace(0, 1, 2),
    'p': np.array([1, 2, 5, 10, 20, 50, 100, 300]),
    'v': np.array([]),
    'h': np.arange(500, 3501, 500)
}

# Set isolines for T-s diagram
diagram.set_isolines(**isolines)
diagram.calc_isolines()

# Draw isolines on the T-s diagram
# diagram.draw_isolines(fig, ax, 'Ts', x_min=4000, x_max=6000, y_min=-200, y_max=1800)

# Adjust the font size of the isoline labels
for text in ax.texts:
    text.set_fontsize(10)

# Plot T-s curves for each component
for key in result_dict.keys():
    datapoints = result_dict[key]['datapoints']
    _ = ax.plot(datapoints['s'], datapoints['T'], color='#ff0000', linewidth=2)
    _ = ax.scatter(datapoints['s'][0], datapoints['T'][0], color='#ff0000')

# Set labels and title for the T-s diagram
ax.set_xlabel('Entropy, s in J/kgK', fontsize=16)
ax.set_ylabel('Temperature, T in °C', fontsize=16)
ax.set_title('T-s Diagram of Rankine Cycle', fontsize=20)

# Set font size for the x-axis and y-axis ticks
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
plt.tight_layout()

# Save the T-s diagram plot as an SVG file
fig.savefig('brayton_ts_diagram.png')
