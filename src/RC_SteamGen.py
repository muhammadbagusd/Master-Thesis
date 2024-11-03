#%% --------------- RC with Steam Generator Super heater ---------
# ---- RC with pump and ventil ---------
from tespy.components import (Compressor, Condenser ,SimpleHeatExchanger, 
                              HeatExchanger, Pump, Turbine, Valve, CycleCloser, 
                              Source, Sink, Drum)
from tespy.connections import Connection, Bus
from tespy.networks import Network
# ---------- Rankine cycle -------------
RC = Network(fluids=['Ethanol', 'R134a', 'water'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# Rankine Cycle Components (Discharging)
p = Pump('RC Pump')
sg = HeatExchanger('RC steam generator')  # Receives heat from hot storage
tb = Turbine('RC Turbine')
cd = Condenser('RC Condenser')
cc = CycleCloser('RC Cycle Closer')  # Closes the Rankine cycle loop
# steam generator
ph = HeatExchanger("preheater")
ev = HeatExchanger("evaporator")
sh = HeatExchanger("Super heater")

# Sources and Sinks
aso = Source('rc Ambient Source 1')
asi = Sink('rc Ambient Sink 1')

# Sources and Sinks
sso = Source('rc Storage Source')
ssi = Sink('rc Storage Sink')


# Rankine Cycle Connections (Closed Loop with CycleCloser)
c1 = Connection(cc, 'out1', tb, 'in1', label='1')
c2 = Connection(tb, 'out1', cd, 'in1', label='2')
c3 = Connection(cd, 'out1', p, 'in1', label='3')
c4 = Connection(p, 'out1', ph, 'in2', label='4')
c5 = Connection(ph, 'out2', ev, 'in2', label='5')
c6 = Connection(ev, 'out2', sh, 'in2', label='6')
c7 = Connection(sh, 'out2', cc, 'in1', label='7')

RC.add_conns(c1, c2, c3, c4, c5, c6, c7)

# Connections to the ambient environment (source and sink)
c11 = Connection(aso, 'out1', cd, 'in2', label='11')
c12 = Connection(cd, 'out2', asi, 'in1', label='12')

RC.add_conns(c11, c12)

# Connections to the steam generator (source and sink)
c21 = Connection(sso, 'out1', sh, 'in1', label='21')
c22 = Connection(sh, 'out1', ev, 'in1', label='22')
c23 = Connection(ev, 'out1', ph, 'in1', label='23')
c24 = Connection(ph, 'out1', ssi, 'in1', label='24')

RC.add_conns(c21, c22, c23,c24)

# ------- codenser connection --------
c11.set_attr(p=1, T=15, fluid={'water': 1})
# -------- storage connection -----------
c21.set_attr(T=80, p=1, fluid={'water': 1}) 
# ----------- main cycle connection ----------
c3.set_attr(p=0.1)
c4.set_attr(p=0.72, T=30, fluid={'ethanol': 1}) 
c6.set_attr(x=1) # evaporate at 70°C
c7.set_attr(Td_bp=5)

# set parameter RC
cd.set_attr(pr1=0.98, pr2=0.98)
tb.set_attr(eta_s=0.8)
p.set_attr(eta_s=0.8, P=1e5)
ph.set_attr(pr1=0.98, pr2=0.98, ttd_u=5)
ev.set_attr(pr1=0.98, pr2=0.98, ttd_u=5)
sh.set_attr(pr1=0.98, pr2=0.98)

# ---------- Generator -------------
gen = Bus("generator")
gen.add_comps(
    {"comp": tb, "char": 0.98, "base": "component"},
    {"comp": p, "char": 0.98, "base": "bus"},
)

RC.add_busses(gen)
RC.solve(mode='design')
RC.print_results()
