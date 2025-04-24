import matplotlib.pyplot as plt
import pandas as pd
from tespy.networks import Network
from tespy.tools import ExergyAnalysis

def plot_sensitivity_from_df(df, param, filename_prefix):
    """
    Plots charging and discharging performance indicators from results DataFrame.
    """
    # --- Charging Plot: COP & eps_char ---
    fig1, ax1 = plt.subplots()

    ax1.plot(df[param], df["COP"], 'bo-', label="COP", markersize=5)
    ax1.set_xlabel(f"{param} (°C)")
    ax1.set_ylabel("COP", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    ax2 = ax1.twinx()
    ax2.plot(df[param], df["eps_char"], 'ro-', label="Exergy Eff. Charging [%]", markersize=5)
    ax2.set_ylabel("Exergy Eff. Charging [%]", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    plt.title(f"Sensitivity Analysis (Charging) – {param}")
    plt.tight_layout()
    fig1.savefig(f"{filename_prefix}_{param}_charging_model2_ihx.png")
    plt.show()

    # --- Discharging Plot: eta & eps_dis ---
    fig2, ax3 = plt.subplots()

    ax3.plot(df[param], df["eta"], 'go-', label="eta", markersize=5)
    ax3.set_xlabel(f"{param} (°C)")
    ax3.set_ylabel("Thermal Efficiency [%]", color="green")
    ax3.tick_params(axis="y", labelcolor="green")

    ax4 = ax3.twinx()
    ax4.plot(df[param], df["eps_dis"], 'mo-', label="Exergy Eff. Discharging [%]", markersize=5)
    ax4.set_ylabel("Exergy Eff. Discharging [%]", color="magenta")
    ax4.tick_params(axis="y", labelcolor="magenta")

    plt.title(f"Sensitivity Analysis (Discharging) – {param}")
    plt.tight_layout()
    fig2.savefig(f"{filename_prefix}_{param}_discharging_model2_ihx.png")
    plt.show()
