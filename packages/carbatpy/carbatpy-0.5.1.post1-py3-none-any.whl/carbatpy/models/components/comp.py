import numpy as np
import scipy.optimize as opti
import pandas as pd
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from datetime import datetime
import os
import copy
import json
import logging
import carbatpy as cb
from carbatpy.helpers.ser_dict import Serializable, DataAll, DataNode
from carbatpy.utils.io_utils import read_config, read_component
from types import SimpleNamespace

warn = SimpleNamespace(value=0, message="All O.K.")
# Logging-Konfiguration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Component(ABC):
    """Components of thermodynamic cycles.

    All have following attributes
        - config : The basic configuration, incl. the calculation method
        - inputs : all specific inputs for calculations
        - output : all important results of the calculation
        - all_data : detailled data points for plotting and
                     further evaluations
        - warning : a value and a message (0, "All o.k.")
    All have following methods:
        - initialize : set/calculate all important values which do not
                        depend on a specific calculation.
        - calculate : this is the main function
        - plot : plot the changes (T-H_dot) in to a joint diagram.
        - save : save the main results and inputs to a directory

                     """

    def __init__(self, name, config, **kwargs):
        """
        Set the basic configuration of a component.

        Parameters
        ----------
        name : string
            name of the component to be configured, must be the same
            as in the config dictionary or file.
        config : string or dictionary
            if it is a string it must be the filename with a yaml or
            json file with the dictionary information. All needed basic
            parameters or default parameters and calculation type are
            set here. Check the io_utils.py file for typical values.
        **kwargs : dictionary
            any further parameters which may be needed.

        Returns
        -------
        None.

        """
        self.name = name
        self.config = read_config(config)
        self.inputs = read_component(config, name)
        self.species = self.config[name].get('species', {})
        self.model = self.config[name].get('model')
        self.calc_type = self.config[name].get('calc_type')
        m_dot = kwargs.get("kwargs", 1.0)
        self.verbose = kwargs.get('verbose', False)
        # default value, can also be changed with calculate
        self.output = {"m_dot": m_dot}
        self.all_data = None
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

        self.warning = copy.copy(warn)
        self._points = cb.CB_DEFAULTS["Components"]["n_points"]
        self.initialize(**kwargs)

    @abstractmethod
    def initialize(self, **kwargs):
        pass

    @abstractmethod
    def calculate(self, in_states=None, out_states=None, run_param=None, **kwargs):
        pass

    @abstractmethod
    def plot(self, plot_info, **kwargs):
        pass

    def _plot_shift(self, first, second, first_direction):
        h_in = self.output['state_in']['working_fluid'][2]
        h_out = self.output['state_out']['working_fluid'][2]

        first = np.array(first)
        second = np.array(second)
        shift = first.max()
        if first_direction == -1:
            shift = first.min()

        direction = +1
        if h_out < h_in:
            shift = shift - (second.max() - second.min())
            direction = -1
        return shift, direction

    def save_results(self, base_dir):
        output_path = os.path.join(base_dir, f"{self.name}_output.json")
        with open(output_path, 'w') as f:
            json.dump(self.output, f, indent=4)

        if isinstance(self.all_data, np.ndarray):
            data_path = os.path.join(base_dir, f"{self.name}_all_data.npy")
            np.save(data_path, self.all_data)
        elif isinstance(self.all_data, pd.DataFrame):
            data_path = os.path.join(base_dir, f"{self.name}_all_data.csv")
            self.all_data.to_csv(data_path, index=False)

        self.logger.info(f"Results saved for {self.name}")

    def _storage_name(self, fluidnames):
        for name in fluidnames:
            if name != "working_fluid":
                return name


