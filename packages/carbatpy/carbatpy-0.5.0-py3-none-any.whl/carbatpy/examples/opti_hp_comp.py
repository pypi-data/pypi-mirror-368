# -*- coding: utf-8 -*-
"""
Example for Optimization of a heat pump (heat_pump_comp) using scipy.optimize

Composition and high pressure (condenser) of the working fluid, and the low
temperature of the double tank cold storage are optimization variables. All
other parameters are fixed in a yaml file (io-cycle-data.yaml).

Created on Mon Aug  4 13:12:24 2025

@author: atakan
Universität Duisburg-Essen, Germany

In the framework of the Priority Programme: "Carnot Batteries: Inverse Design from
Markets to Molecules" (SPP 2403)
https://www.uni-due.de/spp2403/
https://git.uni-due.de/spp-2403/residuals_weather_storage

"""


import numpy as np
import pandas as pd
import carbatpy as cb
import datetime

# Konfiguration und Konstanten (diese können außerhalb des main-Blocks stehen)
current_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-")
OPTI = True
HOW_OPT = "dif_evol"  # "local" # 
STORE_FILENAME = r"C:\Users\atakan\sciebo\results\\" + current_date + "hp_opt_result.csv"

POWER_C = 2000. # compressr power of heat pump

dir_name_out = cb.CB_DEFAULTS["General"]["CB_DATA"]+"\\io-cycle-data.yaml"

# optimization variables, must be present in the file above
conf_m = {"cold_storage": {"temp_low": 274.},
          "working_fluid": {"p_high": 1.49e6,
                            'fractions': [.74, .0, 0.26,  0.0000]}}
# bounds of the optimization variables
bounds_m = {"cold_storage": {"temp_low": [265, 277]},
            "working_fluid":
            {"p_high": [5e5, 01.8e6],
             'fractions': [[0.0, .85], [0.0, .005], [0, 0.5], [0, 0.5]]},

            }

# Run heat pump without optimization, with the configuration conf_m:
if __name__ == "__main__":
    cop_m, ou_m, wa_m, fi_m, ax_m = cb.hp_comp.heat_pump(
        dir_name_out, POWER_C, config=conf_m, verbose=True, plotting=True)
    if any(ns.value != 0 for ns in wa_m.values()):
        print(f"Check Warnings, at least one deviates from 0!\n {wa_m}")
    
    
    if OPTI:
        # for optimization:
    
        opt_res, paths = cb.opti_cycle_comp_helpers.optimize_wf_heat_pump(
            dir_name_out, POWER_C, conf_m, bounds_m, optimize_global=HOW_OPT)
        print(opt_res)
        res_combi = np.column_stack([opt_res.population, opt_res.population_energies])
        np.savetxt(STORE_FILENAME.replace('.csv', '_raw.csv'), res_combi, delimiter=",")
        
    
        if HOW_OPT == "dif_evol":  # or: "dif_evol", "bas_hop"
    
            colnames = ["T_cold", "p_h", "propane",
                        "butane", "pentane"]  # for this input file
            # Prüfe vorsichtshalber auf die richtige Länge:
            assert len(colnames) == opt_res.population.shape[1]
    
            df = pd.DataFrame(opt_res.population, columns=colnames)
            df["cop-weighted"] = opt_res.population_energies
    
            p_l = []
            c6 = []
            p_ratio = []
            cops = []
            for o_val in opt_res.population:
                conf_o = cb.opti_cycle_comp_helpers.insert_optim_data(
                    conf_m, o_val, paths)
                # conf_o = {"working_fluid": {"p_high": o_val[0],  'fractions':  [
                #     *o_val[1:], 1 - np.sum(o_val[1:])]}}
                cop_o, ou_o, wa_o, fi_o, ax_o = cb.hp_comp.heat_pump(
                    dir_name_out, POWER_C, config=conf_o, verbose=True, plotting=True)
                p_l_opt = ou_o['start']['p_low']
                p_h_opt = conf_o["working_fluid"]["p_high"]
                p_l.append(p_l_opt)
                c6.append(1-np.sum(o_val[1:]))
                p_ratio.append(p_h_opt / p_l_opt)
                cops.append(cop_o)
            df["hexane"] = c6  # name for this input file
            df["p_low"] = p_l
            df["p_ratio"] = p_ratio
            df['cop'] = cops
            if STORE_FILENAME is not None:
                df.to_csv(
                    STORE_FILENAME,  # should be '.csv'
                    index=False)
        else:
            o_val = opt_res.x
            conf_o = cb.opti_cycle_comp_helpers.insert_optim_data(
                conf_m, o_val, paths)
            cop_o, ou_o, wa_o, fi_o, ax_o = cb.hp_comp.heat_pump(
                dir_name_out, POWER_C, config=conf_o, verbose=True, plotting=True)
            print(f"COP-Optimized by {HOW_OPT}: {cop_o:.2f}")
