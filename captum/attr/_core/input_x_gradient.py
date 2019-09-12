#!/usr/bin/env python3
from .._utils.common import format_input, _format_attributions
from .._utils.attribution import GradientBasedAttribution
from .._utils.gradient import apply_gradient_requirements, undo_gradient_requirements


class InputXGradient(GradientBasedAttribution):
    def __init__(self, forward_func):
        r"""
        Args:

            forward_func (function): The forward function of the model
                       or any modification of it
        """
        super().__init__(forward_func)

    def attribute(self, inputs, target=None, additional_forward_args=None):
        r""""
        A baseline approach for computing the attribution. It multiplies input with
        the gradient with respect to input.
        https://arxiv.org/abs/1611.07270

        Args:

            inputs (tensor or tuple of tensors):  Input for which
                        attribution is computed. If forward_func takes a single
                        tensor as input, a single input tensor should be provided.
                        If forward_func takes multiple tensors as input, a tuple
                        of the input tensors should be provided. It is assumed
                        that for all given input tensors, dimension 0 corresponds
                        to the number of examples (aka batch size), and if
                        mutliple input tensors are provided, the examples must
                        be aligned appropriately.
            target (int, optional):  Output index for which gradient is computed
                        (for classification cases, this is the target class).
                        If the network returns a scalar value per example,
                        no target index is necessary. (Note: Tuples for multi
                        -dimensional output indices will be supported soon.)
            additional_forward_args (tuple, optional): If the forward function
                        requires additional arguments other than the inputs for
                        which attributions should not be computed, this argument
                        can be provided. It must be a tuple containing tensors or
                        any arbitrary python types. These arguments are provided to
                        forward_func in order following the arguments in inputs.
                        Note that attributions are not computed with respect
                        to these arguments.
                        Default: None

        Return:

                attributions (tensor or tuple of tensors): The input x gradient with
                            respect to each input feature. Attributions will always be
                            the same size as the provided inputs, with each value
                            providing the attribution of the corresponding input index.
                            If a single tensor is provided as inputs, a single tensor is
                            returned. If a tuple is provided for inputs, a tuple of
                            corresponding sized tensors is returned.


        Examples::

            >>> # ImageClassifier takes a single input tensor of images Nx3x32x32,
            >>> # and returns an Nx10 tensor of class probabilities.
            >>> net = ImageClassifier()
            >>> # Generating random input with size 2x3x3x32
            >>> input = torch.randn(2, 3, 32, 32, requires_grad=True)
            >>> # Defining InputXGradient interpreter
            >>> input_x_gradient = InputXGradient(net)
            >>> # Computes inputXgradient for class 4.
            >>> attribution = input_x_gradient.attribute(input, target=4)
        """
        # Keeps track whether original input is a tuple or not before
        # converting it into a tuple.
        is_inputs_tuple = isinstance(inputs, tuple)

        inputs = format_input(inputs)
        gradient_mask = apply_gradient_requirements(inputs)

        gradients = self.gradient_func(
            self.forward_func, inputs, target, additional_forward_args
        )

        attributions = tuple(
            input * gradient for input, gradient in zip(inputs, gradients)
        )
        undo_gradient_requirements(inputs, gradient_mask)
        return _format_attributions(is_inputs_tuple, attributions)
