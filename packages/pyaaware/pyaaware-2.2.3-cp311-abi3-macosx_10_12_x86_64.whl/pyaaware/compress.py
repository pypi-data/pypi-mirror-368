import numpy as np

_POWER_COMPRESSION_FACTOR = 0.3


def _reconstruct_complex(magnitude: np.ndarray, phase: np.ndarray) -> np.ndarray:
    """Reconstruct complex number from magnitude and phase.

    :param magnitude: Magnitude array
    :param phase: Phase array
    :return: Complex-valued array
    """
    real_part = magnitude * np.cos(phase)
    imag_part = magnitude * np.sin(phase)
    return real_part + 1j * imag_part


def power_compress(feature: np.ndarray) -> np.ndarray:
    """Compress a complex-valued feature.

    :param feature: A complex-valued array representing the feature.
    :return: A power-compressed complex-valued array.
    """
    magnitude = np.abs(feature)
    phase = np.angle(feature)
    compressed_magnitude = magnitude**_POWER_COMPRESSION_FACTOR
    return _reconstruct_complex(compressed_magnitude, phase)


def power_uncompress(feature: np.ndarray) -> np.ndarray:
    """Uncompress a power-compressed complex-valued feature.

    :param feature: A complex-valued array representing the power-compressed feature.
    :return: A power-uncompressed complex-valued array.
    """
    magnitude = np.abs(feature)
    phase = np.angle(feature)
    uncompressed_magnitude = magnitude ** (1.0 / _POWER_COMPRESSION_FACTOR)
    return _reconstruct_complex(uncompressed_magnitude, phase)
