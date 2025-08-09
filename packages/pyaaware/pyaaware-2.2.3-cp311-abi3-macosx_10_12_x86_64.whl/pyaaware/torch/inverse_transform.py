import torch

from .transform_types import Overlap


class InverseTransform:
    def __init__(
        self,
        length: int = 256,
        overlap: int = 64,
        bin_start: int = 1,
        bin_end: int = 128,
        ttype: str = "stft-olsa-hanns",
        gain: float = 1,
        trim: bool = True,
    ) -> None:
        from math import sqrt

        self._length = length
        self._overlap = overlap
        self._bin_start = bin_start
        self._bin_end = bin_end
        self._ttype = ttype
        self._gain = gain

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

        self._real_mode = self.bin_end <= self.length // 2
        self._cj_indices = list(range(self.length // 2 + 1, self.length))
        self._i_indices = list(range((self.length + 1) // 2 - 1, 0, -1))
        self._ob_indices = list(range(self.length - self.overlap, self.length))
        self._bin_indices = list(range(self.bin_start, self.bin_end + 1))
        self._bins = self.bin_end - self.bin_start + 1

        self._padding_needed = True

        self._window, self._overlap_type = self._parse_ttype()

        if self._overlap_type not in (Overlap.TDAC, Overlap.TDAC_CO) and len(self._window) != self.length:
            raise RuntimeError("window is not of length length")

        # Check if in sub-bin mode (feature not full bin, thus are zeroed out for transforms)
        if self._ttype in ("tdac", "tdac-co"):
            self._partial_bin = self._bin_start > 0 or self._bin_end < self.length // 2 - 1
            # Full TDAC has bins 0:floor(length/2)-1, must be even
            self._last_full_bin = self.length // 2 - 1
        else:
            self._partial_bin = self._bin_start > 0 or self._bin_end < self.length // 2
            # Full FFT has bins 0:floor(length/2)
            self._last_full_bin = self.length // 2

        self.fold_params = {
            "kernel_size": (self.length, 1),
            "stride": (self.overlap, 1),
        }

        if self._padding_needed:
            self._trim = trim
        else:
            self._trim = False

        self._sqrt_N = sqrt(self.length)
        self._sqrt_eighth = sqrt(1 / 8)

        self._xfs = torch.zeros(self.length, dtype=torch.complex64, device=self.device)
        self._pyo = torch.zeros(self.length, dtype=torch.float32, device=self.device)

    def _parse_ttype(self) -> tuple[torch.Tensor, Overlap]:
        from .transform_types import Window
        from .transform_types import window

        if self.ttype == "stft-olsa-hanns":
            w = window(Window.HANN01, self.length, self.overlap)
            itr_user_gain = self.length / 2
            return self._scale_window(itr_user_gain, w), Overlap.OLA

        if self.ttype == "stft-ols":
            w = window(Window.NONE, self.length, self.overlap)
            itr_user_gain = self.length**2 / self.overlap / 2
            self._padding_needed = False
            return self._scale_window(itr_user_gain, w), Overlap.OLS

        if self.ttype == "stft-olsa":
            w = window(Window.W01, self.length, self.overlap)
            itr_user_gain = self.length / 2
            return self._scale_window(itr_user_gain, w), Overlap.OLA

        if self.ttype == "stft-olsa-hann":
            w = window(Window.NONE, self.length, self.overlap)
            itr_user_gain = self.length / 2
            return self._scale_window(itr_user_gain, w), Overlap.OLA

        if self.ttype == "stft-olsa-hannd":
            w = window(Window.HANN, self.length, self.overlap)
            itr_user_gain = self.length / 3
            return self._scale_window(itr_user_gain, w), Overlap.OLA

        if self.ttype == "stft-olsa-hammd":
            w = window(Window.HAMM, self.length, self.overlap)
            itr_user_gain = self.length / 2.72565243
            return self._scale_window(itr_user_gain, w), Overlap.OLA

        if self.ttype == "stft-ola":
            w = window(Window.NONE, self.length, self.overlap)
            itr_user_gain = self.length**2 / self.overlap / 2
            self._padding_needed = False
            return self._scale_window(itr_user_gain, w), Overlap.OLA

        if self.ttype in ("tdac", "tdac-co"):
            self._overlap = self.length // 2
            self._real_mode = False

            k = torch.arange(1, self.overlap)
            w = (
                torch.conj(
                    torch.exp(-1j * 2 * torch.pi / 8 * (2 * k + 1))
                    * torch.exp(-1j * 2 * torch.pi / (2 * self.length) * k)
                )
                / 4
            )

            if self.ttype == "tdac":
                return w, Overlap.TDAC
            return w, Overlap.TDAC_CO

        raise ValueError(f"Unknown ttype: '{self.ttype}'")

    def _scale_window(self, itr_user_gain: float, w: torch.Tensor) -> torch.Tensor:
        wdc_gain = torch.sum(w)
        o_gain = 1 / (self.gain * wdc_gain / self.overlap) * itr_user_gain
        return w * o_gain

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
    def gain(self) -> float:
        return self._gain

    @property
    def trim(self) -> bool:
        return self._trim

    @property
    def device(self) -> torch.device:
        return self._device

    @property
    def bins(self) -> int:
        return self._bins

    @property
    def window(self) -> torch.Tensor:
        return self._window

    def reset(self) -> None:
        self._xfs = torch.zeros(self.length, dtype=torch.complex64, device=self.device)
        self._pyo = torch.zeros(self.length, dtype=torch.float32, device=self.device)

    def _check_device(self, xf: torch.Tensor) -> None:
        if xf.device != self.device:
            self._device = xf.device
            self._window = self.window.to(self.device)
            self._pyo = self._pyo.to(self.device)
            self._xfs = self._xfs.to(self.device)

    def execute_all(self, xf: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Compute the multichannel, real, inverse FFT of the frequency domain input.

        :param xf: Tensor of frequency domain data with dimensions [batch, frames, bins]
        :return: Tuple containing time domain sample data and frame-based energy data
            yt: [batch, samples]
            energy_t: [batch, frames]
        """
        from .transform_types import Overlap

        if xf.ndim != 2 and xf.ndim != 3:
            raise ValueError("Input must have 2 dimensions [frames, bins] or 3 dimensions [batch, frames, bins]")

        self._check_device(xf)

        no_batch = xf.ndim == 2

        if self._padding_needed:
            padding_samples = self.length - self.overlap
            padding_frames = padding_samples // self.overlap
        else:
            padding_samples = 0
            padding_frames = padding_samples // self.overlap

        xf_pad = torch.nn.functional.pad(xf, (0, 0, 0, padding_frames), mode="constant", value=0)
        if no_batch:
            batch = 1
            frames, bins = xf_pad.shape
        else:
            batch, frames, bins = xf_pad.shape

        if bins != self.bins:
            raise ValueError(f"Input must have {self.bins} bins [batch, frames, bins]")

        samples = frames * self.overlap

        if self._partial_bin:
            if no_batch:
                zero = torch.zeros(
                    (frames, self._last_full_bin + 1),
                    dtype=xf_pad.dtype,
                    device=self.device,
                )
            else:
                zero = torch.zeros(
                    (batch, frames, self._last_full_bin + 1),
                    dtype=xf_pad.dtype,
                    device=self.device,
                )
            # TODO: may need to use clone to keep gradients correct
            zero[..., self._bin_indices] = xf_pad
            xf_pad = zero

        if self._overlap_type == Overlap.OLA:
            # Multichannel, real, inverse FFT, norm='backward' normalizes by 1/n
            yt = torch.fft.irfft(xf_pad, dim=-1, n=self.length, norm="backward")

            # multichannel window, torch.tensor expands over [batch, frames]
            yt = yt * self.window.view(1, -1) if no_batch else yt * self.window.view(1, 1, -1)

            # Use nn.fold() to apply overlap-add
            yt = yt.permute(1, 0) if no_batch else yt.permute(0, 2, 1)
            expected_output_signal_len = self.length + self.overlap * (frames - 1)
            yt = torch.nn.functional.fold(yt, output_size=(expected_output_signal_len, 1), **self.fold_params)
            if no_batch:
                yt = yt.reshape(-1)
                yt = yt[:samples]
            else:
                yt = yt.reshape(yt.shape[0], -1)
                yt = yt[:, :samples]

        elif self._overlap_type == Overlap.OLS:
            # Multichannel, real, inverse FFT, norm='backward' normalizes by 1/n
            yt = torch.fft.irfft(xf_pad, dim=-1, n=self.length, norm="backward")

            # Multichannel window, torch.tensor expands over [batch, frames]
            if no_batch:
                yt = yt * self.window.view(1, -1)
                yt = yt[:, self._ob_indices]
                yt = yt.reshape(-1)
            else:
                yt = yt * self.window.view(1, 1, -1)
                yt = yt[:, :, self._ob_indices]
                yt = yt.reshape(yt.shape[0], -1)

        elif self._overlap_type in (Overlap.TDAC, Overlap.TDAC_CO):
            # Create buffer for complex input to real inverse FFT which wants [batch, frames, length//2+1]
            # note xf_pad already expanded to full-bin, but TDAC full-bin is always one less, i.e. length//2
            if no_batch:
                tdx = torch.zeros((frames, self.overlap + 1), dtype=xf_pad.dtype, device=self.device)
            else:
                tdx = torch.zeros((batch, frames, self.overlap + 1), dtype=xf_pad.dtype, device=self.device)
            if self._overlap_type == Overlap.TDAC:
                if no_batch:
                    tdx[:, 1 : self.overlap] = self.window.view(1, -1) * (
                        xf_pad[:, 0 : self.overlap - 1] - 1j * xf_pad[:, 1 : self.overlap]
                    )
                    tdx[:, 0] = self._sqrt_eighth * (xf_pad[:, 0].real + xf_pad[:, 0].imag)
                    tdx[:, self.overlap] = -self._sqrt_eighth * (
                        xf_pad[:, self._last_full_bin].real + xf_pad[:, self._last_full_bin].imag
                    )
                else:
                    tdx[:, :, 1 : self.overlap] = self.window.view(1, 1, -1) * (
                        xf_pad[:, :, 0 : self.overlap - 1] - 1j * xf_pad[:, :, 1 : self.overlap]
                    )
                    tdx[:, :, 0] = self._sqrt_eighth * (xf_pad[:, :, 0].real + xf_pad[:, :, 0].imag)
                    tdx[:, :, self.overlap] = -self._sqrt_eighth * (
                        xf_pad[:, :, self._last_full_bin].real + xf_pad[:, :, self._last_full_bin].imag
                    )
            else:
                if no_batch:
                    tdx[:, 1 : self.overlap] = (
                        2
                        * self.window.view(1, -1)
                        * (xf_pad[:, 0 : self.overlap - 1] - 1j * xf_pad[:, 1 : self.overlap])
                    )
                    tdx[:, 0] = 2 * self._sqrt_eighth * xf_pad[:, 0].real
                    tdx[:, self.overlap] = -2 * self._sqrt_eighth * xf_pad[:, self._last_full_bin].real
                else:
                    tdx[:, :, 1 : self.overlap] = (
                        2
                        * self.window.view(1, 1, -1)
                        * (xf_pad[:, :, 0 : self.overlap - 1] - 1j * xf_pad[:, :, 1 : self.overlap])
                    )
                    tdx[:, :, 0] = 2 * self._sqrt_eighth * xf_pad[:, :, 0].real
                    tdx[:, :, self.overlap] = -2 * self._sqrt_eighth * xf_pad[:, :, self._last_full_bin].real
            xf_pad = tdx

            # Multichannel, real, inverse FFT, norm='ortho' normalizes by 1/sqrt(n)
            yt = torch.fft.irfft(xf_pad, dim=-1, n=self.length, norm="ortho")

            # Use nn.fold() to apply overlap-add
            yt = yt.permute(1, 0) if no_batch else yt.permute(0, 2, 1)
            expected_output_signal_len = self.length + self.overlap * (frames - 1)
            yt = torch.nn.functional.fold(yt, output_size=(expected_output_signal_len, 1), **self.fold_params)
            if no_batch:
                yt = yt.reshape(-1)
                yt = yt[:samples]
            else:
                yt = yt.reshape(yt.shape[0], -1)
                yt = yt[:, :samples]

        else:
            raise ValueError(f"Unsupported type: '{self.ttype}'")

        if self.trim:
            yt = yt[padding_samples:] if no_batch else yt[:, padding_samples:]

        if no_batch:
            energy_t = torch.mean(torch.square(yt).reshape(-1, self.overlap), dim=-1)
        else:
            energy_t = torch.mean(torch.square(yt).reshape(yt.shape[0], -1, self.overlap), dim=-1)

        return yt, energy_t

    def execute(self, xf: torch.Tensor) -> tuple[torch.Tensor, float]:
        """Compute the real, inverse FFT of the frequency domain input.

        :param xf: Tensor of frequency domain data with dimensions [bins]
        :return: Tuple containing time domain sample data and frame-based energy data
            yt: [samples]
            energy_t: [frames]
        """
        from .transform_types import Overlap

        if xf.ndim != 1:
            raise ValueError("Input must have 1 dimensions [bins]")

        if xf.shape[0] != self.bins:
            raise ValueError(f"Input must have {self.bins} bins")

        self._check_device(xf)

        self._xfs[self._bin_indices] = xf
        if self._real_mode:
            self._xfs[self._cj_indices] = torch.conj(self._xfs[self._i_indices])

        if not self.length % 2:
            self._xfs[self.length // 2].imag = 0  # type: ignore[assignment]

        if self._overlap_type == Overlap.OLA:
            tmp = self.window * torch.fft.irfft(self._xfs, n=self.length, norm="backward") + self._pyo
            self._pyo[0 : (self.length - self.overlap)] = tmp[self.overlap :]
            yt = tmp[0 : self.overlap]
        elif self._overlap_type == Overlap.OLS:
            tmp = self.window * torch.fft.irfft(self._xfs, n=self.length, norm="backward")
            yt = tmp[self._ob_indices]
        elif self._overlap_type in (Overlap.TDAC, Overlap.TDAC_CO):
            if self._overlap_type == Overlap.TDAC:
                self._xfs[self.length // 2] = -self._sqrt_eighth * (
                    self._xfs[self.length // 2 - 1].real + self._xfs[self.length // 2 - 1].imag
                )
                for n in range(self.length // 2 - 1, 0, -1):
                    self._xfs[n] = self.window[n - 1] * (self._xfs[n - 1] - 1j * self._xfs[n])
                self._xfs[0] = self._sqrt_eighth * (self._xfs[0].real + self._xfs[0].imag)
                for n in range(self.length // 2, self.length):
                    self._xfs[n] = torch.conj(self._xfs[self.length - n])
            else:
                self._xfs[self.length // 2] = -2 * self._sqrt_eighth * self._xfs[self.length // 2 - 1].real
                for n in range(self.length // 2 - 1, 0, -1):
                    self._xfs[n] = 2 * self.window[n - 1] * (self._xfs[n - 1] - 1j * self._xfs[n])
                self._xfs[0] = 2 * self._sqrt_eighth * self._xfs[0].real
                for n in range(self.length // 2, self.length):
                    self._xfs[n] = torch.conj(self._xfs[self.length - n])

            tmp = torch.real(torch.fft.irfft(self._xfs, n=self.length, norm="ortho")) + self._pyo
            self._pyo[0 : (self.length - self.overlap)] = tmp[self.overlap :]
            yt = tmp[0 : self.overlap]
        else:
            raise ValueError(f"Unsupported overlap type: '{self._overlap_type}'")

        energy_t = torch.mean(torch.square(yt))
        return yt, float(energy_t)
