from tensorflow.keras.layers import Conv2D, BatchNormalization, Activation, MaxPool2D, Conv2DTranspose, Concatenate, Input
from tensorflow.keras.models import Model
from tensorflow.keras.applications import VGG19
import tensorflow as tf

class ConvolutionBlock(Model):

    def __init__(self, filters):

        super(ConvolutionBlock, self).__init__()
        self.conv1 = Conv2D(filters, 3, padding = 'same')
        self.bn1 = BatchNormalization()
        self.act1 = Activation("relu")

        self.conv2 = Conv2D(filters, 3, padding = 'same')
        self.bn2 = BatchNormalization()
        self.act2 = Activation("relu")

    def call(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.act1(x)

        x = self.conv2(x)
        x = self.bn2(x)
        x = self.act2(x)

        return x


from tensorflow.keras.applications import VGG19


class UNETVGG19(Model):

    def __init__(self, input_shape):
        super(UNETVGG19, self).__init__()
        self.input_shape = input_shape
        vgg19 = VGG19(include_top = False, weights = 'imagenet', input_shape = self.input_shape)
        encoder = Model(inputs = vgg19.input, outputs = vgg19.get_layer("block5_conv4").output)
        #print(encoder.summary())
        #print(len(encoder.layers))

        self.eb1_layers = encoder.layers[0 : 3]

        self.eb1_input = encoder.input#tf.keras.Model(inputs = encoder.input, outputs = self.eb1_layers[-1].output, )
        self.eb1_output = self.eb1_layers[-1].output
        #print(self.eb1_layers)
        #print(len(self.eb1_layers))
        self.eb2_layers = encoder.layers[3 : 6]
        self.eb2_input = self.eb2_layers[0].input
        self.eb2_output = self.eb2_layers[-1].output
        #print(self.eb2_layers)
        #print(len(self.eb2_layers))
        self.eb3_layers = encoder.layers[6 : 11]
        self.eb3_input = self.eb3_layers[0].input
        self.eb3_output = self.eb3_layers[-1].output
        #print(self.eb3_layers)
        #print(len(self.eb3_layers))
        self.eb4_layers = encoder.layers[11 : 16]
        self.eb4_input = self.eb4_layers[0].input
        self.eb4_output = self.eb4_layers[-1].output
        #print(self.eb4_layers)
        #print(len(self.eb4_layers))
        self.eb5_layers = encoder.layers[16 : 21]
        self.eb5_input = self.eb5_layers[0].input
        self.eb5_output = self.eb5_layers[-1].output
        #print(self.eb5_layers)
        #print(len(self.eb5_layers))

        ## Decoders

        self.conv2dt1 = Conv2DTranspose(512, (2,2 ), strides = 2, padding = 'same')
        self.conv_block1 = ConvolutionBlock(512)

        self.conv2dt2 = Conv2DTranspose(256, (2,2), strides = 2, padding = 'same')
        self.conv_block2 = ConvolutionBlock(256)

        self.conv2dt3 = Conv2DTranspose(128, (2, 2), strides = 2, padding = 'same')
        self.conv_block3 = ConvolutionBlock(128)

        self.conv2dt4 = Conv2DTranspose(64, (2, 2), strides = 2, padding = 'same')
        self.conv_block4 = ConvolutionBlock(64)

        self.last_conv = Conv2D(1, 1, padding = 'same', activation = 'sigmoid')

        
    
    def call(self, inputs):
        x = inputs

        eb1_model = tf.keras.Model(inputs = self.eb1_input, outputs = self.eb1_output, name = 'eb1_model')
        b1 = eb1_model(x)

        eb2_model = tf.keras.Model(inputs = self.eb2_input, outputs = self.eb2_output, name = 'eb2_model')
        b2 = eb2_model(b1)

        eb3_model = tf.keras.Model(inputs = self.eb3_input, outputs = self.eb3_output, name = 'eb3_model')
        b3 = eb3_model(b2)

        eb4_model = tf.keras.Model(inputs = self.eb4_input, outputs = self.eb4_output, name = 'eb4_model')
        b4 = eb4_model(b3)

        eb5_model = tf.keras.Model(inputs = self.eb5_input, outputs = self.eb5_output, name = 'eb5_model')
        b5 = eb5_model(b4)

        d1 = self.conv2dt1(b5)

        d1 = Concatenate()([d1, b4])
        d1 = self.conv_block1(d1)

        d2 = self.conv2dt2(d1)
        d2 = Concatenate()([d2, b3])
        d2 = self.conv_block2(d2)

        d3 = self.conv2dt3(d2)
        d3 = Concatenate()([d3, b2])
        d3 = self.conv_block3(d3)

        d4 = self.conv2dt4(d3)
        d4 = Concatenate()([d4, b1])
        d4 = self.conv_block4(d4)

        outputs = self.last_conv(d4)

        return outputs
        
        

    def summary(self):
        x = Input(shape = self.input_shape)
        return Model(inputs = [x], outputs = self.call(x)).summary()