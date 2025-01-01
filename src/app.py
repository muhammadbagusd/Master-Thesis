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
        hx2.set_attr(pr1=0.98, pr2=0.98) # ,ttd_l=5) # uncomment for model with environment temp setting
        ev.set_attr(pr1=0.98, pr2=0.98, ttd_l=5)
        cp.set_attr(eta_s=0.85, P=4e6)
        cd.set_attr(pr1=0.98, pr2=0.98)
        
        # Storage connection
        c24.set_attr(T=temp, m=10, p=10, fluid={"water": 1}) # comment for model with environment temp setting
        # c24.set_attr(m=10, fluid={"water": 1}) # uncomment for model with environment temp setting
      
        # main connection
        c2.set_attr(x=1, fluid={'NH3': 1})
        # c4.set_attr(T=90) # uncomment for model with environment temp setting
        c5.set_attr(x=0)
        c6.set_attr(T=50)
        
        # evaporator connection
        c12.set_attr(m=10)
        c11.set_attr(T=10, p=1, fluid={'water': 1}) # T=temp for model with environment temp setting
        network.solve(mode='design')
        network.print_results()

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
        c21.set_attr(T=100, p=0.5, fluid={'water': 1})
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
    return network, cd, cp, hx1, hx2

nw = Network(p_unit='bar', T_unit='C', h_unit='kJ / kg')

# model with storage output temperature
network = create_connections(network=nw, charging_mode=True, temp=200)

# uncomment for model with environment temp setting
# network = create_connections(network=nw, charging_mode=True, temp=10)
