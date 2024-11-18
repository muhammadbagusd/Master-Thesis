from tespy.components import Compressor, Condenser, SimpleHeatExchanger, HeatExchanger, Pump, Turbine, CycleCloser, Source, Sink
from tespy.connections import Connection
from tespy.networks import Network

# Create Brayton Cycle Network
br = Network(fluids=['Water', 'Nitrogen', 'Methanol'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# Define Components
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
def create_connections(charging_mode=True):
    # Set default connections for charging phase
    if charging_mode:
        # Charging: From compressor to storage via heat exchangers
        c1 = Connection(cc, 'out1', cp, 'in1', label='1') 
        c2 = Connection(cp, 'out1', hhx, 'in1', label='2')
        c3 = Connection(hhx, 'out1', rg, 'in1', label='3')
        c4 = Connection(rg, 'out1', hxa, 'in1', label='4')
        c5 = Connection(hxa, 'out1', tb, 'in1', label='5')
        c6 = Connection(tb, 'out1', chx, 'in1', label='6')
        c7 = Connection(chx, 'out1', hxb, 'in1', label='7')
        c8 = Connection(hxb, 'out1', rg, 'in2', label='8')
        c9 = Connection(rg, 'out2', cc, 'in1', label='9')
        
        # Storage connections for charging phase
        c11 = Connection(cssoc, 'out1', chx, 'in2', label='11')  # Cooling in charging
        c12 = Connection(chx, 'out2', cssic, 'in1', label='12')
        c13 = Connection(hssoc, 'out1', hhx, 'in2', label='13')  # Heat into storage
        c14 = Connection(hhx, 'out2', hssic, 'in1', label='14')

        # Add connections to network
        br.add_conns(c1, c2, c3, c4, c5, c6, c7, c8, c9, c11, c12, c13, c14)
        
        # Set parameter
        cp.set_attr(eta_s=0.98) #, P=5e6
        chx.set_attr(pr1=1, pr2=1, ttd_l=50)
        tb.set_attr(eta_s=0.01)

        # set parameter connections
        c7.set_attr(m=19, fluid={'Nitrogen': 1}) # T=17
        # br_c2.set_attr(h=920)
        c6.set_attr(p=25)
        # br_c3.set_attr(T=287)
        # br_c7.set_attr(h=303)
        c5.set_attr(p=105)
        c11.set_attr(m=10, T=10, p=25, fluid={'Water': 1}) # c12 T=20
        c13.set_attr(x=0)
        c14.set_attr(m=10, p=10, fluid={'Methanol': 1})
    else:
        # Discharging: From compressor to storage via heat exchangers
        c1 = Connection(cc, 'out1', cp, 'in1', label='1') 
        c2 = Connection(cp, 'out1', rg, 'in2', label='2')
        c3 = Connection(rg, 'out2', hxb, 'in1', label='3')
        c4 = Connection(hxb, 'out1', chx, 'in1', label='4')
        c5 = Connection(chx, 'out1', tb, 'in1', label='5')
        c6 = Connection(tb, 'out1', hxa, 'in1', label='6')
        c7 = Connection(hxa, 'out1', rg, 'in1', label='7')
        c8 = Connection(rg, 'out1', hhx, 'in1', label='8')
        c9 = Connection(hhx, 'out1', cc, 'in1', label='9')

        # Storage connections for charging phase
        c11 = Connection(cssoc, 'out1', chx, 'in2', label='11')  # Cooling in charging
        c12 = Connection(chx, 'out2', cssic, 'in1', label='12')
        c13 = Connection(hssod, 'out1', hhx, 'in2', label='13')  # Heat into storage
        c14 = Connection(hhx, 'out2', hssid, 'in1', label='14')

        # Add reversed connections to network
        br.add_conns(c1, c2, c3, c4, c5, c6, c7, c8, c9, c11, c12, c13, c14)
        
        generator = Bus("generator")
        generator.add_comps(
            {"comp": tb, "char": 0.98, "base": "component"},
            {"comp": cp, "char": 0.98, "base": "bus"},
        )
        br.add_busses(generator)
        
        # Set turbine and compressor conditions for discharging phase
        tb.set_attr(eta_s=1)  # Full efficiency for power generation
        cp.set_attr(P=7e6)  # Very low efficiency (no compression during discharge)
        chx.set_attr(pr1=1, pr2=1, Q=-1e3)
        
        # set parameter connections
        c4.set_attr(m=19, fluid={'Nitrogen': 1}) # T=17
        c6.set_attr(p=25)
        c5.set_attr(p=105)
        c11.set_attr(m=10, T=10, p=25, fluid={'Water': 1}) # c12 T=20
        c13.set_attr(x=0, T=213) #, T=271
        c14.set_attr(m=10, fluid={'Methanol': 1})

# Set parameter        
hxa.set_attr(pr=0.98, Q=-1e3)
hxb.set_attr(pr=0.98, Q=-1e3)        
rg.set_attr(pr1=1, pr2=1, Q=-8e6) # ttd_u=30 , Q=-8e6
hhx.set_attr(pr1=1, pr2=0.98, ttd_l=150)

# Choose whether to run charging or discharging
charging_mode = False  # Set to False for discharging phase

# Create appropriate connections
create_connections(charging_mode=charging_mode)


# Solve the network
br.solve(mode='design')
br.print_results()
# {round(abs(hhx.Q.val) / cp.P.val, 4)}
# print(COP)
