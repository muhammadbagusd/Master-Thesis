#%% --------------- RC with Steam Generator ---------
# ---- RC with pump and ventil ---------
from tespy.components import (Compressor, Condenser ,SimpleHeatExchanger, 
                              HeatExchanger, Pump, Turbine, Valve, CycleCloser, 
                              Source, Sink, Drum)
from tespy.connections import Connection, Bus
from tespy.networks import Network
# ---------- Rankine cycle -------------
RC = Network(fluids=['Ethanol', 'R134a'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# Rankine Cycle Components (Discharging)
rc_pump = Pump('RC Pump')
rc_steamGen = HeatExchanger('RC steam generator')  # Receives heat from hot storage
rc_turbine = Turbine('RC Turbine')
rc_condenser = Condenser('RC Condenser')
rc_closer = CycleCloser('RC Cycle Closer')  # Closes the Rankine cycle loop
# steam generator
rc_preheater = HeatExchanger("preheater")
rc_evaporator = HeatExchanger("evaporator")
rc_drum = Drum("drum")

# Sources and Sinks
rc_ambient_source_1 = Source('rc Ambient Source 1')
rc_ambient_sink_1 = Sink('rc Ambient Sink 1')

# Sources and Sinks
rc_ambient_source_2 = Source('rc Ambient Source 2')
rc_ambient_sink_2 = Sink('rc Ambient Sink 2')

# Pump Storage
rc_pump_sto = Pump('RC Pump Storage')
rc_ventil_sto = Valve('RC Valve Storage')

# Rankine Cycle Connections (Closed Loop with CycleCloser)
rc_c1 = Connection(rc_closer, 'out1', rc_turbine, 'in1', label='RC1')
rc_c2 = Connection(rc_turbine, 'out1', rc_condenser, 'in1', label='RC2')
rc_c3 = Connection(rc_condenser, 'out1', rc_pump, 'in1', label='RC3')
rc_c4 = Connection(rc_pump, 'out1', rc_preheater, 'in1', label='RC4')
rc_c5 = Connection(rc_preheater, 'out1', rc_drum, 'in1', label='RC5')
rc_c6 = Connection(rc_drum, 'out1', rc_evaporator, 'in1', label='RC6')
rc_c7 = Connection(rc_evaporator, 'out1', rc_drum, 'in2', label='RC7')
rc_c8 = Connection(rc_drum, 'out2', rc_closer, 'in1', label='RC8')

RC.add_conns(rc_c1, rc_c2, rc_c3, rc_c4, rc_c5, rc_c6, rc_c7, rc_c8)

# Connections to the ambient environment (source and sink)
rc_ambient_c11 = Connection(rc_ambient_source_1, 'out1', rc_condenser, 'in2')
rc_ambient_c12 = Connection(rc_condenser, 'out2', rc_ambient_sink_1, 'in1')

RC.add_conns(rc_ambient_c11, rc_ambient_c12)

# Connections to the steam generator (source and sink)
rc_ambient_c21 = Connection(rc_ambient_source_2, 'out1', rc_evaporator, 'in2')
rc_ambient_c22 = Connection(rc_evaporator, 'out2', rc_preheater, 'in2')
rc_ambient_c23 = Connection(rc_preheater, 'out2', rc_ambient_sink_2, 'in1')

RC.add_conns(rc_ambient_c21, rc_ambient_c22, rc_ambient_c23)

# Connection storage
# rc_storage_c1 =  Connection(rc_pump_sto, 'out1', rc_steamGen, 'in2')
# rc_storage_c2 = Connection(rc_steamGen, 'out2', rc_ventil_sto, 'in1')

# RC.add_conns(rc_storage_c1, rc_storage_c2)

# set parameter RC
rc_condenser.set_attr(pr1=0.98, pr2=0.98)
# rc_steamGen.set_attr(pr1=0.98,pr2=0.98)
rc_turbine.set_attr(eta_s=0.8)
rc_pump.set_attr(eta_s=0.75)
rc_preheater.set_attr(pr1=0.98, pr2=0.98)
rc_evaporator.set_attr(pr1=0.98, pr2=0.98)

rc_pump_sto.set_attr(eta_s=0.75, P=1e4)

rc_ambient_c11.set_attr(m=10, T=10, p=1, fluid={'water': 1})
rc_ambient_c21.set_attr(m=sto_c5.m.val, T=sto_c6.T.val, p=sto_c6.p.val, fluid={'water': 1})
rc_c1.set_attr(m=30, T=400, p=20, fluid={'Ethanol': 1})
rc_c2.set_attr(p=1)
# rc_ambient_c23.set_attr(T=sto_c5.T.val, p=sto_c5.p.val)

# ---------- Generator -------------
generator = Bus("generator")
generator.add_comps(
    {"comp": rc_turbine, "char": 0.98, "base": "component"},
    {"comp": rc_pump, "char": 0.98, "base": "bus"},
    {"comp": rc_pump_sto, "char": 0.98, "base": "bus"},
)
RC.add_busses(generator)

RC.solve(mode='design')
RC.print_results()
