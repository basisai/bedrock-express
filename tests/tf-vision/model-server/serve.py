"""
Script for serving.
"""
from PIL import Image
import tensorflow as tf
import tensorflow_hub as hub


def pre_process(http_body, files):
    return [Image.open(files["image"]).convert('RGB').resize((299, 299))]


class Model:
    def __init__(self):
        self.model = tf.keras.Sequential([
            hub.KerasLayer("https://tfhub.dev/google/imagenet/inception_resnet_v2/classification/4")
        ])
        self.model.build([None, 299, 299, 3])

    def predict(self, features):
        """Makes an inference using the model.

        :param features: An iterable of array-like of shape (height, width, 3)
        :type features: Iterable
        :return: Class label from ImageNet
        :rtype: int
        """
        img = tf.image.convert_image_dtype(features, tf.float32)[tf.newaxis, ...]
        logits = self.model(img)
        return tf.argmax(logits[0]).numpy() - 1 # Labels are 1-indexed


if __name__ == "__main__":
    model = Model()
    print(model.predict(np.array(Image.open("../../208.jpg"))))
