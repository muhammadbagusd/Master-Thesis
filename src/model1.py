# ---------- input storage temperature -----------
from tespy.components import Compressor, Condenser, SimpleHeatExchanger, HeatExchanger, Pump, Turbine, CycleCloser, Source, Sink, Valve
from tespy.connections import Connection, Bus
from tespy.networks import Network
import matplotlib.pyplot as plt
import numpy as np
from fluprodia import FluidPropertyDiagram

def create_connections_charge(network=None, charging_mode=True, Tsto_in=None, Tsto_out=None, Tenv=None):
    # Create Brayton Cycle Network
    # Ensure temp is provided for non-looped operation
    if Tsto_out is None:
        raise ValueError("Temperature must be provided.")

    cp = Compressor('HP Compressor')
    cd = Condenser('HP Condenser')  # Transfers heat to hot storage
    va = Valve('HP Expansion Valve')
    ev = HeatExchanger('HP Evaporator')
    pc = HeatExchanger('Pre Cooler')
    sc = HeatExchanger('sub Cooler')
    cc = CycleCloser('HP Cycle Closer')  # Closes the heat pump loop

    # Storage Sources and Sinks
    sso = Source('Storage Source')
    ssi = Sink('Storage Sink')
    # ambient Source and Sink
    aso = Source('ambient Source')
    asi = Sink('ambient Sink')

    # ORC components
    cp = Pump('RC Pump')
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
        c1 = Connection(cc, 'out1', ev, 'in2', label='1')
        c2 = Connection(ev, 'out2', cp, 'in1', label='2')
        c3 = Connection(cp, 'out1', pc, 'in1', label='3')
        c4 = Connection(pc, 'out1', cd, 'in1', label='4')
        c5 = Connection(cd, 'out1', sc, 'in1', label='5')
        c6 = Connection(sc, 'out1', va, 'in1', label='6')
        c7 = Connection(va, 'out1', cc, 'in1', label='7')

        c11 = Connection(sso, 'out1', sc, 'in2', label='11')
        c12 = Connection(sc, 'out2', cd, 'in2', label='12')
        c13 = Connection(cd, 'out2', pc, 'in2', label='13')
        c14 = Connection(pc, 'out2', ssi, 'in1', label='14')

        c21 = Connection(aso, 'out1', ev, 'in1', label='21')
        c22 = Connection(ev, 'out1', asi, 'in1', label='22')

        network.add_conns(c1, c2, c3, c4, c5, c6, c7, c11, c12, c13, c14, c21, c22)

        ev.set_attr(pr1=1, pr2=1, ttd_l=5) #ttd_l = out1-in2, ttd_u = in1 - out2
        cp.set_attr(eta_s=0.9)
        cd.set_attr(pr1=1, pr2=1, ttd_u=10)
        pc.set_attr(pr1=1, pr2=1, ttd_u=5)
        sc.set_attr(pr1=1, pr2=1)
        # va.set_attr(pr=0.3)

        c21.set_attr(T=Tenv, fluid={"air": 1})
        c22.set_attr(p=1)

        c11.set_attr(T=Tsto_in, p=1, m=10, fluid={"water": 1}) # T=40 for model with environment temp setting
        c14.set_attr(T=Tsto_out)
        
        # c1.set_attr(m=10)
        c2.set_attr(p=8)
        c3.set_attr(p=34.73, fluid={'R32': 1})
        c6.set_attr(T=Tsto_in+5)

        
        # Generator setup
        ep_hp = Bus("Produkt")
        ep_hp.add_comps(
            {"comp": ssi, "char": 0.98, "base": "component"}, # bus itu buat yg masuk ke system, component buat yg keluar
            {"comp": sso, "char": 0.98, "base": "bus"},
        ) 
        ef_hp = Bus('Fuel')
        ef_hp.add_comps(
            {'comp': cp, 'base': 'bus'},
        )
        el_hp = Bus('Loss')
        el_hp.add_comps({'comp': aso, 'base': 'bus'}, {'comp': asi}) # bus itu buat yg masuk ke system, component buat yg keluar

        network.add_busses(ep_hp, ef_hp, el_hp)
        
        network.set_attr(iterinfo=False)
        network.solve(mode='design')
        network.print_results()

    else:
        # ------------ Create Connections f  or Rankine Cycle -------------
        # Rankine Cycle Connections (Closed Loop with CycleCloser)
        c1 = Connection(cc, 'out1', tb, 'in1', label='1')
        c2 = Connection(tb, 'out1', cd, 'in1', label='2')
        c3 = Connection(cd, 'out1', cp, 'in1', label='3')
        c4 = Connection(cp, 'out1', ph, 'in2', label='4')
        c5 = Connection(ph, 'out2', ev, 'in2', label='5')
        c6 = Connection(ev, 'out2', sh, 'in2', label='6')
        c7 = Connection(sh, 'out2', cc, 'in1', label='7')

        c11 = Connection(sso, 'out1', sh, 'in1', label='11')
        c12 = Connection(sh, 'out1', ev, 'in1', label='12')
        c13 = Connection(ev, 'out1', ph, 'in1', label='13')
        c14 = Connection(ph, 'out1', ssi, 'in1', label='14')

        c21 = Connection(aso, 'out1', cd, 'in2', label='21')
        c22 = Connection(cd, 'out2', asi, 'in1', label='22')

        network.add_conns(c1, c2, c3, c4, c5, c6, c7, c11, c12, c13, c14, c21, c22)

        ev.set_attr(pr1=1, pr2=1, ttd_l=5) #ttd_l = out1-in2, ttd_u = in1 - out2
        tb.set_attr(eta_s=0.9) 
        cd.set_attr(pr1=1, pr2=1)
        cp.set_attr(eta_s=0.8)
        ph.set_attr(pr1=1, pr2=1)
        sh.set_attr(pr1=1, pr2=1, ttd_l=10)
        # va.set_attr(pr=0.3)

        c21.set_attr(T=Tenv, p=1, fluid={"air": 1})
        # c22.set_attr()

        c11.set_attr(T=Tsto_out, m=10, p=1, fluid={"water": 1}) # T=40 for model with environment temp setting
        c14.set_attr(T=Tsto_in)

        c1.set_attr(p=8, Td_bp=5, fluid={'R245fa': 1})
        # c3.set_attr(x=0)
        c2.set_attr(p=1)
        # c4.set_attr(T=14.6)
        # c5.set_attr(x=1)
        # c6.set_attr(x=1)

        # Generator setup
        gen = Bus("generator")
        gen.add_comps(
            {"comp": tb, "char": 0.98, "base": "component"},
            {"comp": cp, "char": 0.98, "base": "bus"},
        ) 
        ef_orc = Bus('Fuel')
        ef_orc.add_comps(
            {'comp': sso, 'base': 'bus'},
            {'comp': ssi, 'base': 'component'},
        )
        el_orc = Bus('Loss')
        el_orc.add_comps({'comp': aso, 'base': 'bus'}, {'comp': asi})
        
        network.add_busses(gen, ef_orc, el_orc)
        
        network.set_attr(iterinfo=False)
        network.solve(mode='design')
        network.print_results()
    return network, cd, pc, sc, cp, ep_hp, ef_hp, el_hp
    # return network, gen, ph, ev, sh, ef_orc, el_orc

nw_1 = Network(p_unit='bar', T_unit='C', h_unit='kJ / kg')

# model with storage output temperature
network, cd, pc, sc, cp, ep_hp, ef_hp, el_hp  = create_connections_charge(network=nw_1, charging_mode=True, Tsto_in=16, Tsto_out=90, Tenv=10)
# network, gen, ph, ev, sh, ef_orc, el_orc = create_connections_charge(network=nw_1, charging_mode=False, Tsto_in=20, Tsto_out=90, Tenv=10)
