from CoolProp.CoolProp import PropsSI as PSI
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def qt_diagram_multiple(df, component_names, hot_in, hot_out, cold_in, cold_out, delta_t_min, system, case, 
                        show=False, path=None, step_number=200, tol=1e-2):
    """
    Generate a QT diagram for multiple heat exchangers in a thermal system.

    Args:
        df (pd.DataFrame): DataFrame containing thermodynamic properties.
        component_names (list): List of component names for labeling.
        hot_in (list): List of indices of hot inlets in the DataFrame.
        hot_out (list): List of indices of hot outlets.
        cold_in (list): List of indices of cold inlets.
        cold_out (list): List of indices of cold outlets.
        delta_t_min (float): Minimum allowable temperature difference.
        system (str): Name of the thermal system.
        case (str): Identifier for the simulation case.
        show (bool, optional): Whether to display the plot. Default is False.
        path (str, optional): Filepath to save the plot. Default is None.
        step_number (int, optional): Number of interpolation steps. Default is 200.
        tol (float, optional): Tolerance for temperature difference warnings. Default is 1e-2.

    Returns:
        list: A list containing min and max temperature differences for each heat exchanger.
    """

    mpl.rcParams['font.size'] = 16
    plt.figure(figsize=(14, 7))

    colors = ['red', 'blue', 'green']  # Assign different colors for each HX
    linestyles = ['-', '--', '-.']  # Different line styles for hot/cold sides

    results = []

    for i, component in enumerate(component_names):
        fluid_hot = 'NH3'
        fluid_cold = 'water'

        T_hot_out = df.loc[hot_out[i], 'T']
        T_cold_in = df.loc[cold_in[i], 'T']
        h_hot_in = df.loc[hot_in[i], 'h']
        h_hot_out = df.loc[hot_out[i], 'h']
        h_cold_in = df.loc[cold_in[i], 'h']
        h_cold_out = df.loc[cold_out[i], 'h']
        p_hot_in = df.loc[hot_in[i], 'p']
        p_hot_out = df.loc[hot_out[i], 'p']
        p_cold_in = df.loc[cold_in[i], 'p']
        p_cold_out = df.loc[cold_out[i], 'p']
        m = df.loc[cold_in[i], 'm']

        T_cold = [T_cold_in]
        T_hot = [T_hot_out]
        H_plot = [0]

        for j in np.linspace(1, step_number, step_number):
            h_hot = h_hot_out + (h_hot_in - h_hot_out) / step_number * j
            p_hot = p_hot_out + (p_hot_in - p_hot_out) / step_number * j
            T_hot.append(PSI('T', 'H', h_hot * 1e3, 'P', p_hot * 1e5, fluid_hot) - 273.15)
            h_cold = h_cold_in + (h_cold_out - h_cold_in) / step_number * j
            p_cold = p_cold_in - (p_cold_in - p_cold_out) / step_number * j
            T_cold.append(PSI('T', 'H', h_cold * 1e3, 'P', p_cold * 1e5, fluid_cold) - 273.15)
            H_plot.append((h_cold - h_cold_in) * m)

        difference = [x - y for x, y in zip(T_hot, T_cold)]
        results.append([min(difference), max(difference)])

        plt.plot(H_plot, T_hot, color=colors[i], linestyle=linestyles[0], label=f"{component} - Hot side")
        plt.plot(H_plot, T_cold, color=colors[i], linestyle=linestyles[1], label=f"{component} - Cold side")

        if min(difference) < delta_t_min and abs(min(difference) - delta_t_min) > tol:
            print(f"Warning: Min. temperature difference in {component} is {round(min(difference), 2)}K, lower than {delta_t_min}K.")

    plt.legend()
    plt.xlabel('Q [kW]')
    plt.ylabel('T [°C]')
    plt.title(f"QT diagrams of the heat exchangers in {system} \nfor the case: {case}")
    plt.grid(True)

    if path is not None:
        plt.savefig(path + 'all_hx_ihx.png')
    if show:
        plt.show()

    return results

# Example Usage:
qt_diagram_multiple(data_model1_ihx_tenv.network_char[1].results["Connection"], 
                    ["Heat Exchanger I", "Heat Exchanger II", "Condenser"], 
                    ['4', '5', '6'], ['5', '6', '7'], ['23', '22', '21'], ['24', '23', '22'], 
                    1, "Carnot Battery", "Model I mit IHX", show=True, path='plot/')
