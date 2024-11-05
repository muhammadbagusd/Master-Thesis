# ------------ HP edited ---------------
from tespy.components import (Compressor, Condenser ,SimpleHeatExchanger, 
                              HeatExchanger, Pump, Turbine, Valve, CycleCloser, 
                              Source, Sink)
from tespy.connections import Connection, Bus
from tespy.networks import Network

nw = Network(fluids=['Water', 'NH3', 'ethanol', 'Air'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# Heat Pump Cycle Components (Charging)
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

# Heat Pump Cycle Connections (Closed Loop with CycleCloser)
c1 = Connection(cc, 'out1', ev, 'in1', label='1')
c2 = Connection(ev, 'out1', cp, 'in1', label='2')
c3 = Connection(cp, 'out1', hx1, 'in2', label='3')
c4 = Connection(hx1, 'out2', cd, 'in2', label='4')
c5 = Connection(cd, 'out2', hx2, 'in2', label='5')
c6 = Connection(hx2, 'out2', va, 'in1', label='6')
c7 = Connection(va, 'out1', cc, 'in1', label='7')

nw.add_conns(c1, c2, c3, c4, c5, c6, c7)

# alternative connection
c11 = Connection(aso, 'out1', ev, 'in2', label='11')
c12 = Connection(ev, 'out2', asi, 'in1', label='12')

nw.add_conns(c11, c12)

# ---------- storage -------------
# Hot and Cold Storage Interfaces (Simplified)
c21 = Connection(sso, "out1", hx2, "in1", label='21')
c22 = Connection(hx2, "out1", cd, "in1", label="22")
c23 = Connection(cd, "out1", hx1, "in1", label="23")
c24 = Connection(hx1, "out1", ssi, "in1", label="24")

nw.add_conns(c21, c22, c23, c24)

# ---new parameters ---
hx1.set_attr(pr1=0.98, pr2=0.98, ttd_l=5)
hx2.set_attr(pr1=0.98, pr2=0.98)
cd.set_attr(pr1=0.98, pr2=0.98)
ev.set_attr(pr1=0.98, pr2=0.98, ttd_l=5)
cp.set_attr(eta_s=0.85, P=1e7)

c2.set_attr(x=1, fluid={'NH3': 1})
c4.set_attr(T=80)
c5.set_attr(T=60)
c6.set_attr(T=50)

c11.set_attr(T=5, p=1, fluid={'water': 1})
c12.set_attr(m=10)

c21.set_attr(m=10, p=5, fluid={"water": 1})

nw.solve(mode='design')
nw.print_results()
print(f'COP = {(abs(cd.Q.val)+abs(hx1.Q.val)+abs(hx2.Q.val)) / cp.P.val}')
