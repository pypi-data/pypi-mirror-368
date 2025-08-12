# sumo id prefix
from abc import ABCMeta
from enum import Enum


class DefaultConfig(metaclass=ABCMeta):
    # default path under which the scenario folder with name SumoCommonRoadConfig.scenario_name are located
    scenarios_path = None

    # scenario name and also folder name under which all scenario files are stored
    scenario_name = "<scenario_name>"

    ##
    # simulation
    ##
    dt = 0.1  # length of simulation step of the interface
    delta_steps = 1  # number of sub-steps simulated in SUMO during every dt
    presimulation_steps = (
        30  # number of time steps before simulation with ego vehicle starts
    )
    simulation_steps = 100  # number of simulated (and synchronized) time steps
    # lateral resolution > 0 enables SUMO'S sublane model, see https://sumo.dlr.de/docs/Simulation/SublaneModel.html
    lateral_resolution = 1.0
    # assign lanelet ids to dynamic obstacles. Activate only when required, due to significant computation time.
    add_lanelets_to_dyn_obstacles = False

    # ego vehicle
    ego_veh_width = 1.6
    ego_veh_length = 4.3

    ##
    # TRAFFIC GENERATION
    ##
    # random seed for deterministic sumo traffic generation (applies if not set to None)
    random_seed: int = 1234

    @classmethod
    def from_scenario_name(cls, scenario_name: str):
        """Initialize the config with a scenario name"""
        obj = cls()
        obj.scenario_name = scenario_name
        return obj

    @classmethod
    def from_dict(cls, param_dict: dict):
        """Initialize config from dictionary"""
        obj = cls()
        for param, value in param_dict.items():
            if hasattr(obj, param):
                setattr(obj, param, value)
        return obj


class ParamType(Enum):
    COPY = 0  # needs to be copied from map converter config
    NOT_SET = 1  # needs to be set after planning problem extraction


class InteractiveSumoConfigDefault(DefaultConfig):
    # default path under which the scenario folder with name SumoCommonRoadConfig.scenario_name are located
    scenarios_path = None

    # scenario name and also folder name under which all scenario files are stored
    scenario_name = ParamType.NOT_SET

    ##
    # simulation
    ##
    field_of_view = 400
    dt = 0.1  # length of simulation step of the interface
    delta_steps = 1  # number of sub-steps simulated in SUMO during every dt
    presimulation_steps = (
        ParamType.NOT_SET
    )  # number of time steps before simulation with ego vehicle starts
    simulation_steps = (
        ParamType.NOT_SET
    )  # number of simulated (and synchronized) time steps
    # lateral resolution > 0 enables SUMO'S sublane model, see https://sumo.dlr.de/docs/Simulation/SublaneModel.html
    lateral_resolution = 1.0

    # ego vehicle
    ego_veh_width = 1.674
    ego_veh_length = 4.298

    # random seed for deterministic sumo traffic generation (applies if not set to None)
    random_seed: int = ParamType.COPY
