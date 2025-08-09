import numpy as np


class SED:
    def __init__(
        self,
        thresholds: list[float] | None = None,
        index: list[int] | None = None,
        frame_size: int = 64,
        num_classes: int = 1,
        mutex: bool = False,
    ) -> None:
        self._thresholds = [-38.0, -41.0, -48.0] if thresholds is None else thresholds
        self._index = [1] if index is None else index
        self._frame_size = frame_size
        self._num_classes = num_classes
        self._mutex = mutex

        self._thresholds_lin = self.db_to_lin(self._thresholds)
        self._vad_init = 15

        if self.mutex:
            if self._num_classes <= 1:
                raise ValueError("num_classes must be greater than 1 when in mutex mode")
            if np.count_nonzero(self.index) > 1:
                raise ValueError("index must contain one one non-zero element when in mutex mode")
            self._max_class = self.num_classes - 1
        else:
            self._max_class = self.num_classes

        if len(self.index) > self._max_class:
            raise ValueError(f"index must not contain more than {self._max_class} elements")
        if any(x < 0 for x in self.index):
            raise ValueError("index must contain only positive elements")
        if any(x > self._max_class for x in self.index):
            raise ValueError(f"index elements must not be greater than {self._max_class}")

        self._index_nz = [x - 1 for x in self.index if x > 0]
        self._vad_cnt = self._vad_init

    @property
    def thresholds(self) -> list[float]:
        return self._thresholds

    @property
    def index(self) -> list[int]:
        return self._index

    @property
    def frame_size(self) -> int:
        return self._frame_size

    @property
    def num_classes(self) -> int:
        return self._num_classes

    @property
    def mutex(self) -> bool:
        return self._mutex

    def reset(self):
        self._vad_cnt = self._vad_init

    def execute_all(self, x: np.ndarray) -> np.ndarray:
        frames = x.shape[0]
        y = np.empty((frames, self.num_classes), dtype=np.float32)
        for idx in range(frames):
            y[idx] = self.execute(float(x[idx]))

        return y

    def execute(self, x: float) -> np.ndarray:
        if x > self._thresholds_lin[0]:
            self._vad_cnt = 0
        elif x > self._thresholds_lin[1]:
            self._vad_cnt -= 5
        elif x > self._thresholds_lin[2]:
            self._vad_cnt += 1
        else:
            self._vad_cnt += 2

        if self._vad_cnt < 0:
            self._vad_cnt = 0

        if self._vad_cnt >= self._vad_init:
            self._vad_cnt = self._vad_init

        if self._vad_cnt >= 10:
            value = 0.0
        elif self._vad_cnt > 0:
            value = 0.5
        else:
            value = 1.0

        out = np.zeros(self.num_classes, dtype=np.float32)
        out[self._index_nz] = value

        if self.mutex:
            out[-1] = 1 - value

        return out

    def db_to_lin(self, db: list[float]) -> list[float]:
        return [self.frame_size * 10 ** (x / 10) for x in db]
