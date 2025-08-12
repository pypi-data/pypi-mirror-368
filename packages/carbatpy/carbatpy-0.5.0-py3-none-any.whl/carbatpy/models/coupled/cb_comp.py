# -*- coding: utf-8 -*-
"""
Calculation of a Carnot Battery (PTES) with two energy storages.


Created on Tue Aug  5 12:33:52 2025

@author: atakan
Universität Duisburg-Essen, Germany

In the framework of the Priority Programme: "Carnot Batteries: Inverse Design from
Markets to Molecules" (SPP 2403)
https://www.uni-due.de/spp2403/
https://git.uni-due.de/spp-2403/residuals_weather_storage

"""
import carbatpy as cb


def cb_calc(dir_names, power=1000., **kwargs):
    """
    Runs a Carnot battery model by sequentially simulating a heat pump and an Organic Rankine Cycle (ORC)
    using the provided configuration files or dictionaries.

    The function first executes the heat pump cycle based on the configuration in `dir_names["hp"]`.
    If successful and without warnings, it extracts the relevant thermodynamic conditions and storage states
    to configure and launch the subsequent ORC calculation (using `dir_names["orc"]`).
    Both cycles may accept additional configuration dictionaries (useful for parameter optimization).
    If `plotting` is True, figures for both cycles are generated.

    The overall Carnot battery round-trip efficiency (`rte`) is computed as the product of the heat pump COP
    and the ORC thermal efficiency.

    Parameters
    ----------
    dir_names : dict
        A dictionary with keys "hp" (for heat pump) and "orc" (for ORC), each containing
        either the path to a YAML (or similar) configuration file or a configuration dictionary.
    power : float, optional
        Compressor power for the heat pump [W]. Default is 1000.
    **kwargs :
        Additional keyword arguments. Supported keys:
            config : dict, optional
                Dictionary with additional or overriding configuration for the heat pump (`"hp"`) and/or ORC (`"orc"`)
                in the form {"hp": config_hp_dict, "orc": config_orc_dict}. Useful for optimization or parameter studies.
            verbose : bool, optional
                If True, enables verbose output. Default is False.
            plotting : bool, optional
                If True, generates diagrams for both the heat pump and ORC cycles.

    Returns
    -------
    rte : float
        The round-trip efficiency of the Carnot battery (heat pump COP × ORC thermal efficiency);
        returns -10 if heat pump warnings occur, or -20 if ORC warnings occur.
    results : dict
        A dictionary with two entries:
            "hp"  : [cop_hp, outputs_hp, warnings_hp, fig_hp, ax_hp]
            "orc" : [eta_orc, outputs_orc, warnings_orc, fig_orc, ax_orc]
        Each tuple contains the cycle performance metric, outputs, component warnings, and (optionally) plots.

    Notes
    -----
    This function calls both the heat pump and ORC functions in sequence, using outputs from the heat pump
    (such as working fluid composition and storage temperatures) to configure the ORC run. It is suitable 
    for integrating the full Carnot battery workflow, either for direct calculations, sensitivity studies, 
    or optimization routines.

    If component warnings deviate from zero for either cycle, the function will print diagnostic messages
    (if `verbose` is True) and return a negative code for `rte`.

    Example
    -------
    >>> dir_names = {"hp": "heat_pump_config.yaml", "orc": "orc_config.yaml"}
    >>> rte, results = cb_calc(dir_names, power=1500., config={"hp": hp_opt_config, "orc": orc_opt_config}, plotting=True)
    """
    new_config = kwargs.get(
        "config", {"hp": None, "orc": None})  # for optimizations
    verbose = kwargs.get("verbose", False)
    plotting = kwargs.get("plotting", False)
    results = {}

    cop_h, ou_h, wa_h, fi_h, ax_h = cb.hp_comp.heat_pump(
        dir_names["hp"], config=new_config["hp"], verbose=verbose, plotting=plotting)
    results["hp"] = {"COP" : cop_h,
                     "output": ou_h, 
                     "warnings": wa_h, 
                     "figure": fi_h, 
                     "axes": ax_h}

    if any(ns.value != 0 for ns in wa_h.values()):
        if verbose:
            print(f"Check HP Warnings, at least one deviates from 0!\n {wa_h}")
        return -sum(item.value for item in wa_h.values()), results

    # print(f"COP: {cop_h:.3f}")
    q_h = -ou_h["condenser"]["q_dot"]
    
    # same fluid, same storage temperatures:
    orc_config = cb.utils.io_utils.read_config(dir_names["orc"])
    from_hp_config = {"working_fluid": {"fractions": ou_h["config"]["working_fluid"]["fractions"],
                                        "species": ou_h["config"]["working_fluid"]["species"]},
                      "cold_storage":  {"temp_low": ou_h["config"]["cold_storage"]["temp_low"]},
                      "hot_storage": {"temp_high": ou_h["config"]["hot_storage"]["temp_high"]}}
    for key in from_hp_config:
        if key in orc_config:
            orc_config[key].update(from_hp_config[key])
        else:
            orc_config[key] = from_hp_config[key]
    eta, ou_o, wa_o, fig_o, ax_o = cb.orc_comp.orc(orc_config,
                                                   cop_h,
                                                   q_h,
                                                   config=new_config["orc"],
                                                   plotting=plotting)
    results["orc"] = {"eta_th" : eta, 
                      "output" : ou_o, 
                       "warnings": wa_o, 
                       "figure": fig_o, 
                       "axes": ax_o}
    if any(ns.value != 0 for ns in wa_o.values()):
        if verbose:
            print(f"Check ORC Warnings, at least one deviates from 0!\n {wa_h}")
        return -sum(item.value for item in wa_o.values()), results

    print(f"COP: {cop_h:.3f}, eta: {eta:.3f}, rte: {eta*cop_h:.3f}")
    return eta*cop_h, results


if __name__ == "__main__":
    dir_names_both = {"hp": cb.CB_DEFAULTS["General"]["CB_DATA"]+"\\io-cycle-data.yaml",
                      "orc": cb.CB_DEFAULTS["General"]["CB_DATA"]+"\\io-orc-data.yaml"}
    rte, results_o = cb_calc(dir_names_both, plotting=True)
    print(f"RTE: {rte:.3f}")
