from tensorflow.keras.layers import Input, Conv2D, ZeroPadding2D, UpSampling2D, Dense, concatenate, Conv2DTranspose
from tensorflow.keras.layers import MaxPooling2D, GlobalAveragePooling2D, MaxPooling2D

import numpy as np


class UNetPlusPlus:

	def __init__(self, input_shape = (512, 512, 3), num_classes = 2, deep_supervision = True):
		pass
	def call(self, x):
		pass 

def standard_unit(input_tensor, stage, nb_filter, kernel_size=3):

	act = 'elu'

	x = Conv2D(nb_filter, (kernel_size, kernel_size), activation=act, name='conv'+stage+'_1', kernel_initializer = 'he_normal', padding='same', kernel_regularizer=l2(1e-4))(input_tensor)
	x = Dropout(dropout_rate, name='dp'+stage+'_1')(x)
	x = Conv2D(nb_filter, (kernel_size, kernel_size), activation=act, name='conv'+stage+'_2', kernel_initializer = 'he_normal', padding='same', kernel_regularizer=l2(1e-4))(x)
	x = Dropout(dropout_rate, name='dp'+stage+'_2')(x)

	return x


def Nest_Net(img_rows, img_cols, color_type=1, num_class=1, deep_supervision=False):

	nb_filter = [32,64,128,256,512]
	act = 'elu'

	# # Handle Dimension Ordering for different backends
	# global bn_axis
	# if K.image_dim_ordering() == 'tf':
	#   bn_axis = 3
	#   img_input = Input(shape=(img_rows, img_cols, color_type), name='main_input')
	# else:
	#   bn_axis = 1
	#   img_input = Input(shape=(color_type, img_rows, img_cols), name='main_input')

	conv1_1 = standard_unit(img_input, stage='11', nb_filter=nb_filter[0])
	pool1 = MaxPooling2D((2, 2), strides=(2, 2), name='pool1')(conv1_1)

	conv2_1 = standard_unit(pool1, stage='21', nb_filter=nb_filter[1])
	pool2 = MaxPooling2D((2, 2), strides=(2, 2), name='pool2')(conv2_1)

	up1_2 = Conv2DTranspose(nb_filter[0], (2, 2), strides=(2, 2), name='up12', padding='same')(conv2_1)
	conv1_2 = concatenate([up1_2, conv1_1], name='merge12', axis=bn_axis)
	conv1_2 = standard_unit(conv1_2, stage='12', nb_filter=nb_filter[0])

	conv3_1 = standard_unit(pool2, stage='31', nb_filter=nb_filter[2])
	pool3 = MaxPooling2D((2, 2), strides=(2, 2), name='pool3')(conv3_1)

	up2_2 = Conv2DTranspose(nb_filter[1], (2, 2), strides=(2, 2), name='up22', padding='same')(conv3_1)
	conv2_2 = concatenate([up2_2, conv2_1], name='merge22', axis=bn_axis)
	conv2_2 = standard_unit(conv2_2, stage='22', nb_filter=nb_filter[1])

	up1_3 = Conv2DTranspose(nb_filter[0], (2, 2), strides=(2, 2), name='up13', padding='same')(conv2_2)
	conv1_3 = concatenate([up1_3, conv1_1, conv1_2], name='merge13', axis=bn_axis)
	conv1_3 = standard_unit(conv1_3, stage='13', nb_filter=nb_filter[0])

	conv4_1 = standard_unit(pool3, stage='41', nb_filter=nb_filter[3])
	pool4 = MaxPooling2D((2, 2), strides=(2, 2), name='pool4')(conv4_1)

	up3_2 = Conv2DTranspose(nb_filter[2], (2, 2), strides=(2, 2), name='up32', padding='same')(conv4_1)
	conv3_2 = concatenate([up3_2, conv3_1], name='merge32', axis=bn_axis)
	conv3_2 = standard_unit(conv3_2, stage='32', nb_filter=nb_filter[2])

	up2_3 = Conv2DTranspose(nb_filter[1], (2, 2), strides=(2, 2), name='up23', padding='same')(conv3_2)
	conv2_3 = concatenate([up2_3, conv2_1, conv2_2], name='merge23', axis=bn_axis)
	conv2_3 = standard_unit(conv2_3, stage='23', nb_filter=nb_filter[1])

	up1_4 = Conv2DTranspose(nb_filter[0], (2, 2), strides=(2, 2), name='up14', padding='same')(conv2_3)
	conv1_4 = concatenate([up1_4, conv1_1, conv1_2, conv1_3], name='merge14', axis=bn_axis)
	conv1_4 = standard_unit(conv1_4, stage='14', nb_filter=nb_filter[0])

	conv5_1 = standard_unit(pool4, stage='51', nb_filter=nb_filter[4])

	up4_2 = Conv2DTranspose(nb_filter[3], (2, 2), strides=(2, 2), name='up42', padding='same')(conv5_1)
	conv4_2 = concatenate([up4_2, conv4_1], name='merge42', axis=bn_axis)
	conv4_2 = standard_unit(conv4_2, stage='42', nb_filter=nb_filter[3])

	up3_3 = Conv2DTranspose(nb_filter[2], (2, 2), strides=(2, 2), name='up33', padding='same')(conv4_2)
	conv3_3 = concatenate([up3_3, conv3_1, conv3_2], name='merge33', axis=bn_axis)
	conv3_3 = standard_unit(conv3_3, stage='33', nb_filter=nb_filter[2])

	up2_4 = Conv2DTranspose(nb_filter[1], (2, 2), strides=(2, 2), name='up24', padding='same')(conv3_3)
	conv2_4 = concatenate([up2_4, conv2_1, conv2_2, conv2_3], name='merge24', axis=bn_axis)
	conv2_4 = standard_unit(conv2_4, stage='24', nb_filter=nb_filter[1])

	up1_5 = Conv2DTranspose(nb_filter[0], (2, 2), strides=(2, 2), name='up15', padding='same')(conv2_4)
	conv1_5 = concatenate([up1_5, conv1_1, conv1_2, conv1_3, conv1_4], name='merge15', axis=bn_axis)
	conv1_5 = standard_unit(conv1_5, stage='15', nb_filter=nb_filter[0])

	nestnet_output_1 = Conv2D(num_class, (1, 1), activation='sigmoid', name='output_1', kernel_initializer = 'he_normal', padding='same', kernel_regularizer=l2(1e-4))(conv1_2)
	nestnet_output_2 = Conv2D(num_class, (1, 1), activation='sigmoid', name='output_2', kernel_initializer = 'he_normal', padding='same', kernel_regularizer=l2(1e-4))(conv1_3)
	nestnet_output_3 = Conv2D(num_class, (1, 1), activation='sigmoid', name='output_3', kernel_initializer = 'he_normal', padding='same', kernel_regularizer=l2(1e-4))(conv1_4)
	nestnet_output_4 = Conv2D(num_class, (1, 1), activation='sigmoid', name='output_4', kernel_initializer = 'he_normal', padding='same', kernel_regularizer=l2(1e-4))(conv1_5)

	if deep_supervision:
		model = Model(input=img_input, output=[nestnet_output_1,
											   nestnet_output_2,
											   nestnet_output_3,
											   nestnet_output_4])
	else:
		model = Model(input=img_input, output=[nestnet_output_4])

	return model