class FlowDevice(Component):
    def initialize(self):
        # self.in_state = self.species['working_fluid']['in']
        # self.out_state = self.species['working_fluid']['out']
        # self.p_in = self.species['working_fluid']['p_in']
        # self.p_out = self.species['working_fluid']['p_out']
        pass

    def plot(self, plot_info=None):
        fl_name = "working_fluid"  # list(self.inputs['states'].keys())[0]
        if not plot_info:
            fig, ax = plt.subplots(1)
            plot_info = cb.CB_DEFAULTS["Components"]["Plot"]
            plot_info.update({"ax": ax, "fig": fig})
            plot_info["label"][0] = self.name

        if plot_info["what"][0] == 2:
            data = np.array([self.output["state_in"][fl_name][plot_info["what"][0]],
                             self.output["state_out"][fl_name][plot_info["what"][0]]]) * \
                self.output["m_dot"]
            data = data - data.min()  # + plot_info["x-shift"][0]
            shift = self._plot_shift(plot_info["x-shift"],
                                     [data.min(), data.max()],
                                     plot_info["direction"])
            data = data - data.min() + shift[0]
            plot_info["ax"].plot(data,
                                 [self.output["state_in"][fl_name][plot_info["what"][1]],
                                  self.output["state_out"][fl_name][plot_info["what"][1]]],
                                 plot_info["col"][0],
                                 label=plot_info["label"][0])
            plot_info["ax"].legend()

            return [data.min(), data.max()], shift[1]
        else:
            self.warning.__dict__.update(
                value=130,  message=f"Pump: plotting only implemented fot T-H_dot [2,0]. You requested{plot_info['what']}")
            print(self.warning)


