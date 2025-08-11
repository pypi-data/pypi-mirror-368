from pathlib import Path

from crdata.conversion.tabular.factory import (
    TabularConverterFactory,
)

from ..INTERACTION.implementation import InteractionRecording
from .implementation import MonaMetaScenarioGenerator, MonaRecordingGenerator


class MonaConverterFactory(TabularConverterFactory[InteractionRecording]):
    input_dir: Path

    def build_recording_generator(self) -> MonaRecordingGenerator:
        return MonaRecordingGenerator(
            self.input_dir,
        )

    def build_meta_scenario_creator(self) -> MonaMetaScenarioGenerator:
        return MonaMetaScenarioGenerator()
