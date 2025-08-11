import importlib.resources
from pathlib import Path
from typing import Any, Mapping

from pydantic import PrivateAttr

from crdata.conversion.tabular.factory import (
    TabularConverterFactory,
)
from crdata.conversion.util.yaml import load_yaml

from crdata.datasets.sind.implementation import (
    SindMetaScenarioGenerator,
    SindRecordingGenerator,
    SindScenarioPrototypeGenerator,
    SindWindowMeta,
)
from crdata.conversion.tabular.windowing import FixedTimeRangeWindowGenerator


def _get_sind_config() -> Mapping[str, Any]:
    with importlib.resources.path("crdata.datasets.sind", "config.yaml") as config_path:
        config = load_yaml(str(config_path))
    return config


class SindConverterFactory(TabularConverterFactory[SindWindowMeta]):
    input_dir: Path
    location: str = "Tianjin"
    _config: Mapping[str, Any] = PrivateAttr(default_factory=_get_sind_config)

    def build_recording_generator(self) -> SindRecordingGenerator:
        return SindRecordingGenerator(self.input_dir, self.downsample)

    def build_meta_scenario_creator(self) -> SindMetaScenarioGenerator:
        return SindMetaScenarioGenerator(self.location, self.ego_vehicle_id)

    def build_scenario_prototype_creator(self) -> SindScenarioPrototypeGenerator:
        return SindScenarioPrototypeGenerator(
            self.build_scenario_id_creator(),
            self.build_meta_scenario_creator(),
            traffic_light_incomings=self._config["traffic_light_incomings"],
            traffic_light_positions=self._config["traffic_light_positions"],
        )

    def build_window_generator(self):
        if self.start_time_step is not None and self.end_time_step is not None:
            return FixedTimeRangeWindowGenerator(
                self.start_time_step, self.end_time_step
            )
        return super().build_window_generator()
