from typing import Union, Tuple, List

import cupy as cp
import cupy.typing as cpt
import numpy as np
import numpy.typing as npt
from stss import st2d_cupy, util, st3d_cupy

import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format="%(asctime)s : %(levelname)s : %(module)s : %(message)s",
    datefmt="%I:%M:%S",
)
logger = logging.getLogger(__name__)


def structure_tensor(
    image: cpt.ArrayLike, 
    sigma: float, 
    ring_filter: bool = True, 
    rho: Union[None, float] = None, 
    out_S: Union[None,cpt.NDArray[cp.floating]] = None, 
    eig_decomp: bool = True, truncate: float = 4.0
) -> Tuple[cpt.NDArray[cp.floating], cpt.NDArray[cp.floating], cpt.NDArray[cp.floating]]:
    """Generalized structure tensor for 2D and 3D data.

    Arguments:
        image: cpt.ArrayLike
            A 2D or 3D array containing the image.
        sigma: float
            Derivative Gaussian filter size, correlated to feature size if ring_filter=True.
        ring_filter: bool
            If True, runs the algorithm version with ring filter instead of the integration filter
        rho: float
            Only if ring_filter=False. An integration scale corresponding to the size over the neighborhood in which the
            orientation is to be analysed.
        out_S: cpt.NDArray, optional
            A Numpy array in which to place the output elements of structure tensor S.
        eig_decomp: bool
            If True, the eigenvalues and eigenvectors of the structure tensor are computed.
        truncate: float
            Truncate the filter at this many standard deviations. Default is 4.0.

    Returns:
        S: cpt.NDArray
            An array containing elements of structure tensor.
            If image is 2D, with shape (3, volume.shape), containing (s_xx, s_yy, s_xy).
            If image is 3D, with shape (6, volume.shape), containing (s_xx, s_yy, s_zz, s_xy, s_xz, s_yz).
        val, vec: cpt.NDArray
            Optional eigenvectors and eigenvalues of the structure tensor if eig_decomp=True.
    Authors: papi@dtu.dk, 2023
    """

    if out_S is None:
        # Allocate S.
        if image.ndim == 2:
            S = cp.empty((3,) + image.shape, dtype=image.dtype)
        elif image.ndim == 3:
            S = cp.empty((6,) + image.shape, dtype=image.dtype)
        else:
            raise ValueError("Image must be 2D or 3D.")
    else:
        # S is already allocated.
        S = out_S

    if image.ndim == 2:
        S = st2d_cupy.structure_tensor_2d(image, sigma, ring_filter, rho, S, truncate)
        if eig_decomp:
            val, vec = st2d_cupy.eig_special_2d(S)
            return S, val, vec
        else:
            return S
    elif image.ndim == 3:

        S = st3d_cupy.structure_tensor_3d(image, sigma, ring_filter, rho, S, truncate)
        if eig_decomp:
            val, vec = st3d_cupy.eig_special_3d(S)
            return S, val, vec
        else:
            return S

    else:
        raise ValueError("Image must be 2D or 3D.")


def scale_space(
    image: cpt.ArrayLike,
    sigma_list: List[float],
    correctScale: bool = True,
    ring_filter: bool = True,
    rho_list: Union[None, List[float]] = None,
    gamma: float = 1.2,
    truncate: float = 4.0,
) -> Tuple[cpt.NDArray[cp.floating], cpt.NDArray[cp.floating], cpt.NDArray[cp.floating], cpt.NDArray[cp.floating]]:
    """Structure tensor scale space for 2D and 3D data. Returns a single structure tensor result for each pixel,
    chosen based on the scale that returns the highest trace of the structure tensor matrix.

     Arguments:
        image: cpt.ArrayLike
            A 2D or 3D array containing the image.
        sigma: list[float]
            List of derivative Gaussian filter sizes, correlated to feature size if ring_filter=True.
        correctScale: bool
            If True, the scale values are corrected to better reflect the feature size.
            Set to False for easier scale range selection.
        ring_filter: bool
            If True, runs the algorithm version with ring filter instead of the integration filter
        rho: list[float]
            Only if ring_filter=False. List of integration scales corresponding to the size over the neighborhood in which the
            orientation is to be analysed.
        gamma: float
            Scale-space normalization parameter. Should be set to 1.2, change only for experimental purposes.
        truncate: float
            Truncate the filter at this many standard deviations. Default is 4.0.

    Returns:
        S: cpt.NDArray
            An array containing elements of structure tensor.
            If image is 2D, with shape (3, volume.shape), containing (s_xx, s_yy, s_xy).
            If image is 3D, with shape (6, volume.shape), containing (s_xx, s_yy, s_zz, s_xy, s_xz, s_yz).
        val, vec: cpt.NDArray
            Eigenvectors and eigenvalues of the structure tensor.
        scale: cpt.NDArray
            Scale values chosen for each pixels based on the structure tensor matrix trace

    Authors: papi@dtu.dk, 2023
    """
        
    if correctScale and not ring_filter:
        raise ValueError(
            "Scale correction returns incorrect values if ring filter is disabled. Set correctScale=False or ring_filter=True."
        )

    if image.ndim == 2:
        S_opt = np.empty((3,) + image.shape, dtype=image.dtype)
        S = cp.empty((3,) + image.shape, dtype=image.dtype)
        S_copy = np.empty((3,) + image.shape, dtype=image.dtype)
        S_size = 3
    elif image.ndim == 3:
        S_opt = np.empty((6,) + image.shape, dtype=image.dtype)
        S = cp.empty((6,) + image.shape, dtype=image.dtype)
        S_copy = np.empty((6,) + image.shape, dtype=image.dtype)
        S_size = 6
    else:
        raise ValueError("Image must be 2D or 3D.")

    if gamma != 1.2:
        logger.warning(
            "Gamma is not 1.2. This may result in icorrect scale space calculation."
        )

    # Repeat rho if None
    if rho_list is None:
        rho_list = [None for _ in range(len(sigma_list))]

    # Loop over scales
    for i in range(len(sigma_list)):
        # Compute structure tensor at a single scale
        S = structure_tensor(
            image,
            sigma_list[i],
            ring_filter,
            rho_list[i],
            S,
            eig_decomp=False,
            truncate=truncate,
        )

        S_copy = cp.asnumpy(S)

        # Normalize S scale response
        S_copy *= (sigma_list[i] ** (2 * gamma))

        # Compute trace of the structure tensor matrix
        discr = np.sum(S_copy[0 : np.ceil(S_size / 2).astype(int)], axis=0)

        if i == 0:
            S_opt = np.copy(S_copy)
            scale_opt = np.ones(image.shape, dtype=float) * sigma_list[i]
            discr_opt = np.copy(discr)
        else:
            S_opt = np.where(discr > discr_opt, S_copy, S_opt)
            scale_opt = np.where(discr > discr_opt, sigma_list[i], scale_opt)
            discr_opt = np.where(discr > discr_opt, discr, discr_opt)

        logger.info(f"Scale {np.round(sigma_list[i],3)} done.")

    # Swap to cupy array for efficient computation
    S = cp.array(S_opt)

    # Compute eigenvalues and eigenvectors of the structure tensor
    if image.ndim == 2:
        val, vec = st2d_cupy.eig_special_2d(S)
    elif image.ndim == 3:
        val, vec = st3d_cupy.eig_special_3d(S)

    val = cp.asnumpy(val)
    vec = cp.asnumpy(vec)
    
    # Apply optional scale correction
    if correctScale:
        scale_opt = util.correct_scale(scale_opt, val)

    return S_opt, val, vec, scale_opt
