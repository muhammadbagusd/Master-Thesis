from tespy.components import Compressor, Condenser, SimpleHeatExchanger, HeatExchanger, Pump, Turbine, CycleCloser, Source, Sink, Valve
from tespy.connections import Connection, Bus
from tespy.networks import Network
import matplotlib.pyplot as plt
import numpy as np
from fluprodia import FluidPropertyDiagram

def create_connections(network=None, charging_mode=True, temp=None):
    # Create Brayton Cycle Network
    # Ensure temp is provided for non-looped operation
    if temp is None:
        raise ValueError("Temperature must be provided.")

    # HP Components
    cp = Compressor('HP Compressor')
    cd = Condenser('HP Condenser')  # Transfers heat to hot storage
    va = Valve('HP Expansion Valve')
    ev = HeatExchanger('HP Evaporator')
    cc = CycleCloser('HP Cycle Closer')  # Closes the heat pump loop
    hx1 = HeatExchanger('Heat Exchanger 1')
    hx2 = HeatExchanger('Heat Exchanger 2')
    # Sources and Sinks
    aso = Source('hp Ambient Source ev')
    asi = Sink('hp Ambient Sink ev')
    # Evaporator Sources and Sinks
    sso = Source('Storage Source')
    ssi = Sink('Storage Sink')

    # ORC components
    p = Pump('RC Pump')
    sg = HeatExchanger('RC steam generator')  # Receives heat from hot storage
    tb = Turbine('RC Turbine')
    cd = Condenser('RC Condenser')
    cc = CycleCloser('RC Cycle Closer')  # Closes the Rankine cycle loop
    ph = HeatExchanger("preheater")
    ev = HeatExchanger("evaporator")
    sh = HeatExchanger("Super heater")
    aso = Source('rc Ambient Source 1')
    asi = Sink('rc Ambient Sink 1')
    sso = Source('rc Storage Source')
    ssi = Sink('rc Storage Sink')

    # ------------ Create Connections for Charging Mode -------------
    if charging_mode:
        # Heat Pump Cycle Connections (Closed Loop with CycleCloser)
        c1 = Connection(cc, 'out1', ev, 'in1', label='1')
        c2 = Connection(ev, 'out1', cp, 'in1', label='2')
        c3 = Connection(cp, 'out1', hx1, 'in2', label='3')
        c4 = Connection(hx1, 'out2', cd, 'in2', label='4')
        c5 = Connection(cd, 'out2', hx2, 'in2', label='5')
        c6 = Connection(hx2, 'out2', va, 'in1', label='6')
        c7 = Connection(va, 'out1', cc, 'in1', label='7')

        network.add_conns(c1, c2, c3, c4, c5, c6, c7)

        # Alternative connection
        c11 = Connection(aso, 'out1', ev, 'in2', label='11')
        c12 = Connection(ev, 'out2', asi, 'in1', label='12')
        # Hot and Cold Storage Interfaces
        c21 = Connection(sso, "out1", hx2, "in1", label='21')
        c22 = Connection(hx2, "out1", cd, "in1", label="22")
        c23 = Connection(cd, "out1", hx1, "in1", label="23")
        c24 = Connection(hx1, "out1", ssi, "in1", label="24")

        network.add_conns(c11, c12, c21, c22, c23, c24)
        
        # Set attributes for the heat pump cycle
        hx1.set_attr(pr1=0.98, pr2=0.98, ttd_l=5)
        hx2.set_attr(pr1=0.98, pr2=0.98)
        ev.set_attr(pr1=0.98, pr2=0.98, ttd_l=5)
        cp.set_attr(eta_s=0.85, P=1e7)
        cd.set_attr(pr1=0.98, pr2=0.98)

        c2.set_attr(x=1, fluid={'NH3': 1})
        c4.set_attr(T=80)
        c5.set_attr(T=60)
        c6.set_attr(T=50)
        c12.set_attr(m=10)
        c21.set_attr(m=10, p=0.5, fluid={"water": 1})
        c11.set_attr(T=temp, p=1, fluid={'water': 1})
        network.solve(mode='design')

    else:
        # ------------ Create Connections for Rankine Cycle -------------
        # Rankine Cycle Connections (Closed Loop with CycleCloser)
        c1 = Connection(cc, 'out1', tb, 'in1', label='1')
        c2 = Connection(tb, 'out1', cd, 'in1', label='2')
        c3 = Connection(cd, 'out1', p, 'in1', label='3')
        c4 = Connection(p, 'out1', ph, 'in2', label='4')
        c5 = Connection(ph, 'out2', ev, 'in2', label='5')
        c6 = Connection(ev, 'out2', sh, 'in2', label='6')
        c7 = Connection(sh, 'out2', cc, 'in1', label='7')

        network.add_conns(c1, c2, c3, c4, c5, c6, c7)

        # Connections to ambient environment (source and sink)
        c11 = Connection(aso, 'out1', cd, 'in2', label='11')
        c12 = Connection(cd, 'out2', asi, 'in1', label='12')
        # Connections to steam generator (source and sink)
        c21 = Connection(sso, 'out1', sh, 'in1', label='21')
        c22 = Connection(sh, 'out1', ev, 'in1', label='22')
        c23 = Connection(ev, 'out1', ph, 'in1', label='23')
        c24 = Connection(ph, 'out1', ssi, 'in1', label='24')

        network.add_conns(c11, c12, c21, c22, c23, c24)

        # Set attributes for Rankine cycle
        cd.set_attr(pr1=0.98, pr2=0.98)
        tb.set_attr(eta_s=0.8)
        p.set_attr(eta_s=0.8, P=1e7)
        ph.set_attr(pr1=0.98, pr2=0.98, Q=-5e3)
        ev.set_attr(pr1=0.98, pr2=0.98, Q=-5e3)
        sh.set_attr(pr1=0.98, pr2=0.98)

        # Set Condenser connection
        c11.set_attr(p=1, T=15, fluid={'water': 1})
        # Set Storage connection
        c21.set_attr(T=100, p=1, fluid={'water': 1})
        # Set Main cycle connection
        c3.set_attr(p=0.1)
        c4.set_attr(p=0.72, T=30, fluid={'ethanol': 1})
        c6.set_attr(x=1)  # Evaporate at 70°C
        c7.set_attr(Td_bp=5)

        # Generator setup
        gen = Bus("generator")
        gen.add_comps(
            {"comp": tb, "char": 0.98, "base": "component"},
            {"comp": p, "char": 0.98, "base": "bus"},
        )
        network.add_busses(gen)
    # nw.print_results()
    return network

# ---- plot verschiedene Temperaturen ---------
import matplotlib.pyplot as plt
import numpy as np
from fluprodia import FluidPropertyDiagram

# List of ambient temperatures you want to simulate
ambient_temperatures = [5, 10, 15]  # Modify this list as needed

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
diagram.draw_isolines(fig, ax, 'logph', x_min=0, x_max=3500, y_min=0.5, y_max=2e2)

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
    network = create_connections(network=nw, charging_mode=True, temp=temp)
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
        ax.plot([], [], color=colors[idx], label=f'Temp: {temp}°C')
        
# Set labels and title for the log-p h diagram
ax.set_xlabel('Enthalpy, h in kJ/kg', fontsize=16)
ax.set_ylabel('Pressure, p in bar', fontsize=16)
ax.set_title('log-p h Diagram of Heat Pump', fontsize=20)

# Create a legend for the temperature curves
ax.legend(title='Ambient Temperature', fontsize=12)

# Set font size for the x-axis and y-axis ticks
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
plt.tight_layout()
plt.show()

fig.savefig('cek.png')
