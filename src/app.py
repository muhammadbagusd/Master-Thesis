# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 19:09:09 2024

@author: bagus
"""

# ------------ HP Side ---------------
from tespy.components import (Compressor, Condenser ,SimpleHeatExchanger, HeatExchanger, 
                              Pump, Turbine, Valve, CycleCloser, Source, Sink)
from tespy.connections import Connection,  Bus
from tespy.networks import Network

HP = Network(fluids=['Water', 'NH3'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

# Heat Pump Cycle Components (Charging)
hp_compressor = Compressor('HP Compressor')
hp_condenser = Condenser('HP Condenser')  # Transfers heat to hot storage
hp_valve = Valve('HP Expansion Valve')
hp_evaporator = SimpleHeatExchanger('HP Evaporator')
hp_closer = CycleCloser('HP Cycle Closer')  # Closes the heat pump loop

# Sources and Sinks
hp_ambient_source = Source('hp Ambient Source')
hp_ambient_sink = Sink('hp Ambient Sink')

# Sources and Sinks
hp_ambient_source_ev = Source('hp Ambient Source ev')
hp_ambient_sink_ev = Sink('hp Ambient Sink ev')

# Heat Pump Cycle Connections (Closed Loop with CycleCloser)
hp_c1 = Connection(hp_closer, 'out1', hp_evaporator, 'in1')
hp_c2 = Connection(hp_evaporator, 'out1', hp_compressor, 'in1')
hp_c3 = Connection(hp_compressor, 'out1', hp_condenser, 'in1')
hp_c4 = Connection(hp_condenser, 'out1', hp_valve, 'in1')
hp_c5 = Connection(hp_valve, 'out1', hp_closer, 'in1')

HP.add_conns(hp_c1, hp_c2, hp_c3, hp_c4, hp_c5)

# set Parameter
hp_compressor.set_attr(eta_s=0.98)
hp_condenser.set_attr(pr2=0.99)
hp_evaporator.set_attr(pr=0.98)
hp_valve.set_attr(pr=0.9)

from CoolProp.CoolProp import PropsSI as PSI
p_cond = PSI("P", "Q", 1, "T", 273.15 + 95, 'NH3') / 1e5
h_sat = PSI("H", "Q", 0, "T", 273.15 + 20, 'NH3') / 1e3
h_sat_liq = PSI("H", "Q", 1, "T", 273.15 + 80, 'NH3') / 1e3
hp_c3.set_attr(m=10, T=170, p=92, fluid={'NH3': 1})

# ---------- storage -------------
# Hot and Cold Storage Interfaces (Simplified)
sto_c5 = Connection(hp_ambient_source, "out1", hp_condenser, "in2")
sto_c6 = Connection(hp_condenser, "out2", hp_ambient_sink, "in1")

HP.add_conns(sto_c5, sto_c6)

# set parameter storage
sto_c5.set_attr(m=10, T=30, p=2, fluid={"water": 1})

# ---------- Rankine cycle -------------
RC = Network(fluids=['Water', 'R134a'], p_unit='bar', T_unit='C', h_unit='kJ / kg')

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

# Rankine Cycle Connections (Closed Loop with CycleCloser)
rc_c1 = Connection(rc_closer, 'out1', rc_turbine, 'in1')
rc_c2 = Connection(rc_turbine, 'out1', rc_condenser, 'in1')
rc_c3 = Connection(rc_condenser, 'out1', rc_pump, 'in1')
rc_c4 = Connection(rc_pump, 'out1', rc_steamGen, 'in2')
rc_c5 = Connection(rc_steamGen, 'out2', rc_closer, 'in1')

RC.add_conns(rc_c1, rc_c2, rc_c3, rc_c4, rc_c5)

# Connections to the ambient environment (source and sink)
rc_ambient_c11 = Connection(rc_ambient_source_1, 'out1', rc_condenser, 'in2')
rc_ambient_c12 = Connection(rc_condenser, 'out2', rc_ambient_sink_1, 'in1')

RC.add_conns(rc_ambient_c11, rc_ambient_c12)

# Connections to the ambient environment (source and sink)
rc_ambient_c21 = Connection(rc_ambient_source_2, 'out1', rc_steamGen, 'in1')
rc_ambient_c22 = Connection(rc_steamGen, 'out1', rc_ambient_sink_2, 'in1')

RC.add_conns(rc_ambient_c21, rc_ambient_c22)

# set parameter RC
rc_condenser.set_attr(pr1=1, pr2=0.98)
rc_steamGen.set_attr(pr1=0.98,pr2=0.98)
rc_turbine.set_attr(eta_s=0.9)
rc_pump.set_attr(eta_s=0.75, P=1e4)

rc_ambient_c11.set_attr(m=10, T=50, p=2, fluid={'water': 1})
rc_ambient_c21.set_attr(m=10, p=2, fluid={'water': 1})
rc_c1.set_attr(T=500, p=110, m=10, fluid={'water': 1})

# ---------- Generator -------------
generator = Bus("generator")
generator.add_comps(
    {"comp": rc_turbine, "char": 0.98, "base": "component"},
    {"comp": rc_pump, "char": 0.98, "base": "bus"},
)
RC.add_busses(generator)

import numpy as np
import pandas as pd

# create a list named data
power = [0, 0, 0, 0, 0, 0, 5e5, 5e5, 5e5, 1e5, 1e5, 1e5, 1e5, 4e5, 4e5, 4e5, 4e5, 4e5, 0, 0, 0, 0, 0, 0]

# create Pandas array using data
array1 = pd.DataFrame(power, columns=['Power'])
i=0
for watt in array1['Power']:
    if watt == 0:
        array1.loc[i,1] =  0
        array1.loc[i,2] =  0
        # array1.loc[i,3] =  0
    else:
        hp_compressor.set_attr(P=watt)
        HP.solve(mode='design')
        array1.loc[i,1] =  hp_condenser.Q.val
        array1.loc[i,2] =  10*sto_c6.h.val
        # rc_ambient_c21.set_attr(h=sto_c6.h.val)
        # RC.solve(mode='design')
        # array1.loc[i,3] = -1*generator.P.val
    i=i+1
for j in range(len(array1)):
    if j < 18:
        array1.loc[j,3] = 0
        array1.loc[j,4] = 0
    else:
        array1.loc[j,3] = array1[2].sum()/(6*10)
        rc_ambient_c21.set_attr(h=array1.loc[j,3])
        RC.solve(mode='design')
        array1.loc[j,4] = -1*generator.P.val
        
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(30, 10)) 
ax.plot(array1.index, array1['Power'], color="green")
ax.plot(array1.index, array1[4], color="blue")
ax.fill_between(
    array1.index, array1['Power'], 
    interpolate=True, color="green", alpha=0.25, 
    label="Positive"
)
ax.fill_between(
    array1.index, array1[4], 
    interpolate=True, color="blue", alpha=0.25, 
    label="Positive"
)
ax.set_xlabel('Hours')
ax.set_ylabel('Power in W')
ax.set_xticks(np.arange(0, 24, 1.0))
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.set_title('Test Charging and Discharging Power')
plt.grid(True, which='both', axis='both')
plt.show()
plt.savefig('test.png')
