class train_k_fold_pred():

	def __init__(self, k, tpu, n_class, model_name, train_tfrecs_path, val_tfrecs_path, test_tfrecs_path, GCS_DS_PATH_labeled, GCS_DS_PATH_unlabeled, BATCH_SIZE, EPOCHS, classification_model = 'default', freeze = False, input_shape = [512,512,3], activation = 'softmax', weights = "imagenet", optimizer = "adam", loss = "sparse_categorical_crossentropy", metrics = "sparse_categorical_accuracy", callbacks = None, plot = False, verbose = 0):
		# the number of folds , k
		self.k = k
		self.tpu = tpu
		self.n_class = n_class
		self.model_name = model_name
		
		# for saving the models of each fold
		self.models = []
		# for saving model's folds history
		self.history = []
		# for saving the probabilities of predictions
		self.probabilities = []

		# obtain the training tfrecs path
		self.train_tfrecs_path = train_tfrecs_path
		# obtain the validation tfrecs path
		self.val_tfrecs_path = val_tfrecs_path
		# obtain the test tfrecs path
		self.test_tfrecs_path = test_tfrecs_path

		self.GCS_DS_PATH_labeled = GCS_DS_PATH_labeled
		self.GCS_DS_PATH_unlabeled = GCS_DS_PATH_unlabeled
		self.BATCH_SIZE = BATCH_SIZE
		self.EPOCHS = EPOCHS
		self.classification_model = classification_model
		self.freeze = freeze
		self.input_shape = input_shape
		self.activation = activation
		self.weights = weights
		self.optimizer = optimizer
		self.loss = loss
		self.metrics = metrics
		self.callbacks = callbacks
		self.plot = plot
		self.verbose = verbose
		
		from quick_ml.begin_tpu import get_test_dataset
		self.test_ds = get_test_dataset(self.GCS_DS_PATH_unlabeled, self.test_tfrecs_path, self.BATCH_SIZE)
		self.test_image_ds = self.test_ds.map(lambda image, idnum : image)
		self.NUM_TEST_IMAGES = 0
		for data in self.test_ds.unbatch():
			self.NUM_TEST_IMAGES += 1



	def train_k_fold(self):

		kfolds = KFold(self.k, shuffle = True, random_state = 21)

		TRAINING_FILENAMES = tf.io.gfile.glob(self.GCS_DS_PATH_labeled + self.train_tfrecs_path) + tf.io.gfile.glob(self.GCS_DS_PATH_labeled + self.val_tfrecs_path)

		from quick_ml.load_models_quick import create_model
		from quick_ml.begin_tpu import load_dataset
		
		
		df = pd.DataFrame(columns = ['Model_Fold_Number', 'Accuracy_top1', 'Accuracy_top3', 'Val_Accuracy_top1', 'Val_Accuracy_top3'])

		for fold, (trn_ind, val_ind) in enumerate(kfolds.split(TRAINING_FILENAMES)):
			print(f"Beginning with Model {self.model_name} : Fold Number -> {fold + 1}")
			train_dataset = load_dataset(list(pd.DataFrame({'TRAINING_FILENAMES' : TRAINING_FILENAMES}).loc[trn_ind]['TRAINING_FILENAMES']), labeled = True)
			val_dataset = load_dataset(list(pd.DataFrame({'TRAINING_FILENAMES' : TRAINING_FILENAMES}).loc[val_ind]['TRAINING_FILENAMES']), labeled = True, ordered = True)

			STEPS_PER_EPOCH = len(list(train_dataset)) // self.BATCH_SIZE

			train_dataset = train_dataset.repeat()
			train_dataset = train_dataset.shuffle(2048)
			train_dataset = train_dataset.batch(self.BATCH_SIZE)
			train_dataset = train_dataset.prefetch(tf.data.experimental.AUTOTUNE)

			val_dataset = val_dataset.batch(self.BATCH_SIZE)
			val_dataset = val_dataset.cache()
			val_dataset = val_dataset.prefetch(tf.data.experimental.AUTOTUNE)


			tf.tpu.experimental.initialize_tpu_system(self.tpu)
			strategy = tf.distribute.experimental.TPUStrategy(self.tpu)
			with strategy.scope():
				if self.classification_model != 'default':
					model = create_model(freeze = self.freeze, input_shape = self.input_shape, activation = self.activation, weights= self.weights, optimizer = self.optimizer, loss = self.loss, metrics = self.metrics, classes = self.n_class, model_name = self.model_name, classification_model = self.classification_model)
				else:
					model = create_model(freeze= self.freeze, input_shape = self.input_shape, activation = self.activation, weights = self.weights, optimizer = self.optimizer, loss = self.loss, metrics = self.metrics, classes = self.n_class, model_name = self.model_name)

			history = model.fit(train_dataset, epochs = self.EPOCHS, steps_per_epoch = STEPS_PER_EPOCH, validation_data = val_dataset, verbose = self.verbose)

			self.probabilities.append(model.predict(self.test_image_ds))

			tf.keras.backend.clear_session()
			tf.compat.v1.reset_default_graph()
			del model
			gc.collect()

			df = df.append(pd.DataFrame([[self.model_name + f'_fold_{fold+1}', history.history[self.metrics][-1], np.mean(history.history[self.metrics][-3:]), history.history['val_' + self.metrics][-1], np.mean(history.history['val_' + self.metrics][-3:])]], columns = ['Model_Fold_Number', 'Accuracy_top1', 'Accuracy_top3', 'Val_Accuracy_top1', 'Val_Accuracy_top3']), ignore_index = True)
			print(f'Done with the model fold -> {self.model_name}_fold_{fold+1}')
		return df

	def obtain_predictions(self, weights = None):

		if weights is not None:
			if len(weights) == len(self.probabilities):
				self.probabilities = np.average(self.probabilities, weights = weights, axis = 0)
			else:
				raise Exception("Length of weights array is not equal to the number of folds... Error!")
		else:
			self.probabilities = np.average(self.probabilities, axis = 0)
		
					
		test_ids_ds = self.test_ds.map(lambda image, idnum : idnum).unbatch()
		test_ids = next(iter(test_ids_ds.batch(self.NUM_TEST_IMAGES))).numpy().astype('U')
		print("Generating predictions output file as predictions.csv")
		
		
		if self.n_class == 1:
			predictions = np.array([1 if i >= 0.5 else 0 for i in self.probabilities])
			predictions = np.reshape(predictions, newshape = (self.NUM_TEST_IMAGES,))
		else:
			predictions = np.argmax(self.probabilities, axis = -1)
		np.savetxt('predictions.csv', np.rec.fromarrays([test_ids, predictions]),
			fmt = ['%s', '%d'], delimiter = ',', header = 'id,label', comments = '')


if __name__ != '__main__':
	import numpy as np
	import pandas as pd
	from sklearn.model_selection import KFold
	import os
	import gc
	import tensorflow as tf
	
