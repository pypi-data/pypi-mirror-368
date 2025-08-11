#import tensorflow as tf
from tensorflow.keras.layers import * 
from tensorflow.keras import Model
from tensorflow.keras.optimizers import Adam
import numpy as np
from tensorflow.keras import ops


class ConvolutionBlock(Model):

	def __init__(self, block_input= None, num_filters = 256, kernel_size = 3, dilation_rate = 1, use_bias = False):

		self.block_input = block_input
		self.num_filters = num_filters
		self.kernel_size = kernel_size
		self.dilation_rate = dilation_rate
		self.use_bias = use_bias


		## Layers 

		self.conv1 = Conv2D(self.num_filters, kernel_size = self.kernel_size, dilation_rate = self.dilation_rate, 
			padding = 'same', use_bias = self.use_bias, kernel_initializer = tf.keras.initializers.HeNormal())

		self.bn1 = BatchNormalization()
		self.relu = ops.nn.relu()
		

	def call(self, x):

		x = self.conv1(x)
		x = self.bn1(x)
		x = self.relu(x)

		return x




# def convolution_block(

#     block_input,
#     num_filters=256,
#     kernel_size=3,
#     dilation_rate=1,
#     use_bias=False,
# ):
#     x = layers.Conv2D(
#         num_filters,
#         kernel_size=kernel_size,
#         dilation_rate=dilation_rate,
#         padding="same",
#         use_bias=use_bias,
#         kernel_initializer=tf.keras.initializers.HeNormal(),
#     )(block_input)
#     x = layers.BatchNormalization()(x)
#     return ops.nn.relu(x)

class DilatedSpatialPyramidPooling(Model):

	def __init__(self, dspp_input):
		self.dspp_input = dspp_input
		self.dims = dspp_input.shape

		self.avgpool1 = AveragePooling2D(pool_size = (self.dims[-3], self.dims[-2]))
		self.conv_block1 = ConvolutionBlock()


def DilatedSpatialPyramidPooling(dspp_input):
    dims = dspp_input.shape
    x = layers.AveragePooling2D(pool_size=(dims[-3], dims[-2]))(dspp_input)
    x = convolution_block(x, kernel_size=1, use_bias=True)
    out_pool = layers.UpSampling2D(
        size=(dims[-3] // x.shape[1], dims[-2] // x.shape[2]),
        interpolation="bilinear",
    )(x)

    out_1 = convolution_block(dspp_input, kernel_size=1, dilation_rate=1)
    out_6 = convolution_block(dspp_input, kernel_size=3, dilation_rate=6)
    out_12 = convolution_block(dspp_input, kernel_size=3, dilation_rate=12)
    out_18 = convolution_block(dspp_input, kernel_size=3, dilation_rate=18)

    x = layers.Concatenate(axis=-1)([out_pool, out_1, out_6, out_12, out_18])
    output = convolution_block(x, kernel_size=1)
    return output


def DeeplabV3Plus(image_size, num_classes):
    model_input = tf.keras.Input(shape=(image_size, image_size, 3))
    preprocessed = tf.keras.applications.resnet50.preprocess_input(model_input)
    resnet50 = tf.keras.applications.ResNet50(
        weights="imagenet", include_top=False, input_tensor=preprocessed
    )
    x = resnet50.get_layer("conv4_block6_2_relu").output
    x = DilatedSpatialPyramidPooling(x)

    input_a = layers.UpSampling2D(
        size=(image_size // 4 // x.shape[1], image_size // 4 // x.shape[2]),
        interpolation="bilinear",
    )(x)
    input_b = resnet50.get_layer("conv2_block3_2_relu").output
    input_b = convolution_block(input_b, num_filters=48, kernel_size=1)

    x = layers.Concatenate(axis=-1)([input_a, input_b])
    x = convolution_block(x)
    x = convolution_block(x)
    x = layers.UpSampling2D(
        size=(image_size // x.shape[1], image_size // x.shape[2]),
        interpolation="bilinear",
    )(x)
    model_output = layers.Conv2D(num_classes, kernel_size=(1, 1), padding="same")(x)
    return tf.keras.Model(inputs=model_input, outputs=model_output)


# model = UNet(input_size)
# model.create_model()
# model.compile_model()
# history = model.fit()

# def UNet(input_size = (256, 256, 1), pretrained_weights = None):
# 	inputs = Input(input_size)
# 	conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(inputs)
# 	conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv1)
# 	pool1 = MaxPool2D(pool_size=(2, 2))(conv1)
# 	conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool1)
# 	conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
# 	pool2 = MaxPool2D(pool_size=(2, 2))(conv2)
# 	conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool2)
# 	conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
# 	pool3 = MaxPool2D(pool_size=(2, 2))(conv3)
# 	conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool3)
# 	conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
# 	drop4 = Dropout(0.5)(conv4)
# 	pool4 = MaxPool2D(pool_size=(2, 2))(drop4)
# 	conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool4)
# 	conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
# 	drop5 = Dropout(0.5)(conv5)

# 	up6 = Conv2D(512, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(drop5))
# 	merge6 = Concatenate(axis = 3)([drop4,up6])
# 	conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge6)
# 	conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)
# 	up7 = Conv2D(256, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv6))
# 	merge7 = Concatenate(axis = 3)([conv3,up7])
# 	conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge7)
# 	conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)
# 	up8 = Conv2D(128, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv7))
# 	merge8 = Concatenate(axis = 3)([conv2,up8])
# 	conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge8)
# 	conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)

# 	up9 = Conv2D(64, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv8))
# 	merge9 = Concatenate(axis = 3)([conv1,up9])
# 	conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge9)
# 	conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
# 	conv9 = Conv2D(2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
# 	conv10 = Conv2D(1, 1, activation = 'sigmoid')(conv9)

# 	model = Model(inputs, conv10)

# 	model.compile(optimizer = Adam(learning_rate = 1e-4), loss = 'binary_crossentropy', metrics = ['accuracy'])#[dice_coefficient])#metrics = ['accuracy'])
# 	#model.compile(optimizer = Adam(learning_rate = 1e-4), loss = 'binary_crossentropy', metrics = [dice_coef])
# 	#model.compile(optimizer = Adam(learning_rate = 1e-4), loss = DiceLoss, metrics = [dice_coef])#[sm.metrics.iou_score()]))
# 	if(pretrained_weights):
# 		model.load_weights(pretrained_weights)

# 	return model
