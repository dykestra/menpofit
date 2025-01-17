import numpy as np

from menpofit.math.correlationfilter import mccf, imccf


class IncrementalCorrelationFilterThinWrapper(object):
    r"""
    Wrapper class for defining an Incremental Correlation Filter.

    Parameters
    ----------
    cf_callable : `callable`, optional
        The correlation filter function. Possible options are:

        ============ ===========================================
        Class        Method
        ============ ===========================================
        :map:`mccf`  Multi-Channel Correlation Filter
        :map:`mosse` Minimum Output Sum of Squared Errors Filter
        ============ ===========================================
    icf_callable : `callable`, optional
        The incremental correlation filter function. Possible options are:

        ============= =======================================================
        Class         Method
        ============= =======================================================
        :map:`imccf`  Incremental Multi-Channel Correlation Filter
        :map:`imosse` Incremental Minimum Output Sum of Squared Errors Filter
        ============= =======================================================
    """
    def __init__(self, cf_callable=mccf, icf_callable=imccf):
        self.cf_callable = cf_callable
        self.icf_callable = icf_callable

    def increment(self, A, B, n_x, Z, t):
        r"""
        Method that trains the correlation filter.

        Parameters
        ----------
        A : ``(N,)`` `ndarray`
            The current auto-correlation array, where
            ``N = (patch_h+response_h-1) * (patch_w+response_w-1) * n_channels``
        B : ``(N, N)`` `ndarray`
            The current cross-correlation array, where
            ``N = (patch_h+response_h-1) * (patch_w+response_w-1) * n_channels``
        n_x : `int`
            The current number of images.
        Z : `list` or ``(n_images, n_channels, patch_h, patch_w)`` `ndarray`
            The training images (patches). If `list`, then it consists of
            `n_images` ``(n_channels, patch_h, patch_w)`` `ndarray` members.
        t : ``(1, response_h, response_w)`` `ndarray`
            The desired response.

        Returns
        -------
        correlation_filter : ``(n_channels, response_h, response_w)`` `ndarray`
            The learned correlation filter.
        auto_correlation : ``(N,)`` `ndarray`
            The auto-correlation array, where
            ``N = (patch_h+response_h-1) * (patch_w+response_w-1) * n_channels``
        cross_correlation : ``(N, N)`` `ndarray`
            The cross-correlation array, where
            ``N = (patch_h+response_h-1) * (patch_w+response_w-1) * n_channels``
        """
        # Turn list of X into ndarray
        if isinstance(Z, list):
            Z = np.asarray(Z)
        return self.icf_callable(A, B, n_x, Z, t)

    def train(self, X, t):
        r"""
        Method that trains the correlation filter.

        Parameters
        ----------
        X : `list` or ``(n_images, n_channels, patch_h, patch_w)`` `ndarray`
            The training images (patches). If `list`, then it consists of
            `n_images` ``(n_channels, patch_h, patch_w)`` `ndarray` members.
        t : ``(1, response_h, response_w)`` `ndarray`
            The desired response.

        Returns
        -------
        correlation_filter : ``(n_channels, response_h, response_w)`` `ndarray`
            The learned correlation filter.
        auto_correlation : ``(N,)`` `ndarray`
            The auto-correlation array, where
            ``N = (patch_h+response_h-1) * (patch_w+response_w-1) * n_channels``
        cross_correlation : ``(N, N)`` `ndarray`
            The cross-correlation array, where
            ``N = (patch_h+response_h-1) * (patch_w+response_w-1) * n_channels``
        """
        # Turn list of X into ndarray
        if isinstance(X, list):
            X = np.asarray(X)
        # Return linear svm filter and bias
        return self.cf_callable(X, t)
