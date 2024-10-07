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
br_c1 = Connection(br_closer, 'out1', br_compressor, 'in1')
br_c2 = Connection(br_compressor, 'out1', br_hotHX, 'in1')
br_c3 = Connection(br_hotHX, 'out1', br_regenerator, 'in1')
br_c4 = Connection(br_regenerator, 'out1', br_HX_A, 'in1')
br_c5 = Connection(br_HX_A, 'out1', br_turbine, 'in1')
br_c6 = Connection(br_turbine, 'out1', br_coldHX, 'in1')
br_c7 = Connection(br_coldHX, 'out1', br_HX_B, 'in1')
br_c8 = Connection(br_HX_B, 'out1', br_regenerator, 'in2')
br_c9 = Connection(br_regenerator, 'out2', br_closer, 'in1')

br.add_conns(br_c1, br_c2, br_c3, br_c4, br_c5, br_c6, br_c7, br_c8, br_c9)

# Ambient Connection
br_c11 = Connection(br_cold_sto_charge_so, 'out1', br_coldHX, 'in2')
br_c12 = Connection(br_coldHX, 'out2', br_cold_sto_charge_si, 'in1')

# charge case connection
br_c13_1 = Connection(br_hot_sto_charge_so, 'out1', br_hotHX, 'in2')
br_c14_1 = Connection(br_hotHX, 'out2', br_hot_sto_charge_si, 'in1')

# discharge case connection
# br_c13_2 = Connection(br_hot_sto_discharge_so, 'out1', br_hotHX, 'in2')
# br_c14_2 = Connection(br_hotHX, 'out2', br_hot_sto_discharge_si, 'in1')

br.add_conns(br_c11, br_c12, br_c13_1, br_c14_1)

# set parameter brayton cycle components
br_compressor.set_attr(eta_s=0.98, P=1e6)
br_hotHX.set_attr(pr1=1, pr2=0.98, Q=1e7)
br_coldHX.set_attr(pr1=0.98, pr2=1, Q=-1e5)
br_HX_A.set_attr(pr=0.98, Q=1e2)
br_HX_B.set_attr(pr=0.98)
br_turbine.set_attr(eta_s=0.9)
br_regenerator.set_attr(pr1=1, pr2=0.98, Q=1e2)

# set parameter connections
br_c1.set_attr(m=19, T=500, p=25, fluid={'Nitrogen': 1})
# br_c8.set_attr(T=300, p=25)
# br_c4.set_attr(x=0)
# br_c11.set_attr(x=0)
br_c12.set_attr(m=10, T=80, p=25, fluid={'Water': 1})
br_c13_1.set_attr(x=0)
br_c14_1.set_attr(m=10, p=10, fluid={'Methanol': 1})
# ---------- Generator -------------
generator = Bus("generator")
generator.add_comps(
    {"comp": br_turbine, "char": 0.98, "base": "component"},
    # {"comp": rc_pump, "char": 0.98, "base": "bus"},
    # {"comp": rc_pump_sto, "char": 0.98, "base": "bus"},
)
br.add_busses(generator)

br.solve(mode='design')
br.print_results()

# plot
import matplotlib.pyplot as plt
import numpy as np
from fluprodia import FluidPropertyDiagram

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

# diagram.set_limits(x_min=0, x_max=2100, y_min=1e0, y_max=2e2)
diagram.draw_isolines(fig, ax, 'logph', x_min=10, x_max=1500, y_min=1, y_max=200)

for key in result_dict.keys():
    datapoints = result_dict[key]['datapoints']
    _ = ax.plot(datapoints['h'],datapoints['p'], color='#ff0000')
    _ = ax.scatter(datapoints['h'][0],datapoints['p'][0], color='#ff0000')

fig.savefig('brayton.png')
