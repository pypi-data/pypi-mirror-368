
from tensorflow.keras.layers import *
import tensorflow as tf

from tensorflow.keras.models import Model
from tensorflow.keras.applications import VGG16

class ConvolutionBlock(Model):
	def __init__(self, num_filters):
		super(ConvolutionBlock, self).__init__()
		self.conv1 = Conv2D(num_filters, 3, padding = 'same')
		self.bn1 = BatchNormalization()
		self.act1 = Activation('relu')

		self.conv2 = Conv2D(num_filters, 3, padding = 'same')
		self.bn2 = BatchNormalization()
		self.act2 = Activation('relu')

	def call(self, inputs):
		x = self.conv1(inputs)
		x = self.bn1(x)
		x = self.act1(x)

		x = self.conv2(x)
		x = self.bn2(x)
		x = self.act2(x)
		return x


class UNETVGG16(Model):

	def __init__(self, input_shape = (512, 512, 3)):
		super(UNETVGG16, self).__init__()

		self.input_shape = input_shape

		vgg16 = VGG16(include_top=False, weights="imagenet", input_shape = self.input_shape)#input_tensor = input_tensor)#input_shape = self.input_shape) #input_tensor= input_tensor)#(inputs)# inputs)
		# block1_conv2 = vgg16.get_layer("block1_conv2").output 
		#self.encoder = tf.keras.Model(inputs=vgg16.input, outputs=vgg16.get_layer("block5_pool").output)
		#self.encoder = tf.keras.Model(inputs=vgg16.input, outputs=vgg16.get_layer("block5_conv3").output)
		encoder = tf.keras.Model(inputs = vgg16.input, outputs = vgg16.get_layer('block5_conv3').output)
		skip_outputs = []

		#n_layers = len(self.encoder.layers)
		n_layers = len(encoder.layers)
		self.skip_layers = ['block1_conv2',
						   'block2_conv2',
						   'block3_conv3',
						   'block4_conv3',
						   'block5_conv3']
		i = 0

		#self.encoder_blocks = []
		
		#self.eb1 = None
		#self.eb2 = None
		#self.eb3 = None
		#self.eb4 = None
		#self.eb5 = None
		
		### don't go by this method
		#####self.encoder_blocks = [self.eb1, self.eb2, self.eb3, self.eb4, self.eb5]
		#eb = 0
		"""
		layers = []
		while i < n_layers:
			
			layer = self.encoder.layers[i]     
			layers.append(layer)
			print(layer.name)

			if layer.name in self.skip_layers:
				self.encoder_blocks.append(tf.keras.Sequential(layers))
				#self.encoder_blocks[eb] = tf.keras.Sequential(layers)
				layers = []
				#eb += 1
				print('-----')
			i += 1
		"""

		#print(len(encoder_blocks))

		# works
		#self.eb1, self.eb2, self.eb3, self.eb4, self.eb5 = self.encoder_blocks

		#self.eb1_layers = self.encoder.layers[0:3]
		self.eb1_layers = encoder.layers[0:3]
		#eb1_inp = self.eb1_layers[0]
		#self.eb1_inp = self.encoder.input
		self.eb1_inp = encoder.input

		#self.eb1_out = self.encoder.layers[2].output
		self.eb1_out = encoder.layers[2].output
		#x = self.eb1_layers[1](eb1_inp)
		#eb1_out = self.eb1_layers[2](x)
		#self.eb1_model = tf.keras.Model(inputs = self.eb1_inp, outputs = self.eb1_out, name = 'eb1_model')

		#self.eb2_layers = self.encoder.layers[3:6]
		self.eb2_layers = encoder.layers[3:6]

		#eb2_inp = self.eb2_layers[0]
		self.eb2_inp = self.eb2_layers[0].input
		#x = self.eb2_layers[1](eb2_inp)
		self.eb2_out = self.eb2_layers[2].output
		
		#self.eb2_model = tf.keras.Model(inputs = eb2_inp, outputs = eb2_out, name = 'eb2')
		

		#self.eb3_layers = self.encoder.layers[6 : 10]
		self.eb3_layers = encoder.layers[6 : 10]
		
		self.eb3_inp = self.eb3_layers[0].input
		self.eb3_out = self.eb3_layers[-1].output
		
		#self.eb3_model = tf.keras.Model(inputs = eb3_inp, outputs = eb3_out, name = 'eb3')
		

		#self.eb4_layers = self.encoder.layers[10 : 14]
		self.eb4_layers = encoder.layers[10 : 14]
		self.eb4_inp = self.eb4_layers[0].input
		self.eb4_out = self.eb4_layers[-1].output
		
		#self.eb4_model = tf.keras.Model(inputs = eb4_inp, outputs = eb4_out, name = 'eb4')

		self.eb5_layers = encoder.layers[14 : 18]
		self.eb5_inp = self.eb5_layers[0].input
		self.eb5_out = self.eb5_layers[-1].output
		#self.eb5_model = tf.keras.Model(inputs = eb5_inp, outputs = eb5_out, name = 'eb5')
		
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
		#print(x)

		# works
		#b1 = self.encoder_blocks[0](inputs)

		# works
		#b1 = self.eb1(inputs)

		# doesn't work
		#print(self.eb1_layers[0])
		# b1 = self.eb1_layers[0](inputs)
		# b1 = self.eb1_layers[1](b1)
		# b1 = self.eb1_layers[2](b1)

		# works
		#b1 = self.eb1_model(inputs)

		# works (removes eb1 redundancy from summary)
		eb1_model = tf.keras.Model(inputs = self.eb1_inp, outputs = self.eb1_out, name = 'eb1_model')
		b1 = eb1_model(inputs)
		
		
		# works
		#b2 = self.encoder_blocks[1](b1)

		#works
		#b2 = self.eb2(b1)

		# works (shows the output shapes but with b2 redundancy)
		#b2 = self.eb2_model(b1)

		eb2_model = tf.keras.Model(inputs = self.eb2_inp, outputs = self.eb2_out, name = 'eb2_model')
		b2 = eb2_model(b1)
		

		# works
		#b3 = self.encoder_blocks[2](b2)

		# works
		#b3 = self.eb3(b2)

		# works
		#b3 = self.eb3_model(b2)

		eb3_model = tf.keras.Model(inputs = self.eb3_inp, outputs = self.eb3_out, name = 'eb3')
		b3 = eb3_model(b2)
		
		# works
		#b4 = self.encoder_blocks[3](b3)

		# works
		#b4 = self.eb4(b3)

		# works
		#b4 = self.eb4_model(b3)

		eb4_model = tf.keras.Model(inputs = self.eb4_inp, outputs = self.eb4_out, name = 'eb4')
		b4 = eb4_model(b3)
		#b4 = self.eb4_model(b3)
		

		# works
		#b5 = self.encoder_blocks[4](b4)
		
		# works
		#b5 = self.eb5(b4)

		# works
		#b5 = self.eb5_model(b4)

		eb5_model = tf.keras.Model(inputs = self.eb5_inp, outputs = self.eb5_out, name = 'eb5')
		b5 = eb5_model(b4)
		
		#print(x)
	
		#for layer in self.encoder.layers:
		
			
			#print(layer)
			#x = layer(x)

			#if layer.name in self.skip_layers:
			#    skip_outputs.append(x)

		#print(skip_outputs)

		#d1 = self.conv2dt1(self.b1)
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
		#print("Ran till here successfully")
		return outputs
	def summary(self):
		x = Input(shape = self.input_shape)
		return Model(inputs = [x], outputs = self.call(x)).summary()
