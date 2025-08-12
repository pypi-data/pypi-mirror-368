import logging
from typing import Optional, Union

import numpy as np
from commonroad.common.util import Interval
from commonroad.scenario.obstacle import ObstacleType
from commonroad.scenario.scenario import Scenario

from commonroad_sumo.cr2sumo.map_converter.mapping import VEHICLE_TYPE_CR2SUMO
from commonroad_sumo.cr2sumo.traffic_generator.traffic_generator import (
    AbstractTrafficGenerator,
)
from commonroad_sumo.helpers import SumoTool, execute_sumo_tool
from commonroad_sumo.sumo_config.config import SumoConfig
from commonroad_sumo.sumolib.net import SumoVehicleType, SumoVehicleTypeDistribution
from commonroad_sumo.sumolib.sumo_project import SumoFileType, SumoProject

_LOGGER = logging.getLogger(__name__)


def _create_random_routes(
    scenario: Scenario,
    sumo_project: SumoProject,
    sumo_config: SumoConfig,
) -> bool:
    if len(sumo_config.ego_ids) > sumo_config.n_ego_vehicles:
        _LOGGER.error(
            "total number of given ego_vehicles must be <= n_ego_vehicles, but {}not<={}".format(
                len(sumo_config.ego_ids), sumo_config.n_ego_vehicles
            )
        )
        return False

    if sumo_config.n_ego_vehicles > sumo_config.n_vehicles_max:
        _LOGGER.error(
            "Number of ego vehicles needs to be <= than the total number of vehicles."
            " n_ego_vehicles: {} > n_vehicles_max: {}".format(
                sumo_config.n_ego_vehicles, sumo_config.n_vehicles_max
            )
        )
        return False

    net_file_path = sumo_project.get_file_path(SumoFileType.NET)

    total_lane_length = 0
    for lanelet in scenario.lanelet_network.lanelets:
        total_lane_length += lanelet.distance

    if total_lane_length is not None:
        # calculate period based on traffic frequency depending on map size
        period = 1 / (
            sumo_config.max_veh_per_km * (total_lane_length / 1000) * scenario.dt
        )
        _LOGGER.debug(
            "SUMO traffic generation: traffic frequency is defined "
            "based on the total lane length of the road network."
        )
    elif sumo_config.veh_per_second is not None:
        # vehicles per second
        period = 1 / (sumo_config.veh_per_second * scenario.dt)
        _LOGGER.debug(
            "SUMO traffic generation: the total_lane_length of the road network is not available. "
            "Traffic frequency is defined based on equidistant depature time."
        )
    else:
        period = 0.5
        _LOGGER.debug(
            "SUMO traffic generation: neither total_lane_length nor veh_per_second is defined. "
            "For each second there are two vehicles generated."
        )
    vehicle_trips_file_path = sumo_project.get_file_path(SumoFileType.VEHICLE_TRIPS)
    vehicle_routes_file = sumo_project.create_file(SumoFileType.VEHICLE_ROUTES)

    # TODO: The sampling should be done by a future SumoModelProvider
    def sample_param_value(
        param_value: Union[float, Interval, None],
    ) -> Optional[float]:
        if isinstance(param_value, Interval):
            return np.random.uniform(param_value.start, param_value.end, 1)[0]
        else:
            return param_value

    veh_params = sumo_config.veh_params
    veh_distribution = sumo_config.veh_distribution
    driving_params = sumo_config.driving_params

    vehicle_type_nodes = []
    for obstacle_type, probability in veh_distribution.items():
        if probability <= 0:
            continue

        vehicle_type_id = VEHICLE_TYPE_CR2SUMO[obstacle_type].value
        vehicle_type_node = SumoVehicleType(
            vehicle_type_id=vehicle_type_id,
            gui_shape=vehicle_type_id,
            vehicle_class=vehicle_type_id,
            probability=probability,
            length=sample_param_value(veh_params["length"][obstacle_type]),
            width=sample_param_value(veh_params["width"][obstacle_type]),
            acceleration=sample_param_value(veh_params["accel"][obstacle_type]),
            decceleration=sample_param_value(veh_params["decel"][obstacle_type]),
            max_speed=sample_param_value(veh_params["maxSpeed"][obstacle_type]),
            lc_strategic=sample_param_value(driving_params.get("lcStrategic")),
            lc_cooperative=sample_param_value(driving_params.get("lcCooperative")),
            lc_speed_gain=sample_param_value(driving_params.get("lcSpeedGain")),
            lc_max_speed_lat_standing=sample_param_value(
                driving_params.get("lcMaxSpeedLatStanding")
            ),
            lc_keep_right=sample_param_value(driving_params.get("lcKeepRight")),
            lc_impatience=sample_param_value(driving_params.get("lcImpatience")),
            lc_sigma=sample_param_value(driving_params.get("lcSigma")),
            sigma=sample_param_value(driving_params.get("sigma")),
            speed_dev=sample_param_value(driving_params.get("speedDev")),
            speed_factor=sample_param_value(driving_params.get("speedFactor")),
            impatience=sample_param_value(driving_params.get("impatience")),
        )
        vehicle_type_nodes.append(vehicle_type_node)

    vehicle_type_distribution_node = SumoVehicleTypeDistribution(
        id_="DEFAULT_VEHTYPE", v_types=vehicle_type_nodes
    )
    vehicle_routes_file.add_node(vehicle_type_distribution_node)
    vehicle_routes_file_path = sumo_project.get_file_path(SumoFileType.VEHICLE_ROUTES)
    sumo_project.write()

    # TODO: check result
    execute_sumo_tool(
        SumoTool.RANDOM_TRIPS,
        [
            "-n",
            str(net_file_path),
            "-o",
            str(vehicle_trips_file_path),
            "-r",
            str(vehicle_routes_file_path),
            "-b",
            str(sumo_config.departure_interval_vehicles.start),
            "-e",
            str(sumo_config.departure_interval_vehicles.end),
            "-p",
            str(period),
            "--fringe-factor",
            str(sumo_config.fringe_factor),
            "--seed",
            str(sumo_config.random_seed_trip_generation),
            "--validate",
            '--trip-attributes=departLane="best" departSpeed="max" departPos="random_free"',
            "--allow-fringe",
        ],
    )

    generate_trips_for_pedestrians = False
    if generate_trips_for_pedestrians:
        pedestrian_trips_file_path = sumo_project.get_file_path(
            SumoFileType.PEDESTRIAN_TRIPS
        )
        pedestrian_routes_file_path = sumo_project.get_file_path(
            SumoFileType.PEDESTRIAN_ROUTES
        )
        # TODO: check result
        execute_sumo_tool(
            SumoTool.RANDOM_TRIPS,
            [
                "-n",
                str(net_file_path),
                "-o",
                str(pedestrian_trips_file_path),
                "-r",
                str(pedestrian_routes_file_path),
                "-b",
                str(sumo_config.departure_interval_vehicles.start),
                "-e",
                str(sumo_config.departure_interval_vehicles.end),
                "-p",
                str(1 - sumo_config.veh_distribution[ObstacleType.PEDESTRIAN]),
                "--allow-fringe",
                "--fringe-factor",
                str(sumo_config.fringe_factor),
                "--persontrips",
                "--seed",
                str(sumo_config.random_seed_trip_generation),
                '--trip-attributes= modes="public car" departPos="base"',
                "--allow-fringe",
            ],
        )

    return True


class RandomTripsTrafficGenerator(AbstractTrafficGenerator):
    def __init__(self, seed: int = 1234) -> None:
        self._seed = seed

    def generate_traffic(self, scenario: Scenario, sumo_project: SumoProject) -> bool:
        return _create_random_routes(scenario, sumo_project, SumoConfig())