class FlowMachine(FlowDevice):
    """ FlowMachine means Compressor, Expander, and Pump. """

    def initialize(self):
        super().initialize()
        self.eta_s = self.config.get('eta_s')
        self.dt_superheat = self.config.get('dt_superheat')

    def calculate(self, in_states, out_states, run_param=None, **kwargs):
        """
        Calculates a simple isentropic compressor.

        Results written in self.output

        Parameters
        ----------
        in_states : dictionary
            keys: fluidnmae (str)
            index: state entering, as defined in THERMO_STRING T,p,h,v,s.
        out_states : dictionary
            keys: fluidnmae (str)
            index: output state only the pressure is used out_state[2].
        run_params : dict, optional
            if further parameters must be passed for the calculation.
            - power : power given, mass flow rate calculated
        **kwargs : TYPE
            DESCRIPTION.

        Raises
        ------
        Exception
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # Implementierung der Kompressorberechnung
        if self.verbose:
            self.logger.info(f"Calculating {self.name}")
        fl_name = list(self.inputs['states'].keys())[0]

        fluid_act = self.inputs["act_fluids"][fl_name]
        self.p_out = out_states[fl_name][1]

        # ... Berechnungslogik hier ...
        state_in = fluid_act.set_state(
            [in_states[fl_name][1], in_states[fl_name][2]], "PH")
        if isinstance(state_in, str):
            print(state_in, "function/value needed")
        expander = False
        if fluid_act.properties.pressure > self.p_out:
            expander = True

        if self.calc_type == "const_eta":

            eta_s = self.inputs['parameters']["eta_s"]
            fluid_act.set_state(
                [fluid_act.properties.entropy, self.p_out], "SP")

            diff_enthalpy_s = fluid_act.properties.enthalpy-state_in[2]

            if expander:
                work_specific = diff_enthalpy_s * eta_s
            else:
                work_specific = diff_enthalpy_s / eta_s

            state_out = fluid_act.set_state(
                [state_in[2] + work_specific, self.p_out], "HP")

        else:
            self.warning.__dict__.update(value=100,
                                         messaege=f""""The option{self.calc_type} is not yet implemented for
                                compressors""")
            raise Exception(
                self.warning.message+f' {self.calc_type}')
        match self.inputs['parameters']['fixed']:  # noqa
            case 'power':
                if "power" in run_param.keys():  # along run
                    power = run_param["power"]
                else:  # Default/preset
                    power = self.inputs['parameters']['power']
                m_dot = power / work_specific
            case 'm_dot':
                m_dot = kwargs.get("m_dot", 1.)
                power = m_dot * work_specific
            case _: raise NotImplementedError(f'''FlowMachine:
                                              {self.inputs['parameters']['fixed']} not implemented!''')
        self.inputs["act_fluids"]["working_fluid"] = fluid_act
        #
        self.output.update({"state_in": {fl_name: state_in},
                            "state_out": {fl_name: state_out},
                            "work_specific": work_specific,
                            "power": power,
                            "m_dot": m_dot,
                            "warning": self.warning})
        self.all_data = {fl_name: np.array([state_in, state_out])
                         }


class Throttle(FlowDevice):
    "Simple isenthalpic throttle."

    def calculate(self, in_states, out_states, run_param=None, **kwargs):
        # Implementierung der Drosselberechnung
        if self.verbose:
            self.logger.info(f"Calculating {self.name}")
        # ... Berechnungslogik hier ...
        fl_name = list(self.inputs['states'].keys())[0]
        check_p_out = np.abs(out_states[fl_name][2]-self.config[fl_name]['p_low'])
        if check_p_out > 10 and not self.config[fl_name]['optimize']:
            self.warning = warn(300, f""""Throttle low pressure does
                           not fit to cycle low pressure
                           by {check_p_out} Pa!""")

        m_dot = kwargs.get("m_dot", 1.)
        fluid_act = self.inputs["act_fluids"][fl_name]
        self.p_out = out_states[fl_name][1]

        # ... Berechnungslogik hier ...
        state_in = fluid_act.set_state([in_states[1], in_states[2]], "PH")
        if isinstance(state_in, str):
            print(state_in, "function/value needed")

        if fluid_act.properties.pressure < self.p_out:
            raise ValueError(
                " pressure must drop! {self_out} is higher than {fluid_act.properties.pressure }")

        if self.calc_type == "const_h":

            state_out = fluid_act.set_state(
                [fluid_act.properties.enthalpy, self.p_out], "HP")

        else:
            self.warning.value = 101
            self.warning.message = f""""The option{self.calc_type} is not yet implemented for
                                throttles"""
            raise Exception(
                self.warning_message)

        self.inputs["act_fluids"][fl_name] = fluid_act
        #
        self.output.update({"state_in": {fl_name: state_in},
                            "state_out": {fl_name: state_out},
                            "work_specific": 0.0,
                            "power": 0.0,
                            "m_dot": m_dot,
                            "warning": self.warning})
        self.all_data = {fl_name: np.array([state_in, state_out])
                         }


class HeatExchanger(Component):
    def initialize(self):
        self._area = self.config.get('area')
        self._dt_min = self.config.get('dt_min')
        self._overall_u = self.config.get('overall_u')
        self._fixed = self.inputs['parameters']['fixed']
        self._q_dot = self.config.get('q_dot')

    # @abstractmethod
    # def calculate_heat_transfer(self):
    #     pass


class StaticHeatExchanger(HeatExchanger):
    def initialize(self, **kwargs):
        super().initialize()

        self.input_calc = SimpleNamespace(points=kwargs.get('points', 50),
                                          m_dots=None
                                          )

        self.warning.__dict__.update(value=0, message="All o.k.")
        self.output = {}
        self._set_defaults()

    def _set_defaults(self):
        """ Set the default states as read from the configuration file or dictionary."""
        inputs = self.inputs["states"]
        self._out_def = {}
        self._in_def = {}
        for flname in inputs.keys():
            self._out_def[flname] = inputs[flname]['out']
            self._in_def[flname] = inputs[flname]['in']
        if "q_dot" in self.inputs["parameters"].keys():
            self._q_dot = self.inputs["parameters"]["q_dot"]

    def set_in_out(self, new_state, instate=True):
        """
        Replace either an old input state or output state by a new one.

        Needed for the calculation of the heat exchanger.

        Parameters
        ----------
        new_state : dictionary
           {"fluid-name": numpy-array with state}.
        instate : Boolean, optional
            Is it input or output? The default is True.

        Returns
        -------
        in_state : dictionary
            pass to calculate().
        out_state : dictionary
            pass to calculate().

        """
        inputs = self.inputs["states"]
        out_state = {}
        in_state = {}
        for flname, value in inputs.items():
            out_state[flname] = inputs[flname]['out']
            in_state[flname] = inputs[flname]['in']
        for key, val in new_state.items():
            if instate:
                in_state[key] = val
                self.inputs['states']['working_fluid']['in'] = val

            else:
                out_state[key] = val
                self.inputs['states']['working_fluid']['out'] = val
        # if there is a string  for the output, set the output state:
        if isinstance(self.inputs['states']['working_fluid']['out'], str):
            self._set_w_out()
            out_state =self._out_def
        return in_state, out_state

    def calculate(self, in_states=None, out_states=None,  run_param=None, **kwargs):
        self.warning.__dict__.update(value=0, message="All o.k.")
        verbose = kwargs.get("verbose", False)
        if self.verbose or verbose:
            self.logger.info(f"Calculating {self.name}")

        self._run_param = run_param
        if "q_dot" in run_param:
            self._q_dot = run_param["q_dot"]
        if isinstance(self._q_dot, str):
            self._q_dot = run_param['q_dot']

        if not in_states:
            in_states = self._in_def
            self.warning .__dict__.update(value=2, message="Default values used for I/O")
        if not out_states:
            out_states = self._out_def
            self.warning .__dict__.update(value=2, message="Default values used for I/O")

        fluid_names = list(self.inputs["act_fluids"].keys())
        stn = self._storage_name(fluid_names)
        self.output.update({"m_dot": {},
                            "state_in": {},
                            "state_out": {},
                            })
        self.all_data = {}
        w_out = {}
        self._heating = -1
        mdw_calc = True

        match self._fixed:  # noqa
            case 'q_dot':
                pass
            case 'm_dot_w'| 'q_m_dot_w':
                try:  # {"m_dot": {"working_fluid": m_dot_w}}
                    self.output['m_dot'] = run_param["m_dot"]
                    self.output['m_dot'][stn] = None
                    mdw_calc = False
                except:
                    raise ValueError(f"{self.name}: m_dot not set in run_param!")
            # case 'q_m_dot_w': """#BA 2024-08-15-continue here  This is too early . must come later                 self.output  Out  [2]: {'m_dot': {}, 'state_in': {}, 'state_out': {}}"""
            #     self.output['m_dot'][stn] = np.abs(self._q_dot /
            #                                        (self.output['state_in'][stn][2]
            #                                         - self.output['state_out'][stn][2]))
            #     dh_w = self._q_dot/self.output['m_dot']['working_fluid']
            #     self.output['state_out'][fln] = w_in.set_state([out_states['working_fluid'][1],
            #                                                     in_states['working_fluid'][2] + dh_w],
            #                                                    "PH")

            case _: raise NotImplementedError(f''''StaticHeatExchanger:
                                              {self.inputs['parameters']['fixed']} not implemented!''')
        
        
        
        if self._fixed == 'q_m_dot_w': #BA 2024-08-15-continue here  This is too early . must come later                 self.output  Out  [2]: {'m_dot': {}, 'state_in': {}, 'state_out': {}}"""
            
            dh_w = self._q_dot/self.output['m_dot']['working_fluid']
            w_in_w = copy.copy(self.inputs['act_fluids']['working_fluid'])
            h_out_w = self.inputs['states']["working_fluid"]['in'][2] - dh_w
            out_states['working_fluid'] = w_in_w.set_state([w_in_w.val_dict["Pressure"],
                                                            h_out_w],
                                                           "PH")
        


        for fln in ["working_fluid", stn]:

            w_in = copy.copy(self.inputs['act_fluids'][fln])
            if isinstance(in_states[fln], str) and in_states[fln] == 'ambient':
                t_amb =cb.io_utils._set_temp(in_states[fln])
                if fln !=stn:
                    t_amb+=heating*self.inputs['parameters']["dt_min"]
                p_act = self.config[fln][self.config[self.name]["species"][fln]["p_in"]]
                self.output['state_in'][fln] = w_in.set_state([t_amb,
                                                               p_act],
                                                              "TP")
                
                
            self.output['state_in'][fln] = w_in.set_state([in_states[fln][1],
                                                           in_states[fln][2]],
                                                          "PH")
            self.output['state_out'][fln] = w_in.set_state([out_states[fln][1],
                                                            out_states[fln][2]],
                                                           "PH")
            w_out[fln] = copy.copy(w_in)
            # all states set now

        for fln in ["working_fluid", stn]:
            if not mdw_calc:
                if fln == "working_fluid":  # if mdot for working fluid is fixed
                    self._q_dot = (self.output['state_in'][fln][2]
                                   - self.output['state_out'][fln][2]) * self.output['m_dot'][fln]
                    self.output['m_dot'][stn] = np.abs(self._q_dot /
                                                       (self.output['state_in'][stn][2]
                                                        - self.output['state_out'][stn][2]))
            elif self._fixed == "q_dot":  # q_dot is fixed
                self.output['m_dot'][fln] = np.abs(self._q_dot /
                                                   (self.output['state_in'][fln][2]
                                                    - self.output['state_out'][fln][2]))
            else:
                raise NotImplementedError(
                    f"HeatExch, this fixed value is not implemented {self._fixed}")
            if fln == "working_fluid":
                temp_w_in = self.output['state_in'][fln][0]
                self.all_data[fln] = self._calculate_state_array(w_out[fln],
                                                                 [self.output['state_in'][fln],
                                                                 self.output['state_out'][fln]])
            else:
                temp_s_in = self.output['state_in'][fln][0]
                self.all_data[fln] = self._calculate_state_array(w_out[fln],
                                                                 [self.output['state_out'][fln],
                                                                 self.output['state_in'][fln]
                                                                  ])
        if temp_w_in > temp_s_in:
            self._heating = 1

        d_tempall = self.all_data["working_fluid"][:, 0] - self.all_data[stn][:, 0]
        self.dt_mean, self.dt_min, self.dt_max = d_tempall.mean(), np.abs(
            d_tempall).min(), np.abs(d_tempall).max()

        self._check_temperature_consistency(d_tempall)

        self.output.update({"dt_mean": self.dt_mean,
                           "dt_min": self.dt_min,
                            "dt_max": self.dt_max,
                            "q_dot": -self._q_dot})

    def _calculate_state_array(self, fluid, h_range):

        h_array = np.linspace(h_range[0][2], h_range[1][2], self._points)
        values = np.zeros((self._points, 2))
        values[:, 0] = h_array
        values[:, 1] = h_range[0][1]
        return fluid.set_state_v(values, "HP")

    def _check_temperature_consistency(self, d_tempall):
        self.warning.__dict__.update(value=0, message="All o.k.")
        eps_min = -1e-3
        dt_min_sep = self.inputs["parameters"]["dt_min"]
        positive = np.any(d_tempall > 0)
        negative = np.any(d_tempall < 0)
        below = True
        # print(self.name, self._heating, below, positive, negative)
        if self._heating < 0:
            below = False
        crossing = (positive > 0 and negative > 0)
        wrong_side = (positive > 0 and not below) or (negative > 0 and below)
        abs_dt_min = np.abs(self.dt_min)
        difference = abs_dt_min - dt_min_sep
        # print(f"Debug: abs_dt_min = {abs_dt_min}, dt_min_sep = dt_min_sep}, difference = {difference}")

        if difference < eps_min:
            self.warning .__dict__.update(
                value=np.abs(difference), message="Below minimum approach temperature!")
            # print(f"907: {difference}, {abs_dt_min}, {dt_min_sep},{self.name}")

        elif crossing or wrong_side:
            val_ =np.abs((positive-negative)/(positive+negative))
            self.dt_mean = 1e6
            self.warning.__dict__.update(
                value=val_, message="Temperatures crossing or wrong side!")
        else:
            pass

    def _set_w_out(self):
        stn = self._storage_name(self.inputs['act_fluids'].keys())
        fl_name = "working_fluid"
        s_state = self.inputs['act_fluids'][stn].val_dict
        w_state = self.inputs['states']['working_fluid']['in']
        sign = 1
        if s_state["Temperature"] > w_state[0]:
            sign = -1
        s_out = self.inputs['states'][stn]['out']
        t_w_out = s_state["Temperature"] + sign * self.inputs['parameters']['dt_min']
        w_out = self.inputs['act_fluids']['working_fluid'].set_state(
            [w_state[1], t_w_out], 'PT')
        self.inputs['states'][fl_name]['out'] = w_out
        self._out_def[fl_name] = w_out

        return w_out

    def plot(self, plot_info, **kwargs):
        """
        Plots the H_dot-T-plot (shifted in H).

        Parameters
        ----------
        plot_info : dictionary
            Mainly parameters for a matplotlib plot. In what the things to be plotted
            are given with their thermostring index (2=h, 0 =T), and the shifts along
            H_dot can be specified
            {"fig": fig_act, "ax": ax_act, "what": [2, 0], "col": ["r:", "ko"],
                             "label": ["work,c", "sec,c"], "x-shift": [0, 0]}.
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        float
            the actual shift in H_dot.

        """

        if plot_info["what"][0] == 2:
            for ii, fln in enumerate(self.all_data.keys()):

                # print("Plot info:", plot_info)  # Debugging-Ausgabe

                data = (self.all_data[fln][:, plot_info["what"][0]] - self.all_data[fln][:,
                                                                                         plot_info["what"][0]].min()) * self.output["m_dot"][fln]

                shift = self._plot_shift(
                    plot_info["x-shift"], [data.min(), data.max()], plot_info["direction"])
                data = data - data.min() + shift[0]

                plot_info["ax"].plot(data, self.all_data[fln][:, plot_info["what"][1]],
                                     plot_info["col"][ii], label=plot_info["label"][0])

        else:
            print(
                f"H-Ex: plotting only implemented for T-H_dot [2,0]. You requested {plot_info['what']}")

        self._plot_shift = self.all_data[fln][:, plot_info["what"][0]].min() * \
            self.output["m_dot"][fln]  # + plot_info["x-shift"][0]
        psh_max = self.all_data[fln][:, plot_info["what"][0]].max() * \
            self.output["m_dot"][fln]
        plot_info["ax"].legend()
        return [data.min(), data.max()], shift[1]

    def _change_h_w_out(self, h_out_new):
        inputs = self.inputs["states"]
        out_state = {}
        in_state = {}
        for flname, value in inputs.items():
            out_state[flname] = inputs[flname]['out']
            in_state[flname] = inputs[flname]['in']
        out_state["working_fluid"][2] = h_out_new[0]
        return in_state, out_state

    def _opti_h_func(self, h_act_out,  m_dot_w, inp_o=None, out_o=None,  verbose=False):

        run_p_hex = {"m_dot": {"working_fluid": m_dot_w}}
        instates, outstates = self._change_h_w_out(h_act_out)
        self.calculate(instates, outstates, run_param=run_p_hex)
        if verbose:
            print(self.output["dt_mean"],  hex_act.warning)
        if self.warning.value > 2:
            return +100
        return np.abs(self.output["dt_mean"])

    def hex_opti_work_out(self, inp_act=None, out_act=None, run_p_par=None, verbose=False):
        """
        Optimize the mean temperature difference by varying the working Fluid output state.
        
        Only enthalpy is variied within +/- 5%, pressure remains unchanged.
        
        Parameters
        ----------
        run_p_cond : dictionary
            A value for {"m_dot": 0.01} must be provided, it is kept constant.
        verbose : boolean, optional
            If you want some printing. The default is False.

        Returns
        -------
        None.

        """
        self.calculate(in_states=inp_act, out_states=out_act, run_param=run_p_par)
        if verbose:
            print(
                f"opti_work_out: T-mean before optimization= {condenser.output['dt_mean']} K")
        # condenser._change_h_w_out =_change_h_w_out
        tolerance = 1e-2
        max_iter = 240
        h_act = self.output["state_out"]["working_fluid"][2] * 1.005
        dh = h_act * .051
        bound_act = opti.Bounds(lb=h_act-dh, ub=h_act+dh)

        result = opti.minimize(self._opti_h_func,
                               h_act,
                               args=(run_p_par['m_dot']["working_fluid"],
                                     inp_act,
                                     out_act,),
                               method='Nelder-Mead',
                               tol=tolerance,
                               bounds=bound_act,
                               options={"maxiter": max_iter,  # can take long!
                                        "disp": True})
        if verbose:
            print(f"T-mean after optimization: {result.fun} K\n{result}")


