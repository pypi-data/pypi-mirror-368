#import tensorflow as tf
from tensorflow.keras.layers import * 
from tensorflow.keras import Model
from tensorflow.keras.optimizers import Adam
import numpy as np

from glob import glob
import cv2
import numpy as np
from tqdm import tqdm

class UNet(Model):

	def __init__(self, pretrained_weights = None, input_size = (256, 256, 1), num_classes = 2):

		super().__init__()

		self.num_classes = num_classes

		self.pretrained_weights = pretrained_weights
		self.input_size = input_size



		self.conv1_1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv1_2 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		
		self.conv2_1 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv2_2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		
		self.conv3_1 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv3_2 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		
		self.conv4_1 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv4_2 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		
		self.conv5_1 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv5_2 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')

		self.conv6_1 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv6_2 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		
		self.conv7_1 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv7_2 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		
		self.conv8_1 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv8_2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		
		self.conv9_1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv9_2 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.conv9_3 = Conv2D(2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')

		if num_classes > 2:
			self.conv10 = Conv2D(num_classes, 1, activation = 'softmax')
		else:
			self.conv10 = Conv2D(1, 1, activation = 'sigmoid')
		
		self.pool1 = MaxPool2D(pool_size=(2, 2))
		self.pool2 = MaxPool2D(pool_size=(2, 2))
		self.pool3 = MaxPool2D(pool_size=(2, 2))
		self.pool4 = MaxPool2D(pool_size=(2, 2))
		
		self.drop4 = Dropout(0.5)

		self.drop5 = Dropout(0.5)

		self.up6 = UpSampling2D(size = (2,2))
		self.conv_up6 = Conv2D(512, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.merge6 = Concatenate(axis = 3)

		self.up7 = UpSampling2D(size = (2,2))
		self.conv_up7 = Conv2D(256, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.merge7 = Concatenate(axis = 3)

		self.up8 = UpSampling2D(size = (2,2))
		self.conv_up8 = Conv2D(128, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.merge8 = Concatenate(axis = 3)

		self.up9 = UpSampling2D(size = (2,2))
		self.conv_up9 = Conv2D(64, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')
		self.merge9 = Concatenate(axis = 3)




	def call(self, inputs):


		conv1 = self.conv1_1(inputs)
		conv1 = self.conv1_2(conv1)
		pool1 = self.pool1(conv1)

		conv2 = self.conv2_1(pool1)
		conv2 = self.conv2_2(conv2)
		pool2 = self.pool2(conv2)

		conv3 = self.conv3_1(pool2)
		conv3 = self.conv3_2(conv3)
		pool3 = self.pool3(conv3)

		conv4 = self.conv4_1(pool3)
		conv4 = self.conv4_2(conv4)
		drop4 = self.drop4(conv4)
		pool4 = self.pool4(drop4)

		conv5 = self.conv5_1(pool4)
		conv5 = self.conv5_2(conv5)
		drop5 = self.drop5(conv5)

		up6 = self.up6(drop5)
		up6 = self.conv_up6(up6)
		merge6 = self.merge6([drop4, up6])
		conv6 = self.conv6_1(merge6)
		conv6 = self.conv6_2(conv6)

		up7 = self.up7(conv6)
		up7 = self.conv_up7(up7)
		merge7 = self.merge7([conv3, up7])
		conv7 = self.conv7_1(merge7)
		conv7 = self.conv7_2(conv7)

		up8 = self.up8(conv7)
		up8 = self.conv_up8(up8)
		merge8 = self.merge8([conv2, up8])
		conv8 = self.conv8_1(merge8)
		conv8 = self.conv8_2(conv8)

		up9 = self.up9(conv8)
		up9 = self.conv_up9(up9)
		merge9 = self.merge9([conv1, up9])
		conv9 = self.conv9_1(merge9)
		conv9 = self.conv9_2(conv9)
		conv9 = self.conv9_3(conv9)

		conv10 = self.conv10(conv9)


		#conv6 = self.conv6_1()

		#up6 = Conv2D(512, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(drop5))       

		return conv10

	def summary(self):

		x = Input(shape = self.input_size)
		return Model(inputs = [x], outputs = self.call(x)).summary()

	def plot_model(self):
		import tensorflow as tf
		x = Input(shape = self.input_size)
		return tf.keras.utils.plot_model(Model(inputs = [x], outputs = self.call(x)), show_dtype = True, show_layer_names = True, show_shapes = True)

	#def predict(self, imgs):
	def overlay_predictions(self, preds, test_ds_path, save_to_dir = None, keep_img = False, keep_pred_mask = False):
		test_imgs = glob(test_ds_path)
		test_imgs.sort()
		overlays = []
		for img, pred in tqdm(zip(test_imgs, preds), total = len(preds)):
			org = cv2.imread(img)
			
			img2 = np.zeros(org.shape)

			img2[:, : , 0] = pred.squeeze()
			img2[:, : , 1] = pred.squeeze()
			img2[:, : , 2] = pred.squeeze()
			img2 = (img2 >= 0.5).astype(np.uint8)
			img2 = img2 * 255
			overlay = cv2.addWeighted(img2, 0.5, org, 0.7, 0.0)

			overlays.append(overlay)

			if save_to_dir:
				cv2.imwrite(save_to_dir + '/overlay_' + img.split('/')[-1], overlay)

		return overlays

	def _get_true(self, img, mask):

		return mask


	def get_evaluation_report(self, ds, preds):
		y_true = ds.map(self._get_true)
		y_true = y_true.as_numpy_iterator()

		y_trues = []

		for yt in y_true:
			y_trues.append(yt[0])

		y_trues = np.array(y_trues)

		import pandas as pd

		###if self.num_classes == 2:

		loss_fn = self.get_compile_config()['loss']        
		if loss_fn == 'binary_crossentropy':    

			from tensorflow.keras.losses import BinaryCrossentropy
			bce = BinaryCrossentropy(from_logits = False)    

			## Get metrics
			model_mets = self.get_compile_config()['metrics']
			metrics = []
			metric_names = []
			for m in model_mets:
				if m.lower() == 'accuracy':
					from tensorflow.keras.metrics import BinaryAccuracy
					metrics.append(BinaryAccuracy())
					metric_names.append(m)
			

			#from tensorflow.keras.metrics import BinaryAccuracy
			#m = BinaryAccuracy()

			#accuracy_score(y_true.numpy(), preds[0])
			
			evals = []
			
			for y_t, y_pred in zip(y_trues, preds):
		
				#m.update_state(y_t, y_pred)
				results = []
				for m in metrics:
					m.update_state(y_t, y_pred)
					#print(m.result().numpy())
					results.append(m.result().numpy())



				#print(m.result())
				#evals.append([m.result().numpy(), bce(y_t, y_pred).numpy()])
				#evals.append([results, bce(y_t, y_pred).numpy()])
				results.extend([bce(y_t, y_pred).numpy()])
				evals.append(results) #.extend([bce(y_t, y_pred).numpy()]))
				#print(evals)
			#df = pd.DataFrame(evals, columns = ['Accuracy', 'Loss'])
			metric_names.extend(['Loss'])
			df = pd.DataFrame(evals, columns = metric_names)#.extend(['Loss']))
			return df
		else:
			pass
		



		

	

# class UNet:

#   def __init__(self, pretrained_weights = None, input_size = (256, 256, 1)):
#       self.pretrained_weights = pretrained_weights
#       self.input_size = input_size
#       self.model = None

#   def create_model(self):
#       inputs = Input(self.input_size)
#       conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(inputs)
#       conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv1)
#       pool1 = MaxPool2D(pool_size=(2, 2))(conv1)
#       conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool1)
#       conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
#       pool2 = MaxPool2D(pool_size=(2, 2))(conv2)
#       conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool2)
#       conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
#       pool3 = MaxPool2D(pool_size=(2, 2))(conv3)
#       conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool3)
#       conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
#       drop4 = Dropout(0.5)(conv4)
#       pool4 = MaxPool2D(pool_size=(2, 2))(drop4)

#       conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool4)
#       conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
#       drop5 = Dropout(0.5)(conv5)

#       up6 = Conv2D(512, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(drop5))
#       merge6 = Concatenate(axis = 3)([drop4,up6])
#       conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge6)
#       conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)

#       up7 = Conv2D(256, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv6))
#       merge7 = Concatenate(axis = 3)([conv3,up7])
#       conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge7)
#       conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)

#       up8 = Conv2D(128, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv7))
#       merge8 = Concatenate(axis = 3)([conv2,up8])
#       conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge8)
#       conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)

#       up9 = Conv2D(64, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv8))
#       merge9 = Concatenate(axis = 3)([conv1,up9])
#       conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge9)
#       conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
#       conv9 = Conv2D(2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
#       conv10 = Conv2D(1, 1, activation = 'sigmoid')(conv9)

#       model = Model(inputs, conv10)

#       #model.compile(optimizer = Adam(learning_rate = 1e-4), loss = 'binary_crossentropy', metrics = ['accuracy'])#[dice_coefficient])#metrics = ['accuracy'])
#       #model.compile(optimizer = Adam(learning_rate = 1e-4), loss = 'binary_crossentropy', metrics = [dice_coef])
#       #model.compile(optimizer = Adam(learning_rate = 1e-4), loss = DiceLoss, metrics = [dice_coef])#[sm.metrics.iou_score()]))
#       if(self.pretrained_weights):
#           model.load_weights(self.pretrained_weights)

#       self.model =  model

#   def compile_model(self, optimizer = "adam", lr = 1e-4, loss = 'binary_crossentropy', metrics = ['accuracy']):
#       self.model.compile(optimizer = Adam(learning_rate = lr), loss = loss, metrics = metrics)
#       return self.model

# model = UNet(input_size)
# model.create_model()
# model.compile_model()
# history = model.fit()

# def UNet(input_size = (256, 256, 1), pretrained_weights = None):
#   inputs = Input(input_size)
#   conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(inputs)
#   conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv1)
#   pool1 = MaxPool2D(pool_size=(2, 2))(conv1)
#   conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool1)
#   conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
#   pool2 = MaxPool2D(pool_size=(2, 2))(conv2)
#   conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool2)
#   conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
#   pool3 = MaxPool2D(pool_size=(2, 2))(conv3)
#   conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool3)
#   conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
#   drop4 = Dropout(0.5)(conv4)
#   pool4 = MaxPool2D(pool_size=(2, 2))(drop4)
#   conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool4)
#   conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
#   drop5 = Dropout(0.5)(conv5)

#   up6 = Conv2D(512, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(drop5))
#   merge6 = Concatenate(axis = 3)([drop4,up6])
#   conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge6)
#   conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)
#   up7 = Conv2D(256, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv6))
#   merge7 = Concatenate(axis = 3)([conv3,up7])
#   conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge7)
#   conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)
#   up8 = Conv2D(128, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv7))
#   merge8 = Concatenate(axis = 3)([conv2,up8])
#   conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge8)
#   conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)

#   up9 = Conv2D(64, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv8))
#   merge9 = Concatenate(axis = 3)([conv1,up9])
#   conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge9)
#   conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
#   conv9 = Conv2D(2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
#   conv10 = Conv2D(1, 1, activation = 'sigmoid')(conv9)

#   model = Model(inputs, conv10)

#   model.compile(optimizer = Adam(learning_rate = 1e-4), loss = 'binary_crossentropy', metrics = ['accuracy'])#[dice_coefficient])#metrics = ['accuracy'])
#   #model.compile(optimizer = Adam(learning_rate = 1e-4), loss = 'binary_crossentropy', metrics = [dice_coef])
#   #model.compile(optimizer = Adam(learning_rate = 1e-4), loss = DiceLoss, metrics = [dice_coef])#[sm.metrics.iou_score()]))
#   if(pretrained_weights):
#       model.load_weights(pretrained_weights)

#   return model
