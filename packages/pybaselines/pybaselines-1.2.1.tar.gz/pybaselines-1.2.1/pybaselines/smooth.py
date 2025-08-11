# -*- coding: utf-8 -*-
"""Smoothing-based techniques for fitting baselines to experimental data.

Created on March 7, 2021
@author: Donald Erb

"""

import warnings

import numpy as np
from scipy.ndimage import median_filter, uniform_filter1d
from scipy.signal import savgol_coeffs

from ._algorithm_setup import _Algorithm, _class_wrapper
from ._compat import jit, trapezoid
from ._validation import _check_half_window, _check_scalar
from .utils import (
    ParameterWarning, _get_edges, gaussian, gaussian_kernel, optimize_window,
    pad_edges, padded_convolve, relative_difference
)


class _Smooth(_Algorithm):
    """A base class for all smoothing algorithms."""

    @_Algorithm._register
    def noise_median(self, data, half_window=None, smooth_half_window=None, sigma=None,
                     pad_kwargs=None, **kwargs):
        """
        The noise-median method for baseline identification.

        Assumes the baseline can be considered as the median value within a moving
        window, and the resulting baseline is then smoothed with a Gaussian kernel.

        Parameters
        ----------
        data : array-like, shape (N,)
            The y-values of the measured data, with N data points.
        half_window : int, optional
            The index-based size to use for the median window. The total window
            size will range from [-half_window, ..., half_window] with size
            2 * half_window + 1. Default is None, which will use twice the output from
            :func:`.optimize_window`, which is an okay starting value.
        smooth_half_window : int, optional
            The half window to use for smoothing. Default is None, which will use
            the same value as `half_window`.
        sigma : float, optional
            The standard deviation of the smoothing Gaussian kernel. Default is None,
            which will use (2 * `smooth_half_window` + 1) / 6.
        pad_kwargs : dict, optional
            A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
            the edges of the data to prevent edge effects from convolution. Default is None.
        **kwargs

            .. deprecated:: 1.2.0
                Passing additional keyword arguments is deprecated and will be removed in version
                1.4.0. Pass keyword arguments using `pad_kwargs`.

        Returns
        -------
        baseline : numpy.ndarray, shape (N,)
            The calculated and smoothed baseline.
        dict
            An empty dictionary, just to match the output of all other algorithms.

        References
        ----------
        Friedrichs, M., A model-free algorithm for the removal of baseline
        artifacts. J. Biomolecular NMR, 1995, 5, 147-153.

        """
        y, half_window = self._setup_smooth(
            data, half_window, window_multiplier=2, pad_kwargs=pad_kwargs, **kwargs
        )
        window_size = 2 * half_window + 1
        median = median_filter(y, [window_size], mode='nearest')
        if smooth_half_window is None:
            smooth_window = window_size
        else:
            smooth_window = 2 * _check_half_window(smooth_half_window, allow_zero=True) + 1
        if sigma is None:
            # the gaussian kernel will includes +- 3 sigma
            sigma = smooth_window / 6
        baseline = padded_convolve(median, gaussian_kernel(smooth_window, sigma))
        return baseline[half_window:-half_window], {}

    @_Algorithm._register
    def snip(self, data, max_half_window=None, decreasing=False, smooth_half_window=None,
             filter_order=2, pad_kwargs=None, **kwargs):
        """
        Statistics-sensitive Non-linear Iterative Peak-clipping (SNIP).

        Parameters
        ----------
        data : array-like, shape (N,)
            The y-values of the measured data, with N data points.
        max_half_window : int or Sequence(int, int), optional
            The maximum number of iterations. Should be set such that
            `max_half_window` is approxiamtely ``(w-1)/2``, where ``w`` is the index-based
            width of a feature or peak. `max_half_window` can also be a sequence of
            two integers for asymmetric peaks, with the first item corresponding to
            the `max_half_window` of the peak's left edge, and the second item
            for the peak's right edge [3]_. Default is None, which will use the output
            from :func:`.optimize_window`, which is an okay starting value.
        decreasing : bool, optional
            If False (default), will iterate through window sizes from 1 to
            `max_half_window`. If True, will reverse the order and iterate from
            `max_half_window` to 1, which gives a smoother baseline according to [3]_
            and [4]_.
        smooth_half_window : int, optional
            The half window to use for smoothing the data. If `smooth_half_window`
            is greater than 0, will perform a moving average smooth on the data for
            each window, which gives better results for noisy data [3]_. Default is
            None, which will not perform any smoothing.
        filter_order : {2, 4, 6, 8}, optional
            If the measured data has a more complicated baseline consisting of other
            elements such as Compton edges, then a higher `filter_order` should be
            selected [3]_. Default is 2, which works well for approximating a linear
            baseline.
        pad_kwargs : dict, optional
            A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
            the edges of the data to prevent edge effects from smoothing. Default is None.
        **kwargs

            .. deprecated:: 1.2.0
                Passing additional keyword arguments is deprecated and will be removed in version
                1.4.0. Pass keyword arguments using `pad_kwargs`.

        Returns
        -------
        baseline : numpy.ndarray, shape (N,)
            The calculated baseline.
        dict
            An empty dictionary, just to match the output of all other algorithms.

        Raises
        ------
        ValueError
            Raised if `filter_order` is not 2, 4, 6, or 8.

        Warns
        -----
        UserWarning
            Raised if max_half_window is greater than (len(data) - 1) // 2.

        Notes
        -----
        Algorithm initially developed by [1]_, and this specific version of the
        algorithm is adapted from [2]_, [3]_, and [4]_.

        If data covers several orders of magnitude, better results can be obtained
        by first transforming the data using log-log-square transform before
        using SNIP [2]_::

            transformed_data =  np.log(np.log(np.sqrt(data + 1) + 1) + 1)

        and then baseline can then be reverted back to the original scale using inverse::

            baseline = -1 + (np.exp(np.exp(snip(transformed_data)) - 1) - 1)**2

        References
        ----------
        .. [1] Ryan, C.G., et al. SNIP, A Statistics-Sensitive Background Treatment
            For The Quantitative Analysis Of Pixe Spectra In Geoscience Applications.
            Nuclear Instruments and Methods in Physics Research B, 1988, 934, 396-402.
        .. [2] Morháč, M., et al. Background elimination methods for multidimensional
            coincidence γ-ray spectra. Nuclear Instruments and Methods in Physics
            Research A, 1997, 401, 113-132.
        .. [3] Morháč, M., et al. Peak Clipping Algorithms for Background Estimation in
            Spectroscopic Data. Applied Spectroscopy, 2008, 62(1), 91-106.
        .. [4] Morháč, M. An algorithm for determination of peak regions and baseline
            elimination in spectroscopic data. Nuclear Instruments and Methods in
            Physics Research A, 2009, 60, 478-487.

        """
        # TODO potentially add adaptive window sizes from [4]_, or at least allow inputting
        # an array of max_half_windows; would need to have a separate function for array
        # windows since it would no longer be able to be vectorized
        if filter_order not in {2, 4, 6, 8}:
            raise ValueError('filter_order must be 2, 4, 6, or 8')

        if max_half_window is None:
            max_half_window = optimize_window(data)
        half_windows = _check_half_window(max_half_window, two_d=True)
        for i, half_window in enumerate(half_windows):
            if half_window > (self._size - 1) // 2:
                warnings.warn(
                    'max_half_window values greater than (len(data) - 1) / 2 have no effect.',
                    ParameterWarning, stacklevel=2
                )
                half_windows[i] = (self._size - 1) // 2

        max_of_half_windows = np.max(half_windows)
        if decreasing:
            range_args = (max_of_half_windows, 0, -1)
        else:
            range_args = (1, max_of_half_windows + 1, 1)

        y = self._setup_smooth(data, max_of_half_windows, pad_kwargs=pad_kwargs, **kwargs)[0]
        num_y = self._size + 2 * max_of_half_windows
        smooth = smooth_half_window is not None and smooth_half_window > 0
        if smooth:
            smooth_window = 2 * _check_half_window(smooth_half_window) + 1
        baseline = y.copy()
        for i in range(*range_args):
            i_left = min(i, half_windows[0])
            i_right = min(i, half_windows[1])

            filters = (
                baseline[i - i_left:num_y - i - i_left] + baseline[i + i_right:num_y - i + i_right]
            ) / 2
            if filter_order > 2:
                filters_new = (
                    - (
                        baseline[i - i_left:num_y - i - i_left]
                        + baseline[i + i_right:num_y - i + i_right]
                    )
                    + 4 * (
                        baseline[i - i_left // 2:-i - i_left // 2]
                        + baseline[i + i_right // 2:-i + i_right // 2]
                    )
                ) / 6
                filters = np.maximum(filters, filters_new)
            if filter_order > 4:
                filters_new = (
                    baseline[i - i_left:num_y - i - i_left]
                    + baseline[i + i_right:num_y - i + i_right]
                    - 6 * (
                        baseline[i - 2 * i_left // 3:-i - 2 * i_left // 3]
                        + baseline[i + 2 * i_right // 3:-i + 2 * i_right // 3]
                    )
                    + 15 * (
                        baseline[i - i_left // 3:-i - i_left // 3]
                        + baseline[i + i_right // 3:-i + i_right // 3]
                    )
                ) / 20
                filters = np.maximum(filters, filters_new)
            if filter_order > 6:
                filters_new = (
                    - (
                        baseline[i - i_left:num_y - i - i_left]
                        + baseline[i + i_right:num_y - i + i_right]
                    )
                    + 8 * (
                        baseline[i - 3 * i_left // 4:-i - 3 * i_left // 4]
                        + baseline[i + 3 * i_right // 4:-i + 3 * i_right // 4]
                    )
                    - 28 * (
                        baseline[i - i_left // 2:-i - i_left // 2]
                        + baseline[i + i_right // 2:-i + i_right // 2]
                    )
                    + 56 * (
                        baseline[i - i_left // 4:-i - i_left // 4]
                        + baseline[i + i_right // 4:-i + i_right // 4]
                    )
                ) / 70
                filters = np.maximum(filters, filters_new)

            if smooth:
                previous_baseline = uniform_filter1d(baseline, smooth_window)[i:-i]
            else:
                previous_baseline = baseline[i:-i]
            baseline[i:-i] = np.where(baseline[i:-i] > filters, filters, previous_baseline)

        return baseline[max_of_half_windows:-max_of_half_windows], {}

    @_Algorithm._register
    def swima(self, data, min_half_window=3, max_half_window=None, smooth_half_window=None,
              pad_kwargs=None, **kwargs):
        """
        Small-window moving average (SWiMA) baseline.

        Computes an iterative moving average to smooth peaks and obtain the baseline.

        Parameters
        ----------
        data : array-like, shape (N,)
            The y-values of the measured data, with N data points.
        min_half_window : int, optional
            The minimum half window value that must be reached before the exit criteria
            is considered. Can be increased to reduce the calculation time. Default is 3.
        max_half_window : int, optional
            The maximum number of iterations. Default is None, which will use
            (N - 1) / 2. Typically does not need to be specified.
        smooth_half_window : int, optional
            The half window to use for smoothing the input data with a moving average.
            Default is None, which will use N / 50. Use a value of 0 or less to not
            smooth the data. See Notes below for more details.
        pad_kwargs : dict, optional
            A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
            the edges of the data to prevent edge effects from smoothing. Default is None.
        **kwargs

            .. deprecated:: 1.2.0
                Passing additional keyword arguments is deprecated and will be removed in version
                1.4.0. Pass keyword arguments using `pad_kwargs`.

        Returns
        -------
        baseline : numpy.ndarray, shape (N,)
            The calculated baseline.
        dict
            A dictionary with the following items:

            * 'half_window': list(int)
                A list of the half windows at which the exit criteria was reached.
                Has a length of 1 if the main exit criteria was intially reached,
                otherwise has a length of 2.
            * 'converged': list(bool or None)
                A list of the convergence status. Has a length of 1 if the main
                exit criteria was intially reached, otherwise has a length of 2.
                Each convergence status is True if the main exit criteria was
                reached, False if the second exit criteria was reached, and None
                if `max_half_window` is reached before either exit criteria.

        Notes
        -----
        This algorithm requires the input data to be fairly smooth (noise-free), so it
        is recommended to either smooth the data beforehand, or specify a
        `smooth_half_window` value. Non-smooth data can cause the exit criteria to be
        reached prematurely (can be avoided by setting a larger `min_half_window`), while
        over-smoothed data can cause the exit criteria to be reached later than optimal.

        The half-window at which convergence occurs is roughly close to the index-based
        full-width-at-half-maximum of a peak or feature, but can vary. Therfore, it is
        better to set a `min_half_window` that is smaller than expected to not miss the
        exit criteria.

        If the main exit criteria is not reached on the initial fit, a gaussian baseline
        (which is well handled by this algorithm) is added to the data, and it is re-fit.

        References
        ----------
        Schulze, H., et al. A Small-Window Moving Average-Based Fully Automated
        Baseline Estimation Method for Raman Spectra. Applied Spectroscopy, 2012,
        66(7), 757-764.

        """
        if max_half_window is None:
            max_half_window = (self._size - 1) // 2
        min_half_window = _check_half_window(min_half_window, allow_zero=True)
        y = self._setup_smooth(data, max_half_window, pad_kwargs=pad_kwargs, **kwargs)[0]
        len_y = self._size + 2 * max_half_window  # includes padding of max_half_window at each side
        data_slice = slice(max_half_window, -max_half_window)
        if smooth_half_window is None:
            smooth_half_window = max(1, (len_y - 2 * max_half_window) // 50)
        if smooth_half_window > 0:
            y = uniform_filter1d(y, 2 * _check_half_window(smooth_half_window) + 1)

        *_, pseudo_inverse = self._setup_polynomial(
            y, None, poly_order=3, calc_vander=True, calc_pinv=True
        )
        baseline, converged, half_window = _swima_loop(
            y, self._polynomial.vandermonde, pseudo_inverse, data_slice, max_half_window,
            min_half_window
        )
        converges = [converged]
        half_windows = [half_window]
        if not converged:
            residual = y - baseline
            gaussian_bkg = gaussian(
                np.arange(len_y), np.max(residual), len_y / 2, len_y / 6
            )
            baseline_2, converged, half_window = _swima_loop(
                residual + gaussian_bkg, self._polynomial.vandermonde, pseudo_inverse, data_slice,
                max_half_window, 3
            )
            baseline += baseline_2 - gaussian_bkg
            converges.append(converged)
            half_windows.append(half_window)

        return baseline[data_slice], {'half_window': half_windows, 'converged': converges}

    @_Algorithm._register
    def ipsa(self, data, half_window=None, max_iter=500, tol=None, roi=None,
             original_criteria=False, pad_kwargs=None, **kwargs):
        """
        Iterative Polynomial Smoothing Algorithm (IPSA).

        Parameters
        ----------
        data : array-like, shape (N,)
            The y-values of the measured data, with N data points.
        half_window : int
            The half-window to use for the smoothing each iteration. Should be
            approximately equal to the full-width-at-half-maximum of the peaks or features
            in the data. Default is None, which will use 4 times the output of
            :func:`.optimize_window`, which is not always a good value, but at least scales
            with the number of data points and gives a starting point for tuning the parameter.
        max_iter : int, optional
            The maximum number of iterations. Default is 500.
        tol : float, optional
            The exit criteria. Default is None, which uses 1e-3 if `original_criteria` is
            False, and ``1 / (max(data) - min(data))`` if `original_criteria` is True.
        roi : slice or array-like, shape(N,)
            The region of interest, such that ``np.asarray(data)[roi]`` gives the values
            for calculating the tolerance if `original_criteria` is True. Not used if
            `original_criteria` is True. Default is None, which uses all values in `data`.
        original_criteria : bool, optional
            Whether to use the original exit criteria from the reference, which is difficult
            to use since it requires knowledge of how high the peaks should be after baseline
            correction. If False (default), then compares ``norm(old, new) / norm(old)``, where
            `old` is the previous iteration's baseline, and `new` is the current iteration's
            baseline.
        pad_kwargs : dict, optional
            A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
            the edges of the data to prevent edge effects from smoothing. Default is None.
        **kwargs

            .. deprecated:: 1.2.0
                Passing additional keyword arguments is deprecated and will be removed in version
                1.4.0. Pass keyword arguments using `pad_kwargs`.

        Returns
        -------
        baseline : numpy.ndarray, shape (N,)
            The calculated baseline.
        params : dict
            A dictionary with the following items:

            * 'tol_history': numpy.ndarray
                An array containing the calculated tolerance values for
                each iteration. The length of the array is the number of iterations
                completed. If the last value in the array is greater than the input
                `tol` value, then the function did not converge.

        References
        ----------
        Wang, T., et al. Background Subtraction of Raman Spectra Based on Iterative
        Polynomial Smoothing. Applied Spectroscopy. 2017, 71(6), 1169-1179.

        """
        y, output_half_window = self._setup_smooth(
            data, half_window, pad_type='full', window_multiplier=4, pad_kwargs=pad_kwargs,
            **kwargs
        )
        window_size = 2 * output_half_window + 1
        y0 = y
        data_slice = slice(window_size, -window_size)
        if original_criteria:
            if roi is None:
                roi = slice(None)
            elif not isinstance(roi, slice):
                roi = np.asarray(roi)

        if tol is None:
            if original_criteria:
                # guess what the desired height should be; not a great guess, but it's
                # something
                tol = 1 / np.ptp(y[data_slice][roi])
            else:
                tol = 1e-3

        savgol_coef = savgol_coeffs(window_size, 2)
        tol_history = np.empty(max_iter + 1)
        old_baseline = y[data_slice]
        for i in range(max_iter + 1):
            baseline = padded_convolve(y, savgol_coef, 'edge')
            if original_criteria:
                residual = (y0 - baseline)[data_slice][roi]
                calc_tol = abs(residual.min() / residual.max())
            else:
                calc_tol = relative_difference(old_baseline, baseline[data_slice])
            tol_history[i] = calc_tol
            if calc_tol < tol:
                break
            y = np.minimum(y0, baseline)
            old_baseline = baseline[data_slice]

        return baseline[data_slice], {'tol_history': tol_history[:i + 1]}

    @_Algorithm._register
    def ria(self, data, half_window=None, max_iter=500, tol=1e-2, side='both',
            width_scale=0.1, height_scale=1., sigma_scale=1 / 12, pad_kwargs=None, **kwargs):
        """
        Range Independent Algorithm (RIA).

        Adds additional data to the left and/or right of the input data, and then
        iteratively smooths until the area of the additional data is removed.

        Parameters
        ----------
        data : array-like, shape (N,)
            The y-values of the measured data, with N data points.
        half_window : int, optional
            The half-window to use for the smoothing each iteration. Should be
            approximately equal to the full-width-at-half-maximum of the peaks or features
            in the data. Default is None, which will use the output of :func:`.optimize_window`,
            which is not always a good value, but at least scales with the number of data points
            and gives a starting point for tuning the parameter.
        max_iter : int, optional
            The maximum number of iterations. Default is 500.
        tol : float, optional
            The exit criteria. Default is 1e-2.
        side : {'both', 'left', 'right'}, optional
            The side of the measured data to extend. Default is 'both'.
        width_scale : float, optional
            The number of data points added to each side is `width_scale` * N. Default
            is 0.1.
        height_scale : float, optional
            The height of the added Gaussian peak(s) is calculated as
            `height_scale` * max(`data`). Default is 1.
        sigma_scale : float, optional
            The sigma value for the added Gaussian peak(s) is calculated as
            `sigma_scale` * `width_scale` * N. Default is 1/12, which will make
            the Gaussian span +- 6 sigma, making its total width about half of the
            added length.
        pad_kwargs : dict, optional
            A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
            the edges of the data when adding the extended left and/or right sections.
        **kwargs

            .. deprecated:: 1.2.0
                Passing additional keyword arguments is deprecated and will be removed in version
                1.4.0. Pass keyword arguments using `pad_kwargs`.

        Returns
        -------
        baseline : numpy.ndarray, shape (N,)
            The calculated baseline.
        params : dict
            A dictionary with the following items:

            * 'tol_history': numpy.ndarray
                An array containing the calculated tolerance values for
                each iteration. The length of the array is the number of iterations
                completed. If the last value in the array is greater than the input
                `tol` value, then the function did not converge (if the array length
                is equal to `max_iter`) or the areas of the smoothed extended regions
                exceeded their initial areas (if the array length is < `max_iter`).

        Raises
        ------
        ValueError
            Raised if `side` is not 'left', 'right', or 'both'.

        References
        ----------
        Krishna, H., et al. Range-independent background subtraction algorithm for
        recovery of Raman spectra of biological tissue. J Raman Spectroscopy. 2012,
        43(12), 1884-1894.

        """
        side = side.lower()
        if side not in ('left', 'right', 'both'):
            raise ValueError('side must be "left", "right", or "both"')
        # note: only pass pad_kwargs to setup_smooth to validate pad_kwargs and kwargs; no
        # padding is done
        y, half_window = self._setup_smooth(
            data, half_window, pad_type=None, pad_kwargs=pad_kwargs, **kwargs
        )
        min_x, max_x = self.x_domain
        x_range = max_x - min_x

        added_window = int(self._size * width_scale)
        lower_bound = 0
        upper_bound = 0
        known_area = 0.

        # TODO should make this a function that could be used by
        # optimizers.optimize_extended_range too
        pad_kwargs = pad_kwargs if pad_kwargs is not None else {}
        added_left, added_right = _get_edges(y, added_window, **pad_kwargs, **kwargs)
        added_gaussian = gaussian(
            np.linspace(-added_window / 2, added_window / 2, added_window),
            height_scale * abs(y.max()), 0, added_window * sigma_scale
        )
        if side in ('left', 'both'):
            added_x_left = np.linspace(
                min_x - x_range * (width_scale / 2), min_x, added_window + 1
            )[:-1]
            added_y_left = added_gaussian + added_left
            lower_bound = added_window
            known_area += trapezoid(added_gaussian, added_x_left)
        else:
            added_x_left = []
            added_y_left = []

        if side in ('right', 'both'):
            added_x_right = np.linspace(
                max_x, max_x + x_range * (width_scale / 2), added_window + 1
            )[1:]
            added_y_right = added_gaussian + added_right
            upper_bound = added_window
            known_area += trapezoid(added_gaussian, added_x_right)
        else:
            added_x_right = []
            added_y_right = []

        fit_x_data = np.concatenate((added_x_left, self.x, added_x_right))
        fit_data = np.concatenate((added_y_left, y, added_y_right))

        upper_max = fit_data.shape[0] - upper_bound
        tol_history = np.empty(max_iter)
        window_size = 2 * half_window + 1
        smoother_array = pad_edges(fit_data, window_size, extrapolate_window=2)
        data_slice = slice(window_size, -window_size)
        for i in range(max_iter):
            # only smooth fit_data so that the outer section remains unchanged by
            # smoothing and edge effects are ignored
            smoother_array[data_slice] = uniform_filter1d(smoother_array, window_size)[data_slice]
            residual = fit_data - smoother_array[data_slice]
            calc_area = trapezoid(residual[:lower_bound], fit_x_data[:lower_bound])
            if upper_bound:
                calc_area += trapezoid(residual[-upper_bound:], fit_x_data[-upper_bound:])
            calc_difference = relative_difference(known_area, calc_area)
            tol_history[i] = calc_difference
            if calc_difference < tol or calc_area > known_area:
                break
            smoother_array[data_slice] = np.minimum(fit_data, smoother_array[data_slice])

        baseline = smoother_array[data_slice][lower_bound:upper_max]

        return baseline, {'tol_history': tol_history[:i + 1]}

    @_Algorithm._register
    def peak_filling(self, data, half_window=None, sections=None, max_iter=5, lam_smooth=None):
        """
        The 4S (Smooth, Subsample, Suppress, Stretch) Peak Filling algorithm.

        Smooths and truncates the input. Each value is then replaced in-place by the minimum of
        the value or the average of the moving window, with the half-window size decreasing
        exponentially from the input `half_window` to 1. The result is then interpolated back
        into the original data size.

        Parameters
        ----------
        data : array-like, shape (N,)
            The y-values of the measured data, with N data points.
        half_window : int, optional
            The index-based size to use for the moving average window. The total window
            size will range from [-half_window, ..., half_window] with size
            ``2 * half_window + 1``. Default is None, which will use two or three times the
            output from func:`.optimize_window`, which is an okay starting value.
        sections : int or Sequence[int, ...], optional
            If the input is an integer, it sets the number of equally sized
            segments the data will be split into. If the input is a sequence, each integer
            in the sequence will be the index that splits two segments, which allows
            constructing unequally sized segments. The minimum of each section will be used
            to represent the input data for determining the baseline. Higher `sections` values
            are needed for baselines with higher curvature. Default is None, which will use
            ``N // 10``.
        max_iter : int, optional
            The number of iterations to perform smoothing. Each iteration, the size of the
            window used for the moving average will shrink logarithmically, starting at
            ``2 * half_window + 1`` and ending at 3. Default is 5.
        lam_smooth : float or None, optional
            The parameter for smoothing the input using Whittaker smoothing.
            Set to 0 or None (default) to skip smoothing.

        Returns
        -------
        baseline : numpy.ndarray, shape (N,)
            The calculated baseline.
        params : dict
            A dictionary with the following items:

            * 'x_fit': numpy.ndarray, shape (P,)
                The truncated x-values used for fitting and interpolating the baseline.
            * 'baseline_fit': numpy.ndarray, shape (P,)
                The truncated baseline values used to interpolate the final baseline.

        Raises
        ------
        TypeError
            Raised if `sections` is an integer not between 1 and ``N``, or if `sections`
            is a sequence with any value not between 0 and ``N - 1``.

        Notes
        -----
        The input parameter `sections` will determine the necessary `half_window` and `max_iter`
        values required to correctly fit the baseline. Likewise, `max_iter` is highly correlated
        with `half_window`.

        References
        ----------
        Liland, K. 4S Peak Filling - baseline estimation by iterative mean suppression. MethodsX.
        2015, 2, 135-140.

        """
        if sections is None:
            sections = self._size // 10
            scalar_sections = True
        else:
            sections, scalar_sections = _check_scalar(
                sections, None, coerce_0d=False, dtype=np.intp
            )
            if scalar_sections and (sections < 1 or sections > self._size):
                raise ValueError(
                    f'There must be between 1 and {self._size} sections for peak_filling'
                )
            elif (
                not scalar_sections
                and (np.any(sections < 0) or np.any(sections > self._size - 1))
            ):
                raise ValueError(
                    f'Section indices must be between 0 and {self._size - 1} for peak_filling'
                )

        if scalar_sections:
            y_truncated = np.empty(sections)
            x_truncated = np.empty(sections)
            indices = np.linspace(0, self._size, sections + 1, dtype=np.intp)
        else:
            # np.unique already sorts so do not need to check order
            indices = np.unique(np.concatenate(([0], sections, [self._size])))
            len_arrays = len(indices) - 1
            y_truncated = np.empty(len_arrays)
            x_truncated = np.empty(len_arrays)

        if lam_smooth is not None and lam_smooth > 0:
            _, _, whittaker_system = self._setup_whittaker(data, lam_smooth, diff_order=2)
            data = whittaker_system.solve(whittaker_system.add_diagonal(1.), data)

        for i, (left_idx, right_idx) in enumerate(zip(indices[:-1], indices[1:])):
            y_truncated[i] = data[left_idx:right_idx].min()
            x_truncated[i] = self.x[left_idx:right_idx].mean()
        # include first and last values to prevent edge effects if they are not already included
        left_pad = 1 if x_truncated[0] != self.x[0] else 0
        right_pad = 1 if x_truncated[-1] != self.x[-1] else 0
        x_truncated = np.pad(
            x_truncated, [left_pad, right_pad], 'constant',
            constant_values=([self.x[0], self.x[-1]])
        )
        y_truncated = np.pad(
            y_truncated, [left_pad, right_pad], 'constant', constant_values=([data[0], data[-1]],)
        )

        _, half_win = self._setup_smooth(
            y_truncated, half_window, pad_type=None, window_multiplier=3 if max_iter < 3 else 2
        )
        if half_win > (sections - 1) // 2:
            if half_window is not None:  # only emit warning if user input half window
                warnings.warn(
                    'half_window values greater than (sections - 1) // 2 have no effect.',
                    ParameterWarning, stacklevel=2
                )
            half_win = (sections - 1) // 2
        # logspace still works when max_iter=1; use ceil rather than using dtype=int
        # in logspace since the int casting will floor the result and cause several half
        # windows of 1
        half_windows = np.ceil(np.logspace(np.log10(half_win), 0, max_iter)).astype(int)
        half_windows[0] = half_win  # rounding issues can shift initial half window +- 1

        for half_win in half_windows:
            y_truncated = _directional_min_moving_avg(y_truncated, sections, half_win)
            y_truncated = _directional_min_moving_avg(y_truncated[::-1], sections, half_win)[::-1]

        baseline = np.interp(self.x, x_truncated, y_truncated)

        return baseline, {'x_fit': x_truncated, 'baseline_fit': y_truncated}


_smooth_wrapper = _class_wrapper(_Smooth)


@_smooth_wrapper
def noise_median(data, half_window=None, smooth_half_window=None, sigma=None, x_data=None,
                 pad_kwargs=None, **kwargs):
    """
    The noise-median method for baseline identification.

    Assumes the baseline can be considered as the median value within a moving
    window, and the resulting baseline is then smoothed with a Gaussian kernel.

    Parameters
    ----------
    data : array-like, shape (N,)
        The y-values of the measured data, with N data points.
    half_window : int, optional
        The index-based size to use for the median window. The total window
        size will range from [-half_window, ..., half_window] with size
        2 * half_window + 1. Default is None, which will use twice the output from
        :func:`.optimize_window`, which is an okay starting value.
    smooth_half_window : int, optional
        The half window to use for smoothing. Default is None, which will use
        the same value as `half_window`.
    sigma : float, optional
        The standard deviation of the smoothing Gaussian kernel. Default is None,
        which will use (2 * `smooth_half_window` + 1) / 6.
    x_data : array-like, optional
        The x-values. Not used by this function, but input is allowed for consistency
        with other functions.
    pad_kwargs : dict, optional
        A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
        the edges of the data to prevent edge effects from convolution. Default is None.
    **kwargs

        .. deprecated:: 1.2.0
            Passing additional keyword arguments is deprecated and will be removed in version
            1.4.0. Pass keyword arguments using `pad_kwargs`.

    Returns
    -------
    baseline : numpy.ndarray, shape (N,)
        The calculated and smoothed baseline.
    dict
        An empty dictionary, just to match the output of all other algorithms.

    References
    ----------
    Friedrichs, M., A model-free algorithm for the removal of baseline
    artifacts. J. Biomolecular NMR, 1995, 5, 147-153.

    """


@_smooth_wrapper
def snip(data, max_half_window=None, decreasing=False, smooth_half_window=None,
         filter_order=2, x_data=None, pad_kwargs=None, **kwargs):
    """
    Statistics-sensitive Non-linear Iterative Peak-clipping (SNIP).

    Parameters
    ----------
    data : array-like, shape (N,)
        The y-values of the measured data, with N data points.
    max_half_window : int or Sequence(int, int), optional
        The maximum number of iterations. Should be set such that
        `max_half_window` is approxiamtely ``(w-1)/2``, where ``w`` is the index-based
        width of a feature or peak. `max_half_window` can also be a sequence of
        two integers for asymmetric peaks, with the first item corresponding to
        the `max_half_window` of the peak's left edge, and the second item
        for the peak's right edge [3]_. Default is None, which will use the output
        from :func:`.optimize_window`, which is an okay starting value.
    decreasing : bool, optional
        If False (default), will iterate through window sizes from 1 to
        `max_half_window`. If True, will reverse the order and iterate from
        `max_half_window` to 1, which gives a smoother baseline according to [3]_
        and [4]_.
    smooth_half_window : int, optional
        The half window to use for smoothing the data. If `smooth_half_window`
        is greater than 0, will perform a moving average smooth on the data for
        each window, which gives better results for noisy data [3]_. Default is
        None, which will not perform any smoothing.
    filter_order : {2, 4, 6, 8}, optional
        If the measured data has a more complicated baseline consisting of other
        elements such as Compton edges, then a higher `filter_order` should be
        selected [3]_. Default is 2, which works well for approximating a linear
        baseline.
    x_data : array-like, optional
        The x-values. Not used by this function, but input is allowed for consistency
        with other functions.
    pad_kwargs : dict, optional
        A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
        the edges of the data to prevent edge effects from smoothing. Default is None.
    **kwargs

        .. deprecated:: 1.2.0
            Passing additional keyword arguments is deprecated and will be removed in version
            1.4.0. Pass keyword arguments using `pad_kwargs`.

    Returns
    -------
    baseline : numpy.ndarray, shape (N,)
        The calculated baseline.
    dict
        An empty dictionary, just to match the output of all other algorithms.

    Raises
    ------
    ValueError
        Raised if `filter_order` is not 2, 4, 6, or 8.

    Warns
    -----
    UserWarning
        Raised if max_half_window is greater than (len(data) - 1) // 2.

    Notes
    -----
    Algorithm initially developed by [1]_, and this specific version of the
    algorithm is adapted from [2]_, [3]_, and [4]_.

    If data covers several orders of magnitude, better results can be obtained
    by first transforming the data using log-log-square transform before
    using SNIP [2]_::

        transformed_data =  np.log(np.log(np.sqrt(data + 1) + 1) + 1)

    and then baseline can then be reverted back to the original scale using inverse::

        baseline = -1 + (np.exp(np.exp(snip(transformed_data)) - 1) - 1)**2

    References
    ----------
    .. [1] Ryan, C.G., et al. SNIP, A Statistics-Sensitive Background Treatment
           For The Quantitative Analysis Of Pixe Spectra In Geoscience Applications.
           Nuclear Instruments and Methods in Physics Research B, 1988, 934, 396-402.
    .. [2] Morháč, M., et al. Background elimination methods for multidimensional
           coincidence γ-ray spectra. Nuclear Instruments and Methods in Physics
           Research A, 1997, 401, 113-132.
    .. [3] Morháč, M., et al. Peak Clipping Algorithms for Background Estimation in
           Spectroscopic Data. Applied Spectroscopy, 2008, 62(1), 91-106.
    .. [4] Morháč, M. An algorithm for determination of peak regions and baseline
           elimination in spectroscopic data. Nuclear Instruments and Methods in
           Physics Research A, 2009, 60, 478-487.

    """


def _swima_loop(y, vander, pseudo_inverse, data_slice, max_half_window, min_half_window=3):
    """
    Computes an iterative moving average to smooth peaks and obtain the baseline.

    The internal loop of the small-window moving average (SWiMA) algorithm.

    Parameters
    ----------
    y : numpy.ndarray, shape (N + 2 * max_half_window,)
        The array of the measured data with N data points padded at each edge with
        `max_half_window` extra data points.
    vander : numpy.ndarray, shape (N - 1, 4)
        The Vandermonde matrix for computing the 3rd order polynomial fit of the
        differential of the residual. Used for the alternate exit criteria.
    pseudo_inverse : numpy.ndarray, shape (4, N - 1)
        The pseudo-inverse of the Vandermonde matrix for computing the 3rd order
        polynomial fit of the differential of the residual. Used for the alternate
        exit criteria.
    data_slice : slice
        The slice used for separating the actual values of `y` from the extended y
        array.
    max_half_window : int
        The maximum allowable half window.
    min_half_window : int, optional
        The minimum half window that must be reached before exit criteria are
        considered. Default is 3.

    Returns
    -------
    baseline : numpy.ndarray, shape (N + 2 * max_half_window,)
        The baseline with the padded edges.
    converged : bool or None
        Whether the main exit criteria was achieved. True if it was, False
        if the alternate exit criteria was achieved, and None if `max_half_window`
        was reached before either exit criteria.
    half_window : int
        The half window at which the exit criteria was reached.

    Notes
    -----
    Uses a moving average rather than a 0-degree Savitzky-Golay filter since
    they are equivalent and the moving average is faster.

    The second exit criteria is based on Figure 2 in the reference, since the
    slightly different definition of criteria two stated in the text was always
    reached before the main exit criteria, which is not the desired outcome.

    References
    ----------
    Schulze, H., et al. A Small-Window Moving Average-Based Fully Automated
    Baseline Estimation Method for Raman Spectra. Applied Spectroscopy, 2012,
    66(7), 757-764.

    """
    actual_y = y[data_slice]
    baseline = y
    min_half_window_check = min_half_window - 2
    area_current = -1
    area_old = -1
    converged = None
    for half_window in range(1, max_half_window + 1):
        baseline_new = np.minimum(baseline, uniform_filter1d(baseline, 2 * half_window + 1))
        # only begin calculating the area when near the lowest allowed half window
        if half_window > min_half_window_check:
            area_new = trapezoid(baseline[data_slice] - baseline_new[data_slice])
            # exit criteria 1
            if area_new > area_current and area_current < area_old:
                converged = True
                # subtract 1 since minimum area was reached the previous iteration
                half_window -= 1
                break
            if half_window > min_half_window:
                diff_current = np.gradient(actual_y - baseline_new[data_slice])
                poly_diff_current = trapezoid(abs(vander @ (pseudo_inverse @ diff_current)))
                # exit criteria 2, means baseline is not well fit
                if poly_diff_current > 0.15 * trapezoid(abs(diff_current)):
                    converged = False
                    break
            area_old = area_current
            area_current = area_new
        baseline = baseline_new

    return baseline, converged, half_window


@_smooth_wrapper
def swima(data, min_half_window=3, max_half_window=None, smooth_half_window=None,
          x_data=None, pad_kwargs=None, **kwargs):
    """
    Small-window moving average (SWiMA) baseline.

    Computes an iterative moving average to smooth peaks and obtain the baseline.

    Parameters
    ----------
    data : array-like, shape (N,)
        The y-values of the measured data, with N data points.
    min_half_window : int, optional
        The minimum half window value that must be reached before the exit criteria
        is considered. Can be increased to reduce the calculation time. Default is 3.
    max_half_window : int, optional
        The maximum number of iterations. Default is None, which will use
        (N - 1) / 2. Typically does not need to be specified.
    smooth_half_window : int, optional
        The half window to use for smoothing the input data with a moving average.
        Default is None, which will use N / 50. Use a value of 0 or less to not
        smooth the data. See Notes below for more details.
    x_data : array-like, optional
        The x-values. Not used by this function, but input is allowed for consistency
        with other functions.
    pad_kwargs : dict, optional
        A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
        the edges of the data to prevent edge effects from smoothing. Default is None.
    **kwargs

        .. deprecated:: 1.2.0
            Passing additional keyword arguments is deprecated and will be removed in version
            1.4.0. Pass keyword arguments using `pad_kwargs`.

    Returns
    -------
    baseline : numpy.ndarray, shape (N,)
        The calculated baseline.
    dict
        A dictionary with the following items:

        * 'half_window': list(int)
            A list of the half windows at which the exit criteria was reached.
            Has a length of 1 if the main exit criteria was intially reached,
            otherwise has a length of 2.
        * 'converged': list(bool or None)
            A list of the convergence status. Has a length of 1 if the main
            exit criteria was intially reached, otherwise has a length of 2.
            Each convergence status is True if the main exit criteria was
            reached, False if the second exit criteria was reached, and None
            if `max_half_window` is reached before either exit criteria.

    Notes
    -----
    This algorithm requires the input data to be fairly smooth (noise-free), so it
    is recommended to either smooth the data beforehand, or specify a
    `smooth_half_window` value. Non-smooth data can cause the exit criteria to be
    reached prematurely (can be avoided by setting a larger `min_half_window`), while
    over-smoothed data can cause the exit criteria to be reached later than optimal.

    The half-window at which convergence occurs is roughly close to the index-based
    full-width-at-half-maximum of a peak or feature, but can vary. Therfore, it is
    better to set a `min_half_window` that is smaller than expected to not miss the
    exit criteria.

    If the main exit criteria is not reached on the initial fit, a gaussian baseline
    (which is well handled by this algorithm) is added to the data, and it is re-fit.

    References
    ----------
    Schulze, H., et al. A Small-Window Moving Average-Based Fully Automated
    Baseline Estimation Method for Raman Spectra. Applied Spectroscopy, 2012,
    66(7), 757-764.

    """


@_smooth_wrapper
def ipsa(data, half_window=None, max_iter=500, tol=None, roi=None,
         original_criteria=False, x_data=None, pad_kwargs=None, **kwargs):
    """
    Iterative Polynomial Smoothing Algorithm (IPSA).

    Parameters
    ----------
    data : array-like, shape (N,)
        The y-values of the measured data, with N data points.
    half_window : int
        The half-window to use for the smoothing each iteration. Should be
        approximately equal to the full-width-at-half-maximum of the peaks or features
        in the data. Default is None, which will use 4 times the output of
        :func:`.optimize_window`, which is not always a good value, but at least scales
        with the number of data points and gives a starting point for tuning the parameter.
    max_iter : int, optional
        The maximum number of iterations. Default is 500.
    tol : float, optional
        The exit criteria. Default is None, which uses 1e-3 if `original_criteria` is
        False, and ``1 / (max(data) - min(data))`` if `original_criteria` is True.
    roi : slice or array-like, shape(N,)
        The region of interest, such that ``np.asarray(data)[roi]`` gives the values
        for calculating the tolerance if `original_criteria` is True. Not used if
        `original_criteria` is True. Default is None, which uses all values in `data`.
    original_criteria : bool, optional
        Whether to use the original exit criteria from the reference, which is difficult
        to use since it requires knowledge of how high the peaks should be after baseline
        correction. If False (default), then compares ``norm(old, new) / norm(old)``, where
        `old` is the previous iteration's baseline, and `new` is the current iteration's
        baseline.
    x_data : array-like, optional
        The x-values. Not used by this function, but input is allowed for consistency
        with other functions.
    pad_kwargs : dict, optional
        A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
        the edges of the data to prevent edge effects from smoothing. Default is None.
    **kwargs

        .. deprecated:: 1.2.0
            Passing additional keyword arguments is deprecated and will be removed in version
            1.4.0. Pass keyword arguments using `pad_kwargs`.

    Returns
    -------
    baseline : numpy.ndarray, shape (N,)
        The calculated baseline.
    params : dict
        A dictionary with the following items:

        * 'tol_history': numpy.ndarray
            An array containing the calculated tolerance values for
            each iteration. The length of the array is the number of iterations
            completed. If the last value in the array is greater than the input
            `tol` value, then the function did not converge.

    References
    ----------
    Wang, T., et al. Background Subtraction of Raman Spectra Based on Iterative
    Polynomial Smoothing. Applied Spectroscopy. 2017, 71(6), 1169-1179.

    """


@_smooth_wrapper
def ria(data, x_data=None, half_window=None, max_iter=500, tol=1e-2, side='both',
        width_scale=0.1, height_scale=1., sigma_scale=1. / 12., pad_kwargs=None, **kwargs):
    """
    Range Independent Algorithm (RIA).

    Adds additional data to the left and/or right of the input data, and then
    iteratively smooths until the area of the additional data is removed.

    Parameters
    ----------
    data : array-like, shape (N,)
        The y-values of the measured data, with N data points.
    x_data : array-like, shape (N,), optional
        The x-values of the measured data. Default is None, which will create an
        array from -1 to 1 with N points.
    half_window : int, optional
        The half-window to use for the smoothing each iteration. Should be
        approximately equal to the full-width-at-half-maximum of the peaks or features
        in the data. Default is None, which will use the output of :func:`.optimize_window`,
        which is not always a good value, but at least scales with the number of data points
        and gives a starting point for tuning the parameter.
    max_iter : int, optional
        The maximum number of iterations. Default is 500.
    tol : float, optional
        The exit criteria. Default is 1e-2.
    side : {'both', 'left', 'right'}, optional
        The side of the measured data to extend. Default is 'both'.
    width_scale : float, optional
        The number of data points added to each side is `width_scale` * N. Default
        is 0.1.
    height_scale : float, optional
        The height of the added Gaussian peak(s) is calculated as
        `height_scale` * max(`data`). Default is 1.
    sigma_scale : float, optional
        The sigma value for the added Gaussian peak(s) is calculated as
        `sigma_scale` * `width_scale` * N. Default is 1/12, which will make
        the Gaussian span +- 6 sigma, making its total width about half of the
        added length.
    pad_kwargs : dict, optional
        A dictionary of keyword arguments to pass to :func:`.pad_edges` for padding
        the edges of the data when adding the extended left and/or right sections.
    **kwargs

        .. deprecated:: 1.2.0
            Passing additional keyword arguments is deprecated and will be removed in version
            1.4.0. Pass keyword arguments using `pad_kwargs`.

    Returns
    -------
    baseline : numpy.ndarray, shape (N,)
        The calculated baseline.
    params : dict
        A dictionary with the following items:

        * 'tol_history': numpy.ndarray
            An array containing the calculated tolerance values for
            each iteration. The length of the array is the number of iterations
            completed. If the last value in the array is greater than the input
            `tol` value, then the function did not converge (if the array length
            is equal to `max_iter`) or the areas of the smoothed extended regions
            exceeded their initial areas (if the array length is < `max_iter`).

    Raises
    ------
    ValueError
        Raised if `side` is not 'left', 'right', or 'both'.

    References
    ----------
    Krishna, H., et al. Range-independent background subtraction algorithm for
    recovery of Raman spectra of biological tissue. J Raman Spectroscopy. 2012,
    43(12), 1884-1894.

    """


@jit(nopython=True, cache=True)
def _directional_min_moving_avg(y, data_len, half_window):
    """
    Calculates the miniumum of a moving average and current value and modifies in-place.

    Since the data is modified in-place, the smoothing has a directional
    effect that is canceled out by calling this function a second time with
    the reversed output and then reversing that output.

    Parameters
    ----------
    y : numpy.ndarray
        The array of data to smooth.
    data_len : int
        The length of the array `y`. Used to prevent calling ``len(y)`` each
        time this function is called.
    half_window : int
        The half window used for the moving average.

    Returns
    -------
    y : numpy.ndarray
        The smoothed input. The input `y` is also modified in-place.

    Notes
    -----
    Increases and decreases the window width on the edges because otherwise the data
    becomes shifted; to prevent shifting, the window must always be centered.

    Uses a shrinking window rather than padding the data since [1]_ states (and is
    readily observed when using typical moving minimums) that the output can otherwise
    cause too low of a value when data is steep near the ends.

    Calculates the rolling mean using Welford's method [2]_ to improve calculation speed over
    calling ``numpy.mean`` on each subarray, which scales quite poorly compared to Welford's
    method with increasing half-window sizes.

    References
    ----------
    .. [1] Liland, K. 4S Peak Filling - baseline estimation by iterative mean suppression.
           MethodsX. 2 (2015) 135-140.

    .. [2] https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance

    """
    if half_window > (data_len - 1) // 2:
        half_window = (data_len - 1) // 2

    window_size = 2 * half_window + 1
    mean = y[0]
    # fill the first window; have to go to half_window + 1 since the final calculation
    # needs to adjust for the window finally filling up
    last_window = 1
    for i in range(1, half_window + 1):
        new_window = last_window + 2  # 2 * i + 1 = 2 * (i - 1) + 1 + 2 == last_window + 2
        # advance and grow window to recenter new window at index i
        for j in range(last_window, new_window):
            mean += (y[j] - mean) / (j + 1)
        last_window = new_window
        val = y[i]
        if mean < val:
            # adjust mean for new value
            y[i] = mean
            mean += (mean - val) / new_window

    for i in range(half_window + 1, data_len - half_window):
        mean += (y[i + half_window] - y[i - half_window - 1]) / window_size
        val = y[i]
        if mean < val:
            y[i] = mean
            mean += (mean - val) / window_size

    # finally shrink window on right edge
    last_window = window_size
    for i in range(data_len - half_window, data_len - 1):
        new_window = last_window - 2  # 2 * (i - 1) + 1 = 2 * i - 1 == last_window - 2
        for j in range(data_len - last_window, data_len - new_window):
            last_window -= 1
            mean += (mean - y[j]) / last_window
        val = y[i]
        if mean < val:
            y[i] = mean
            mean += (mean - val) / new_window

    return y


@_smooth_wrapper
def peak_filling(data, x_data=None, half_window=None, sections=None, max_iter=5, lam_smooth=None):
    """
    The 4S (Smooth, Subsample, Suppress, Stretch) Peak Filling algorithm.

    Smooths and truncates the input. Each value is then replaced in-place by the minimum of
    the value or the average of the moving window, with the half-window size decreasing
    exponentially from the input `half_window` to 1. The result is then interpolated back
    into the original data size.

    Parameters
    ----------
    data : array-like, shape (N,)
        The y-values of the measured data, with N data points.
    x_data : array-like, shape (N,), optional
        The x-values of the measured data. Default is None, which will create an
        array from -1 to 1 with N points. Not used within this function.
    half_window : int, optional
        The index-based size to use for the moving average window. The total window
        size will range from [-half_window, ..., half_window] with size
        ``2 * half_window + 1``. Default is None, which will use two or three times the
        output from func:`.optimize_window`, which is an okay starting value.
    sections : int, optional
        The number of sections to divide the input data into for subsampling. The
        minimum of each section will be used to represent the input data for determining
        the baseline. Higher `sections` values are needed for baselines with higher
        curvature. Default is None, which will use ``N // 10``.
    max_iter : int, optional
        The number of iterations to perform smoothing. Each iteration, the size of the
        window used for the moving average will shrink logarithmically, starting at
        ``2 * half_window + 1`` and ending at 3. Default is 5.
    lam_smooth : float or None, optional
        The parameter for smoothing the input using Whittaker smoothing.
        Set to 0 or None (default) to skip smoothing.

    Returns
    -------
    baseline : numpy.ndarray, shape (N,)
        The calculated baseline.
    params : dict
        A dictionary with the following items:

        * 'x_fit': numpy.ndarray, shape (P,)
            The truncated x-values used for fitting the baseline.
        * 'baseline_fit': numpy.ndarray, shape (P,)
            The truncated y-values used for fitting the baseline.

    Raises
    ------
    TypeError
        Raised if `sections` is not an integer.

    Notes
    -----
    The input parameter `sections` will determine the necessary `half_window` and `max_iter`
    values required to correctly fit the baseline. Likewise, `max_iter` is highly correlated
    with `half_window`.

    References
    ----------
    Liland, K. 4S Peak Filling - baseline estimation by iterative mean suppression. MethodsX.
    2015, 2, 135-140.

    """
