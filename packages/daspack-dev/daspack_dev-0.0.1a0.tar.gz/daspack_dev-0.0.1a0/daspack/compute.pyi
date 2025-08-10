# daspack/compute.pyi
from __future__ import annotations

import numpy as np
import numpy.typing as npt
from typing import Literal, Tuple, Union, List
from numpy.typing import NDArray

__all__ = ["DASCoder", "Quantizer"]
# daspack.pyi

class Quantizer:
    """
    Quantizer type for encoding DASPack streams.

    Parameters
    ----------
    Uniform : step : float
        Uniform scalar quantizer with given step size (float64 arrays).
    Lossless : None
        Lossless quantizer for integer arrays (int32).
    """

    @staticmethod
    def Uniform(step: float) -> Quantizer: ...
    @staticmethod
    def Lossless() -> Quantizer: ...

class DASCoder:
    """
    High-level encoder/decoder for DASPack bitstreams.

    Parameters
    ----------
    threads : int, default=1
        Number of threads to use for compression/decompression.
    """

    def __init__(self, threads: int = 1) -> None: ...
    def encode(
        self,
        data: np.ndarray,
        quantizer: Quantizer,
        blocksize: Tuple[int, int] = (1000, 1000),
        levels: int = 1,
        order: int = 1,
    ) -> bytes:
        """
        Encode a 2D NumPy array to a DASPack stream.

        Parameters
        ----------
        data : ndarray
            2D array to encode.
            Must be float64 for Uniform, int32 for Lossless.
        quantizer : Quantizer
            Quantizer to use (Uniform or Lossless).
        blocksize : (int, int), default=(1000, 1000)
            Compression block size.
        levels : int, default=1
            Predictor levels in both dimensions.
        order : int, default=1
            Prediction order.

        Returns
        -------
        bytes
            Encoded DASPack stream.
        """
        ...

    def decode(self, stream: bytes) -> np.ndarray:
        """
        Decode a DASPack stream into a NumPy array.

        The array dtype is inferred from the bitstream:
        float64 for Uniform quantizer, int32 for Lossless.

        Parameters
        ----------
        stream : bytes
            Encoded DASPack stream.

        Returns
        -------
        ndarray
            2D NumPy array with shape and dtype restored from the stream.
        """
        ...

def fwd_dwt_txfm_2d(data: npt.NDArray[np.int32]) -> npt.NDArray[np.int32]:
    """
    Perform the forward biorthogonal 5/3 transform with a lifting scheme.
    Ensures lossless reconstruction.
    """
    pass

def inv_dwt_txfm_2d(data: npt.NDArray[np.int32]) -> npt.NDArray[np.int32]:
    """
    Perform the inverse biorthogonal 5/3 transform with a lifting scheme.
    Ensures lossless reconstruction.
    """
    pass

def predict_block(
    data: npt.NDArray[np.int32], levels: int, lpc_order: int
) -> Tuple[
    npt.NDArray[np.int32], npt.NDArray[np.float64], npt.NDArray[np.float64]
]:
    """
     Forward prediction for 2D data.

    Steps:
        1) Multi-level wavelet transform.
        2) Row-wise LPC on the LL subband.
        3) Column-wise LPC on the LL subband.

    Parameters
    ----------
    data : np.ndarray
        Input 2D data array.

    Returns
    -------
    tuple
        Tuple containing:
            - np.ndarray: Wavelet coefficients with residuals.
            - np.ndarray: LPC coefficients for each row.
            - np.ndarray: LPC coefficients for each column.
    """
    pass

def reconstruct_block(
    residual: npt.NDArray[np.int32],
    row_coefs: npt.NDArray[np.float64],
    col_coefs: npt.NDArray[np.float64],
    levels: int,
    lpc_order: int,
) -> npt.NDArray[np.int32]:
    """
    Reconstruct the original 2D data from residuals and LPC coefs.

    Steps:
        1) Column-wise inverse LPC.
        2) Row-wise inverse LPC.
        3) Inverse multi-level wavelet transform.

    Parameters
    ----------
    residual : np.ndarray
        Wavelet coefficients with residuals in the LL subband.
    row_coefs : np.ndarray
        LPC coefficients for each row.
    col_coefs : np.ndarray
        LPC coefficients for each column.
    levels : int
        Number of cascaded Wavelet Transforms
    lpc_order : int
        Order of the LPC filter.

    Returns
    -------
    np.ndarray
        Reconstructed 2D signal.
    """
    pass

def compress_data(data: npt.NDArray[np.int32]) -> npt.NDArray[np.uint8]:
    pass

def decompress_data(
    data: npt.NDArray[np.uint8], shape: Tuple[int, int]
) -> npt.NDArray[np.int32]:
    pass

def compress_block(
    data: npt.NDArray[np.int32],
    block_height: int,
    block_width: int,
    lx: int,
    lt: int,
    lpc_order: int,
    tail_cut: float,
) -> Tuple[
    List[npt.NDArray[np.uint8]],
    List[npt.NDArray[np.uint8]],
    List[npt.NDArray[np.uint8]],
]:
    """
    Compress a 2D integer array using block-based compression.

    Parameters:
        data: 2D array of int32 values to compress.
        block_height: Height of each block.
        block_width: Width of each block.
        lx: Horizontal context parameter.
        lt: Vertical context parameter.
        lpc_order: Order of the linear predictive coding.
        tail_cut: Threshold to cut off tail values.

    Returns:
        A tuple of three lists containing 1D uint8 arrays:
        (residuals, row coefficients, column coefficients).
    """
    ...

def decompress_block(
    residuals: List[npt.NDArray[np.uint8]],
    row_coefs: List[npt.NDArray[np.uint8]],
    col_coefs: List[npt.NDArray[np.uint8]],
    data_height: int,
    data_width: int,
    block_height: int,
    block_width: int,
    lx: int,
    lt: int,
    lpc_order: int,
    tail_cut: float,
) -> npt.NDArray[np.int32]:
    """
    Decompress block-compressed data back into the original 2D integer array.

    Parameters:
        residuals: List of 1D uint8 arrays representing block residuals.
        row_coefs: List of 1D uint8 arrays for LPC row coefficients.
        col_coefs: List of 1D uint8 arrays for LPC column coefficients.
        data_height: Original height of the data.
        data_width: Original width of the data.
        block_height: Height of each block.
        block_width: Width of each block.
        lx: Horizontal context parameter.
        lt: Vertical context parameter.
        lpc_order: Order of the linear predictive coding.
        tail_cut: Threshold to cut off tail values.

    Returns:
        A 2D int32 array representing the decompressed data.
    """
    ...

def encode_exp_golomb(
    data: npt.NDArray[np.int32], k: int
) -> npt.NDArray[np.uint8]:
    """Encode an array of integers using a k-exponential golomb code."""
    pass

def decode_exp_golomb(
    data: npt.NDArray[np.uint8], count: int, k: int
) -> npt.NDArray[np.int32]:
    """Decode using a k-exponential golomb code with exactly `count` values."""
    pass

def compress_residuals(
    data: npt.NDArray[np.int32], tail_cut: float
) -> npt.NDArray[np.uint8]:
    """
    Obtain a compressed representation of `data` by assuming
    a Laplace distribution in each row.
    """
    pass

def decompress_residuals(
    data: npt.NDArray[np.uint8], tail_cut: float
) -> npt.NDArray[np.int32]:
    """
    Obtain a compressed representation of `data` by assuming
    a Laplace distribution in each row.
    """
    pass
