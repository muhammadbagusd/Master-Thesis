# ---------- input storage temperature -----------
from tespy.components import Compressor, Condenser, SimpleHeatExchanger, HeatExchanger, Pump, Turbine, CycleCloser, Source, Sink, Valve
from tespy.connections import Connection, Bus
from tespy.networks import Network
import matplotlib.pyplot as plt
import numpy as np
from fluprodia import FluidPropertyDiagram

def create_connections_discharge(network=None, charging_mode=True, Tsto_in=None, Tsto_out=None, Tenv=None):
    # Create Brayton Cycle Network
    # Ensure temp is provided for non-looped operation
    if Tsto_out is None:
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
        c1 = Connection(cc, 'out1', ev, 'in2', label='1')
        c2 = Connection(ev, 'out2', cp, 'in1', label='2')
        c3 = Connection(cp, 'out1', hx1, 'in1', label='3')
        c4 = Connection(hx1, 'out1', hx2, 'in1', label='4')
        c5 = Connection(hx2, 'out1', cd, 'in1', label='5')
        c6 = Connection(cd, 'out1', va, 'in1', label='6')
        c7 = Connection(va, 'out1', cc, 'in1', label='7')

        network.add_conns(c1, c2, c3, c4, c5, c6, c7)

        # Alternative connection
        c11 = Connection(aso, 'out1', ev, 'in1', label='11')
        c12 = Connection(ev, 'out1', asi, 'in1', label='12')
        # Hot and Cold Storage Interfaces
        c21 = Connection(sso, "out1", cd, "in2", label='21')
        c22 = Connection(cd, "out2", hx2, "in2", label="22")
        c23 = Connection(hx2, "out2", hx1, "in2", label="23")
        c24 = Connection(hx1, "out2", ssi, "in1", label="24")

        network.add_conns(c11, c12, c21, c22, c23, c24)
        
        # Set attributes for the heat pump cycle
        # Set up for model with storage temperature
        hx1.set_attr(pr2=1, pr1=1, kA=1e5) # ttd_l=5) # uncomment for model with environment temp setting
        hx2.set_attr(pr1=1, ttd_l=5) # ttd_u=5) 
        ev.set_attr(pr1=1, ttd_u=5) #ttd_l = out1-in2, ttd_u = in1 - out2
        cp.set_attr(P=5e6)
        cd.set_attr(pr1=1, pr2=1, ttd_l=5)
        # va.set_attr(pr=0.1)
        # Storage connection
        c24.set_attr(T=Tsto_out, x=0, fluid={"water": 1}) # T=40 for model with environment temp setting
        # c23.set_attr(T=120)
        c21.set_attr(x=0, T=Tsto_in)
        # main connection
        c1.set_attr(p=5)
        c2.set_attr(m=10, x=1, fluid={'NH3': 1})
        # c7.set_attr(p=1)
        # c3.set_attr(p=10) # comment for Model with evironment temp setting
        # c4.set_attr(T=190)
        # c5.set_attr(T=185)
        # c7.set_attr(T=-10)
        # c6.set_attr(x=0)
        # evaporator connection
        c12.set_attr(m=10)
        c11.set_attr(T=Tenv, p=1, fluid={'water': 1})
        
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
        network.solve(mode='design')
        network.print_results()

    else:
        # ------------ Create Connections f  or Rankine Cycle -------------
        # Rankine Cycle Connections (Closed Loop with CycleCloser)
        c1 = Connection(cc, 'out1', tb, 'in1', label='31')
        c2 = Connection(tb, 'out1', cd, 'in1', label='32')
        c3 = Connection(cd, 'out1', p, 'in1', label='33')
        c4 = Connection(p, 'out1', ph, 'in2', label='34')
        c5 = Connection(ph, 'out2', ev, 'in2', label='35')
        c6 = Connection(ev, 'out2', sh, 'in2', label='36')
        c7 = Connection(sh, 'out2', cc, 'in1', label='37')

        network.add_conns(c1, c2, c3, c4, c5, c6, c7)

        # Connections to ambient environment (source and sink)
        c11 = Connection(aso, 'out1', cd, 'in2', label='41')
        c12 = Connection(cd, 'out2', asi, 'in1', label='42')
        # Connections to steam generator (source and sink)
        c21 = Connection(sso, 'out1', sh, 'in1', label='25')
        c22 = Connection(sh, 'out1', ev, 'in1', label='26')
        c23 = Connection(ev, 'out1', ph, 'in1', label='27')
        c24 = Connection(ph, 'out1', ssi, 'in1', label='28')

        network.add_conns(c11, c12, c21, c22, c23, c24)

        # Set attributes for Rankine cycle
        cd.set_attr(pr1=0.98, pr2=0.98) 
        tb.set_attr(eta_s=0.9)
        p.set_attr(eta_s=0.95)
        ph.set_attr( pr2=0.98)
        ev.set_attr(pr1=0.98, pr2=0.98)
        sh.set_attr(pr1=0.98, pr2=1, ttd_l=50)

        # Set Condenser connection
        c11.set_attr(p=1, T=Tenv, fluid={'water': 1}) 
        c12.set_attr(m=10)
        # Set Storage connection
        c21.set_attr(T=Tsto_out, x=0, fluid={'water': 1})
        c24.set_attr(T=Tsto_in, x=0)
        # Set Main cycle connection
        # c2.set_attr(x=0.9)
        c3.set_attr(T=80)
        #c3.set_attr(m=10, fluid={'ethanol': 1})
        c6.set_attr(x=1)  # Evaporate at 70°C
        c7.set_attr(Td_bp=5)
        c4.set_attr(m=10, fluid={'ethanol': 1})
        c5.set_attr(x=0.9)

        # Generator setup
        gen = Bus("generator")
        gen.add_comps(
            {"comp": tb, "char": 0.98, "base": "component"},
            {"comp": p, "char": 0.98, "base": "bus"},
        ) 
        ef_orc = Bus('Fuel')
        ef_orc.add_comps(
            {'comp': sso, 'base': 'bus'},
            {'comp': ssi, 'base': 'component'},
        )
        el_orc = Bus('Loss')
        el_orc.add_comps({'comp': aso, 'base': 'bus'}, {'comp': asi})
        
        network.add_busses(gen, ef_orc, el_orc)
        
        network.solve(mode='design')
        network.print_results()
    # return network, cd, hx1, hx2, cp, ep_hp, ef_hp, el_hp
    return network, gen, ph, ev, sh, ef_orc, el_orc

nw_1 = Network(p_unit='bar', T_unit='C', h_unit='kJ / kg')

# model with storage output temperature
# network, cd, hx1, hx2, cp, ep_hp, ef_hp, el_hp  = create_connections_discharge(network=nw_1, charging_mode=True, Tsto_in=70, Tsto_out=170, Tenv=10)
network, gen, ph, ev, sh, ef_orc, el_orc = create_connections_discharge(network=nw_1, charging_mode=False, Tsto_in=70, Tsto_out=170, Tenv=10)
