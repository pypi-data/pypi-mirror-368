import numpy as np


def write_wav(name: str, audio: np.ndarray, sample_rate: int = 44100) -> None:
    """Write a WAV file.

    Args:
        name: Output filename (should end with .wav)
        audio: Audio data as 1D numpy array (mono only)
        sample_rate: Sample rate in Hz
    """
    # Only accept 1D arrays (mono audio)
    import struct

    if audio.ndim != 1:
        raise ValueError("Audio must be a 1D array (mono only)")

    audio_data = audio

    # Convert to 16-bit PCM
    if audio_data.dtype in [np.float32, np.float64]:
        # Floating point: clamp to [-1, 1] and scale to int16 range
        audio_data = np.clip(audio_data, -1.0, 1.0)
        audio_data = (audio_data * 32767).astype(np.int16)
    elif audio_data.dtype == np.int16:
        # Already int16, no conversion needed
        pass
    elif audio_data.dtype == np.int8:
        # 8-bit signed: range -128 to 127, scale to int16 range
        audio_data = (audio_data.astype(np.int32) * 32767 // 127).astype(np.int16)
    elif audio_data.dtype == np.uint8:
        # 8-bit unsigned: range 0 to 255, convert to signed then scale
        audio_data = ((audio_data.astype(np.int32) - 128) * 32767 // 127).astype(np.int16)
    elif audio_data.dtype == np.int32:
        # 32-bit signed: scale down to int16 range
        audio_data = (audio_data // 65536).astype(np.int16)
    elif audio_data.dtype == np.uint16:
        # 16-bit unsigned: convert to 16-bit signed
        audio_data = (audio_data.astype(np.int32) - 32768).astype(np.int16)
    elif audio_data.dtype == np.uint32:
        # 32-bit unsigned: convert to signed then scale down to int16 range
        audio_data = ((audio_data.astype(np.int64) - 2147483648) // 65536).astype(np.int16)
    else:
        # For any other type, try to convert to float first, then to int16
        audio_data = audio_data.astype(np.float64)
        # Normalize to [-1, 1] range based on the data range
        data_min, data_max = audio_data.min(), audio_data.max()
        if data_max > data_min:
            audio_data = 2.0 * (audio_data - data_min) / (data_max - data_min) - 1.0
        audio_data = np.clip(audio_data, -1.0, 1.0)
        audio_data = (audio_data * 32767).astype(np.int16)

    # WAV file parameters (mono only)
    num_channels = 1
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = len(audio_data) * 2  # 2 bytes per 16-bit sample

    with open(name, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))  # File size - 8
        f.write(b"WAVE")

        # fmt subchunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))  # Subchunk size
        f.write(struct.pack("<H", 1))  # Audio format (1 = PCM)
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", block_align))
        f.write(struct.pack("<H", bits_per_sample))

        # data subchunk
        f.write(b"data")
        f.write(struct.pack("<I", data_size))

        # Write audio data
        audio_bytes = audio_data.astype("<i2").tobytes()
        f.write(audio_bytes)
