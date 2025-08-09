import numpy as np
import torch

from .transform_types import Overlap


class ForwardTransform:
    def __init__(
        self,
        length: int = 256,
        overlap: int = 64,
        bin_start: int = 1,
        bin_end: int = 128,
        ttype: str = "stft-olsa-hanns",
    ) -> None:
        self._length = length
        self._overlap = overlap
        self._bin_start = bin_start
        self._bin_end = bin_end
        self._ttype = ttype

        # Note: init is always on CPU; will move if needed in execute_all() or execute()
        self._device = torch.device("cpu")

        if self.length % self.overlap:
            raise ValueError("overlap is not a factor of length")

        if self.bin_start >= self.length:
            raise ValueError("bin_start is greater than length")

        if self.bin_end >= self.length:
            raise ValueError("bin_end is greater than length")

        if self.bin_start >= self.bin_end:
            raise ValueError("bin_start is greater than bin_end")

        self._num_overlap = self.length // self.overlap
        self._overlap_indices = torch.empty((self._num_overlap, self.length), dtype=torch.int)
        for n in range(self._num_overlap):
            start = self.overlap * (n + 1)
            self._overlap_indices[n, :] = torch.floor(torch.tensor(range(start, start + self.length)) % self.length)

        self._bin_indices = list(range(self.bin_start, self.bin_end + 1))
        self._bins = self.bin_end - self.bin_start + 1

        self._window, self._overlap_type = self._parse_ttype()

        if self._overlap_type not in (Overlap.TDAC, Overlap.TDAC_CO) and len(self._window) != self.length:
            raise RuntimeError("window is not of length length")

        self.fold_params = {
            "kernel_size": (self.length, 1),
            "stride": (self.overlap, 1),
        }

        self._xs = torch.zeros(self.length, dtype=torch.float32, device=self.device)
        self._overlap_count = 0

    def _parse_ttype(self) -> tuple[torch.Tensor, Overlap]:
        from .transform_types import Overlap
        from .transform_types import Window
        from .transform_types import window

        if self.ttype == "stft-olsa-hanns" or self.ttype == "stft-ols" or self.ttype == "stft-olsa":
            w = window(Window.NONE, self.length, self.overlap)
            w = w * 2 / self.length
            return w, Overlap.OLS

        if self.ttype == "stft-olsa-hann" or self.ttype == "stft-olsa-hannd":
            w = window(Window.HANN, self.length, self.overlap)
            w = w * 2 / torch.sum(w)
            return w, Overlap.OLS

        if self.ttype == "stft-olsa-hammd":
            w = window(Window.HAMM, self.length, self.overlap)
            w = w * 2 / torch.sum(w)
            return w, Overlap.OLS

        if self.ttype == "stft-ola":
            w = window(Window.NONE, self.length, self.overlap)
            w = w * 2 / self.length
            return w, Overlap.OLA

        if self.ttype in ("tdac", "tdac-co"):
            self._overlap = self.length // 2
            k = torch.arange(0, self._overlap + 1)
            w = torch.exp(-1j * 2 * torch.pi / 8 * (2 * k + 1)) * torch.exp(-1j * 2 * torch.pi / (2 * self.length) * k)

            if self.ttype == "tdac":
                return w, Overlap.TDAC

            return w, Overlap.TDAC_CO

        raise ValueError(f"Unknown ttype: '{self.ttype}'")

    @property
    def length(self) -> int:
        return self._length

    @property
    def overlap(self) -> int:
        return self._overlap

    @property
    def bin_start(self) -> int:
        return self._bin_start

    @property
    def bin_end(self) -> int:
        return self._bin_end

    @property
    def ttype(self) -> str:
        return self._ttype

    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def bins(self) -> int:
        return self._bins

    @property
    def window(self) -> torch.Tensor:
        return self._window

    def frames(self, xt: torch.Tensor) -> int:
        return int(np.ceil(xt.shape[-1] / self.overlap))

    def reset(self) -> None:
        self._xs = torch.zeros(self.length, dtype=torch.float32, device=self.device)
        self._overlap_count = 0

    def _check_device(self, xt: torch.Tensor) -> None:
        if xt.device != self.device:
            self._device = xt.device
            self._window = self.window.to(self.device)
            self._xs = self._xs.to(self.device)

    def execute_all(self, xt: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Compute the multichannel, forward FFT of the time domain input.

        :param xt: Tensor of time domain data with dimensions [batch, samples]
        :return: Tuple containing frequency domain frame data and frame-based energy data
            yf: [batch, frames, bins]
            energy_t: [batch, frames]
        """
        from .transform_types import Overlap

        if xt.ndim != 1 and xt.ndim != 2:
            raise ValueError("Input must have 1 or 2 dimensions")

        self._check_device(xt)

        no_batch = xt.ndim == 1
        if no_batch:
            batches = 1
            samples = xt.shape[0]
        else:
            batches, samples = xt.shape

        frames = self.frames(xt)
        extra_samples = frames * self.overlap - samples

        if self._overlap_type == Overlap.OLA:
            xt_pad = torch.nn.functional.pad(
                input=xt.reshape((batches, samples)),
                pad=(0, extra_samples),
                mode="constant",
                value=0,
            )

            ytn = xt_pad.reshape(batches, frames, self.overlap)
            energy_t = torch.mean(torch.square(ytn), dim=-1)

            ytn = self.window.view(1, -1) * torch.concatenate(
                (
                    ytn,
                    torch.zeros(
                        (batches, frames, self.length - self.overlap),
                        dtype=xt.dtype,
                        device=self.device,
                    ),
                ),
                dim=-1,
            )
            if no_batch:
                ytn = ytn.squeeze()
                energy_t = energy_t.squeeze()

            yf = torch.fft.rfft(ytn, dim=-1, n=self.length)
        elif self._overlap_type == Overlap.OLS:
            xt_pad = torch.nn.functional.pad(
                input=xt.reshape((batches, samples)),
                pad=(self.length - self.overlap, extra_samples),
                mode="constant",
                value=0,
            )

            ytn = (
                torch.nn.functional.unfold(
                    xt_pad.unsqueeze(-1),
                    kernel_size=(self.length, 1),
                    padding=0,
                    dilation=1,
                    stride=(self.overlap, 1),
                )
                .reshape((batches, self.length, frames))
                .permute(0, 2, 1)
            )

            energy_t = torch.mean(torch.square(ytn), dim=-1)

            ytn = self.window.view(1, -1) * ytn
            if no_batch:
                ytn = ytn.squeeze()
                energy_t = energy_t.squeeze()

            yf = torch.fft.rfft(ytn, dim=-1, n=self.length)
        elif self._overlap_type in (Overlap.TDAC, Overlap.TDAC_CO):
            xt_pad = torch.nn.functional.pad(
                input=xt.reshape((batches, samples)),
                pad=(self.length - self.overlap, extra_samples),
                mode="constant",
                value=0,
            )

            ytn = (
                torch.nn.functional.unfold(
                    xt_pad.unsqueeze(-1),
                    kernel_size=(self.length, 1),
                    padding=0,
                    dilation=1,
                    stride=(self.overlap, 1),
                )
                .reshape((batches, self.length, frames))
                .permute(0, 2, 1)
            )

            energy_t = torch.mean(torch.square(ytn), dim=-1)
            yf = torch.fft.rfft(ytn, dim=-1, n=self.length, norm="ortho")
            yf = 1j * self.window[: self.overlap] * yf[..., : self.overlap] + self.window[1:] * yf[..., 1:]

            if no_batch:
                yf = yf.squeeze()
                energy_t = energy_t.squeeze()

            if self._overlap_type == Overlap.TDAC_CO:
                yf = torch.real(yf)
        else:
            raise ValueError(f"Unsupported overlap type: '{self._overlap_type}")

        yf = yf[..., self._bin_indices]

        return yf, energy_t

    def execute(self, xt: torch.Tensor) -> tuple[torch.Tensor, float]:
        """Compute the forward FFT of the time domain input.

        :param xt: Tensor of time domain data with dimensions [samples]
        :return: Tuple containing frequency domain frame data and frame-based energy data
            yf: [bins]
            energy_t: scalar
        """
        from .transform_types import Overlap

        if xt.ndim != 1:
            raise ValueError("Input must have 1 dimensions [bins]")

        if xt.shape[0] != self.overlap:
            raise ValueError(f"Input must have {self.overlap} samples")

        self._check_device(xt)

        if self._overlap_type == Overlap.OLA:
            ytn = self.window * torch.concatenate(
                (
                    xt,
                    torch.zeros(self.length - self.overlap, dtype=torch.float32, device=self.device),
                )
            )
            energy_t = torch.mean(torch.square(xt))
            tmp = torch.fft.rfft(ytn, n=self.length)
        elif self._overlap_type == Overlap.OLS:
            self._xs[self._overlap_indices[self._overlap_count, (self.length - self.overlap) : self.length]] = xt
            ytn = self._xs[self._overlap_indices[self._overlap_count, :]]
            energy_t = torch.mean(torch.square(ytn))
            ytn = self.window * ytn
            tmp = torch.fft.rfft(ytn, n=self.length)
            self._overlap_count = (self._overlap_count + 1) % self._num_overlap
        elif self._overlap_type in (Overlap.TDAC, Overlap.TDAC_CO):
            self._xs[self._overlap_indices[self._overlap_count, (self.length - self.overlap) : self.length]] = xt
            ytn = self._xs[self._overlap_indices[self._overlap_count, :]]
            energy_t = torch.mean(torch.square(ytn))
            tmp = torch.fft.rfft(ytn, n=self.length, norm="ortho")
            tmp = (
                1j * self.window[0 : self.overlap] * tmp[0 : self.overlap]
                + self.window[1 : self.overlap + 1] * tmp[1 : self.overlap + 1]
            )
            if self._overlap_type == Overlap.TDAC_CO:
                tmp = torch.real(tmp)
            self._overlap_count = (self._overlap_count + 1) % self._num_overlap
        else:
            raise ValueError(f"Unsupported overlap type: '{self._overlap_type}")

        yf = tmp[self._bin_indices]
        return yf, float(energy_t)