class Start(FlowDevice):
    def initialize(self, **kwargs):
        """
        Returns the starting state of the working_fluid only.

        Returns
        -------
        None.

        """
        # if not self.output["m_dot"]:
        self.warning.__dict__.update(value=0, message="All o.k.")
        m_dot = kwargs.get("m_dot", 1.)
        self._check_start()
        fl_name = "working_fluid"  # list(self.inputs['states'].keys())[0]
        self.output = {"state_out": {fl_name: self.inputs['states'][fl_name]['out']},
                       "state_in": {fl_name: self.inputs['states'][fl_name]['in']},
                       "m_dot": m_dot,  # Dummy
                       "p_low": self.p_low,                    
                       "warning": self.warning}

        self.all_data = {fl_name: np.array([self.inputs['states'][fl_name]['in'],
                                           self.inputs['states'][fl_name]['out']])
                         }

    def calculate(self, in_states=None, out_states=None, run_param=None, **kwargs):
        self.logger.info(f"Calculating {self.name}")
        # Implementierung der Startpunktberechnung
        pass

    def _check_start(self):
        stn = self._storage_name(self.inputs['act_fluids'].keys())
        fl_name = "working_fluid"
        s_state = self.inputs['act_fluids'][stn].val_dict
        w_state = self.inputs['act_fluids']['working_fluid'].val_dict
        self.p_low = w_state['Pressure']  # setting pressure
        sign = 1
        eps_diff = 1e-3
        if s_state["Temperature"] > w_state["Temperature"]:
            sign = -1
            
        if self.config["process"]["name"] == "heat_pump":
            sat_state = self.inputs['act_fluids']['working_fluid'].set_state(
                [w_state['Pressure'], 1], "PQ")
            if (w_state["Temperature"] - sat_state[0]) - self.inputs["parameters"]['dt_superheat'] < -eps_diff:
                val_ = self.inputs["parameters"]['dt_superheat'] / (w_state["Temperature"] - sat_state[0])
                self.warning.__dict__.update(
                    value=val_, message=f"dT superheating did not fit, low pressure was changed! WF:{w_state['Temperature']} Sat-T: {sat_state[0]}, p:{w_state['Pressure']})")
        
        elif self.config["process"]["name"] == "orc":
            sat_state = self.inputs['act_fluids']['working_fluid'].set_state(
                [w_state['Pressure'], 0], "PQ")
            if self.inputs["parameters"]['dt_subcool'] + (w_state["Temperature"] - sat_state[0]) >= eps_diff:
                self.warning.__dict__.update(
                    value=1, message="dT subcooling was too low, low pressure was changed!")

        if (w_state["Temperature"] - s_state["Temperature"]) * sign < self.inputs["parameters"]['dt_min']:
            self.warning.value += 2
            self.warning.message = self.warning.message + "AND dT_min was too low"
        if self.warning.value > 0:
            if self.config["process"]["name"] == "heat_pump":

                t_sat_new = s_state["Temperature"] + sign*(self.inputs["parameters"]
                                                           ['dt_superheat'] + self.inputs["parameters"]['dt_min'])
                w_sat_state = self.inputs['act_fluids']['working_fluid'].set_state(
                    [t_sat_new, 1], "TQ")
                self.p_low = p_new = w_sat_state[1]  # setting new pressure
                self.warning.message += f", p_new: {p_new}"
                t_new = t_sat_new - sign*(self.inputs["parameters"]['dt_superheat'])
                
            elif self.config["process"]["name"] == "orc":
                t_sat_new = s_state["Temperature"] - sign*(self.inputs["parameters"]
                                                           ['dt_subcool'] + self.inputs["parameters"]['dt_min'])
                w_sat_state = self.inputs['act_fluids']['working_fluid'].set_state(
                    [t_sat_new, 1], "TQ")
                t_new = t_sat_new - sign * self.inputs["parameters"]['dt_subcool']
                self.p_low = p_new = w_sat_state[1]  # setting new pressure
                self.warning.message += f", p_new: {p_new}"
                
            
            
            w_new_state = self.inputs['act_fluids']['working_fluid'].set_state(
                [p_new, t_new], "PT")
            self.inputs['states'][fl_name]['out'] = w_new_state
            self.inputs['states'][fl_name]['in'] = w_new_state
            # self.output.update( {"state_out": {"working_fluid": w_new_state},
            #                "state_in": {"working_fluid": w_new_state},
            #                })
            # self.all_data.update( {fl_name: np.array([w_new_state,
            #                                    w_new_state])
            # })
        