### GFG 


import tensorflow as tf 

# Defining the Convolutional Block
def conv_block(inputs, num_filters):
	# Applying the sequence of Convolutional, Batch Normalization
	# and Activation Layers to the input tensor
	x = tf.keras.Sequential([
		# Convolutional Layer
		tf.keras.layers.Conv2D(num_filters, 3, padding='same'),
		# Batch Normalization Layer
		tf.keras.layers.BatchNormalization(),
		# Activation Layer
		tf.keras.layers.Activation('relu'),
		# Convolutional Layer
		tf.keras.layers.Conv2D(num_filters, 3, padding='same'),
		# Batch Normalization Layer
		tf.keras.layers.BatchNormalization(),
		# Activation Layer
		tf.keras.layers.Activation('relu')
	])(inputs)

	# Returning the output of the Convolutional Block
	return x



# Defining the Unet++ Model
def unet_plus_plus_model(input_shape=(256, 256, 3), num_classes=1, deep_supervision=True):
	inputs = tf.keras.layers.Input(shape=input_shape)

	# Encoding Path
	x_00 = conv_block(inputs, 64)
	x_10 = conv_block(tf.keras.layers.MaxPooling2D()(x_00), 128)
	x_20 = conv_block(tf.keras.layers.MaxPooling2D()(x_10), 256)
	x_30 = conv_block(tf.keras.layers.MaxPooling2D()(x_20), 512)
	x_40 = conv_block(tf.keras.layers.MaxPooling2D()(x_30), 1024)

	# Nested Decoding Path
	x_01 = conv_block(tf.keras.layers.concatenate(
		[x_00, tf.keras.layers.UpSampling2D()(x_10)]), 64)
	x_11 = conv_block(tf.keras.layers.concatenate(
		[x_10, tf.keras.layers.UpSampling2D()(x_20)]), 128)
	x_21 = conv_block(tf.keras.layers.concatenate(
		[x_20, tf.keras.layers.UpSampling2D()(x_30)]), 256)
	x_31 = conv_block(tf.keras.layers.concatenate(
		[x_30, tf.keras.layers.UpSampling2D()(x_40)]), 512)

	x_02 = conv_block(tf.keras.layers.concatenate(
		[x_00, x_01, tf.keras.layers.UpSampling2D()(x_11)]), 64)
	x_12 = conv_block(tf.keras.layers.concatenate(
		[x_10, x_11, tf.keras.layers.UpSampling2D()(x_21)]), 128)
	x_22 = conv_block(tf.keras.layers.concatenate(
		[x_20, x_21, tf.keras.layers.UpSampling2D()(x_31)]), 256)

	x_03 = conv_block(tf.keras.layers.concatenate(
		[x_00, x_01, x_02, tf.keras.layers.UpSampling2D()(x_12)]), 64)
	x_13 = conv_block(tf.keras.layers.concatenate(
		[x_10, x_11, x_12, tf.keras.layers.UpSampling2D()(x_22)]), 128)

	x_04 = conv_block(tf.keras.layers.concatenate(
		[x_00, x_01, x_02, x_03, tf.keras.layers.UpSampling2D()(x_13)]), 64)

	# Deep Supervision Path
	# If deep supervision is enabled, then the model will output the segmentation maps
	# at each stage of the decoding path
	if deep_supervision:
		outputs = [
			tf.keras.layers.Conv2D(num_classes, 1)(x_01),
			tf.keras.layers.Conv2D(num_classes, 1)(x_02),
			tf.keras.layers.Conv2D(num_classes, 1)(x_03),
			tf.keras.layers.Conv2D(num_classes, 1)(x_04)
		]
		# Concatenating the segmentation maps
		outputs = tf.keras.layers.concatenate(outputs, axis=0)

	# If deep supervision is disabled, then the model will output the final segmentation map
	# which is the segmentation map at the end of the decoding path
	else:
		outputs = tf.keras.layers.Conv2D(num_classes, 1)(x_04)

	# Creating the model
	model = tf.keras.Model(
		inputs=inputs, outputs=outputs, name='Unet_plus_plus')

	# Returning the model
	return model


