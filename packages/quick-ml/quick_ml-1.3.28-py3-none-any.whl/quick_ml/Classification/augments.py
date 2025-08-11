# perform various data augmentations 


## callbacks supported



def rampup_lrfn(epoch):

	"""
	Fine Tune the pretrained model weights in a better and smooth manner.
	Use this as a callback feature during the model training.
	"""
	
	if epoch < LR_RAMPUP_EPOCHS:
		lr = (LR_MAX - LR_START) / LR_RAMPUP_EPOCHS * epoch + LR_START
	elif epoch < LR_RAMPUP_EPOCHS + LR_SUSTAIN_EPOCHS : 
		lr = LR_MAX
	else:
		lr = (LR_MAX - LR_MIN) + LR_EXP_DECAY**(epoch - LR_RAMPUP_EPOCHS - LR_SUSTAIN_EPOCHS) + LR_MIN

	return lr



def stepped_lrfn(epoch):
	return 1e-4 * (0.75 ** np.floor(epoch / 2))

def step_decay(epoch):
	initAlpha = 0.01
	factor = 0.25
	dropEvery = 5
	
	alpha = initAlpha * (factor ** np.floor((1+epoch) / dropEvery))
	return float(alpha)

def simple_lrfn(epoch):

	if epoch < 6:
		return 0.001
	elif 6 < epoch < 12 : 
		return 0.0005
	elif 12 < epoch < 18 : 
		return 0.00008
	else:
		return 0.000006

	return



def define_callbacks(lr_scheduler = None):
	
	global callbacks
	
	callbacks = {}
	if lr_scheduler is not None:
		callbacks['lr_scheduler'] = lr_scheduler
	else:
		callbacks['lr_scheduler'] = None

	if len(list(callbacks.keys())) == 0:
		print("Error! No callbacks defined but callback called")

## Worked, integrate later
def check_arguments(func):
	flag = True
	def inner(*args, **kwargs):
		
		for arg in args:
			print(arg)
		
		for arg in kwargs:
			print(arg)
					
		if flag:
			func(*args, **kwargs)	
		else:
			print("Error! Check your arguments format! Define the arguments as per the instructions..")
	
	return inner


#@check_arguments
def define_augmentations(flip_left_right = False, hue = None, contrast = None, brightness = None, random_crop = None, random_saturation = None,random_zoom = None, flip_up_down = False, random_rotation = None, random_shear = None, random_shift = None):
	
	
	global augments
	
	augments = {}

	if flip_left_right:
		augments['flip_left_right'] = True

	if hue:
		augments['random_hue'] = hue

	if contrast:
		augments['random_contrast'] = contrast

	if brightness:
		augments['brightness'] = brightness
	
	if random_crop:
		augments['random_crop'] = random_crop
	
	if random_saturation:
		augments['random_saturation'] = random_saturation
	
	if random_zoom:
		augments['random_zoom'] = random_zoom
		
	if flip_up_down:
		augments['flip_up_down'] = True
	
	if random_rotation:
		augments['random_rotation'] = random_rotation
			
	if random_shear:
		augments['random_shear'] = random_shear
	
	if random_shift:
		augments['random_shift'] = random_shift

	print("Defined augmentes -> \n", augments, "\n")
	if len(list(augments.items())) == 0:
		print("Error! Define augments called but no augments defined...")
		return



def augmentations(image, label):

	global augments
	
	for aug in augments.items():
		if aug[0] == 'flip_left_right' and aug[1] == True:
			image = tf.image.random_flip_left_right(image)
		if aug[0] == 'random_hue':
			image = tf.image.random_hue(image, aug[1])
		if aug[0] == 'random_contrast':
			image = tf.image.random_contrast(image, aug[1][0], aug[1][1])
		if aug[0] == 'brightness':
			image = tf.image.random_brightness(image, aug[1])
		if aug[0] == 'random_crop':
			image = tf.image.random_crop(image, [aug[1][0], aug[1][1],aug[1][2]])
		if aug[0] == 'random_saturation':
			image = tf.image.random_saturation(image, aug[1][0], aug[1][1])
		if aug[0] == 'random_zoom':
			image = tf.keras.preprocessing.image.random_zoom(image, (aug[1][0], aug[1][1]))
		if aug[0] == 'flip_up_down' and aug[1] == True:
			image = tf.image.random_flip_up_down(image)
		if aug[0] == 'random_rotation':
			image = tf.keras.preprocessing.image.random_rotation(image, aug[1])
		if aug[0] == 'random_shear':
			image = tf.keras.preprocessing.image.random_shear(image, aug[1])
		if aug[0] == 'random_shift':
			image = tf.keras.preprocessing.image.random_shift(image, aug[1][0], aug[1][1])
		

	return image, label




