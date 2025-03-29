# --------- Temperature Storage out to HP ----------------
from tespy.tools import ExergyAnalysis
import pandas as pd

Tsto_out = [175, 180, 185, 190]
data_model1_ihx_tstoOut = []
# Iterate over each ambient temperature
for idx, temp in enumerate(Tsto_out):
    # ------------- charging --------------
    nw_char = Network(p_unit='bar', T_unit='C', h_unit='kJ / kg')
    network_char, cd, hx1, hx2, cp, ep_hp, ef_hp, el_hp = create_connections_charg(network=nw_char, charging_mode=True, Tsto_in=75, Tsto_out=temp, Tenv=10)
    COP = abs(cd.Q.val+hx1.Q.val+hx2.Q.val) / cp.P.val
    ean_char = ExergyAnalysis(network=network_char, E_P=[ep_hp], E_F=[ef_hp], E_L=[el_hp])
    ean_char.analyse(pamb=1, Tamb=10)
    eps_char = 100*ean_char.network_data.epsilon
    # ------- Discharging -----------------
    nw_dis = Network(p_unit='bar', T_unit='C', h_unit='kJ / kg')
    network_dis, gen, ph, ev, sh, ef_orc, el_orc = create_connections_discharge(network=nw_dis, charging_mode=False, Tsto_in=75, Tsto_out=temp, Tenv=10)
    eta = 100*(gen.P.val/(ph.Q.val+ev.Q.val+sh.Q.val))
    ean_dis = ExergyAnalysis(network=network_dis, E_P=[gen], E_F=[ef_orc], E_L=[el_orc])
    ean_dis.analyse(pamb=1, Tamb=10)
    eps_dis = 100*ean_dis.network_data.epsilon
    data_model1_ihx_tstoOut.append([idx, temp, COP, eta, eps_char, eps_dis, network_char, network_dis, ean_char, ean_dis])

data_model1_ihx_tstoOut = pd.DataFrame(data_model1_ihx_tstoOut, columns=["Iteration", "Tsto_out", "COP", "eta", "eps_char", "eps_dis", "network_char", "network_dis", "ean_char", "ean_dis"])
