# -------- Tenv -------------
import numpy as np
import matplotlib.pyplot as plt

# Given Data
# T_env = np.array([5, 10, 15, 20, 25])  # Temperature variations
# COP = np.array([2.481411, 2.491777, 2.501325, 2.510001, 2.517745])  # COP values
# eps_char = np.array([55.869444, 52.879090, 49.830769, 46.726790, 43.569679])  # Exergy efficiency

Tenv= data_model1_ihx_tenv["Tenv"].to_numpy()
COP= data_model1_ihx_tenv["COP"].to_numpy()
eps_char= data_model1_ihx_tenv["eps_char"].to_numpy()

# Reference Values (Taking middle value)
T_ref = np.median(Tenv)  
COP_ref = np.median(COP) 
eps_char_ref = np.median(eps_char) 

# Relative Change Calculation (%) - First Plot
COP_rel_change = ((COP - COP_ref) / COP_ref) * 100
eps_rel_change = ((eps_char - eps_char_ref) / eps_char_ref) * 100
T_deviation = ((Tenv - T_ref) / T_ref) * 100  # Deviation in %

# First Plot - Sensitivity Analysis
fig1=plt.figure(figsize=(8,5))
plt.plot(T_deviation, COP_rel_change, 'r-', label="COP (%)")
plt.plot(T_deviation, eps_rel_change, 'b-', label="Exergy Efficiency (%)")
plt.xlabel("Abweichung (%)")
plt.ylabel("Relative Änderung (%)")
plt.title("Sensitivitätsanalyse \n COP und Exergieeffizienz w.r.t Tenv")
plt.legend()
plt.grid(True)
plt.show()

# Sensitivity Index Calculation (Delta change) - Second Plot
delta_COP = np.gradient(COP, Tenv) / (COP_ref / T_ref)
delta_eps = np.gradient(eps_char, Tenv) / (eps_char_ref / T_ref)

# Second Plot - Sensitivity Index
fig2=plt.figure(figsize=(8,5))
plt.plot(T_deviation, delta_COP, 'r-', label="Sensitivity Index of COP")
plt.plot(T_deviation, delta_eps, 'b-', label="Sensitivity Index of Exergy Efficiency")
plt.xlabel("Abweichung (%)")
plt.ylabel("Sensitivitätsindex (S)")
plt.title("Sensitivitätsindex für COP und Exergieeffizienz")
plt.legend()
plt.grid(True)
plt.show()

fig1.savefig('senv_Model1_ihx_Tenv.png')