def get_models_training_report(models,tpu, n_class, GCS_DS_PATH, train_tfrec_path, steps_per_epoch, epochs, batch_size, val_tfrec_path ,  classification_model = 'default', freeze = False, input_shape = [512,512,3], activation = 'softmax', weights = "imagenet", optimizer = "adam", loss = "sparse_categorical_crossentropy", metrics = "sparse_categorical_accuracy", plot = False):
	
	import pandas as pd
	import numpy as np
	import gc
	from quick_ml.load_models_quick import create_model
	from quick_ml.begin_tpu import get_training_dataset
	from quick_ml.begin_tpu import get_validation_dataset
	
	print("Num classes => " , n_class)
	print("\n\n", '#'*90, '\n\n')
	print("\n\n TO OBTAIN THE BEST PERFORMANCE, PLEASE USE THE PRETRAINED MODEL WEIGHTS AS INPUT. Dataset Link -> https://www.kaggle.com/superficiallybot/tf-keras-pretrained-weights\n\n")
	print("\n\n", '#'*90, '\n\n')
	
	df = pd.DataFrame(columns = ['Model_Name', 'Accuracy_top1', 'Accuracy_top3', "Val_Accuracy_top1", "Val_Accuracy_top3"])

	for m in models:
		overall = {}
		print(f"Beginning with model -> {m}")
		tf.tpu.experimental.initialize_tpu_system(tpu)
		strategy = tf.distribute.experimental.TPUStrategy(tpu)
		with strategy.scope():
			if classification_model != 'default':
				model = create_model( freeze = freeze, input_shape = input_shape, activation = activation, weights = weights, optimizer = optimizer, loss = loss, metrics = metrics, classes = n_class, model_name = m, classification_model = classification_model)
			else:
				model = create_model( freeze = freeze, input_shape = input_shape, activation = activation, weights = weights, optimizer = optimizer, loss = loss, metrics = metrics , classes = n_class, model_name = m)
				
		for epoch in range(epochs):
			if epoch == 0:
				#print(f"\nEpoch # {epoch + 1}\n")
				#print(f"\nCurrent Learning Rate -> {K.eval(model.optimizer.lr)}")
				history = model.fit(get_training_dataset(GCS_DS_PATH, train_tfrec_path, batch_size, augmentation = True), validation_data = get_validation_dataset(GCS_DS_PATH, val_tfrec_path, batch_size, augmentation = True), epochs = 1, steps_per_epoch = steps_per_epoch, batch_size = batch_size, verbose = 0)
				if callbacks is not None:
					set_learning_rate(model, epoch + 1)
				
				for k,v in history.history.items():
					overall[k] = v
			
			else:
				#print(f"\nEpoch # {epoch + 1}\n")
				#print(f"\nCurrent Learning Rate -> {K.eval(model.optimizer.lr)}")
				
				history = model.fit(get_training_dataset(GCS_DS_PATH, train_tfrec_path, batch_size, augmentation = True), validation_data = get_validation_dataset(GCS_DS_PATH, val_tfrec_path, batch_size, augmentation = True), epochs = 1, steps_per_epoch = steps_per_epoch, batch_size = batch_size, verbose = 0)
				
				if callbacks is not None:
					set_learning_rate(model, epoch + 1)
			
				for k,v in history.history.items():
					overall[k].extend(v)
				
				
				
		tf.keras.backend.clear_session()
		tf.compat.v1.reset_default_graph()
		del model
		gc.collect()
		
		df = df.append(pd.DataFrame([[m, overall[metrics][-1], np.mean(overall[metrics][-3:]) , overall['val_' + metrics][-1], np.mean(overall['val_' + metrics][-3:])]], columns = ['Model_Name', 'Accuracy_top1', 'Accuracy_top3', "Val_Accuracy_top1", "Val_Accuracy_top3"]), ignore_index = True)
		print(f"Done with model -> {m}")

	if plot:

		print("Plotting Feature Coming soon...")

		## under making
		"""import matplotlib.plt as plt
		import seaborn as sns

		sns.lineplot(x = list(range(1,epochs + 1)), y = histories[0].history[metrics], label = 'Training Accuracy');
		sns.lineplot(x = list(range(1,epochs + 1)), y = histories[0].history['val_' + metrics], label = 'Validation Accuracy').set_title(f'{metrics} Plot vs Epoch');
		plt.show()"""

	return df