def create_component(name, config):
    component_type = config.get('model')
    if component_type == 'FlowDevice':
        if name == 'compressor':
            return FlowMachine(name, config)
        elif name == 'throttle':
            return Throttle(name, config)
    elif component_type == 'StaticHeatExchanger':
        return StaticHeatExchanger(name, config)
    elif component_type == 'Start':
        return Start(name, config)
    else:
        raise ValueError(f"Unknown component type: {component_type, name}")


class Cycle:
    def __init__(self, config):
        self.config = config
        self.components = {}
        self.fluids = {}
        self.process = config['process']
        self.logger = logging.getLogger(f"{__name__}.Cycle")
        self.initialize()

    def initialize(self):
        # Nur die im Prozess/Zyklus aufgeführten Komponenten initialisieren
        for component_name in self.process['cycle']:
            if component_name in self.config:
                component_config = self.config[component_name]
                self.components[component_name] = create_component(
                    component_name, self.config)
            else:
                self.logger.warning(
                    f"Component {component_name} mentioned in cycle but not found in configuration")

        # Fluide initialisieren
        if 'fluids_all' in self.config:
            for fluid_name, fluid_type in self.config['fluids_all'].items():
                if fluid_name in self.config:
                    self.fluids[fluid_name] = self.config[fluid_name]
                else:
                    self.logger.warning(
                        f"Fluid {fluid_name} mentioned in fluids_all but not found in configuration")

        self.logger.info("Cycle initialized")

    def calculate(self):
        self.logger.info("Starting cycle calculation")
        for step in self.process['cycle']:
            if step in self.components:
                self.components[step].calculate()
            else:
                self.logger.warning(f"Calculation step {step} not found in components")
        self.logger.info("Cycle calculation completed")

    def plot(self):
        fig, axes = plt.subplots(len(self.components), 1,
                                 figsize=(10, 5*len(self.components)))
        axes = [axes] if len(self.components) == 1 else axes
        for i, (name, component) in enumerate(self.components.items()):
            component.plot(fig, axes[i])
        plt.tight_layout()
        plt.show()
        self.logger.info("Cycle plots generated")

    def save_results(self):
        base_dir = os.path.join("results", datetime.now().strftime("%Y-%m-%d-%H-%M"))
        os.makedirs(base_dir, exist_ok=True)
        for component in self.components.values():
            component.save_results(base_dir)
        self.logger.info(f"All results saved in {base_dir}")

