from typing import Any

import numpy as np

from .feature_generator_parser import parse_feature_mode


class FeatureGenerator:
    def __init__(self, feature_mode: str, truth_parameters: dict[str, dict[str, int | None]] | None = None) -> None:
        parsed = parse_feature_mode(feature_mode)
        self._feature_mode = parsed.feature_mode
        self._eftransform = parsed.eftransform
        self._ftransform = parsed.ftransform
        self._itransform = parsed.itransform
        self._bin_start = parsed.bin_start
        self._bin_end = parsed.bin_end
        self._bins = parsed.bins
        self._bwin = parsed.bwin
        self._twin = parsed.twin
        self._decimation = parsed.decimation
        self._stride = parsed.stride
        self._step = parsed.step
        self._cmptype = parsed.cmptype
        self._bandedge = parsed.bandedge
        self._num_bandedges = parsed.num_bandedges
        self._feature_parameters = parsed.feature_parameters
        self._hbandsize = parsed.hbandsize

        if truth_parameters is None:
            self._truth_parameters = {}
        else:
            self._truth_parameters = truth_parameters

        self._total_truth_parameters = sum(
            [x for category in self._truth_parameters.values() for x in category.values() if x is not None]
        )

        self._decimation_count = 0
        self._stride_count = 0
        self._step_count = 0
        self._feature_history = np.zeros((self.stride, self.feature_parameters), dtype=np.float32)
        self._truth_decimation_history = np.zeros((self.decimation, self.total_truth_parameters), dtype=np.float32)
        self._truth_history = np.zeros((self.stride, self.total_truth_parameters), dtype=np.float32)

        self._eof = False
        self._feature = np.empty((self.stride, self.feature_parameters), dtype=np.float32)
        self._truth = np.empty((self.stride, self.total_truth_parameters), dtype=np.float32)

    @property
    def feature_mode(self) -> str:
        return self._feature_mode.name

    @property
    def total_truth_parameters(self) -> int:
        return self._total_truth_parameters

    @property
    def bin_start(self) -> int:
        return self._bin_start

    @property
    def bin_end(self) -> int:
        return self._bin_end

    @property
    def feature_parameters(self) -> int:
        return self._feature_parameters

    @property
    def stride(self) -> int:
        return self._stride

    @property
    def step(self) -> int:
        return self._step

    @property
    def is_sov(self) -> int:
        return self._stride != self._step

    @property
    def decimation(self) -> int:
        return self._decimation

    @property
    def feature_size(self) -> int:
        return self.ftransform_overlap * self.decimation * self.stride

    @property
    def ftransform_length(self) -> int:
        return self._ftransform.length

    @property
    def ftransform_overlap(self) -> int:
        return self._ftransform.overlap

    @property
    def ftransform_ttype(self) -> str:
        return self._ftransform.ttype

    @property
    def eftransform_length(self) -> int:
        return self._eftransform.length

    @property
    def eftransform_overlap(self) -> int:
        return self._eftransform.overlap

    @property
    def eftransform_ttype(self) -> str:
        return self._eftransform.ttype

    @property
    def itransform_length(self) -> int:
        return self._itransform.length

    @property
    def itransform_overlap(self) -> int:
        return self._itransform.overlap

    @property
    def itransform_ttype(self) -> str:
        return self._itransform.ttype

    def reset(self) -> None:
        self._decimation_count = 0
        self._stride_count = 0
        self._step_count = 0
        self._feature = np.zeros((self.stride, self.feature_parameters), dtype=np.float32)
        self._truth = np.zeros((self.stride, self.total_truth_parameters), dtype=np.float32)
        self._eof = False
        self._feature_history = np.zeros((self.feature_parameters, 1, self.stride), dtype=np.float32)
        self._truth_decimation_history = np.zeros((self.total_truth_parameters, 1, self.decimation), dtype=np.float32)
        self._truth_history = np.zeros((self.total_truth_parameters, 1, self.stride), dtype=np.float32)

    def execute_all(
        self,
        xf: np.ndarray,
        truth_in: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[np.ndarray, dict[str, dict[str, Any]] | None]:
        if xf.ndim != 2:
            raise ValueError("xf must be an 2-dimensional array")

        input_frames, bins = xf.shape

        if bins != self._bins:
            raise ValueError("bins dimension does not match configuration")

        if truth_in is not None:
            if truth_in.keys() != self._truth_parameters.keys():
                raise ValueError("truth_in does not match truth configuration")
            for category in truth_in:
                if truth_in[category].keys() != self._truth_parameters[category].keys():
                    raise ValueError("truth_in does not match truth configuration")

            for category in self._truth_parameters:
                for name, value in self._truth_parameters[category].items():
                    if value is not None:
                        if truth_in[category][name].ndim != 2:
                            raise ValueError(f"truth_in, '{category}: {name}', must be an 2-dimensional array")
                        if truth_in[category][name].shape[0] != input_frames:
                            raise ValueError(f"truth_in, '{category}: {name}', must have {input_frames} frames")
                        if truth_in[category][name].shape[1] != value:
                            raise ValueError(f"truth_in, '{category}: {name}', must have {value} parameters")

            flat_truth = np.concatenate(
                tuple(
                    truth_in[category][name]
                    for category in self._truth_parameters
                    for name, value in self._truth_parameters[category].items()
                    if value is not None
                ),
                axis=1,
            )
        else:
            flat_truth = None

        output_frames = input_frames // (self.step * self.decimation)

        feature = np.empty((output_frames, self.stride, self.feature_parameters), dtype=np.float32)
        truth = np.empty((output_frames, self.stride, self.total_truth_parameters), dtype=np.float32)

        output_frame = 0
        for input_frame in range(input_frames):
            if flat_truth is not None:
                self._execute(xf[input_frame], flat_truth[input_frame])
            else:
                self._execute(xf[input_frame])

            if self.eof():
                feature[output_frame] = self.feature()
                truth[output_frame] = self.truth()
                output_frame += 1

        truth_out: dict[str, Any] | None = None
        if truth_in is not None:
            truth_out = {}
            start_index = 0
            for category in self._truth_parameters:
                truth_out[category] = {}
                for name, value in self._truth_parameters[category].items():
                    if value is not None:
                        truth_out[category][name] = truth[:, :, start_index : start_index + value]
                        start_index += value
                    else:
                        truth_out[category][name] = truth_in[category][name]

        return feature, truth_out

    def _execute(self, xf: np.ndarray, truth_in: np.ndarray | None = None) -> None:
        if xf.ndim != 1:
            raise ValueError("xf must be a 1-dimensional array")

        bins = xf.shape[0]
        if bins != self._bins:
            raise ValueError("bins dimension does not match configuration")

        self._feature = np.zeros((self.stride, self.feature_parameters), dtype=np.float32)
        self._truth = np.zeros((self.stride, self.total_truth_parameters), dtype=np.float32)
        self._eof = False

        if truth_in is not None:
            if truth_in.ndim != 1:
                raise ValueError("truth_in must be a 1-dimensional array")
            if truth_in.shape[0] != self.total_truth_parameters:
                raise ValueError("truth_in shape does not match configuration")

        if truth_in is not None:
            self._truth_decimation_history[self._decimation_count] = truth_in

        if (self._decimation_count + 1) % self.decimation == 0:
            if truth_in is not None:
                self._truth_history[self._stride_count] = np.max(self._truth_decimation_history, axis=0)

            self._feature_history[self._stride_count] = self._compute_feature(xf)

            if (self._step_count + 1) % self.step == 0:
                idx = range(self._stride_count + 1 - self.stride, self._stride_count + 1)
                self._feature = self._feature_history[idx]

                if truth_in is not None:
                    self._truth = self._truth_history[idx]

                self._eof = True

            self._stride_count = (self._stride_count + 1) % self.stride
            self._step_count = (self._step_count + 1) % self.step

        self._decimation_count = (self._decimation_count + 1) % self.decimation

    def _compute_feature(self, xf: np.ndarray) -> np.ndarray:
        if self._twin == "hann":
            tmp1 = xf / 2
            tmp2 = xf / 4
            xfw = (
                tmp1[: self._bins]
                - np.append(tmp2[1 : self._bins], np.conj(tmp2[self._bins - 2]))
                - np.append(np.conj(tmp2[1]), tmp2[: self._bins - 1])
            )
        elif self._twin == "none":
            xfw = xf
        else:
            raise ValueError("Invalid feature mode")

        if self._bwin == "tri":
            xfhe = np.real(xfw * np.conj(xfw))
            bando = np.zeros(self._num_bandedges, dtype=np.float32)
            for bi in range(self._num_bandedges - 1):
                for bj in range(self._hbandsize[bi + 1]):
                    tweight = bj / self._hbandsize[bi + 1]
                    bdidx = self._bandedge[bi] + bj - self.bin_start
                    bando[bi] = bando[bi] + xfhe[bdidx] * (1 - tweight)
                    bando[bi + 1] = bando[bi + 1] + xfhe[bdidx] * tweight

            if self._hbandsize[-1] > 0:
                for bj in range(self._hbandsize[-1]):
                    tweight = bj / self._hbandsize[-1]
                    bdidx = self._bandedge[-1] + bj - self.bin_start
                    bando[-1] = bando[-1] + xfhe[bdidx] * (1 - tweight)

            if self._hbandsize[0] > 0:
                for bj in range(self._hbandsize[0], 0, -1):
                    tweight = bj / (self._hbandsize[0] + 1)
                    bando[0] = bando[0] + xfhe[bj - 1] * tweight

            if self._bandedge[0] <= self.bin_start:
                bando[0] = bando[0] * 2

            if self._bandedge[-1] >= self.bin_end:
                bando[-1] = bando[-1] * 2

        elif self._bwin == "rect":
            raise ValueError("Invalid feature mode")

        elif self._bwin == "none":
            if self._cmptype in ("none", "plcd3", "plcd3p"):
                bando = xfw
            elif self._cmptype in ("cbrte", "loge"):
                bando = xfw * np.conj(xfw)
            else:
                raise ValueError("Invalid feature mode")

        else:
            raise ValueError("Invalid feature mode")

        if self._cmptype == "cbrte":
            feature = np.cbrt(np.real(bando))
        elif self._cmptype == "loge":
            feature = np.log(np.real(bando) * 2**16 + 2**-46)
        elif self._cmptype == "plcd3":
            cmag = np.power(np.abs(bando), 0.3)
            if self.ftransform_ttype == "tdac-co":
                feature = cmag
            else:
                phase = np.angle(bando)
                feature = np.concatenate((cmag * np.cos(phase), cmag * np.sin(phase)))
        elif self._cmptype == "plcd3p":
            cmag = np.power(np.abs(bando), 0.3)
            if self.ftransform_ttype == "tdac-co":
                feature = cmag
            else:
                phase = np.angle(bando)
                feature = np.concatenate((cmag, phase))
        elif self._cmptype == "none":
            if self.ftransform_ttype == "tdac-co":
                feature = np.real(bando)
            else:
                feature = np.concatenate((np.real(bando), np.imag(bando)))
        else:
            raise ValueError("Invalid feature mode")

        feature.clip(-(2**15), 2**15 - 1, out=feature)
        return feature

    def eof(self) -> bool:
        return self._eof

    def feature(self) -> np.ndarray:
        return self._feature

    def truth(self) -> np.ndarray:
        return self._truth