def set_learning_rate(model, epoch):
	
	global callbacks
	
	if callbacks['lr_scheduler'] is not None:
		lr_scheduler = callbacks['lr_scheduler']
		if lr_scheduler == 'rampup':
			lr = rampup_lrfn(epoch)
			K.set_value(model.optimizer.learning_rate, lr)
			print(f"Learning Rate changed to {K.eval(model.optimizer.lr)}")
		elif lr_scheduler == 'simple':
			lr = simple_lrfn(epoch)
			K.set_value(model.optimizer.learning_rate, lr)
			print(f"Learning Rate changed to {K.eval(model.optimizer.lr)}")
		elif lr_scheduler == 'step_decay':
			lr = step_decay(epoch)
			K.set_value(model.optimizer.learning_rate, lr)
			print(f"Learning Rate changed to {K.eval(model.optimizer.lr)}")
		elif lr_scheduler == 'stepped':
			lr = step_decay(epoch)
			K.set_value(model.optimizer.learning_rate, lr)
			print(f"Learning Rate changed to {K.eval(model.optimizer.lr)}")
		
	


def augment_and_train(model, GCS_DS_PATH, train_tfrec_path, val_tfrec_path, batch_size, epochs, steps_per_epoch, plot = False):

	from quick_ml.begin_tpu import get_training_dataset
	from quick_ml.begin_tpu import get_validation_dataset

	overall = {}
	
	
	
	for epoch in range(epochs):
	
		if epoch == 0:
			print(f"\nEpoch # {epoch + 1}\n")
			print(f"\nCurrent Learning Rate -> {K.eval(model.optimizer.lr)}")
			history = model.fit(get_training_dataset(GCS_DS_PATH, train_tfrec_path, batch_size, augmentation = True), validation_data = get_validation_dataset(GCS_DS_PATH, val_tfrec_path, batch_size, augmentation = True), epochs = 1, steps_per_epoch = steps_per_epoch, batch_size = batch_size, verbose = 1)
			if callbacks is not None:
				set_learning_rate(model, epoch + 1)
			
			for k,v in history.history.items():
				overall[k] = v
				
				
		else:
		
			print(f"\nEpoch # {epoch + 1}\n")
			print(f"\nCurrent Learning Rate -> {K.eval(model.optimizer.lr)}")
			history = model.fit(get_training_dataset(GCS_DS_PATH, train_tfrec_path, batch_size, augmentation = True), validation_data = get_validation_dataset(GCS_DS_PATH, val_tfrec_path, batch_size, augmentation = True), epochs = 1, steps_per_epoch = steps_per_epoch, batch_size = batch_size, verbose = 1)
			if callbacks is not None:
				set_learning_rate(model, epoch + 1)
			
			for k,v in history.history.items():
				overall[k].extend(v)
		
	
	if plot:
		import matplotlib.pyplot as plt
		import seaborn as sns

		keys = list(overall.keys())
		
		

		sns.lineplot(x = list(range(1, epochs + 1)), y = overall[keys[0]], label = 'Training Accuracy', color = 'k');
		sns.lineplot(x = list(range(1, epochs + 1)), y = overall[keys[2]], label = 'Validation Accuracy', color = 'red');
		plt.show()


	




if __name__ != "__main__":
	global LR_MAX
	global LR_MIN
	global LR_RAMPUP_EPOCHS
	global LR_SUSTAIN_EPOCHS
	global LR_EXP_DEC
	global LR_START
	
	import tensorflow as tf
	import numpy as np
	LR_MAX = 0.00005 * 8
	LR_MIN = 0.00001
	LR_RAMPUP_EPOCHS = 5
	LR_SUSTAIN_EPOCHS = 0
	LR_EXP_DECAY = 0.8
	LR_START = 0.00001
	import tensorflow.keras.backend as K
