from enum import Enum

import torch


class Overlap(Enum):
    OLA = "OLA"
    OLS = "OLS"
    TDAC = "TDAC"
    TDAC_CO = "TDAC_CO"


class Window(Enum):
    NONE = "none"
    HANN = "hann"
    HAMM = "hamm"
    W01 = "w01"
    HANN01 = "hann01"


def window(window_type: Window, length: int, overlap: int, periodic: bool = True) -> torch.Tensor:
    """Generate window

    :param window_type: Window type
    :param length: Transform length
    :param overlap: Overlap amount
    :param periodic: Window is periodic if True, otherwise it is symmetric
    :return: window [N]
    """
    sym = not periodic

    if window_type == Window.NONE:
        return torch.ones(length, dtype=torch.float32)

    if window_type == Window.HANN:
        return torch.signal.windows.hann(M=length, sym=sym, dtype=torch.float32)

    if window_type == Window.HAMM:
        return torch.signal.windows.hamming(M=length, sym=sym, dtype=torch.float32)

    if window_type == Window.W01:
        if not (length / overlap) % 2:
            return torch.concatenate(
                (
                    torch.zeros(length // 2, dtype=torch.float32),
                    torch.ones(length // 2, dtype=torch.float32),
                )
            )
        else:
            return torch.concatenate(
                (
                    torch.zeros(length - overlap, dtype=torch.float32),
                    torch.ones(overlap, dtype=torch.float32),
                )
            )

    if window_type == Window.HANN01:
        if (length // 4) < overlap:
            raise ValueError(f"{window_type} window requires R <= N/4")
        if length / 2 % 2:
            raise ValueError(f"{window_type} window requires N to be even")
        return torch.concatenate(
            (
                torch.zeros(length // 2, dtype=torch.float32),
                torch.signal.windows.hann(M=length // 2, sym=sym, dtype=torch.float32),
            )
        )

    raise ValueError(f"Unknown window type: {window_type}")
