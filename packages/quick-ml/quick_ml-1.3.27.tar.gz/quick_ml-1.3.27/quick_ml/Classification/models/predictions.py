## function for obtaining predictions through GCS_DS_PATH
def get_predictions_tfrec(GCS_DS_PATH, test_tfrec_path, BATCH_SIZE, model, output_filename):
	import numpy as np
	from quick_ml.begin_tpu import get_test_dataset
	testdata = get_test_dataset(GCS_DS_PATH, test_tfrec_path, BATCH_SIZE)
	images = testdata.map(lambda image, idnum : image)
	ids = testdata.map(lambda image, idnum : idnum).unbatch()

	NUM_TEST_IMAGES = 0
	for data in testdata.unbatch():
		NUM_TEST_IMAGES += 1

	#probabilities = model.predict(images)
	#predictions = np.argmax(probabilities,axis = -1)
	predictions = model.predict_classes(images)
	predictions = np.reshape(predictions, newshape = (NUM_TEST_IMAGES,))
	print("Generating Output File...")
	ids = next(iter(ids.batch(NUM_TEST_IMAGES))).numpy().astype('U')
	np.savetxt(output_filename, np.rec.fromarrays([ids, predictions]), fmt = ['%s', '%d'], delimiter = ',', header = 'id,label', comments = '')
	print(f"predictions obtained with filename as {output_filename}")

## function to obtain predictions directly from the dataset
def get_predictions(testTFdataset, model, output_filename):
	import numpy as np
	images = testTFdataset.map(lambda image, idnum : image)
	test_ids = testTFdataset.map(lambda image, idnum : idnum).unbatch()

	NUM_TEST_IMAGES = 0
	for data in testTFdataset.unbatch():
		NUM_TEST_IMAGES += 1

	#probabilities = model.predict(images)
	#predictions = np.argmax(probabilities, axis = -1)
	predictions = model.predict_classes(images)
	predictions = np.reshape(predictions, newshape = (NUM_TEST_IMAGES,))
	print("Generating Output File..")
	test_ids = next(iter(test_ids.batch(NUM_TEST_IMAGES))).numpy().astype('U')
	np.savetxt(output_filename, np.rec.fromarrays([test_ids, predictions]), fmt=['%s', '%d'], delimiter=',', header='id,label', comments='')
	print(f"predictions obtained with filename as -> {output_filename}")


	
## functions for ensembling using Models
def ensemble_model_average(models_list, testTFdataset, classification_type):
	import numpy as np

	test_images_ds = testTFdataset.map(lambda image, idnum : image)
	NUM_IMAGES = 0
	for data in test_images_ds.unbatch():
		NUM_IMAGES += 1
	if classification_type == 'multiclass':
		probs = np.average([models_list[i].predict(test_images_ds) for i in range(len(models_list))], axis = 0)
		preds = np.argmax(probs, axis = -1)
	elif classification_type == 'binary':
		
		preds = np.average([models_list[i].predict(test_images_ds) for i in range(len(models_list))], axis = 0)
		preds = np.array([1 if i >= 0.5 else 0 for i in preds])
		preds = np.reshape(preds, newshape = (NUM_IMAGES,) )
	else:
		print("Choose classification type between 'multiclass' & 'binary'...Not a valid Input.. Exiting")
		return
	return preds

def ensemble_model_weighted(weights, models_list, testTFdataset, classification_type):
	import numpy as np
	probs = []
	test_images_ds = testTFdataset.map(lambda image, idnum : image)
	NUM_IMAGES = 0
	for data in test_images_ds.unbatch():
		NUM_IMAGES += 1
	
	if classification_type == 'binary':
		preds = np.array(sum([models_list[i].predict(test_images_ds) * weights[i] for i in range(len(models_list))]))    
		preds = np.array([1 if i >= 0.5 else 0 for i in preds])
		preds = np.reshape(preds, newshape = (NUM_IMAGES,))
		return preds
	elif classification_type == 'multiclass':
		
		for model in models_list:
			probs.append(model.predict(test_images_ds))

		final_probs = None
		for i, w in enumerate(weights):
			final_probs = w * probs[i]

		preds = np.argmax(final_probs, axis = -1)
	
	else:
		print("Classification type not between 'binary' and 'multiclass'. Please choose the correct classification type...Exiting..")
		return
	return preds


def ensemble_predictions(models_list,  testTFdataset, ensemble_type = 'Model Averaging', classification_type = 'mutliclass', weights = None):
	import numpy as np
	if ensemble_type == 'Model Averaging':
		print("Computing predictions through Model Averaging")
		preds =  ensemble_model_average(models_list, testTFdataset, classification_type)
		print("Generating output file...")

		ids = testTFdataset.map(lambda image, idnum : idnum).unbatch()

		NUM_TEST_IMAGES = 0
		for data in testTFdataset.unbatch():
			NUM_TEST_IMAGES += 1

		ids = next(iter(ids.batch(NUM_TEST_IMAGES))).numpy().astype('U')
		np.savetxt('ensemble_model_averaging.csv', np.rec.fromarrays([ids, preds]), fmt = ['%s', '%d'], delimiter = ',', header = 'id,label', comments = '')
		print("Predictions obtained with the output filename as -> ensemble_model_average")

	elif ensemble_type == 'Model Weighted':
		if weights is None:
			print("Weights not defined for Model Weighted..Exiting...\n Please define weights in a list such that sum(weights) = 1.")
			return
			
		if len(weights) != len(models_list):
			print("Length of weights doesn't match length of models_list... Exiting...")
			return 
		print("Computing predictions through Model Weighted")
		preds =  ensemble_model_weighted(weights, models_list, testTFdataset, classification_type)

		print("Generating output file...")

		ids = testTFdataset.map(lambda image, idnum : idnum).unbatch()

		NUM_TEST_IMAGES = 0
		for data in testTFdataset.unbatch():
			NUM_TEST_IMAGES += 1

		ids = next(iter(ids.batch(NUM_TEST_IMAGES))).numpy().astype('U')
		np.savetxt('ensemble_model_weighted.csv', np.rec.fromarrays([ids, preds]), fmt = ['%s', '%d'], delimiter = ',', header = 'id,label', comments = '')
		print("Predictions obtained with the output filename as -> ensemble_model_weighted.csv")


	else:
		print("Please choose ensemble_type between 'Model Averaging' or 'Model Weighted'")
		return
	#return preds



## function for having test time augmentations
def test_time_augmentations():
	print("Feature Coming Soon!")


if __name__ != '__main__':
	import os
	#os.system('pip install tensorflow==2.2.0')
	import tensorflow as tf 
	import numpy as np