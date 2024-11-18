from tespy.components import Compressor, Condenser, SimpleHeatExchanger, HeatExchanger, Pump, Turbine, CycleCloser, Source, Sink
from tespy.connections import Connection
from tespy.networks import Network

# Create Brayton Cycle Network
nw = Network(fluids=['Ethanol', 'water', 'NH3'], p_unit='bar', T_unit='C', h_unit='kJ / kg')
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

# Create network connections (start with charging phase)
def create_connections(charging_mode=True):
    # Set default connections for charging phase
    if charging_mode:
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
        # Hot and Cold Storage Interfaces (Simplified)
        c21 = Connection(sso, "out1", hx2, "in1", label='21')
        c22 = Connection(hx2, "out1", cd, "in1", label="22")
        c23 = Connection(cd, "out1", hx1, "in1", label="23")
        c24 = Connection(hx1, "out1", ssi, "in1", label="24")

        nw.add_conns(c11, c12, c21, c22, c23, c24)

        # ---new parameters ---
        hx1.set_attr(pr1=0.98, pr2=0.98, ttd_l=5)
        hx2.set_attr(pr1=0.98, pr2=0.98)
        ev.set_attr(pr1=0.98, pr2=0.98, ttd_l=5)
        cp.set_attr(eta_s=0.85, P=1e7)

        c2.set_attr(x=1, fluid={'NH3': 1})
        c4.set_attr(T=80)
        c5.set_attr(T=60)
        c6.set_attr(T=50)
        c11.set_attr(T=5, p=1, fluid={'water': 1})
        c12.set_attr(m=10)
        c21.set_attr(m=10, p=0.5, fluid={"water": 1})
    else:
        # Rankine Cycle Connections (Closed Loop with CycleCloser)
        c1 = Connection(cc, 'out1', tb, 'in1', label='1')
        c2 = Connection(tb, 'out1', cd, 'in1', label='2')
        c3 = Connection(cd, 'out1', p, 'in1', label='3')
        c4 = Connection(p, 'out1', ph, 'in2', label='4')
        c5 = Connection(ph, 'out2', ev, 'in2', label='5')
        c6 = Connection(ev, 'out2', sh, 'in2', label='6')
        c7 = Connection(sh, 'out2', cc, 'in1', label='7')

        nw.add_conns(c1, c2, c3, c4, c5, c6, c7)

        # Connections to the ambient environment (source and sink)
        c11 = Connection(aso, 'out1', cd, 'in2', label='11')
        c12 = Connection(cd, 'out2', asi, 'in1', label='12')
        # Connections to the steam generator (source and sink)
        c21 = Connection(sso, 'out1', sh, 'in1', label='21')
        c22 = Connection(sh, 'out1', ev, 'in1', label='22')
        c23 = Connection(ev, 'out1', ph, 'in1', label='23')
        c24 = Connection(ph, 'out1', ssi, 'in1', label='24')

        nw.add_conns(c11, c12, c21, c22, c23,c24)
        
        # ------- codenser connection --------
        c11.set_attr(p=1, T=15, fluid={'water': 1})
        # -------- storage connection -----------
        c21.set_attr(T=100, p=1, fluid={'water': 1}) 
        # ----------- main cycle connection ----------
        c3.set_attr(p=0.1)
        c4.set_attr(p=0.72, T=30, fluid={'ethanol': 1}) 
        c6.set_attr(x=1) # evaporate at 70°C
        c7.set_attr(Td_bp=5)

        # set parameter RC
        tb.set_attr(eta_s=0.8)
        p.set_attr(eta_s=0.8, P=1e7)
        ph.set_attr(pr1=0.98, pr2=0.98, Q=-5e3)
        ev.set_attr(pr1=0.98, pr2=0.98, Q=-5e3)
        sh.set_attr(pr1=0.98, pr2=0.98)

        # ---------- Generator -------------
        gen = Bus("generator")
        gen.add_comps(
            {"comp": tb, "char": 0.98, "base": "component"},
            {"comp": p, "char": 0.98, "base": "bus"},
        )
        nw.add_busses(gen)

# Set parameter        
cd.set_attr(pr1=0.98, pr2=0.98)

# Choose whether to run charging or discharging
charging_mode = False  # Set to False for discharging phase

# Create appropriate connections
create_connections(charging_mode=charging_mode)


# Solve the network
nw.solve(mode='design')
nw.print_results()
# {round(abs(hhx.Q.val) / cp.P.val, 4)}
# print(COP)