from tensorflow.keras.layers import * 
from tensorflow.keras import Model
import tensorflow as tf 


class ConvBlock(Model):

    def __init__(self, num_filters):

        super().__init__()

        self.conv_1_1 = tf.keras.layers.Conv2D(num_filters, 3, padding='same')
        self.bn_1_1 = tf.keras.layers.BatchNormalization()
        self.act_1_1 = tf.keras.layers.Activation('relu')

        self.conv_1_2 = tf.keras.layers.Conv2D(num_filters, 3, padding = 'same')
        self.bn_1_2 = tf.keras.layers.BatchNormalization()
        self.act_1_2 = tf.keras.layers.Activation('relu')

    def call(self, inputs):

        conv1 = self.conv_1_1(inputs)
        conv1 = self.bn_1_1(conv1)
        conv1 = self.act_1_1(conv1)
        conv1 = self.conv_1_2(conv1)
        conv1 = self.bn_1_2(conv1)
        conv1 = self.act_1_2(conv1)
        return conv1

    
class UnetPlusPlus:

    def __init__(self, input_shape=(256, 256, 3), num_classes=1, deep_supervision=True):
        self.input_size = input_shape
        self.num_classes = num_classes 
        self.deep_supervision = deep_supervision


        ## Conv Block with 64 filters
        # self.conv_1_1 = tf.keras.layers.Conv2D(64, 3, padding='same')
        # self.bn_1_1 = tf.keras.layers.BatchNormalization()
        # self.act_1_1 = tf.keras.layers.Activation('relu')

        # self.conv_1_2 = tf.keras.layers.Conv2D(64, 3, padding = 'same')
        # self.bn_1_2 = tf.keras.layers.BatchNormalization()
        # self.act_1_2 = tf.keras.layers.Activation('relu')
        self.conv_block1 = ConvBlock(64)

        self.max_pool_1 = tf.keras.layers.MaxPooling2D()

        ## Conv BLock 2
        # self.conv_2_1 = tf.keras.layers.Conv2D(128, 3, padding='same')
        # self.bn_2_1 = tf.keras.layers.BatchNormalization()
        # self.act_2_1 = tf.keras.layers.Activation('relu')

        # self.conv_2_2 = tf.keras.layers.Conv2D(128, 3, padding = 'same')
        # self.bn_2_2 = tf.keras.layers.BatchNormalization()
        # self.act_2_2 = tf.keras.layers.Activation('relu')
        self.conv_block2 = ConvBlock(128)
        self.max_pool_2 = tf.keras.layers.MaxPooling2D()

        ## Conv Block 3
        # self.conv_3_1 = tf.keras.layers.Conv2D(256, 3, padding='same')
        # self.bn_3_1 = tf.keras.layers.BatchNormalization()
        # self.act_3_1 = tf.keras.layers.Activation('relu')

        # self.conv_3_2 = tf.keras.layers.Conv2D(256, 3, padding = 'same')
        # self.bn_3_2 = tf.keras.layers.BatchNormalization()
        # self.act_3_2 = tf.keras.layers.Activation('relu')
        self.conv_block3 = ConvBlock(256)
        self.max_pool_3 = tf.keras.layers.MaxPooling2D()


        ## Conv Block 4
        # self.conv_4_1 = tf.keras.layers.Conv2D(512, 3, padding='same')
        # self.bn_4_1 = tf.keras.layers.BatchNormalization()
        # self.act_4_1 = tf.keras.layers.Activation('relu')

        # self.conv_4_2 = tf.keras.layers.Conv2D(512, 3, padding = 'same')
        # self.bn_4_2 = tf.keras.layers.BatchNormalization()
        # self.act_4_2 = tf.keras.layers.Activation('relu')
        self.conv_block4 = ConvBlock(512)
        self.max_pool_4 = tf.keras.layers.MaxPooling2D()

        ## Conv Block 5
        # self.conv_5_1 = tf.keras.layers.Conv2D(1024, 3, padding='same')
        # self.bn_5_1 = tf.keras.layers.BatchNormalization()
        # self.act_5_1 = tf.keras.layers.Activation('relu')

        # self.conv_5_2 = tf.keras.layers.Conv2D(1024, 3, padding = 'same')
        # self.bn_5_2 = tf.keras.layers.BatchNormalization()
        # self.act_5_2 = tf.keras.layers.Activation('relu')
        self.conv_block5 = ConvBlock(1024)
        self.max_pool_5 = tf.keras.layers.MaxPooling2D()

        ## Nested 
        
        self.up_1 = tf.keras.layers.UpSampling2D()
        
        ## Nested Conv Block 1 [6]
        # self.conv_6_1 = tf.keras.layers.Conv2D(64, 3, padding='same')
        # self.bn_6_1 = tf.keras.layers.BatchNormalization()
        # self.act_6_1 = tf.keras.layers.Activation('relu')

        # self.conv_6_2 = tf.keras.layers.Conv2D(64, 3, padding = 'same')
        # self.bn_6_2 = tf.keras.layers.BatchNormalization()
        # self.act_6_2 = tf.keras.layers.Activation('relu')
        self.conv_block6 = ConvBlock(64)

        ## Nested Conv Block 2 [7]

        self.up_2 = tf.keras.layers.UpSampling2D()

        # self.conv_7_1 = tf.keras.layers.Conv2D(128, 3, padding='same')
        # self.bn_7_1 = tf.keras.layers.BatchNormalization()
        # self.act_7_1 = tf.keras.layers.Activation('relu')

        # self.conv_7_2 = tf.keras.layers.Conv2D(128, 3, padding = 'same')
        # self.bn_7_2 = tf.keras.layers.BatchNormalization()
        # self.act_7_2 = tf.keras.layers.Activation('relu')
        self.conv_block7 = ConvBlock(128)

        ## Nested Conv Block 3 [8]

        self.up_3 = tf.keras.layers.UpSampling2D()

        # self.conv_8_1 = tf.keras.layers.Conv2D(256, 3, padding='same')
        # self.bn_8_1 = tf.keras.layers.BatchNormalization()
        # self.act_8_1 = tf.keras.layers.Activation('relu')

        # self.conv_8_2 = tf.keras.layers.Conv2D(256, 3, padding = 'same')
        # self.bn_8_2 = tf.keras.layers.BatchNormalization()
        # self.act_8_2 = tf.keras.layers.Activation('relu')
        self.conv_block8 = ConvBlock(256)

        ## Nested Conv Block 4 [9]

        self.up_4 = tf.keras.layers.UpSampling2D()

        # self.conv_9_1 = tf.keras.layers.Conv2D(512, 3, padding='same')
        # self.bn_9_1 = tf.keras.layers.BatchNormalization()
        # self.act_9_1 = tf.keras.layers.Activation('relu')

        # self.conv_9_2 = tf.keras.layers.Conv2D(512, 3, padding = 'same')
        # self.bn_9_2 = tf.keras.layers.BatchNormalization()
        # self.act_9_2 = tf.keras.layers.Activation('relu')
        self.conv_block9 = ConvBlock(512)

        ### Double Concats
        ## Nested Conv Block 5 [10]

        self.up_5 = tf.keras.layers.UpSampling2D()

        # self.conv_10_1 = tf.keras.layers.Conv2D(64, 3, padding='same')
        # self.bn_10_1 = tf.keras.layers.BatchNormalization()
        # self.act_10_1 = tf.keras.layers.Activation('relu')

        # self.conv_10_2 = tf.keras.layers.Conv2D(64, 3, padding = 'same')
        # self.bn_10_2 = tf.keras.layers.BatchNormalization()
        # self.act_10_2 = tf.keras.layers.Activation('relu')
        self.conv_block10 = ConvBlock(64)


        ## Nested Conv Block 6 [11]
        self.up_6 = tf.keras.layers.UpSampling2D()

        # self.conv_11_1 = tf.keras.layers.Conv2D(128, 3, padding='same')
        # self.bn_11_1 = tf.keras.layers.BatchNormalization()
        # self.act_11_1 = tf.keras.layers.Activation('relu')

        # self.conv_11_2 = tf.keras.layers.Conv2D(128, 3, padding = 'same')
        # self.bn_11_2 = tf.keras.layers.BatchNormalization()
        # self.act_11_2 = tf.keras.layers.Activation('relu')
        self.conv_block11 = ConvBlock(128)

        ## Nested Conv Block 7 [12]
        self.up_7 = tf.keras.layers.UpSampling2D()

        # self.conv_12_1 = tf.keras.layers.Conv2D(256, 3, padding='same')
        # self.bn_12_1 = tf.keras.layers.BatchNormalization()
        # self.act_12_1 = tf.keras.layers.Activation('relu')

        # self.conv_12_2 = tf.keras.layers.Conv2D(256, 3, padding = 'same')
        # self.bn_12_2 = tf.keras.layers.BatchNormalization()
        # self.act_12_2 = tf.keras.layers.Activation('relu')
        self.conv_block12 = ConvBlock(256)

        ### Triple Concats
        ## Nested Conv Block 8 [13]
        self.up_8 = tf.keras.layers.UpSampling2D()

        # self.conv_13_1 = tf.keras.layers.Conv2D(64, 3, padding='same')
        # self.bn_13_1 = tf.keras.layers.BatchNormalization()
        # self.act_13_1 = tf.keras.layers.Activation('relu')

        # self.conv_13_2 = tf.keras.layers.Conv2D(64, 3, padding = 'same')
        # self.bn_13_2 = tf.keras.layers.BatchNormalization()
        # self.act_13_2 = tf.keras.layers.Activation('relu')
        self.conv_block13 = ConvBlock(64)

        ## Nested Conv Block 9 [14]
        self.up_9 = tf.keras.layers.UpSampling2D()

        # self.conv_14_1 = tf.keras.layers.Conv2D(128, 3, padding='same')
        # self.bn_14_1 = tf.keras.layers.BatchNormalization()
        # self.act_14_1 = tf.keras.layers.Activation('relu')

        # self.conv_14_2 = tf.keras.layers.Conv2D(128, 3, padding = 'same')
        # self.bn_14_2 = tf.keras.layers.BatchNormalization()
        # self.act_14_2 = tf.keras.layers.Activation('relu')
        self.conv_block14 = ConvBlock(128)

        ## Nested Conv Block 10 [15]
        self.up_10 = tf.keras.layers.UpSampling2D()

        # self.conv_15_1 = tf.keras.layers.Conv2D(64, 3, padding='same')
        # self.bn_15_1 = tf.keras.layers.BatchNormalization()
        # self.act_15_1 = tf.keras.layers.Activation('relu')

        # self.conv_15_2 = tf.keras.layers.Conv2D(64, 3, padding = 'same')
        # self.bn_15_2 = tf.keras.layers.BatchNormalization()
        # self.act_15_2 = tf.keras.layers.Activation('relu')
        self.conv_block15 = ConvBlock(64)
        
        
        if num_classes == 1 or num_classes == 2:
            self.last_conv = tf.keras.layers.Conv2D(1, 1)
        else:
            self.last_conv = tf.keras.layers.Conv2D(num_classes, 1)
        
    def conv_block(self):
        pass 
    
    def call(self, inputs):


        ###
        # Encoder Network
        ###
        
        ## Conv Block 1
        # x_00 = self.conv_1_1(inputs)
        # x_00 = self.bn_1_1(x_00)
        # x_00 = self.act_1_1(x_00)
        
        # x_00 = self.conv_1_2(x_00)
        # x_00 = self.bn_1_2(x_00)
        # x_00 = self.act_1_2(x_00)
        # x_00 = self.max_pool_1(x_00)
        x_00 = self.conv_block1(inputs)
        x_00 = self.max_pool_1(x_00)

        ## Conv Block 2
        # x_10 = self.conv_2_1(x_00)
        # x_10 = self.bn_2_1(x_10)
        # x_10 = self.act_2_1(x_10)
        
        # x_10 = self.conv_2_2(x_10)
        # x_10 = self.bn_2_2(x_10)
        # x_10 = self.act_2_2(x_10)
        x_10 = self.conv_block2(x_00)
        x_10 = self.max_pool_2(x_10)

        ## Conv Block 3
        
        # x_20 = self.conv_3_1(x_10)
        # x_20 = self.bn_3_1(x_20)
        # x_20 = self.act_3_1(x_20)
        
        # x_20 = self.conv_3_2(x_20)
        # x_20 = self.bn_3_2(x_20)
        # x_20 = self.act_3_2(x_20)
        x_20 = self.conv_block3(x_10)
        x_20 = self.max_pool_3(x_20)

        ## Conv Block 4
        
        # x_30 = self.conv_4_1(x_20)
        # x_30 = self.bn_4_1(x_30)
        # x_30 = self.act_4_1(x_30)
        
        # x_30 = self.conv_4_2(x_30)
        # x_30 = self.bn_4_2(x_30)
        # x_30 = self.act_4_2(x_30)
        x_30 = self.conv_block4(x_20)
        x_30 = self.max_pool_4(x_30)

        ## Conv Block 5
        
        # x_40 = self.conv_5_1(x_30)
        # x_40 = self.bn_5_1(x_40)
        # x_40 = self.act_5_1(x_40)
        
        # x_40 = self.conv_5_2(x_40)
        # x_40 = self.bn_5_2(x_40)
        # x_40 = self.act_5_2(x_40)
        x_40 = self.conv_block5(x_30)
        x_40 = self.max_pool_5(x_40)

        # Nested Decoding Path

        ## Nest 1
        x_10_up = self.up_1(x_10)
        x_00_10up_merged = tf.keras.layers.concatenate([x_00, x_10_up])#self.concat1([x_00, x_10_up])
        # x_01 = self.conv_6_1(x_00_10up_merged)
        # x_01 = self.bn_6_1(x_01)
        # x_01 = self.act_6_1(x_01)

        # x_01 = self.conv_6_2(x_01)
        # x_01 = self.bn_6_2(x_01)
        # x_01 = self.act_6_2(x_01)
        x_01 = self.conv_block6(x_00_10up_merged)

        ## Nest 2
        x_20_up = self.up_2(x_20)
        x_10_20up_merged = tf.keras.layers.concatenate([x_10, x_20_up])
        # x_11 = self.conv_7_1(x_10_20up_merged)
        # x_11 = self.bn_7_1(x_11)
        # x_11 = self.act_7_1(x_11)

        # x_11 = self.conv_7_2(x_11)
        # x_11 = self.bn_7_2(x_11)
        # x_11 = self.act_7_2(x_11)
        x_11 = self.conv_block7(x_10_20up_merged)


        ## Nest 3
        
        x_30_up = self.up_3(x_30)
        x_20_30up_merged = tf.keras.layers.concatenate([x_20, x_30_up])
        # x_21 = self.conv_8_1(x_20_30up_merged)
        # x_21 = self.bn_8_1(x_21)
        # x_21 = self.act_8_1(x_21)

        # x_21 = self.conv_8_2(x_21)
        # x_21 = self.bn_8_2(x_21)
        # x_21 = self.act_8_2(x_21)
        x_21 = self.conv_block8(x_20_30up_merged)        
        
        
        ## Nest 4
        x_40_up = self.up_4(x_40)
        x_30_40up_merged = tf.keras.layers.concatenate([x_30, x_40_up])
        # x_31 = self.conv_9_1(x_30_40up_merged)
        # x_31 = self.bn_9_1(x_31)
        # x_31 = self.act_9_1(x_31)

        # x_31 = self.conv_9_2(x_31)
        # x_31 = self.bn_9_2(x_31)
        # x_31 = self.act_9_2(x_31)
        x_31 = self.conv_block9(x_30_40up_merged)


        ### Double Concats
        ## Nest 5
        x_11_up = self.up_5(x_11)
        x_00_01_11up_merged = tf.keras.layers.concatenate([x_00, x_01, x_11_up])
        # x_02 = self.conv_10_1(x_00_01_11up_merged)
        # x_02 = self.bn_10_1(x_02)
        # x_02 = self.act_10_1(x_02)

        # x_02 = self.conv_10_2(x_02)
        # x_02 = self.bn_10_2(x_02)
        # x_02 = self.act_10_2(x_02)
        x_02 = self.conv_block10(x_00_01_11up_merged)

        ### ------
        ## Nest 6
        x_21_up = self.up_6(x_21)
        x_10_11_21up_merged = tf.keras.layers.concatenate([x_10, x_11, x_21_up])
        # x_12 = self.conv_11_1(x_10_11_21up_merged)
        # x_12 = self.bn_11_1(x_12)
        # x_12 = self.act_11_1(x_12)

        # x_12 = self.conv_11_2(x_12)
        # x_12 = self.bn_11_2(x_12)
        # x_12 = self.act_11_2(x_12)
        x_12 = self.conv_block11(x_10_11_21up_merged)
        ## Nest 7
        x_31_up = self.up_7(x_31)
        x_20_21_31up_merged = tf.keras.layers.concatenate([x_20, x_21, x_31_up])
        # x_22 = self.conv_12_1(x_20_21_31up_merged)
        # x_22 = self.bn_12_1(x_22)
        # x_22 = self.act_12_1(x_22)

        # x_22 = self.conv_12_2(x_22)
        # x_22 = self.bn_12_2(x_22)
        # x_22 = self.act_12_2(x_22)
        x_22 = self.conv_block12(x_20_21_31up_merged)
        
        ### Triple Concats
        
        ## Nest 8
        x_12_up = self.up_8(x_12)
        x_00_01_02_12up_merged = tf.keras.layers.concatenate([x_00, x_01, x_02, x_12_up])
        # x_03 = self.conv_13_1(x_00_01_02_12up_merged)
        # x_03 = self.bn_13_1(x_03)
        # x_03 = self.act_13_1(x_03)

        # x_03 = self.conv_13_2(x_03)
        # x_03 = self.bn_13_2(x_03)
        # x_03 = self.act_13_2(x_03)
        x_03 = self.conv_block13(x_00_01_02_12up_merged)

        ## Nest 9
        x_22_up = self.up_9(x_22)
        x_10_11_12_22up_merged = tf.keras.layers.concatenate([x_10, x_11, x_12, x_22_up])
        # x_13 = self.conv_14_1(x_10_11_12_22up_merged)
        # x_13 = self.bn_14_1(x_13)
        # x_13 = self.act_14_1(x_13)

        # x_13 = self.conv_14_2(x_13)
        # x_13 = self.bn_14_2(x_13)
        # x_13 = self.act_14_2(x_13)
        x_13 = self.conv_block14(x_10_11_12_22up_merged)

        ### 4 concats
        ## Nest 10
        
        x_13_up = self.up_10(x_13)
        x_00_01_02_03_13up_merged = tf.keras.layers.concatenate([x_00, x_01, x_02, x_03, x_13_up])
        # x_04 = self.conv_15_1(x_00_01_02_03_13up_merged)
        # x_04 = self.bn_15_1(x_04)
        # x_04 = self.act_15_1(x_04)

        # x_04 = self.conv_15_2(x_04)
        # x_04 = self.bn_15_2(x_04)
        # x_04 = self.act_15_2(x_04)
        x_04 = self.conv_block15(x_00_01_02_03_13up_merged)
        
        outputs = self.last_conv(x_04)#tf.keras.layers.Conv2D(num_classes, 1)(x_04)
                
        return outputs

    def summary(self):
        x = Input(shape = self.input_size)
        return Model(inputs = [x], outputs = self.call(x)).summary()
        
    


# Testing the model
if __name__ == "__main__":
	# Creating the model
	model = unet_plus_plus_model(input_shape=(
		512, 512, 3), num_classes=2, deep_supervision=True)

	# Printing the model summary
	model.summary()
