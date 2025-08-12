import logging
from typing import Set

from commonroad.prediction.prediction import TrajectoryPrediction
from commonroad.scenario.obstacle import ObstacleType
from commonroad.scenario.scenario import Scenario

import sumolib
from commonroad_sumo.cr2sumo.map_converter.mapping import VEHICLE_TYPE_CR2SUMO
from commonroad_sumo.cr2sumo.map_converter.util import (
    get_state_list_of_dynamic_obstacle,
)
from commonroad_sumo.cr2sumo.traffic_generator.traffic_generator import (
    AbstractTrafficGenerator,
)
from commonroad_sumo.errors import SumoTrafficGenerationError
from commonroad_sumo.helpers import SumoApplication, execute_sumo_application
from commonroad_sumo.sumolib.net import SumoVehicle, SumoVehicleType
from commonroad_sumo.sumolib.sumo_project import SumoFileType, SumoProject

_LOGGER = logging.getLogger(__name__)


def _get_set_of_obstacle_types_in_scenario(scenario: Scenario) -> Set[ObstacleType]:
    obstacle_types = set()
    for obstacle in scenario.dynamic_obstacles:
        obstacle_types.add(obstacle.obstacle_type)

    return obstacle_types


def _populate_route_file_with_vehicle_type_definitions_for_obstacle_types(
    scenario: Scenario, sumo_project: SumoProject
) -> None:
    route_definition_file = sumo_project.create_file(SumoFileType.VEHICLE_ROUTES)

    for obstacle_type in _get_set_of_obstacle_types_in_scenario(scenario):
        vehicle_type = VEHICLE_TYPE_CR2SUMO[obstacle_type]
        route_definition_file.add_node(SumoVehicleType.from_vehicle_type(vehicle_type))


def _create_routes_from_trajectories(
    scenario: Scenario,
    sumo_project: SumoProject,
    map_matching_delta: float,
    safe: bool = True,
) -> bool:
    _populate_route_file_with_vehicle_type_definitions_for_obstacle_types(
        scenario, sumo_project
    )

    # TODO: depends on the file being created already
    route_definition_file = sumo_project.get_file(SumoFileType.VEHICLE_ROUTES)

    sumo_net: sumolib.net.Net = sumolib.net.readNet(
        sumo_project.get_file_path(SumoFileType.NET)
    )
    for dynamic_obstacle in scenario.dynamic_obstacles:
        if dynamic_obstacle.prediction is None:
            continue

        if not isinstance(dynamic_obstacle.prediction, TrajectoryPrediction):
            raise SumoTrafficGenerationError()

        state_list = get_state_list_of_dynamic_obstacle(dynamic_obstacle)
        position_trace = [tuple(state.position) for state in state_list]
        # TODO: Delta has to be set so high, so that we correctly match inside junctions
        # can we determine a more specific delta, based on the properties of the scenario?
        edges = sumolib.route.mapTrace(
            position_trace, sumo_net, delta=map_matching_delta
        )
        if len(edges) == 0:
            _LOGGER.warning(
                "The trajectory of the vehicle %s could not be mapped to any edges, because it either happens outside of the lanelet network or happens soley inside a SUMO junction. It will be skipped.",
                dynamic_obstacle.obstacle_id,
            )
            continue

        depart_lane_idx, depart_lane_pos, _ = edges[0].getClosestLanePosDist(
            position_trace[0]
        )
        arrival_lane_idx, arrival_lane_pos, _ = edges[-1].getClosestLanePosDist(
            position_trace[-1]
        )
        vehicle = SumoVehicle(
            vehicle_id=str(dynamic_obstacle.obstacle_id),
            depart_time=state_list[0].time_step * scenario.dt,
            depart_speed=state_list[0].velocity,
            depart_lane_id=depart_lane_idx,
            depart_pos=depart_lane_pos,
            arrival_lane_id=arrival_lane_idx,
            arrival_pos=arrival_lane_pos,
            vehicle_type=VEHICLE_TYPE_CR2SUMO[dynamic_obstacle.obstacle_type].value,
            edge_ids=[edge.getID() for edge in edges],
            insertion_checks=safe,
        )
        # TODO: make this type check
        route_definition_file.add_node(vehicle)  # type: ignore

    sumo_project.write()

    execute_sumo_application(
        SumoApplication.DUAROUTER,
        [
            "-n",
            str(sumo_project.get_file_path(SumoFileType.NET)),
            "-r",
            str(sumo_project.get_file_path(SumoFileType.VEHICLE_ROUTES)),
            "--ignore-errors",
            "--repair",
            "true",
            "-o",
            str(sumo_project.get_file_path(SumoFileType.VEHICLE_ROUTES)),
        ],
    )

    return True


class _TrajectoryTrafficGenerator(AbstractTrafficGenerator):
    def __init__(self, map_matching_delta: int = 5, safe: bool = True) -> None:
        super().__init__()
        self._map_matching_delta = map_matching_delta
        self._safe = safe

    def generate_traffic(self, scenario: Scenario, sumo_project: SumoProject) -> bool:
        return _create_routes_from_trajectories(
            scenario, sumo_project, self._map_matching_delta, self._safe
        )


class SafeResimulationTrafficGenerator(_TrajectoryTrafficGenerator):
    def __init__(self, map_matching_delta: int = 5) -> None:
        super().__init__(map_matching_delta, safe=True)


class UnsafeResimulationTrafficGenerator(_TrajectoryTrafficGenerator):
    def __init__(self, map_matching_delta: int = 5) -> None:
        super().__init__(map_matching_delta, safe=False)
