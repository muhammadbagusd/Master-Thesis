from tespy.components import Compressor, Condenser, SimpleHeatExchanger, HeatExchanger, Pump, Turbine, CycleCloser, Source, Sink
from tespy.connections import Connection, Bus
from tespy.networks import Network

def create_connections(network=None, charging_mode=True, temp=None):
# Create Brayton Cycle Network
# br = Network(fluids=['Water', 'Nitrogen', 'Methanol'], p_unit='bar', T_unit='C', h_unit='kJ / kg')
# Define Components
    if temp is None:
        raise ValueError("Temperature must be provided.")
        
    cp = Compressor('Compressor')
    tb = Turbine('Turbine')
    hhx = HeatExchanger('Heat Exchanger Hot Storage')
    chx = HeatExchanger('Heat Exchanger Cold Storage')
    hxa = SimpleHeatExchanger('Simple Heat Exchanger A')
    hxb = SimpleHeatExchanger('Simple Heat Exchanger B')
    rg = HeatExchanger('Regenerator')
    cc = CycleCloser('Cycle Closer')

    # Define Storage Tanks
    hssoc = Source('Hot Storage Charge Source')
    hssic = Sink('Hot Storage Charge Sink')
    hssod = Source('Hot Storage Discharge Source')
    hssid= Sink('Hot Storage Discharge Sink')
    cssoc = Source('Cold Storage Charge Source')
    cssic = Sink('Cold Storage Charge Sink')

    # Create network connections (start with charging phase)
    # Set default connections for charging phase
    if charging_mode:
        # Charging: From compressor to storage via heat exchangers
        c1 = Connection(cc, 'out1', cp, 'in1', label='c1') 
        c2 = Connection(cp, 'out1', hhx, 'in1', label='c2')
        c3 = Connection(hhx, 'out1', rg, 'in1', label='c3')
        c4 = Connection(rg, 'out1', hxa, 'in1', label='c4')
        c5 = Connection(hxa, 'out1', tb, 'in1', label='c5')
        c6 = Connection(tb, 'out1', chx, 'in2', label='c6')
        c7 = Connection(chx, 'out2', hxb, 'in1', label='c7')
        c8 = Connection(hxb, 'out1', rg, 'in2', label='c8')
        c9 = Connection(rg, 'out2', cc, 'in1', label='c9')
        
        # Storage connections for charging phase
        c11 = Connection(cssoc, 'out1', chx, 'in1', label='c11')  # Cooling in charging
        c12 = Connection(chx, 'out1', cssic, 'in1', label='c12')
        c13 = Connection(hssoc, 'out1', hhx, 'in2', label='c13')  # Heat into storage
        c14 = Connection(hhx, 'out2', hssic, 'in1', label='c14')

        # Add connections to network
        network.add_conns(c1, c2, c3, c4, c5, c6, c7, c8, c9, c11, c12, c13, c14)
        
        # Set parameter        
        hxa.set_attr(pr=0.98)
        hxb.set_attr(pr=0.98)        
        rg.set_attr(pr1=1, pr2=1, ttd_u=5) # ttd_u=30 , Q=-8e6
        hhx.set_attr(pr1=1, pr2=1, ttd_u=10)
        cp.set_attr(eta_s=0.9) #, P=5e6
        chx.set_attr(pr1=1, pr2=1, ttd_u=5)  #ttd_l = out1-in2, ttd_u = in1 - out2
        tb.set_attr(eta_s=0.85)

        # set parameter connections
        # c1.set_attr(m=10, T=250, fluid={'Nitrogen': 1})
        c2.set_attr(m=10, p=105)
        # c3.set_attr(T=200)
        # c4.set_attr(T=temp+10)
        c5.set_attr(T=temp)
        # c6.set_attr(T=-75)
        c7.set_attr(fluid={'Nitrogen': 1}) # T=17
        c8.set_attr(T=temp)
        
        # reservoir cold und hot
        c11.set_attr(T=temp, x=0)
        c12.set_attr(m=10, fluid={'water': 1})# c12 T=20
        c13.set_attr(p=30, T=200)
        c14.set_attr(m=10, T=400, fluid={'air': 1}) # kudu ati2 jangan sampai jdnya COP<1, pasin sama ttd_u di hhx
        
        network.set_attr(iterinfo=False)
        network.solve(mode='design')
        network.print_results()
        
    else:
        # Discharging: From compressor to storage via heat exchangers
        d1 = Connection(cc, 'out1', hxb, 'in1', label='d1')
        # d2 = Connection(rg, 'out1', hxb, 'in1', label='d2')
        d3 = Connection(hxb, 'out1', chx, 'in1', label='d3')
        d4 = Connection(chx, 'out1', cp, 'in1', label='d4')
        d5 = Connection(cp, 'out1', hhx, 'in2', label='d5')
        # d6 = Connection(hxa, 'out1', rg, 'in2', label='d6')
        # d7 = Connection(rg, 'out2', hhx, 'in2', label='d7')
        d8 = Connection(hhx, 'out2', tb, 'in1', label='d8')
        d9 = Connection(tb, 'out1', cc, 'in1', label='d9')

        # Storage connections for charging phase
        d11 = Connection(cssoc, 'out1', chx, 'in2', label='d11')  # Cooling in charging
        d12 = Connection(chx, 'out2', cssic, 'in1', label='d12')
        d13 = Connection(hssod, 'out1', hhx, 'in1', label='d13')  # Heat into storage
        d14 = Connection(hhx, 'out1', hssid, 'in1', label='d14')

        # Add reversed connections to network
        network.add_conns(d1, d3, d4, d5, d8, d9, d11, d12, d13, d14)
        
        generator = Bus("generator")
        generator.add_comps(
            {"comp": tb, "char": 0.98, "base": "component"},
            {"comp": cp, "char": 0.98, "base": "bus"},
        )
        network.add_busses(generator)
        
        # Set turbine and compressor conditions for discharging phase
        tb.set_attr(eta_s=0.9) # Full efficiency for power generation
        cp.set_attr(eta_s=0.95)  # Very low efficiency (no compression during discharge)
        chx.set_attr(pr1=1, pr2=1)
        # rg.set_attr(pr1=1, pr2=1) # ttd_u=30 , Q=-8e6
        # Set parameter        
        # hxa.set_attr(pr=0.98, Q=-1e5)
        hxb.set_attr(pr=0.98)        
        hhx.set_attr(pr1=1, pr2=1, ttd_u=10)
        
        # set parameter connections
        # d1.set_attr(m=10, T=200)
        d3.set_attr(m=10, T=temp+50)
        d4.set_attr(T=temp)
        d5.set_attr(p=105, fluid={'Nitrogen': 1}) # T=17
        # d5.set_attr(T=250)
        # d6.set_attr(T=25)

        d11.set_attr(T=temp, x=0)
        d12.set_attr(m=5, fluid={'water': 1})# c12 T=20
        d13.set_attr(p=30, T=400) #, T=271
        d14.set_attr(m=10, T=200, fluid={'air': 1}) 
        
        network.solve(mode='design')
        network.print_results()
    return network, rg, hhx, chx, hxa, hxb, cp, tb
    # return  network, generator, rg, hhx, chx, hxa, hxb, tb

br = Network(fluids=['Water', 'Nitrogen', 'Methanol'], p_unit='bar', T_unit='C', h_unit='kJ / kg')
# network, generator, rg, hhx, chx, hxa, hxb, tb  = create_connections(network=br, charging_mode=False, temp=10)
network, rg, hhx, chx, hxa, hxb, cp, tb  = create_connections(network=br, charging_mode=True, temp=10)
