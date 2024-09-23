# ------------ HP edited ---------------
from tespy.components import (Compressor, Condenser ,SimpleHeatExchanger, 
                              HeatExchanger, Pump, Turbine, Valve, CycleCloser, 
                              Source, Sink)
from tespy.connections import Connection, Bus
from tespy.networks import Network

nw = Network(fluids=['Water', 'NH3', 'ethanol'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

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

# Sources and Sinks
hp_ambient_source_ev = Source('hp Ambient Source ev')
hp_ambient_sink_ev = Sink('hp Ambient Sink ev')
 
# Pump evaporator
hp_pump_ev = Pump('hp Pump ev')
hp_ventil_ev = Valve('hp Valve ev')

# Heat Pump Cycle Connections (Closed Loop with CycleCloser)
hp_c1 = Connection(hp_closer, 'out1', hp_evaporator, 'in1')
hp_c2 = Connection(hp_evaporator, 'out1', hp_compressor, 'in1')
hp_c3 = Connection(hp_compressor, 'out1', hp_condenser, 'in1')
hp_c4 = Connection(hp_condenser, 'out1', hp_valve, 'in1')
hp_c5 = Connection(hp_valve, 'out1', hp_closer, 'in1')

nw.add_conns(hp_c1, hp_c2, hp_c3, hp_c4, hp_c5)

ev_c1 = Connection(hp_ambient_source_ev, 'out1', hp_pump_ev, 'in1')
ev_c2 = Connection(hp_pump_ev, 'out1', hp_evaporator, 'in2')
ev_c3 = Connection(hp_evaporator, 'out2', hp_ventil_ev, 'in1')
ev_c4 = Connection(hp_ventil_ev, 'out1', hp_ambient_sink_ev, 'in1')
nw.add_conns(ev_c1, ev_c2, ev_c3, ev_c4)
ev_c1.set_attr(m=30, T=10, p=1, fluid={"water": 1})
ev_c4.set_attr(p=1)

# set Parameter
hp_compressor.set_attr(eta_s=1, P=1e5)
hp_condenser.set_attr(pr1=1, pr2=1)
hp_evaporator.set_attr(pr1=1, pr2=1)
hp_pump_ev.set_attr(eta_s=1, P=1e5)

from CoolProp.CoolProp import PropsSI as PSI
hp_c3.set_attr(m=2, p=30, fluid={'NH3': 1})
hp_c2.set_attr(x=1)

# ---------- storage -------------
# Hot and Cold Storage Interfaces (Simplified)
sto_c5 = Connection(hp_ambient_source, "out1", hp_condenser, "in2")
sto_c6 = Connection(hp_condenser, "out2", hp_ambient_sink, "in1")

nw.add_conns(sto_c5, sto_c6)

# set parameter storage
sto_c5.set_attr(m=30, T=70, p=20, fluid={"water": 1})

nw.solve(mode='design')
#%% RC
# ---- RC with pump and ventil ---------
# ---------- Rankine cycle -------------
RC = Network(fluids=['Ethanol', 'R134a'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# Rankine Cycle Components (Discharging)
rc_pump = Pump('RC Pump')
rc_steamGen = HeatExchanger('RC steam generator')  # Receives heat from hot storage
rc_turbine = Turbine('RC Turbine')
rc_condenser = Condenser('RC Condenser')
rc_closer = CycleCloser('RC Cycle Closer')  # Closes the Rankine cycle loop

# Sources and Sinks
rc_ambient_source_1 = Source('rc Ambient Source 1')
rc_ambient_sink_1 = Sink('rc Ambient Sink 1')

# Sources and Sinks
rc_ambient_source_2 = Source('rc Ambient Source 2')
rc_ambient_sink_2 = Sink('rc Ambient Sink 2')

# Pump Storage
rc_pump_sto = Pump('RC Pump Storage')
rc_ventil_sto = Valve('RC Valve Storage')

# Rankine Cycle Connections (Closed Loop with CycleCloser)
rc_c1 = Connection(rc_closer, 'out1', rc_turbine, 'in1')
rc_c2 = Connection(rc_turbine, 'out1', rc_condenser, 'in1')
rc_c3 = Connection(rc_condenser, 'out1', rc_pump, 'in1')
rc_c4 = Connection(rc_pump, 'out1', rc_steamGen, 'in1')
rc_c5 = Connection(rc_steamGen, 'out1', rc_closer, 'in1')

RC.add_conns(rc_c1, rc_c2, rc_c3, rc_c4, rc_c5)

# Connections to the ambient environment (source and sink)
rc_ambient_c11 = Connection(rc_ambient_source_1, 'out1', rc_condenser, 'in2')
rc_ambient_c12 = Connection(rc_condenser, 'out2', rc_ambient_sink_1, 'in1')

RC.add_conns(rc_ambient_c11, rc_ambient_c12)

# Connections to the ambient environment (source and sink)
rc_ambient_c21 = Connection(rc_ambient_source_2, 'out1', rc_pump_sto, 'in1')
rc_ambient_c22 = Connection(rc_ventil_sto, 'out1', rc_ambient_sink_2, 'in1')

RC.add_conns(rc_ambient_c21, rc_ambient_c22)

# Connection storage
rc_storage_c1 =  Connection(rc_pump_sto, 'out1', rc_steamGen, 'in2')
rc_storage_c2 = Connection(rc_steamGen, 'out2', rc_ventil_sto, 'in1')

RC.add_conns(rc_storage_c1, rc_storage_c2)

# set parameter RC
rc_condenser.set_attr(pr1=1, pr2=1)
rc_steamGen.set_attr(pr1=1,pr2=1)
rc_turbine.set_attr(eta_s=0.9)
rc_pump.set_attr(eta_s=0.75, P=1e4)

rc_pump_sto.set_attr(eta_s=0.75, P=1e4)

rc_ambient_c11.set_attr(m=10, T=10, p=2, fluid={'Ethanol': 1})
rc_ambient_c21.set_attr(m=sto_c5.m.val, T=sto_c6.T.val, p=sto_c6.p.val, fluid={'water': 1})
rc_c2.set_attr(T=350, p=5, fluid={'Ethanol': 1})
rc_ambient_c22.set_attr(T=sto_c5.T.val, p=sto_c5.p.val)

# ---------- Generator -------------
generator = Bus("generator")
generator.add_comps(
    {"comp": rc_turbine, "char": 0.98, "base": "component"},
    {"comp": rc_pump, "char": 0.98, "base": "bus"},
    {"comp": rc_pump_sto, "char": 0.98, "base": "bus"},
)
RC.add_busses(generator)

RC.solve(mode='design')
# RC.print_results()
#%% different ambient temperature
import numpy as np
import pandas as pd

# create a list named data
T0 = [10, 15, 20, 25, 30, 35]

# create Pandas array using data
array1 = pd.DataFrame(T0, columns=['Temp0'])

for i in range(len(array1)):
    array1.loc[i,1] =  abs(hp_condenser.Q.val/(hp_compressor.P.val+hp_pump_ev.P.val))
    array1.loc[i,2] = abs(generator.P.val/rc_steamGen.Q.val)*100

#%% Plot
# log-p-h
import matplotlib.pyplot as plt
import numpy as np
from fluprodia import FluidPropertyDiagram

diagram = FluidPropertyDiagram('NH3')
diagram.set_unit_system(T='°C', p='bar', h='kJ/kg')

# Create a figure and axis for plotting T-s diagram
fig, ax = plt.subplots(1, figsize=(20, 10))
isolines = {
    'Q': np.linspace(0, 1, 2),
    'p': np.array([1, 2, 5, 10, 20, 50, 100, 300]),
    'v': np.array([]),
    'h': np.arange(500, 3501, 500)
}

# Storing the model result in the dictionary
for j in range(len(array1)):
    result_dict = {}
    result_dict.update(
        {cp.label: cp.get_plotting_data()[1] for cp in nw.comps['object']
         if cp.get_plotting_data() is not None})

    # Iterate over the results obtained from TESPy simulation
    for key, data in result_dict.items():
        # Calculate individual isolines for T-s diagram
        result_dict[key]['datapoints'] = diagram.calc_individual_isoline(**data)

    # Set isolines for T-s diagram
    diagram.set_isolines(**isolines)
    diagram.calc_isolines()

    # diagram.set_limits(x_min=0, x_max=2100, y_min=1e0, y_max=2e2)
    diagram.draw_isolines(fig, ax, 'logph', x_min=0, x_max=2100, y_min=0.5, y_max=2e2)
    
    for key in result_dict.keys():
        datapoints = result_dict[key]['datapoints']
        _ = ax.plot(datapoints['h'],datapoints['p'], color='#ff0000')
        #_ = ax.scatter(datapoints['h'][0],datapoints['p'][0])

fig.savefig('NH3_logph.png')

#T-s
# Initial Setup
diagram = FluidPropertyDiagram('ethanol')
diagram.set_unit_system(T='°C', p='bar', h='kJ/kg')

# Storing the model result in the dictionary
result_dict = {}
result_dict.update(
    {cp.label: cp.get_plotting_data()[1] for cp in RC.comps['object']
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
diagram.draw_isolines(fig, ax, 'Ts', x_min=0, x_max=4000, y_min=0, y_max=400)

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
fig.savefig('rankine_ts_diagram.png')
