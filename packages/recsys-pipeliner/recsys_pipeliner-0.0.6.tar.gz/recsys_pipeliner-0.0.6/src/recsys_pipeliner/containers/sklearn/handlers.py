from __future__ import absolute_import
import numpy as np
import os
import logging

from sagemaker_inference import content_types, decoder, encoder
from sagemaker_inference.default_inference_handler import DefaultInferenceHandler
from sagemaker_inference.default_handler_service import DefaultHandlerService
from sagemaker_inference.transformer import Transformer

logging.basicConfig(level=logging.INFO)


class InferenceHandler(DefaultInferenceHandler):
    @staticmethod
    def default_model_fn(model_dir):
        """Loads a model. For Scikit-learn, a default function to load a model is not provided.
        Users should provide customized model_fn() in script.
        Args:
            model_dir: a directory where model is saved.
        Returns: A Scikit-learn model.
        """
        raise NotImplementedError("Please provide a model_fn implementation.")

    @staticmethod
    def default_input_fn(input_data, content_type):
        """Takes request data and de-serializes the data into an object for prediction.
            When an InvokeEndpoint operation is made against an Endpoint running SageMaker model server,
            the model server receives two pieces of information:
                - The request Content-Type, for example "application/json"
                - The request data, which is at most 5 MB (5 * 1024 * 1024 bytes) in size.
            The input_fn is responsible to take the request data and pre-process it before prediction.
        Args:
            input_data (obj): the request data.
            content_type (str): the request Content-Type.
        Returns:
            (obj): data ready for prediction.
        """
        np_array = decoder.decode(input_data, content_type)

        if len(np_array.shape) == 1:
            np_array = np_array.reshape(1, -1)
        return np_array.astype(np.float32) if content_type in content_types.UTF8_TYPES else np_array

    @staticmethod
    def default_predict_fn(input_data, model):
        """A default predict_fn for Scikit-learn. Calls a model on data deserialized in input_fn.
        Args:
            input_data: input data (Numpy array) for prediction deserialized by input_fn
            model: Scikit-learn model loaded in memory by model_fn
        Returns: a prediction
        """
        output = model.predict(input_data)
        return output

    @staticmethod
    def default_output_fn(prediction, accept):
        """Function responsible to serialize the prediction for the response.
        Args:
            prediction (obj): prediction returned by predict_fn .
            accept (str): accept content-type expected by the client.
        Returns:
            (worker.Response): a Flask response object with the following args:
                * Args:
                    response: the serialized data to return
                    accept: the content-type that the data was transformed to.
        """
        return encoder.encode(prediction, accept), accept


class HandlerService(DefaultHandlerService):
    """Handler service that is executed by the model server.
    Determines specific default inference handlers to use based on the type MXNet model being used.
    This class extends ``DefaultHandlerService``, which define the following:
        - The ``handle`` method is invoked for all incoming inference requests to the model server.
        - The ``initialize`` method is invoked at model server start up.
    Based on: https://github.com/awslabs/mxnet-model-server/blob/master/docs/custom_service.md
    """
    def __init__(self):
        self._initialized = False
        transformer = Transformer(default_inference_handler=InferenceHandler())
        super(HandlerService, self).__init__(transformer=transformer)

    def initialize(self, context):
        """Initialize the model server.
        Args:
            context (obj): The SageMaker context object.
        """
        logging.info(f"### HandlerService initialize ###")
        logging.info(f"context: {context}")
        self._initialized = True
        super(HandlerService, self).initialize(context)

    @property
    def initialized(self):
        return self._initialized