import numpy as np

_COMPLEX_COMPONENTS = 2  # Real and imaginary parts


def _validate_stacked_array(array: np.ndarray) -> int:
    """Validate a stacked complex array and return the half-size.

    :param array: Array to validate
    :return: Half size of the last dimension
    :raises ValueError: If validation fails
    """
    last_dim_size = array.shape[-1]
    if last_dim_size % _COMPLEX_COMPONENTS != 0:
        raise ValueError("last dimension must be a multiple of 2")

    return last_dim_size // _COMPLEX_COMPONENTS


def stack_complex(unstacked: np.ndarray) -> np.ndarray:
    """Stack a complex array.

    A stacked array doubles the last dimension and organizes the data as:
        - first half is all the real data
        - second half is all the imaginary data
    :param unstacked: An nD array containing complex data
    :return: A stacked array
    :raises ValueError: If input validation fails
    """
    shape = list(unstacked.shape)
    shape[-1] *= _COMPLEX_COMPONENTS
    stacked = np.empty(shape, dtype=np.float32)

    half_size = unstacked.shape[-1]
    stacked[..., :half_size] = np.real(unstacked)
    stacked[..., half_size:] = np.imag(unstacked)

    return stacked


def unstack_complex(stacked: np.ndarray) -> np.ndarray:
    """Unstack a stacked complex array.

    :param stacked: An nD array where the last dimension contains stacked complex data in which the first half
        is all the real data and the second half is all the imaginary data
    :return: An unstacked complex array
    :raises ValueError: If input validation fails
    """
    half_size = _validate_stacked_array(stacked)

    real_part = stacked[..., :half_size]
    imag_part = stacked[..., half_size:]

    return real_part + 1j * imag_part


def stacked_complex_real(stacked: np.ndarray) -> np.ndarray:
    """Get the real elements from a stacked complex array.

    :param stacked: An nD array where the last dimension contains stacked complex data in which the first half
        is all the real data and the second half is all the imaginary data
    :return: The real elements
    :raises ValueError: If input validation fails
    """
    half_size = _validate_stacked_array(stacked)
    return stacked[..., :half_size]


def stacked_complex_imag(stacked: np.ndarray) -> np.ndarray:
    """Get the imaginary elements from a stacked complex array.

    :param stacked: An nD array where the last dimension contains stacked complex data in which the first half
        is all the real data and the second half is all the imaginary data
    :return: The imaginary elements
    :raises ValueError: If input validation fails
    """
    half_size = _validate_stacked_array(stacked)
    return stacked[..., half_size:]
