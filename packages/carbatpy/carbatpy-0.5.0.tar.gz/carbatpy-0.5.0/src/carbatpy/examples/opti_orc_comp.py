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

OPTI = True
HOW_OPT = "dif_evol"
STORE_FILENAME = None
COP = 3.05
Q_DOT_HIGH = 3000.
WITH_COMPOSITION = False

dir_name_out = cb.CB_DEFAULTS["General"]["CB_DATA"]+"\\io-orc-data.yaml"

# optimization variables, must be present in the file above
if WITH_COMPOSITION:
    conf_m = {"cold_storage": {"temp_low": 254.},
              "working_fluid": {"p_high": .49e6,
                                'fractions': [.74, .0, 0.26,  0.0000]}}
    # bounds of the optimization variables
    bounds_m = {"cold_storage": {"temp_low": [255, 277]},
                "working_fluid":
                {"p_high": [4e5, 0.6e6],
                 'fractions': [[0.0, .85], [0.0, .005], [0, 0.5], [0, 0.5]]},
    
                }
else:
    conf_m = {"cold_storage": {"temp_low": 254.},
              "working_fluid": {"p_high": .58e6,
                                'p_low': 3.5e5}}
    # bounds of the optimization variables
    bounds_m = {"cold_storage": {"temp_low": [250, 277]},
                "working_fluid":
                {"p_high": [4.1e5, 1.1e6],
                 'p_low': [3.0e5, 3.9e5]},
    
                }

# Run heat pump without optimization, with the configuration conf_m:

eta_m, ou_m, wa_m, fi_m, ax_m = cb.orc_comp.orc(
    dir_name_out, COP, Q_DOT_HIGH, config=conf_m, verbose=True, plotting=True)
if any(ns.value != 0 for ns in wa_m.values()):
    print(f"Check Warnings, at least one deviates from 0!\n {wa_m}")

if __name__ == '__main__':
    
    if OPTI:
        # for optimization:
        print('\nOptimization is running ...\n')
    
        opt_res, paths = cb.opti_cycle_comp_helpers.optimize_orc(
            dir_name_out, COP, Q_DOT_HIGH, conf_m, bounds_m, optimize_global=HOW_OPT,
            verbose=True)
        print(opt_res)
    
        if HOW_OPT == "dif_evol":  # or: "dif_evol", "bas_hop"
    
            colnames = ["T_cold", "p_h", "p_l"]  # for this input file
            # Prüfe vorsichtshalber auf die richtige Länge:
            assert len(colnames) == opt_res.population.shape[1]
    
            df = pd.DataFrame(opt_res.population, columns=colnames)
            df["eta-weighted"] = opt_res.population_energies
    
            p_l = []
            c6 = []
            p_ratio = []
            etas = []
            for o_val in opt_res.population:
                conf_o = cb.opti_cycle_comp_helpers.insert_optim_data(
                    conf_m, o_val, paths)
                # conf_o = {"working_fluid": {"p_high": o_val[0],  'fractions':  [
                #     *o_val[1:], 1 - np.sum(o_val[1:])]}}
                eta_o, ou_o, wa_o, fi_o, ax_o = cb.orc_comp.orc(
                    dir_name_out, COP, Q_DOT_HIGH, config=conf_o, verbose=True, plotting=True)
                p_l_opt = ou_o['start']['p_low']
                p_h_opt = conf_o["working_fluid"]["p_high"]
                p_l.append(p_l_opt)
                c6.append(1-np.sum(o_val[1:]))
                p_ratio.append(p_h_opt / p_l_opt)
                etas.append(eta_o)
            #df["hexane"] = c6  # name for this input file
            #df["p_low"] = p_l
            df["p_ratio"] = p_ratio
            df['eta_th'] = eta_o
            if STORE_FILENAME is not None:
                df.to_csv(
                    STORE_FILENAME,  # should be '.csv'
                    index=False)
        else:
            o_val = opt_res.x
            conf_o = cb.opti_cycle_comp_helpers.insert_optim_data(
                conf_m, o_val, paths)
            eta_o, ou_o, wa_o, fi_o, ax_o = cb.orc_comp.orc(
                dir_name_out, COP, Q_DOT_HIGH, config=conf_o, verbose=True, plotting=True)
            print(f"eta_th-Optimized by {HOW_OPT}: {eta_o:.2f}")
