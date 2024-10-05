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
# hp_ventil_ev = Valve('hp Valve ev')

# Heat Pump Cycle Connections (Closed Loop with CycleCloser)
hp_c1 = Connection(hp_closer, 'out1', hp_evaporator, 'in1', label='1')
hp_c2 = Connection(hp_evaporator, 'out1', hp_compressor, 'in1', label='2')
hp_c3 = Connection(hp_compressor, 'out1', hp_condenser, 'in1', label='3')
hp_c4 = Connection(hp_condenser, 'out1', hp_valve, 'in1', label='4')
hp_c5 = Connection(hp_valve, 'out1', hp_closer, 'in1', label='5')

nw.add_conns(hp_c1, hp_c2, hp_c3, hp_c4, hp_c5)

ev_c1 = Connection(hp_ambient_source_ev, 'out1', hp_pump_ev, 'in1', label='ev 1')
ev_c2 = Connection(hp_pump_ev, 'out1', hp_evaporator, 'in2', label='ev 2')
ev_c3 = Connection(hp_evaporator, 'out2', hp_ambient_sink_ev, 'in1', label='ev 3')
# ev_c4 = Connection(hp_ventil_ev, 'out1', hp_ambient_sink_ev, 'in1', label='ev 4')
nw.add_conns(ev_c1, ev_c2, ev_c3)
ev_c1.set_attr(m=10, T=10, p=1, fluid={"water": 1})
ev_c3.set_attr(p=ev_c1.p.val)

# set Parameter
hp_compressor.set_attr(eta_s=1, P=1e5)
hp_condenser.set_attr(pr1=1, pr2=1, ttd_l=30)
hp_evaporator.set_attr(pr1=1, pr2=0.9, ttd_l=2)
hp_pump_ev.set_attr(eta_s=0.78)

from CoolProp.CoolProp import PropsSI as PSI
hp_c3.set_attr(m=30, fluid={'NH3': 1})
hp_c2.set_attr(x=1)

# ---------- storage -------------
# Hot and Cold Storage Interfaces (Simplified)
sto_c5 = Connection(hp_ambient_source, "out1", hp_condenser, "in2")
sto_c6 = Connection(hp_condenser, "out2", hp_ambient_sink, "in1")

nw.add_conns(sto_c5, sto_c6)

# set parameter storage
sto_c5.set_attr(m=30, p=5, fluid={"water": 1})

nw.solve(mode='design')
nw.print_results()
