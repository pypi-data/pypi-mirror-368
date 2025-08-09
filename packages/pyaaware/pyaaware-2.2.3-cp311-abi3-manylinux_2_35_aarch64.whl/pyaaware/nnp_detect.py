from enum import IntEnum
from typing import Any

import numpy as np


class State(IntEnum):
    LOOK_FOR_RISE = 0
    LOOK_FOR_FALL = 1
    HOLD = 2


class NNPDetect:
    def __init__(
        self,
        channels: int | None = None,
        classes: int | None = None,
        risethresh: list[float] | None = None,
        fallthresh: list[float] | None = None,
        riseframes: list[int] | None = None,
        fallframes: list[int] | None = None,
        hold: list[int] | None = None,
        smoothf: list[float] | None = None,
    ) -> None:
        self._channels = 1 if channels is None else channels
        self._classes = 1 if classes is None else classes
        self._risethresh = [0.5] if risethresh is None else risethresh
        self._fallthresh = [0.5] if fallthresh is None else fallthresh
        self._riseframes = [0] if riseframes is None else riseframes
        self._fallframes = [0] if fallframes is None else fallframes
        self._hold = [0] if hold is None else hold
        self._smoothf = [0.0] if smoothf is None else smoothf

        self._risethresh = self.extend_parameter(self._risethresh)
        self._fallthresh = self.extend_parameter(self._fallthresh)
        self._riseframes = self.extend_parameter(self._riseframes)
        self._fallframes = self.extend_parameter(self._fallframes)
        self._hold = self.extend_parameter(self._hold)
        self._smoothf = self.extend_parameter(self._smoothf)

        self._state = np.zeros((self.channels, self.classes), dtype=int)
        self._rise_cnt = np.zeros((self.channels, self.classes), dtype=int)
        self._fall_cnt = np.zeros((self.channels, self.classes), dtype=int)
        self._hold_cnt = np.zeros((self.channels, self.classes), dtype=int)
        self._detect = np.zeros((self.channels, self.classes), dtype=int)
        self._smooth = np.zeros((self.channels, self.classes), dtype=float)

    def extend_parameter(self, param: list[Any]) -> list[Any]:
        if len(param) == 1:
            return param * self.classes
        if len(param) != self.classes:
            raise ValueError("length of configuration parameter does not match 'classes'")
        return param

    @property
    def channels(self) -> int:
        return self._channels

    @property
    def classes(self) -> int:
        return self._classes

    @property
    def risethresh(self) -> list[float]:
        return self._risethresh

    @property
    def fallthresh(self) -> list[float]:
        return self._fallthresh

    @property
    def riseframes(self) -> list[int]:
        return self._riseframes

    @property
    def fallframes(self) -> list[int]:
        return self._fallframes

    @property
    def hold(self) -> list[int]:
        return self._hold

    @property
    def smoothf(self) -> list[float]:
        return self._smoothf

    def reset(self):
        self._state = np.zeros((self.channels, self.classes), dtype=int)
        self._rise_cnt = np.zeros((self.channels, self.classes), dtype=int)
        self._fall_cnt = np.zeros((self.channels, self.classes), dtype=int)
        self._hold_cnt = np.zeros((self.channels, self.classes), dtype=int)
        self._detect = np.zeros((self.channels, self.classes), dtype=bool)
        self._smooth = np.zeros((self.channels, self.classes), dtype=float)

    def execute_all(self, prob: np.ndarray, eof: np.ndarray) -> np.ndarray:
        if prob.ndim != 3:
            raise ValueError("prob should be a 3D array")

        channels, classes, frames = prob.shape
        if channels != self.channels or classes != self.classes:
            raise ValueError(f"prob should have dimensions: [{self.channels}, {self.classes}, frames]")

        if eof.ndim != 1 or eof.size != frames:
            raise ValueError("eof should be a 1d array with the same number of frames as prob")

        detect = np.empty((self.channels, self.classes, frames), dtype=int)
        for in_idx in range(frames):
            detect[:, :, in_idx] = self.execute(prob[:, :, in_idx], bool(eof[in_idx]))

        return detect

    def execute(self, prob: np.ndarray, eof: bool) -> np.ndarray:
        if prob.ndim != 2:
            raise ValueError("prob should be a 2D array")

        channels, classes = prob.shape
        if channels != self.channels or classes != self.classes:
            raise ValueError(f"prob should have dimensions: [{self.channels}, {self.classes}]")

        if not eof:
            return np.zeros((self.channels, self.classes), dtype=bool)

        for nci in range(self.classes):
            for chi in range(self.channels):
                self._smooth[chi, nci] = (
                    self.smoothf[nci] * self._smooth[chi, nci] + (1 - self._smoothf[nci]) * prob[chi, nci]
                )

                if self._state[chi, nci] == State.LOOK_FOR_RISE:
                    if self._smooth[chi, nci] > self.risethresh[nci]:
                        if self._rise_cnt[chi, nci] >= self.riseframes[nci]:
                            self._state[chi, nci] = State.LOOK_FOR_FALL
                            self._fall_cnt[chi, nci] = 0
                            self._hold_cnt[chi, nci] = 1
                        else:
                            self._rise_cnt[chi, nci] += 1
                    else:
                        self._rise_cnt[chi, nci] = 0

                elif self._state[chi, nci] == State.LOOK_FOR_FALL:
                    if self._smooth[chi, nci] < self.fallthresh[nci]:
                        if self._fall_cnt[chi, nci] >= self.fallframes[nci]:
                            if self._hold_cnt[chi, nci] >= self.hold[nci]:
                                self._state[chi, nci] = State.LOOK_FOR_RISE
                                self._rise_cnt[chi, nci] = 0
                                self._fall_cnt[chi, nci] = 0
                                self._hold_cnt[chi, nci] = 0
                            else:
                                self._state[chi, nci] = State.HOLD
                                self._hold_cnt[chi, nci] += 1
                        else:
                            self._fall_cnt[chi, nci] += 1
                            self._hold_cnt[chi, nci] += 1
                    else:
                        self._fall_cnt[chi, nci] = 0
                        self._hold_cnt[chi, nci] += 1

                elif self._state[chi, nci] == State.HOLD:
                    if self._hold_cnt[chi, nci] >= self.hold[nci]:
                        self._state[chi, nci] = State.LOOK_FOR_RISE
                        self._rise_cnt[chi, nci] = 0
                        self._fall_cnt[chi, nci] = 0
                        self._hold_cnt[chi, nci] = 0
                    else:
                        self._hold_cnt[chi, nci] += 1

                else:
                    raise RuntimeError("invalid state")

                self._detect[chi, nci] = int(self._hold_cnt[chi, nci] > 0)

        return self._detect
