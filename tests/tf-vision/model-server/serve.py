"""
Script for serving.
"""
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from bedrock_client.bedrock.model import BaseModel
from PIL import Image


class Model(BaseModel):
    def __init__(self):
        self.model = tf.keras.Sequential(
            [
                hub.KerasLayer(
                    "https://tfhub.dev/google/imagenet/inception_resnet_v2/classification/4"
                )
            ]
        )
        self.model.build([None, 299, 299, 3])

    def pre_process(self, http_body, files):
        features = np.array(Image.open(files["image"]).convert("RGB").resize((299, 299)))
        return tf.image.convert_image_dtype(features, tf.float32)[tf.newaxis, ...]

    def predict(self, features):
        """Makes an inference using the model.

        :param features: An iterable of array-like of shape (height, width, 3)
        :type features: Iterable
        :return: Class label from ImageNet
        :rtype: int
        """
        logits = self.model(features)
        # Labels are 1-indexed
        return [int(tf.argmax(sample).numpy() - 1) for sample in logits]
