import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout

from .....experimental.utils.torch2tf.layers import AdaptiveAvgpooling2D
from .....experimental.utils.torch2tf.layers.conv import Convolution2D
from .....experimental.utils.torch2tf.layers.pooling import MAXPOOL2D
from .....experimental.utils.torch2tf.layers.linear import LinearDense
from ..download_model_weights import download_model_weights

import numpy as np

class Features(tf.keras.Model):

    def __init__(self) -> None:

        super().__init__()

        # features COnv2D 0, 3, 6, 8, 11, 13, 16, 18
        self.conv1 = Convolution2D(64, (3, 3), (1,1), (1,1))

        self.act1 = tf.keras.layers.ReLU()
        self.maxpool1 = MAXPOOL2D((2,2), 2, 0, 1)

        self.conv2 = Convolution2D(128, (3, 3), (1,1), (1,1))
        self.act2 = tf.keras.layers.ReLU()
        self.maxpool2 = MAXPOOL2D((2,2), 2, 0, 1)

        self.conv3 = Convolution2D(256, (3, 3), (1,1), (1,1))
        self.act3 = tf.keras.layers.ReLU()

        self.conv4 = Convolution2D(256, (3,3), (1,1), (1,1))
        self.act4 = tf.keras.layers.ReLU()

        self.maxpool3 = MAXPOOL2D((2,2), 2, 0, 1)

        self.conv5 = Convolution2D(512, (3,3), (1,1), (1,1))
        self.act5 = tf.keras.layers.ReLU()

        self.conv6 = Convolution2D(512, (3,3), (1,1), (1,1))
        self.act6 = tf.keras.layers.ReLU()

        self.maxpool4 = MAXPOOL2D((2,2), 2, 0, 1)

        self.conv7 = Convolution2D(512, (3,3), (1,1), (1,1))
        self.act7 = tf.keras.layers.ReLU()

        self.conv8 = Convolution2D(512, (3,3), (1,1), (1,1))
        self.act8 = tf.keras.layers.ReLU()
        self.maxpool5 = MAXPOOL2D((2,2), 2, 0, 1)

    def call(self, x):
        x = self.conv1(x)
        x = self.act1(x)
        x = self.maxpool1(x)

        x = self.conv2(x)

        x = self.act2(x)
        x = self.maxpool2(x)

        x = self.conv3(x)
        x = self.act3(x)

        x = self.conv4(x)
        x = self.act4(x)

        x = self.maxpool3(x)

        x = self.conv5(x)
        x = self.act5(x)

        x = self.conv6(x)
        x = self.act6(x)

        x = self.maxpool4(x)

        x = self.conv7(x)
        x = self.act7(x)

        x = self.conv8(x)
        x = self.act8(x)
        x = self.maxpool5(x)
        return x


class Classifier(tf.keras.Model):

    def __init__(self, num_classes = 1000):
        super(Classifier, self).__init__()


        self.linear1 = LinearDense(4096)

        self.act1 = tf.keras.layers.ReLU()
        self.dropout1 = Dropout(0.5)

        self.linear2 = LinearDense(4096)
        self.act2 = tf.keras.layers.ReLU()
        self.dropout2 = Dropout(0.5)

        self.num_classes = num_classes

        if self.num_classes > 2:
            self.linear3 = LinearDense(self.num_classes, activation="softmax")
        else:
            self.linear3 = LinearDense(1, activation = 'sigmoid')


    def call(self, x):

        x = tf.transpose(x, (0, 3, 1, 2))

        x = tf.keras.layers.Flatten()(x)
        x = self.linear1(x)
        x = self.act1(x)
        x = self.dropout1(x)

        x = self.linear2(x)
        x = self.act2(x)
        x = self.dropout2(x)

        x = self.linear3(x)

        return x


class VGG11(tf.keras.Model):

    def __init__(self, img_size = (224,224, 3), num_classes = 1000, weights = None):

        super(VGG11, self).__init__()
        self.img_size = img_size
        self.num_classes = num_classes

        self.features = Features()
        self.avg_pool = AdaptiveAvgpooling2D((7,7))
        self.classifier = Classifier(num_classes)

        if weights == 'imagenet':
            ## Weights sourced from PyTorch's Official Torchvision VGG11 Model IMAGENET1K_V1

            x = np.random.rand(1, 224, 224, 3)
            self.build((None, 224, 224, 3))
            self.call(x)

            self.load_weights(download_model_weights('vgg11', True, 'imagenet'))


    def call(self, x):
        x = self.features(x)
        x = self.avg_pool(x)

        x = self.classifier(x)

        return x

    def summary(
        self,
        line_length=None,
        positions=None,
        print_fn=None,
        expand_nested=False,
        show_trainable=False,
        layer_range=None,
    ):
        x = tf.keras.layers.Input(shape = self.img_size)
        return tf.keras.Model(inputs = x, outputs = self.call(x)).summary()

 
