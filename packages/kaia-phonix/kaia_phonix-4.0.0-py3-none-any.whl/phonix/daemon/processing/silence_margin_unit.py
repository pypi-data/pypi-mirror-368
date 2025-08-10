import time

from .core import State, MicState, IUnit
import numpy as np
from .sound_buffer import SoundBuffer
from dataclasses import dataclass
from avatar.messaging import IMessage

@dataclass
class SilenceLevelReport(IMessage):
    silence_level: float



class SilenceMarginUnit(IUnit):
    def __init__(self,
                 silence_level: float,
                 silence_length_in_seconds: float,
                 time_between_silence_level_reports_in_seconds: float|None = 0.05
                 ):
        self.silence_level = silence_level
        self.silence_length_in_seconds = silence_length_in_seconds
        self.buffer: SoundBuffer|None = None
        self.time_between_silence_level_reports_in_seconds = time_between_silence_level_reports_in_seconds
        self.last_silence_report_time = time.monotonic()

    def get_level(self):
        return np.mean(np.abs(self.buffer.buffer))/np.iinfo(np.int16).max

    def process(self, input: IUnit.Input) -> State|None:
        t = time.monotonic()
        if self.time_between_silence_level_reports_in_seconds is not None:
            if t - self.last_silence_report_time > self.time_between_silence_level_reports_in_seconds:
                input.client.put(SilenceLevelReport(self.silence_level))
                self.last_silence_report_time = t

        if input.state.mic_state not in [MicState.Opening, MicState.Open, MicState.Recording]:
            return

        if self.buffer is None:
            self.buffer = SoundBuffer(self.silence_length_in_seconds)
        self.buffer.add(input.mic_data)
        level = self.get_level()

        if input.state.mic_state == MicState.Opening:
            if level < self.silence_level:
                self.buffer = None
                return State(MicState.Open)


        if input.state.mic_state == MicState.Open:
            if level > self.silence_level:
                self.buffer = None
                return State(MicState.Recording)

        if input.state.mic_state == MicState.Recording:
            if level < self.silence_level:
                self.buffer = None
                return State(MicState.Sending)



