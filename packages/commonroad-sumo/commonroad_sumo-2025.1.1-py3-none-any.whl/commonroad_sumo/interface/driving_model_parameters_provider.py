from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Optional, Union

import numpy as np
from commonroad.common.util import Interval
from commonroad.scenario.obstacle import ObstacleType, Rectangle


class DrivingModelParametersProvider(ABC):
    """
    Provides parameters based on the given obstacle type
    """

    @abstractmethod
    def get_shape(self, obstacle_type: ObstacleType) -> Rectangle: ...

    @abstractmethod
    def get_accel(self, obstacle_type: ObstacleType) -> float: ...

    @abstractmethod
    def get_decel(self, obstacle_type: ObstacleType) -> float: ...

    @abstractmethod
    def get_min_gap(self, obstacle_type: ObstacleType) -> float: ...

    @abstractmethod
    def get_max_speed(self, obstacle_type: ObstacleType) -> float: ...


@dataclass
class DrivingModelParameters:
    length: Union[float, Interval]
    width: Union[float, Interval]
    min_gap: Union[float, Interval]
    # The following parameters cannot be set for pedestrians
    accel: Optional[Union[float, Interval]] = None
    decel: Optional[Union[float, Interval]] = None
    max_speed: Optional[Union[float, Interval]] = None
    lc_strategic: Optional[Union[float, Interval]] = None
    lc_speed_gain: Optional[Union[float, Interval]] = None
    lc_cooperative: Optional[Union[float, Interval]] = None
    lc_sigma: Optional[Union[float, Interval]] = None
    lc_impatience: Optional[Union[float, Interval]] = None
    impatience: Optional[Union[float, Interval]] = None
    speed_dev: Optional[Union[float, Interval]] = None
    speed_factor: Optional[Union[float, Interval]] = None


class StaticDrivingModelParametersProvider(DrivingModelParametersProvider):
    """
    Provides a parameter sampling over a static, predefined set of values.
    If the parameter is a simple value this value will be used.
    If the parameter is definied as an interval, values will be selected from this interval according to a uniform distribution.
    """

    DEFAULT_DRIVING_MODEL_PARAMETERS = {
        ObstacleType.CAR: DrivingModelParameters(
            length=5.0,
            width=2.0,
            # default 2.9 m/s²
            accel=Interval(2, 2.9),
            # default 7.5 m/s²
            decel=Interval(4, 6.5),
            # default 180/3.6 m/s
            max_speed=180 / 3.6,
            min_gap=2.5,
        ),
        ObstacleType.TRUCK: DrivingModelParameters(
            length=7.5,
            width=2.6,
            accel=Interval(1, 1.5),
            decel=Interval(3, 4.5),
            max_speed=130 / 3.6,
            min_gap=2.5,
        ),
        ObstacleType.BUS: DrivingModelParameters(
            length=12.4,
            width=2.7,
            min_gap=2.5,
            accel=Interval(1, 1.4),
            decel=Interval(3, 4.5),
            max_speed=85 / 3.6,
        ),
        ObstacleType.BICYCLE: DrivingModelParameters(
            length=2.0,
            width=0.68,
            # default 0.5
            min_gap=1.0,
            # default 1.2
            accel=Interval(1, 1.4),
            # default 3
            decel=Interval(2.5, 3.5),
            # default 85/3.6
            max_speed=25 / 3.6,
        ),
        ObstacleType.PEDESTRIAN: DrivingModelParameters(
            length=0.415, width=0.678, min_gap=0.25
        ),
    }

    def __init__(
        self,
        driving_model_parameters: Optional[
            Dict[ObstacleType, DrivingModelParameters]
        ] = None,
    ):
        # We need to copy the parameter dict here, because otherwise overriding the values
        # would also override the values for all other instances
        self._driving_model_parameters = deepcopy(self.DEFAULT_DRIVING_MODEL_PARAMETERS)
        if driving_model_parameters:
            # If we received model parameters, those should override the default ones
            for obstacle_type, parameters_set in driving_model_parameters.items():
                self._driving_model_parameters[obstacle_type] = parameters_set

    def _get_driving_model_parameters(
        self, obstacle_type: ObstacleType
    ) -> DrivingModelParameters:
        if obstacle_type in self._driving_model_parameters:
            return self._driving_model_parameters[obstacle_type]
        else:
            raise ValueError(
                f"No driving model parameters for obstacle type '{obstacle_type}'"
            )

    def _sample_driving_model_parameter(self, parameter: Union[Interval, float]):
        if isinstance(parameter, Interval):
            assert (
                0 <= parameter.start <= parameter.end
            ), f"All values in the interval need to be positive: {parameter}"
            return float(np.random.uniform(parameter.start, parameter.end))
        else:
            return parameter

    def get_shape(self, obstacle_type: ObstacleType) -> Rectangle:
        """
        :return: A Rectangle with the length and width sampled
        """
        # TODO: The legacy implemention only allowed the definition of Rectangles
        # but it will be great if the caller could provide the base shape
        parameters = self._get_driving_model_parameters(obstacle_type)
        length = self._sample_driving_model_parameter(parameters.length)
        width = self._sample_driving_model_parameter(parameters.width)
        return Rectangle(length, width)

    def get_accel(self, obstacle_type: ObstacleType) -> float:
        parameters = self._get_driving_model_parameters(obstacle_type)
        if parameters.accel is None:
            raise ValueError(
                f"Parameter 'accel' is not set for obstacle type '{obstacle_type}'"
            )
        return self._sample_driving_model_parameter(parameters.accel)

    def get_decel(self, obstacle_type: ObstacleType) -> float:
        parameters = self._get_driving_model_parameters(obstacle_type)
        if parameters.decel is None:
            raise ValueError(
                f"Parameter 'decel' is not set for obstacle type '{obstacle_type}'"
            )
        return self._sample_driving_model_parameter(parameters.decel)

    def get_min_gap(self, obstacle_type: ObstacleType) -> float:
        parameters = self._get_driving_model_parameters(obstacle_type)
        return self._sample_driving_model_parameter(parameters.min_gap)

    def get_max_speed(self, obstacle_type: ObstacleType) -> float:
        parameters = self._get_driving_model_parameters(obstacle_type)
        if parameters.max_speed is None:
            raise ValueError(
                f"Parameter 'max_speed' is not set for obstacle type '{obstacle_type}'"
            )
        return self._sample_driving_model_parameter(parameters.max_speed)
