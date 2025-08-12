"""Top-level package for carbatpy."""

__author__ = """Burak Atakan"""
__email__ = 'burak.atakan@uni-due.de'


# __all__ =[]
import os
import sys
# read version from installed package
from importlib.metadata import version

import pandas as pd

try:
    __version__ = version('carbatpy')
except:
    __version__ = "unknown"

pd.set_option("mode.copy_on_write", True)

sys.path.insert(0,os.path.abspath('../src'))
sys.path.insert(0,os.path.abspath('..'))


try:
    from cb_config import _T_SURROUNDING, _RESULTS_DIR, \
                            _P_SURROUNDING,_CARBATPY_BASE_DIR, TREND, CB_DEFAULTS
   
except:
    from .cb_config import _T_SURROUNDING, _RESULTS_DIR, \
                            _P_SURROUNDING,_CARBATPY_BASE_DIR, TREND, CB_DEFAULTS
 
import carbatpy.models as models
import carbatpy.utils as utils
import carbatpy.helpers as helpers



from carbatpy.utils import exergy_loss as exlo
from carbatpy.helpers import file_copy, ser_dict, opti_cycle_comp_helpers

import carbatpy.models.cb_fluids.fluid_props as fprop
from carbatpy.models.cb_fluids.fluid_props import Fluid, FluidModel, init_fluid
#from carbatpy.models.components import compressor_simple, throttle_simple
from carbatpy.models.components import heat_exchanger_thermo_v2 as hex_th
from carbatpy.models.components.single_flow import FlowDeviceOld
from carbatpy.models.components import comp
from carbatpy.models.components.class_he import  heat_exchanger
from carbatpy.models.components.surrogates import  Surrogate
import carbatpy.models.components.heat_transfer 


from carbatpy.models.coupled import heat_pump_comp as hp_comp
from carbatpy.models.coupled import orc_comp, cb_comp
from carbatpy.models.coupled import heat_pump_simple as hp_simple
from carbatpy.models.coupled import orc_simple_v2 as orc_simple
from carbatpy.models.coupled import read_cycle_structure
from carbatpy.utils import curve_min_distance_finder, property_eval_mixture, optimize

