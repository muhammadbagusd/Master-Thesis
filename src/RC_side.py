#%% RC
# ---- RC with pump and ventil ---------
# ---------- Rankine cycle -------------
RC = Network(fluids=['Ethanol', 'R134a'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# Rankine Cycle Components (Discharging)
rc_pump = Pump('RC Pump')
rc_steamGen = HeatExchanger('RC steam generator')  # Receives heat from hot storage
rc_turbine = Turbine('RC Turbine')
rc_condenser = Condenser('RC Condenser')
rc_closer = CycleCloser('RC Cycle Closer')  # Closes the Rankine cycle loop

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
rc_c4 = Connection(rc_pump, 'out1', rc_steamGen, 'in1', label='RC4')
rc_c5 = Connection(rc_steamGen, 'out1', rc_closer, 'in1', label='RC5')

RC.add_conns(rc_c1, rc_c2, rc_c3, rc_c4, rc_c5)

# Connections to the ambient environment (source and sink)
rc_ambient_c11 = Connection(rc_ambient_source_1, 'out1', rc_condenser, 'in2')
rc_ambient_c12 = Connection(rc_condenser, 'out2', rc_ambient_sink_1, 'in1')

RC.add_conns(rc_ambient_c11, rc_ambient_c12)

# Connections to the ambient environment (source and sink)
rc_ambient_c21 = Connection(rc_ambient_source_2, 'out1', rc_pump_sto, 'in1')
rc_ambient_c22 = Connection(rc_ventil_sto, 'out1', rc_ambient_sink_2, 'in1')

RC.add_conns(rc_ambient_c21, rc_ambient_c22)

# Connection storage
rc_storage_c1 =  Connection(rc_pump_sto, 'out1', rc_steamGen, 'in2')
rc_storage_c2 = Connection(rc_steamGen, 'out2', rc_ventil_sto, 'in1')

RC.add_conns(rc_storage_c1, rc_storage_c2)

# set parameter RC
rc_condenser.set_attr(pr1=1, pr2=1)
rc_steamGen.set_attr(pr1=1,pr2=1)
rc_turbine.set_attr(eta_s=0.9)
rc_pump.set_attr(eta_s=0.75, P=1e4)

rc_pump_sto.set_attr(eta_s=0.75, P=1e4)

rc_ambient_c11.set_attr(m=10, T=10, p=2, fluid={'Ethanol': 1})
rc_ambient_c21.set_attr(m=sto_c5.m.val, T=sto_c6.T.val, p=sto_c6.p.val, fluid={'water': 1})
rc_c2.set_attr(T=350, p=5, fluid={'Ethanol': 1})
rc_ambient_c22.set_attr(T=sto_c5.T.val, p=sto_c5.p.val)

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
