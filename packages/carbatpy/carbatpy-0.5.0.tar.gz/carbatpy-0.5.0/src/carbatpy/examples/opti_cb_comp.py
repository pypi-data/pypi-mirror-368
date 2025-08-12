# -*- coding: utf-8 -*-
"""
Example for Optimization of a Carnot battery, with a heat pump (heat_pump_comp) 
for charging and an ORC for discharging using scipy.optimize

Composition and high pressure (condenser) of the working fluid, and the low
temperature of the double tank cold storage are optimization variables for the heat pump. All
other parameters are fixed in a yaml file (io-cycle-data.yaml). For the ORC, the same
composition is used and only the two working fluid pressure levels are optimized.

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
STORE_FILENAME = r"C:\Users\atakan\sciebo\results\\" + current_date + "cb_opt_result.csv"
POWER_C = 2000. # compressr power of heat pump

dir_names_both = {"hp": cb.CB_DEFAULTS["General"]["CB_DATA"]+"\\io-cycle-data.yaml",
                  "orc": cb.CB_DEFAULTS["General"]["CB_DATA"]+"\\io-orc-data.yaml"}

# optimization variables, must be present in the file above
conf_hp = {"cold_storage": {"temp_low": 274.},
          "working_fluid": {"p_high": 1.49e6,
                            "p_low": 1.6e5,
                            'fractions': [.74, .0, 0.26,  0.0000],
                            }
          }
conf_orc = {"working_fluid": {"p_high": 6.49e5,
                            "p_low": 2.6e5,
                            }
            }

# bounds of the optimization variables
bounds_hp = {"cold_storage": {"temp_low": [265, 277]},
            "working_fluid":
            {"p_high": [13.e5, 01.8e6],
             "p_low":[1e5, 1.9e5],
             'fractions': [[0.6, .85], [0.0, .07], [0.1, 0.3], [0, 0.05]]},
            }
bounds_orc = {"working_fluid":
            {"p_high": [5e5, 0.82e6],
             "p_low":[3.10e5, 3.9e5],},
            }

configs_m ={"hp" : conf_hp,
          "orc": conf_orc}
bounds_m = {"hp" : bounds_hp,
            "orc" : bounds_orc}

# WICHTIG: Der ausführbare Code muss in diesem Block stehen!
if __name__ == "__main__":
    if OPTI:
        # for optimization:
        print("Carnot battery optimization is running. It may take a while!")
        opt_res, paths = cb.opti_cycle_comp_helpers.optimize_cb(
            dir_names_both, POWER_C, configs_m, bounds_m, optimize_global=HOW_OPT)
        print(opt_res)
        res_combi = np.column_stack([opt_res.population, opt_res.population_energies])
        np.savetxt(STORE_FILENAME.replace('.csv', '_raw.csv'), res_combi, delimiter=",")
        # if HOW_OPT == "dif_evol":  # or: "dif_evol", "bas_hop"
            # colnames = ["T_cold", "p_h", "propane",
            #             "butane", "pentane"]  # for this input file
            # Prüfe vorsichtshalber auf die richtige Länge:
            # assert len(colnames) == opt_res.population.shape[1]
            # df = pd.DataFrame(opt_res.population)
            # df["RTE"] = opt_res.population_energies
            # if STORE_FILENAME is not None:
            #     df.to_csv(STORE_FILENAME)