# Die create_component Funktion bleibt unverändert


# Verwendung
def main():
    dir_name = cb.CB_DEFAULTS["General"]["RES_DIR"]
    logger.info("Starting thermodynamic cycle calculation")
    cycle_config = read_config(dir_name+"\\io-cycle-data.yaml")
    cycle = Cycle(cycle_config)
    cycle.calculate()
    cycle.plot()
    cycle.save_results()
    logger.info("Thermodynamic cycle calculation completed")


if __name__ == "__main__":

    # ------- input data -----------
    dir_name = cb.CB_DEFAULTS["General"]["CB_DATA"]+"\\io-cycle-data.yaml"

    # ================ CALCULATIONS ==============================
    # ------ Start/initial condition ----
    # but the mass flow rate is yet unknown, plotting must be delayed
    start = Start("start", dir_name, m_dot=10e-3)

    # ----- compressor --------------
    # prescribed power, working_fluid mass flow rate is calculated here
    run_p_comp = {"power": 1500.}
    compressor = FlowMachine("compressor", dir_name)
    p_high = compressor.config['working_fluid']['p_high']
    compressor.calculate(start.output["state_out"],
                         {'working_fluid': [600, p_high, 5e5]},
                         run_param=run_p_comp)  # ,  m_dot=10e-3)
    # for the output only p_high is used! Now m_dot is known for the working fluid.
    m_dot_w = compressor.output["m_dot"]
    start = Start("start", dir_name, m_dot=m_dot_w)

    # ----- coondenser --------------
    run_p_cond = {"m_dot": {"working_fluid": m_dot_w}}

    condenser = StaticHeatExchanger("condenser", dir_name)

    condenser.calculate(run_param=run_p_cond)
    condenser.hex_opti_work_out(run_p_par=run_p_cond)

    # condenser.output["state_out"]["working_fluid"]
    throttle = Throttle("throttle", dir_name)
    throttle.calculate(condenser.output["state_out"]["working_fluid"],
                       compressor.output["state_in"],
                       m_dot=m_dot_w)

    evaporator = StaticHeatExchanger("evaporator", dir_name)
    inp1, outp1 = evaporator.set_in_out(
        {'working_fluid': throttle.output['state_out']["working_fluid"]})
    inp2, outp2 = evaporator.set_in_out(
        start.output['state_in'], False)
    evaporator.calculate(inp1, outp2, run_param=run_p_cond)

    print(f"COP: {np.abs(condenser.output["q_dot"]/run_p_comp["power"]):.4f}")

    # =========== Calculations finished ====================
    # --------- plot preparation ------------

    fig, ax = plt.subplots(1)
    plot_info = cb.CB_DEFAULTS["Components"]["Plot"]
    plot_info.update({"ax": ax, "fig": fig})

    pl_inf = plot_info.copy()  # for the starting point (dot)
    pl_inf.update({"label": ["start", ""],
                   "col": ["ok", "bv"],
                   "direction": 1, })
    #
    #     Plotting starts
    shift, direct = start.plot(pl_inf)

    plot_info.update({"x-shift": shift,
                      "direction": direct,
                      "label": [compressor.name, ""],
                      "col": ["-r", "bv-"]})
    shift, direct = compressor.plot(plot_info)

    plot_info.update({"x-shift": shift,
                      "direction": direct,
                      "label": [condenser.name, ""],
                      "col": [":r", "rv-"]})
    shift, direct = condenser.plot(plot_info)

    plot_info.update({"x-shift": shift,
                      "direction": direct,
                      "label": [throttle.name, ""],
                      "col": ["-b", "bv-"]})
    shift, direct = throttle.plot(plot_info)

    plot_info.update({"x-shift": shift,
                      "direction": direct,
                      "label": [evaporator.name, ""],
                      "col": [":b", "bv-"]})
    shift4 = evaporator.plot(plot_info)
