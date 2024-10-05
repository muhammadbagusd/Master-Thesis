# ------------ HP edited ---------------
from tespy.components import (Compressor, Condenser ,SimpleHeatExchanger, 
                              HeatExchanger, Pump, Turbine, Valve, CycleCloser, 
                              Source, Sink)
from tespy.connections import Connection, Bus
from tespy.networks import Network

nw = Network(fluids=['Water', 'NH3', 'ethanol', 'Air'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# Heat Pump Cycle Components (Charging)
hp_compressor = Compressor('HP Compressor')
hp_condenser = Condenser('HP Condenser')  # Transfers heat to hot storage
hp_valve = Valve('HP Expansion Valve')
hp_evaporator = HeatExchanger('HP Evaporator')
hp_closer = CycleCloser('HP Cycle Closer')  # Closes the heat pump loop

# Sources and Sinks
hp_ambient_source_ev = Source('hp Ambient Source ev')
hp_ambient_sink_ev = Sink('hp Ambient Sink ev')

# Evaporator Sources and Sinks
hp_ambient_source = Source('hp Ambient Source')
hp_ambient_sink = Sink('hp Ambient Sink')
 
# Pump evaporator
# hp_pump_ev = Pump('hp Pump ev')
# hp_ventil_ev = Valve('hp Valve ev')

# Heat Pump Cycle Connections (Closed Loop with CycleCloser)
hp_c1 = Connection(hp_closer, 'out1', hp_evaporator, 'in1', label='1. cc to ev')
hp_c2 = Connection(hp_evaporator, 'out1', hp_compressor, 'in1', label='2. ev to cp')
hp_c3 = Connection(hp_compressor, 'out1', hp_condenser, 'in1', label='3. cp to cd')
hp_c4 = Connection(hp_condenser, 'out1', hp_valve, 'in1', label='4. cd to va')
hp_c5 = Connection(hp_valve, 'out1', hp_closer, 'in1', label='5. va to cc')

nw.add_conns(hp_c1, hp_c2, hp_c3, hp_c4, hp_c5)

# ev_c1 = Connection(hp_ambient_source_ev, 'out1', hp_pump_ev, 'in1', label='HE_amb: ambient to pump')
# ev_c2 = Connection(hp_pump_ev, 'out1', hp_evaporator, 'in2', label='HE_amb: pump to ev')
# ev_c3 = Connection(hp_evaporator, 'out2', hp_ambient_sink_ev, 'in1', label='HE_amb: ev to ambient')
# ev_c4 = Connection(hp_ventil_ev, 'out1', hp_ambient_sink_ev, 'in1', label='ev 4')

# alternative connection
ev_c1 = Connection(hp_ambient_source_ev, 'out1', hp_evaporator, 'in2', label='HE_amb: ambient to ev')
ev_c2 = Connection(hp_evaporator, 'out2', hp_ambient_sink_ev, 'in1', label='HE_amb: ev to ambient')

nw.add_conns(ev_c1, ev_c2)

# ---------- storage -------------
# Hot and Cold Storage Interfaces (Simplified)
sto_c5 = Connection(hp_ambient_source, "out1", hp_condenser, "in2", label='HE_sto: storage to cd')
sto_c6 = Connection(hp_condenser, "out2", hp_ambient_sink, "in1",label="HE_sto: cd to storage")

nw.add_conns(sto_c5, sto_c6)

# ev_c1.set_attr(T=10, p=1, fluid={"air": 1})
# ev_c2.set_attr(p=ev_c1.p.val)

# set Parameter
# hp_compressor.set_attr(eta_s=0.78)
# hp_condenser.set_attr(pr1=1, pr2=1, Q=-1e6)
# hp_evaporator.set_attr(pr1=1, pr2=0.9, ttd_l=2)
# hp_pump_ev.set_attr(eta_s=0.78)

# hp_c4.set_attr(m=30, T=80, fluid={'NH3': 1})
#hp_c2.set_attr(T=30)
#hp_c1.set_attr(T=20)
# hp_c2.set_attr(x=1)

# ---new parameters ---
hp_condenser.set_attr(pr1=0.98, pr2=0.98, ttd_u=10)
hp_evaporator.set_attr(pr1=0.98, pr2=0.98, ttd_l=10)
hp_compressor.set_attr(eta_s=0.85, P=1e7)

hp_c2.set_attr(x=1, fluid={'NH3': 1})
hp_c4.set_attr(T=80)

ev_c1.set_attr(m=10, T=5, p=1, fluid={'water': 1})

sto_c5.set_attr(m=10, p=5, fluid={"water": 1})

# set parameter storage
# sto_c5.set_attr(m=30, p=10, fluid={"water": 1})

nw.solve(mode='design')
nw.print_results()
# -------------------------------------------------PLOT----------------------------------------------------------------------
#%% Plot
# Adding feature to plot the T-s Diagram using fluprodia library
# Importing necessary library
import matplotlib.pyplot as plt
import numpy as np
from fluprodia import FluidPropertyDiagram

# Initial Setup
diagram = FluidPropertyDiagram('NH3')
diagram.set_unit_system(T='°C', p='bar', h='kJ/kg')

# Storing the model result in the dictionary
result_dict = {}
result_dict.update(
    {cp.label: cp.get_plotting_data()[1] for cp in nw.comps['object']
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
diagram.draw_isolines(fig, ax, 'logph', x_min=0, x_max=2100, y_min=0.5, y_max=2e2)

# Adjust the font size of the isoline labels
for text in ax.texts:
    text.set_fontsize(10)

# Plot T-s curves for each component
for key in result_dict.keys():
    datapoints = result_dict[key]['datapoints']
    _ = ax.plot(datapoints['h'],datapoints['p'], color='#ff0000', linewidth=2)
    _ = ax.scatter(datapoints['h'][0],datapoints['p'][0], color='#ff0000')

# Set labels and title for the log-p h diagram
ax.set_xlabel('Enthalpy, h in J/kg', fontsize=16)
ax.set_ylabel('Druck, p in bar', fontsize=16)
ax.set_title('log-p h Diagram of Heat Pump', fontsize=20)

# Set font size for the x-axis and y-axis ticks
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
plt.tight_layout()

fig.savefig('NH3_logph.png')
print(f'COP = {abs(hp_condenser.Q.val) / hp_compressor.P.val}')
