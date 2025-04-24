from tespy.components import Compressor, Condenser, HeatExchanger, Pump, Turbine, CycleCloser, Source, Sink, Valve
from tespy.connections import Connection, Bus
from tespy.networks import Network

def create_system(network, mode='charging', Tsto_in=None, Tsto_out=None, Tenv=None):
    if Tsto_out is None or Tsto_in is None or Tenv is None:
        raise ValueError("Missing required temperature values.")

    # Components common to charging (Brayton) side with IHX
    cp = Compressor('Compressor')
    cd = Condenser('Condenser')
    va = Valve('Expansion Valve')
    ev = HeatExchanger('Evaporator')
    pc = HeatExchanger('Pre Cooler')
    sc = HeatExchanger('Sub Cooler')
    ihx = HeatExchanger('Internal Heat Exchanger')
    cc = CycleCloser('Cycle Closer')
    sso = Source('Storage Source')
    ssi = Sink('Storage Sink')
    aso = Source('Ambient Source')
    asi = Sink('Ambient Sink')

    # ORC components (shared in both modes)
    p = Pump('Pump')
    tb = Turbine('Turbine')
    rc_cd = Condenser('RC Condenser')
    rc_cc = CycleCloser('RC Cycle Closer')
    ph = HeatExchanger("Preheater")
    rc_ev = HeatExchanger("RC Evaporator")
    sh = HeatExchanger("Superheater")

    if mode == 'charging':
        # Connections for HP system with IHX
        c1 = Connection(cc, 'out1', ev, 'in2')
        c2 = Connection(ev, 'out2', ihx, 'in2')
        c3 = Connection(ihx, 'out2', cp, 'in1')
        c4 = Connection(cp, 'out1', pc, 'in1')
        c5 = Connection(pc, 'out1', cd, 'in1')
        c6 = Connection(cd, 'out1', sc, 'in1')
        c7 = Connection(sc, 'out1', ihx, 'in1')
        c8 = Connection(ihx, 'out1', va, 'in1')
        c9 = Connection(va, 'out1', cc, 'in1')

        c21 = Connection(sso, 'out1', sc, 'in2')
        c22 = Connection(sc, 'out2', cd, 'in2')
        c23 = Connection(cd, 'out2', pc, 'in2')
        c24 = Connection(pc, 'out2', ssi, 'in1')

        c11 = Connection(aso, 'out1', ev, 'in1')
        c12 = Connection(ev, 'out1', asi, 'in1')

        network.add_conns(c1, c2, c3, c4, c5, c6, c7, c8, c9, c11, c12, c21, c22, c23, c24)

        # Component attributes
        ev.set_attr(pr1=1, pr2=1, ttd_l=5)
        cp.set_attr(eta_s=0.9)
        cd.set_attr(pr1=1, pr2=1, ttd_u=5)
        pc.set_attr(pr1=1, pr2=1, ttd_u=5)
        sc.set_attr(pr1=1, pr2=1)
        ihx.set_attr(pr1=1, pr2=1)

        # Connection attributes
        c11.set_attr(T=Tenv, fluid={"air": 1})
        c12.set_attr(p=1)
        c21.set_attr(T=Tsto_in, p=1, m=10, fluid={"water": 1})
        c24.set_attr(T=Tsto_out)
        c2.set_attr(p=9.5, x=1)
        c4.set_attr(p=31, fluid={'R32': 1})
        c7.set_attr(T=Tsto_in + 5)

        # Busses
        ep = Bus("Produkt")
        ep.add_comps({"comp": ssi, "char": 0.98, "base": "component"},
                     {"comp": sso, "char": 0.98, "base": "bus"})

        ef = Bus('Fuel')
        ef.add_comps({'comp': cp, 'base': 'bus'})

        el = Bus('Loss')
        el.add_comps({'comp': aso, 'base': 'bus'}, {'comp': asi})

        network.add_busses(ep, ef, el)
        network.set_attr(iterinfo=False)
        network.solve(mode='design')
        return network, ep, ef, el, cd, pc, sc, cp

    else:
        # ORC side – same as original
        c31 = Connection(rc_cc, 'out1', tb, 'in1')
        c32 = Connection(tb, 'out1', rc_cd, 'in1')
        c33 = Connection(rc_cd, 'out1', p, 'in1')
        c34 = Connection(p, 'out1', ph, 'in2')
        c35 = Connection(ph, 'out2', rc_ev, 'in2')
        c36 = Connection(rc_ev, 'out2', sh, 'in2')
        c37 = Connection(sh, 'out2', rc_cc, 'in1')

        c25 = Connection(sso, 'out1', sh, 'in1')
        c26 = Connection(sh, 'out1', rc_ev, 'in1')
        c27 = Connection(rc_ev, 'out1', ph, 'in1')
        c28 = Connection(ph, 'out1', ssi, 'in1')

        c41 = Connection(aso, 'out1', rc_cd, 'in2')
        c42 = Connection(rc_cd, 'out2', asi, 'in1')

        network.add_conns(c31, c32, c33, c34, c35, c36, c37, c25, c26, c27, c28, c41, c42)

        rc_ev.set_attr(pr1=1, pr2=1, ttd_l=5)
        tb.set_attr(eta_s=0.9)
        rc_cd.set_attr(pr1=1, pr2=1, ttd_u=5)
        ph.set_attr(pr1=1, pr2=1, ttd_l=5)
        sh.set_attr(pr1=1, pr2=1, ttd_l=5)

        c41.set_attr(T=Tenv, p=1, fluid={"air": 1})
        c25.set_attr(T=Tsto_out, m=10, p=1, fluid={"water": 1})
        c28.set_attr(T=Tsto_in)
        c31.set_attr(p=8, T=Tsto_out-5, fluid={'R245fa': 1})
        c32.set_attr(p=1)

        gen = Bus("generator")
        gen.add_comps({"comp": tb, "char": 0.98, "base": "component"},
                      {"comp": p, "char": 0.98, "base": "bus"})

        ef = Bus('Fuel')
        ef.add_comps({'comp': sso, 'base': 'bus'},
                     {'comp': ssi, 'base': 'component'})

        el = Bus('Loss')
        el.add_comps({'comp': aso, 'base': 'bus'}, {'comp': asi})

        network.add_busses(gen, ef, el)
        network.set_attr(iterinfo=False)
        network.solve(mode='design')
        return network, gen, ef, el, ph, rc_ev, sh
