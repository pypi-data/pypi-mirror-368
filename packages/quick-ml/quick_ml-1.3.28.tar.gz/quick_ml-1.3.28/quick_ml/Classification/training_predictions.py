def get_models_training_report(strategy, models,tpu, n_class, traindata, steps_per_epoch, epochs, batch_size, val_data,  classification_model = 'default', freeze = False, input_shape = [512,512,3], activation = 'softmax', weights = "imagenet", optimizer = "adam", loss = "sparse_categorical_crossentropy", metrics = "sparse_categorical_accuracy", callbacks = None, plot = False):
	
	import pandas as pd
	import numpy as np
	import gc
	from quick_ml.Classification.load_models_quick import create_model
	print("Num classes => " , n_class)
	print("\n\n", '#'*90, '\n\n')
	print("\n\n TO OBTAIN THE BEST PERFORMANCE, PLEASE USE THE PRETRAINED MODEL WEIGHTS AS INPUT. Dataset Link -> https://www.kaggle.com/superficiallybot/tf-keras-pretrained-weights\n\n")
	print("\n\n", '#'*90, '\n\n')
	
	df = pd.DataFrame(columns = ['Model_Name', 'Accuracy_top1', 'Accuracy_top3', "Val_Accuracy_top1", "Val_Accuracy_top3"])

	for m in models:
		print(f"Beginning with model -> {m}")
		#tf.tpu.experimental.initialize_tpu_system(tpu)
		#strategy = tf.distribute.experimental.TPUStrategy(tpu)
		with strategy.scope():
			if classification_model != 'default':
				model = create_model( freeze = freeze, input_shape = input_shape, activation = activation, weights = weights, optimizer = optimizer, loss = loss, metrics = metrics, classes = n_class, model_name = m, classification_model = classification_model)
			else:
				model = create_model( freeze = freeze, input_shape = input_shape, activation = activation, weights = weights, optimizer = optimizer, loss = loss, metrics = metrics , classes = n_class, model_name = m)
				

		history = model.fit(traindata, steps_per_epoch = steps_per_epoch, epochs = epochs,batch_size = batch_size, validation_data =  val_data, callbacks = callbacks, verbose = 0)
		tf.keras.backend.clear_session()
		tf.compat.v1.reset_default_graph()
		del model
		gc.collect()
		
		#df = df.append(pd.DataFrame([[m, history.history[metrics][-1], np.mean(history.history[metrics][-3:]) , history.history['val_' + metrics][-1], np.mean(history.history['val_' + metrics][-3:])]], columns = ['Model_Name', 'Accuracy_top1', 'Accuracy_top3', "Val_Accuracy_top1", "Val_Accuracy_top3"]), ignore_index = True)
		df = pd.concat([df, pd.DataFrame([[m, history.history[metrics][-1], np.mean(history.history[metrics][-3:]) , history.history['val_' + metrics][-1], np.mean(history.history['val_' + metrics][-3:])]], columns = ['Model_Name', 'Accuracy_top1', 'Accuracy_top3', "Val_Accuracy_top1", "Val_Accuracy_top3"])], ignore_index=True)

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


if __name__ != "__main__":
	#import os
	#print("Installing the reqd libraries...\n")
	#os.system("pip install tensorflow==2.2.0")
	#os.system("pip install keras==2.4.3")
	import tensorflow as tf