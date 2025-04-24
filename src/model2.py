# unified_model.py

from tespy.components import Compressor, Condenser, HeatExchanger, Pump, Turbine, CycleCloser, Source, Sink
from tespy.connections import Connection, Bus
from tespy.networks import Network
from tespy.tools import ExergyAnalysis
import pandas as pd

def create_system(network, mode='charging', Tsto_in=None, Tsto_out=None, Tenv=None):
    # Validate inputs
    if Tsto_out is None or Tsto_in is None or Tenv is None:
        raise ValueError("Missing required temperature values.")
  

    cp = Compressor('Compressor')
    tb = Turbine('Turbine')
    hhx = HeatExchanger('Heat Exchanger Hot Storage')
    chx = HeatExchanger('Heat Exchanger Cold Storage')
    rg = HeatExchanger('Regenerator')
    cc = CycleCloser('Cycle Closer')

    # Define Storage Tanks
    hssoc = Source('Hot Storage Source')
    hssic = Sink('Hot Storage Sink')
    cssoc = Source('Cold Storage Source')
    cssic = Sink('Cold Storage Sink')

    if mode == 'charging':
        # Charging: From compressor to storage via heat exchangers
        c1 = Connection(cc, 'out1', cp, 'in1', label='c1') 
        c2 = Connection(cp, 'out1', hhx, 'in1', label='c2')
        c3 = Connection(hhx, 'out1', tb, 'in1', label='c3')
        c4 = Connection(tb, 'out1', chx, 'in2', label='c4')
        c5 = Connection(chx, 'out2', cc, 'in1', label='c5')
        # Storage connections for charging phase
        c11 = Connection(cssoc, 'out1', chx, 'in1', label='c11')  
        c12 = Connection(chx, 'out1', cssic, 'in1', label='c12')
        c13 = Connection(hssoc, 'out1', hhx, 'in2', label='c13') 
        c14 = Connection(hhx, 'out2', hssic, 'in1', label='c14')

        # Add connections to network
        network.add_conns(c1, c2, c3, c4, c5, c11, c12, c13, c14)

        hhx.set_attr(pr1=1, pr2=1, ttd_u=10)
        chx.set_attr(pr1=1, pr2=1, ttd_u=1)
        tb.set_attr(eta_s=0.95)
        # set parameter connections
        c1.set_attr(p=18)
        c2.set_attr(m=10, fluid={'Nitrogen': 1}) 
        c3.set_attr(p=105, T=Tenv+10)
        
        c11.set_attr(T=Tenv, x=0) 
        c12.set_attr(m=5, fluid={'water': 1})
        
        c13.set_attr(T=Tenv, p=30)
        c14.set_attr(T=Tsto_out, fluid={'air': 1})
        # Busses
        ep = Bus("Produkt")
        ep.add_comps({"comp": hssic, "char": 0.98, "base": "component"},
                     {"comp": hssoc, "char": 0.98, "base": "bus"})

        ef = Bus('Fuel')
        ef.add_comps({"comp": tb, "char": 0.98, "base": "component"},
                      {"comp": cp, "char": 0.98, "base": "bus"})

        el = Bus('Loss')
        el.add_comps({'comp': cssoc, 'base': 'bus'}, {'comp': cssic})

        network.add_busses(ep, ef, el)
        network.set_attr(iterinfo=False)
        network.solve(mode='design')
    else:
        # Discharging: From compressor to storage via heat exchangers
        d1 = Connection(cc, 'out1', chx, 'in1', label='d1')
        d2 = Connection(chx, 'out1', cp, 'in1', label='d2')
        d3 = Connection(cp, 'out1', hhx, 'in2', label='d3')
        d4 = Connection(hhx, 'out2', tb, 'in1', label='d4')
        d5 = Connection(tb, 'out1', cc, 'in1', label='d5')
        # Storage connections for charging phase
        d11 = Connection(cssoc, 'out1', chx, 'in2', label='d11')  
        d12 = Connection(chx, 'out2', cssic, 'in1', label='d12')
        d13 = Connection(hssoc, 'out1', hhx, 'in1', label='d13')  
        d14 = Connection(hhx, 'out1', hssic, 'in1', label='d14')
        # Add reversed connections to network
        network.add_conns(d1, d2, d3, d4, d5, d11, d12, d13, d14)

        # Set turbine and compressor conditions for discharging phase
        tb.set_attr(eta_s=0.9) 
        chx.set_attr(pr1=1, pr2=1, ttd_u=120) 
        hhx.set_attr(pr1=1, pr2=1, ttd_l=1)
        # set parameter connections
        d1.set_attr(p=18)
        d2.set_attr(T=Tenv)
        d3.set_attr(m=10, p=105, fluid={'Nitrogen': 1})
        d11.set_attr(T=Tenv, x=0) 
        d12.set_attr(m=5, fluid={'water': 1})
        d13.set_attr(p=30, T=Tsto_out) 
        d14.set_attr(T=Tsto_in, fluid={'air': 1}) 

        # Busses
        ef = Bus("Produkt")
        ef.add_comps({"comp": hssic, "char": 0.98, "base": "component"},
                     {"comp": hssoc, "char": 0.98, "base": "bus"})

        ep = Bus('Fuel')
        ep.add_comps({"comp": tb, "char": 0.98, "base": "component"},
                      {"comp": cp, "char": 0.98, "base": "bus"})

        el = Bus('Loss')
        el.add_comps({'comp': cssoc, 'base': 'bus'}, {'comp': cssic})

        network.add_busses(ep, ef, el)
        network.set_attr(iterinfo=False)
        network.solve(mode='design')
    return network, ep, ef, el, hhx, chx, tb, cp
