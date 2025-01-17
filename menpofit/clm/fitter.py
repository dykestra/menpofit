from menpofit.fitter import MultiScaleParametricFitter
from menpofit import checks

from .algorithm import RegularisedLandmarkMeanShift
from .result import CLMResult


class CLMFitter(MultiScaleParametricFitter):
    r"""
    Abstract class for defining a CLM fitter.

    .. note:: When using a method with a parametric shape model, the first step
              is to **reconstruct the initial shape** using the shape model. The
              generated reconstructed shape is then used as initialisation for
              the iterative optimisation. This step takes place at each scale
              and it is not considered as an iteration, thus it is not counted
              for the provided `max_iters`.

    Parameters
    ----------
    clm : :map:`CLM` or `subclass`
        The trained CLM model.
    algorithms : `list` of `class`
        The list of algorithm objects that will perform the fitting per scale.
    """
    def __init__(self, clm, algorithms):
        self._model = clm
        # Call superclass
        super(CLMFitter, self).__init__(
            scales=clm.scales, reference_shape=clm.reference_shape,
            holistic_features=clm.holistic_features, algorithms=algorithms)

    @property
    def clm(self):
        r"""
        The trained CLM model.

        :type: :map:`CLM` or `subclass`
        """
        return self._model

    def _fitter_result(self, image, algorithm_results, affine_transforms,
                       scale_transforms, gt_shape=None):
        r"""
        Function the creates the multi-scale fitting result object.

        Parameters
        ----------
        image : `menpo.image.Image` or subclass
            The image that was fitted.
        algorithm_results : `list` of :map:`CLMAlgorithmResult` or subclass
            The list of fitting result per scale.
        affine_transforms : `list` of `menpo.transform.Affine`
            The list of affine transforms per scale that are the inverses of the
            transformations introduced by the rescale wrt the reference shape as
            well as the feature extraction.
        scale_transforms : `list` of `menpo.shape.Scale`
            The list of inverse scaling transforms per scale.
        gt_shape : `menpo.shape.PointCloud`, optional
            The ground truth shape associated to the image.

        Returns
        -------
        fitting_result : :map:`CLMResult` or subclass
            The multi-scale fitting result containing the result of the fitting
            procedure.
        """
        return CLMResult(results=algorithm_results, scales=self.scales,
                         affine_transforms=affine_transforms,
                         scale_transforms=scale_transforms, image=image,
                         gt_shape=gt_shape)


class GradientDescentCLMFitter(CLMFitter):
    r"""
    Class for defining an CLM fitter using gradient descent optimization.

    .. note:: When using a method with a parametric shape model, the first step
              is to **reconstruct the initial shape** using the shape model. The
              generated reconstructed shape is then used as initialisation for
              the iterative optimisation. This step takes place at each scale
              and it is not considered as an iteration, thus it is not counted
              for the provided `max_iters`.

    Parameters
    ----------
    clm : :map:`CLM` or `subclass`
        The trained CLM model.
    gd_algorithm_cls : `class`, optional
        The gradient descent optimisation algorithm that will get applied. The
        possible options are :map:`RegularisedLandmarkMeanShift` and
        :map:`ActiveShapeModel`.
    n_shape : `int` or `float` or `list` of those or ``None``, optional
        The number of shape components that will be used. If `int`, then it
        defines the exact number of active components. If `float`, then it
        defines the percentage of variance to keep. If `int` or `float`, then
        the provided value will be applied for all scales. If `list`, then it
        defines a value per scale. If ``None``, then all the available
        components will be used. Note that this simply sets the active
        components without trimming the unused ones. Also, the available
        components may have already been trimmed to `max_shape_components`
        during training.
    """
    def __init__(self, clm, gd_algorithm_cls=RegularisedLandmarkMeanShift,
                 n_shape=None):
        # Store CLM trained model
        self._model = clm

        # Check parameter
        checks.set_models_components(clm.shape_models, n_shape)

        # Get list of algorithm objects per scale
        algorithms = [gd_algorithm_cls(clm.expert_ensembles[i],
                                       clm.shape_models[i])
                      for i in range(clm.n_scales)]

        # Call superclass
        super(GradientDescentCLMFitter, self).__init__(clm=clm,
                                                       algorithms=algorithms)

    def __str__(self):
        # Compute scale info strings
        scales_info = []
        lvl_str_tmplt = r"""   - Scale {}
     - {} active shape components
     - {} similarity transform components"""
        for k, s in enumerate(self.scales):
            scales_info.append(lvl_str_tmplt.format(
                    s,
                    self.clm.shape_models[k].n_active_components,
                    self.clm.shape_models[k].n_global_parameters))
        scales_info = '\n'.join(scales_info)

        cls_str = r"""{class_title}
 - Scales: {scales}
{scales_info}
    """.format(class_title=self.algorithms[0].__str__(),
               scales=self.scales,
               scales_info=scales_info)
        return self.clm.__str__() + cls_str
