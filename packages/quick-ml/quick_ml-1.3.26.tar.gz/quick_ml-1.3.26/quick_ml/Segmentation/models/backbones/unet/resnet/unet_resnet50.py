from tensorflow.keras.layers import *
import tensorflow as tf

from tensorflow.keras.models import Model
from tensorflow.keras.applications import ResNet50

class ConvolutionBlock(Model):

    def __init__(self, num_filters):
        super(ConvolutionBlock, self).__init__()
        self.conv1 = Conv2D(num_filters, 3, padding = 'same')
        self.bn1 = BatchNormalization()
        self.act1 = Activation("relu")

        self.conv2 = Conv2D(num_filters, 3, padding = 'same')
        self.bn2 = BatchNormalization()
        self.act2 = Activation("relu")

    def call(self, inputs):

        x = self.conv1(inputs)
        x = self.bn1(x)
        x = self.act1(x)

        x = self.conv2(x)
        x = self.bn2(x)
        x = self.act2(x)

        return x


class UNETResNet50(Model):

    def __init__(self, input_shape = (512, 512, 3), weights = 'imagenet'):

        super(UNETResNet50, self).__init__()

        self.input_shape = input_shape

        resnet50 = ResNet50(include_top = False, weights = weights, input_shape = self.input_shape)

        encoder = tf.keras.Model(inputs = resnet50.input, outputs = resnet50.get_layer("conv4_block6_out").output)

        #s1 = resnet50.layers[0].output#resnet50.get_layer("input_1").output           ## (512 x 512)
        #s2 = resnet50.get_layer("conv1_relu").output        ## (256 x 256)
        #s3 = resnet50.get_layer("conv2_block3_out").output  ## (128 x 128)
        #s4 = resnet50.get_layer("conv3_block4_out").output  ## (64 x 64)
 
        #""" Bridge """
        #b1 = resnet50.get_layer("conv4_block6_out").output
        self.eb1_layers = encoder.layers[0]

        self.eb1_inp = encoder.input
        self.eb1_out = encoder.layers[0].output

        self.eb2_layers = encoder.layers[1 : 5]

        self.eb2_inp = self.eb2_layers[0].input
        self.eb2_out = self.eb2_layers[-1].output

        self.eb3_layers = encoder.layers[5 : 39]

        self.eb3_inp = self.eb3_layers[0].input
        self.eb3_out = self.eb3_layers[-1].output

        self.eb4_layers = encoder.layers[39 : 81]

        self.eb4_inp = self.eb4_layers[0].input
        self.eb4_out = self.eb4_layers[-1].output

        self.eb5_layers = encoder.layers[81 : 143]

        self.eb5_inp = self.eb5_layers[0].input
        self.eb5_out = self.eb5_layers[-1].output

        # Decoders
        self.conv2dt1 = Conv2DTranspose(512, (2, 2), strides = 2, padding = 'same')
        self.conv_block1 = ConvolutionBlock(512)

        #self.maxpool1 = MaxPool2D((2,2))

        self.conv2dt2 = Conv2DTranspose(256, (2, 2), strides = 2, padding = 'same')
        self.conv_block2 = ConvolutionBlock(256)

        #self.maxpool2 = MaxPool2D((2,2))

        self.conv2dt3 = Conv2DTranspose(128, (2, 2), strides = 2, padding = 'same')
        self.conv_block3 = ConvolutionBlock(128)

        #self.maxpool3 = MaxPool2D((2,2))

        self.conv2dt4 = Conv2DTranspose(64, (2, 2), strides = 2, padding = 'same')
        self.conv_block4 = ConvolutionBlock(64)

        #self.maxpool4 = MaxPool2D((2,2))

        #self.maxpool5 = MaxPool2D((2,2))
        
        # Last conv
        self.last_conv = Conv2D(1, 1, padding = 'same', activation = 'sigmoid')

    def call(self, inputs):

        x = inputs
        eb1_model = tf.keras.Model(inputs = self.eb1_inp, outputs = self.eb1_out, name = 'eb1_model')
        b1 = eb1_model(inputs)

        eb2_model = tf.keras.Model(inputs = self.eb2_inp, outputs = self.eb2_out, name = 'eb2_model')
        b2 = eb2_model(b1)

        eb3_model = tf.keras.Model(inputs = self.eb3_inp, outputs = self.eb3_out, name = 'eb3_model')
        b3 = eb3_model(b2)

        eb4_model = tf.keras.Model(inputs = self.eb4_inp, outputs = self.eb4_out, name = 'eb4_model')
        b4 = eb4_model(b3)

        eb5_model = tf.keras.Model(inputs = self.eb5_inp, outputs = self.eb5_out, name = 'eb5_model')
        b5 = eb5_model(b4)
        
        d1 = self.conv2dt1(b5)
        #d1 = Concatenate()([d1, self.s4])        
        d1 = Concatenate()([d1, b4])        
        d1 = self.conv_block1(d1)

        d2 = self.conv2dt2(d1)
        #d2 = Concatenate()([d2, self.s3])
        d2 = Concatenate()([d2, b3])
        d2 = self.conv_block2(d2)
        
        
        d3 = self.conv2dt3(d2)
        #d3 = Concatenate()([d3, self.s2])
        d3 = Concatenate()([d3, b2])
        d3 = self.conv_block3(d3)

        
        d4 = self.conv2dt4(d3)
        #d4 = Concatenate()([d4, self.s1])
        d4 = Concatenate()([d4, b1])
        d4 = self.conv_block4(d4)
        
        outputs = self.last_conv(d4)
        return outputs

    def summary(self):
        x = Input(shape = self.input_shape)
        return Model(inputs = [x], outputs = self.call(x)).summary()