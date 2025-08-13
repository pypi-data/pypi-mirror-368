def _int64_feature(value):
	return tf.train.Feature(int64_list = tf.train.Int64List(value = [value]))

def _bytes_feature(value):
	return tf.train.Feature(bytes_list = tf.train.BytesList(value = [value]))

def load_image(addr, IMAGE_SIZE = (192,192)):
	# read the img & resize to the image size
	# converting the loaded BGR image to RGB image

	img = cv2.imread(addr)
	if img is None:
		return None
	img = cv2.resize(img, IMAGE_SIZE, interpolation = cv2.INTER_CUBIC)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	return img

def get_addrs_labels(data_dir):

	data_path = data_dir + '/*/*.jpg'

	addrs = glob.glob(data_path)
	
	classes = os.listdir(data_dir)
	classes.sort()

	labels_dict = {}
	for i, class_ in enumerate(classes):
		labels_dict[class_] = i
	print(f"Class Encodings for the Dataset Folder is as follows -> \n\n {labels_dict}")
	
	labels = []
	for addr in addrs:
		label = None
		for i in classes:
			if i in addr:
				label = i
				break
		labels.append(labels_dict[label])

	# shuffling the data
	c = list(zip(addrs, labels))
	shuffle(c)

	addrs, labels = zip(*c)

	return addrs, labels


def affirmationcsv(func):
	def inner(*args, **kwargs):

		print("""Please ensure that the data format is of the following structure. -> \n

			csv file format. 

			| Image      | Id    |
			------------------
			|Image1.jpg  | classA|
			|Image2.jpg  | classB|
			|Image3.jpg  | classA|
			|Image4.jpg  | classC|
			|ImageN.jpg  | classN|

			AND

			DATA_DIR of Images follows the following structure -> \n

			/data 
				|
				|-> Image1.jpg
				|-> Image2.jpg
				|-> Image3.jpg
				|
				|-> ImageN.jpg


			""")
		func(*args, **kwargs)

	return inner

@affirmationcsv
def create_tfrecords_from_csv(data_dir, csv_path, outputfilename, IMAGE_SIZE = (192,192)):
	

	import pandas as pd 
	df = pd.read_csv(csv_path)

	df.sort_values(['Image'], axis = 0, inplace = True)

	addrs = glob.glob(data_dir + '/*.jpg')
	addrs.sort()
	labels = list(df['Id'])
	
	labels_dict = {}
	labels_unique = list(set(labels))
	labels_unique.sort()

	for i, class_ in enumerate(labels_unique):
		labels_dict[class_] = i
		
	print(f"Encodings for the classes are -> {labels_dict}")
	
	labels = [labels_dict[i] for i in labels]
	
	c = list(zip(addrs, labels))
	shuffle(c)


	addrs, labels = zip(*c)
	create_tfrecord_labeled(addrs, labels, outputfilename, IMAGE_SIZE)



@affirmationcsv
def create_split_tfrecords_from_csv(data_dir, csv_path, outfile1name, outfile2name, split_size_ratio , IMAGE_SIZE = (192,192)):
	
	import pandas as pd
	df = pd.read_csv(csv_path)

	df.sort_values(['Image'], axis = 0, inplace = True)

	addrs = glob.glob(data_dir + '/*.jpg')
	addrs.sort()
	labels = list(df['Id'])
	
	labels_dict = {}
	labels_unique = list(set(labels))
	labels_unique.sort()

	for i, class_ in enumerate(labels_unique):
		labels_dict[class_] = i
		
	print(f"Encodings for the classes are -> {labels_dict}")
	
	labels = [labels_dict[i] for i in labels]
	
	c = list(zip(addrs, labels))
	shuffle(c)
	addrs, labels = zip(*c)

	file1_addrs = addrs[0 : int(split_size_ratio * len(addrs))]
	file1_labels = labels[0: int(split_size_ratio * len(labels))]

	file2_addrs = addrs[int(split_size_ratio * len(addrs)) :]
	file2_labels =  labels[int(split_size_ratio * len(labels)):]

	create_tfrecord_labeled(file1_addrs, file1_labels, outfile1name, IMAGE_SIZE)
	create_tfrecord_labeled(file2_addrs, file2_labels, outfile2name, IMAGE_SIZE)

def retrieve_file_paths(dirName):
	filePaths = []
	
	for root, directories, files in os.walk(dirName):
		for filename in files:
			filePath = os.path.join(root, filename)
			filePaths.append(filePath)
			
	return filePaths


def create_split_tfrecords_data(data_dir, outfile1name, output1folder, outfile2name, output2folder, split_size_ratio,num_parts1 = 1, num_parts2 = 1,  IMAGE_SIZE = (192,192), zip = False):

	print(f"Split ratio -> {split_size_ratio}")
	addrs, labels = get_addrs_labels(data_dir)

	file1_addrs = addrs[0 : int(split_size_ratio * len(addrs))]
	file1_labels = labels[0: int(split_size_ratio * len(labels))]

	file2_addrs = addrs[int(split_size_ratio * len(addrs)) :]
	file2_labels =  labels[int(split_size_ratio * len(labels)):]
	
	os.mkdir(output1folder); os.mkdir(output2folder)
	
	from pathlib import Path
	os.chdir(output1folder)
	create_tfrecord_labeled(file1_addrs, file1_labels, outfile1name, IMAGE_SIZE, num_parts1)
	os.chdir(Path(os.getcwd()).parent)
	os.chdir(output2folder)
	create_tfrecord_labeled(file2_addrs, file2_labels, outfile2name, IMAGE_SIZE, num_parts2)
	os.chdir(Path(os.getcwd()).parent)
	
	if zip:
		folder1_files = retrieve_file_paths(str(Path(output1folder).absolute()))
		folder2_files = retrieve_file_paths(str(Path(output2folder).absolute()))
		
		import zipfile
		
		zip_file = zipfile.ZipFile('data' + '.zip', 'w')
		with zip_file:
			for file in folder1_files:
				zip_file.write(file)
			for file in folder2_files:
				zip_file.write(file)
	
	print("Data Successfully created!")

def affirmationfolder(func):
	def inner(*args,**kwargs):
		print("""
		Ensure that the data directory has the following structure ->

		/data|
			 |
			 |-> class1
			 |-> class2
			 |-> class3
			 |-> class4
			 .
			 .
			 .
			 |-> classN

		the input to data_dir must the path to /data folder. & Make sure that the images are in .jpg format
		""")
		func(*args, **kwargs)
	return inner

@affirmationfolder
def create_tfrecord_labeled(addrs, labels, out_filename, IMAGE_SIZE = (192,192), num_parts = 1):



	print(f"Beginning to write data to {out_filename}\n\n")
	if num_parts == 1:
		
		writer = tf.io.TFRecordWriter(out_filename)
		for i in range(len(addrs)):
			if i % 300 == 0:
				print("Data written -> {}/{}".format(i, len(addrs)))
				sys.stdout.flush()

			# loading the image
			img = load_image(addrs[i], IMAGE_SIZE)
			label = labels[i]

			if img is None:
				continue

			# feature creation

			feature = {
				'image' : _bytes_feature(img.tostring()),
				'label' : _int64_feature(label)
			}



			# example protocol buffer
			example = tf.train.Example(features = tf.train.Features(feature = feature))

			# serialize the write the output to the file
			writer.write(example.SerializeToString())
		writer.close()
		sys.stdout.flush()
		print(f"Done with writing data to {out_filename}\n\n")
		print("""
				Your Labeled TFRecord Format is -> 

				{
				'image' : tf.io.FixedLenFeature([], tf.string),
				'label' : tf.io.FixedLenFeature([], tf.int64)
				}

				You would be asked the TFRecord Format while reading the training and validation dataset.
		""")
		print("Now after you have obtained the tfrecords, you need to upload them to GCS Buckets to utlize TPU computation...")
		print("To do so, the easiest method is uploading on Kaggle.")
		print("""
			1. Public Datasets

			from kaggle_datasets import KaggleDatasets
			GCS_DS_PATH = KaggleDatasets().get_gcs_path()


			2. Private Datasets

			# Get the credentials from the Cloud SDK
			from kaggle_secrets import UserSecretsClient
			user_secrets = UserSecretsClient()
			user_credential = user_secrets.get_gcloud_credential()

			# Set the credentials
			user_secrets.set_tensorflow_credential(user_credential)

			# Use a familiar call to get the GCS path of the dataset
			from kaggle_datasets import KaggleDatasets
			GCS_DS_PATH = KaggleDatasets().get_gcs_path()
			""")
	else:
		
		chunk_size = len(addrs) // num_parts
		
		indx = 0
		
		for part in range(num_parts):
			writer = tf.io.TFRecordWriter(out_filename.split('.')[0] + f'_part_{part+1}.' + out_filename.split('.')[1])
			addrs_ = addrs[indx : indx + chunk_size]
			labels_ = labels[indx : indx + chunk_size]
			if part == num_parts - 1:
				addrs_ = addrs[indx:]
				labels_ = labels[indx:]
			for i in range(len(addrs_)):
				if i % 100 == 0:
					print("Data written -> {}/{}".format(i, len(addrs_)))
					sys.stdout.flush()

				# loading the image
				img = load_image(addrs_[i], IMAGE_SIZE)
				label = labels_[i]

				if img is None:
					continue

				# feature creation

				feature = {
					'image' : _bytes_feature(img.tostring()),
					'label' : _int64_feature(label)
				}



				# example protocol buffer
				example = tf.train.Example(features = tf.train.Features(feature = feature))

				# serialize the write the output to the file
				writer.write(example.SerializeToString())
			writer.close()
			sys.stdout.flush()
			indx = indx + chunk_size
			print(f"Done with writing data to {out_filename.split('.')[0] + f'_part_{part+1}.' + out_filename.split('.')[1]}\n\n")
			print("""
				Your Labeled TFRecord Format is -> 

				{
				'image' : tf.io.FixedLenFeature([], tf.string),
				'label' : tf.io.FixedLenFeature([], tf.int64)
				}

				You would be asked the TFRecord Format while reading the training and validation dataset.
			""")
			print("Now after you have obtained the tfrecords, you need to upload them to GCS Buckets to utlize TPU computation...")
			print("To do so, the easiest method is uploading on Kaggle.")
			print("""
				1. Public Datasets

				from kaggle_datasets import KaggleDatasets
				GCS_DS_PATH = KaggleDatasets().get_gcs_path()


				2. Private Datasets

				# Get the credentials from the Cloud SDK
				from kaggle_secrets import UserSecretsClient
				user_secrets = UserSecretsClient()
				user_credential = user_secrets.get_gcloud_credential()

				# Set the credentials
				user_secrets.set_tensorflow_credential(user_credential)
	
				# Use a familiar call to get the GCS path of the dataset
				from kaggle_datasets import KaggleDatasets
				GCS_DS_PATH = KaggleDatasets().get_gcs_path()
				""")

def get_addrs_ids(data_dir):
	data_path = data_dir + '/*.jpg'

	addrs = glob.glob(data_path)

	ids = os.listdir(data_dir)


	return addrs, ids


def create_tfrecord_unlabeled(out_filename, addrs, ids, IMAGE_SIZE = (192,192)):
	print("""
		The Data for this should be unlabeled. 

		The folder structure should be

		data |
			 |
			 |->filename1.jpg
			 |->filename2.jpg
			 |->filename3.jpg
			 |->filename4.jpg
			 |.
			 ..
			 ..
			 |->filenameN.jpg


		""")

	print(f"Beginning to write the {out_filename}\n\n")
	writer = tf.io.TFRecordWriter(out_filename)
	for i in range(len(addrs)):
		if i % 300 == 0:
			print("Data Written -> {}/{}".format(i, len(addrs)))
			sys.stdout.flush()

		#loading the image
		img = load_image(addrs[i], IMAGE_SIZE)
		idnum = ids[i]

		if img is None:
			continue

		#feature creation
		feature = {
			'image' : _bytes_feature(img.tostring()),
			'idnum' : _bytes_feature(idnum.encode())
		}

		# example protocol buffer
		example = tf.train.Example(features = tf.train.Features(feature = feature))


		# serialize & write
		writer.write(example.SerializeToString())
	writer.close()
	sys.stdout.flush()

	print("""
			Your Unlabeled TFRecord Format is -> 

			{
			'image' : tf.io.FixedLenFeature([], tf.string),
			'idnum' : tf.io.FixedLenFeature([], tf.string)
			}

			You would be asked the TFRecord Format while reading the test dataset.
	""")
	print("After you have obtained the tfrecords, you need to upload the tfrecords to GCS Buckets for TPU computation")
	print("To do so, the easiest method is to upload on Kaggle. Either as a public or as a private dataset.")
	print("""
		NOTE: Fully Functional and working with Public Datasets
		1. Public Datasets

		from kaggle_datasets import KaggleDatasets
		GCS_DS_PATH = KaggleDatasets().get_gcs_path()


		NOTE : Not tested with Private Datasets
		2. Private Datasets

		# Get the credentials from the Cloud SDK
		from kaggle_secrets import UserSecretsClient
		user_secrets = UserSecretsClient()
		user_credential = user_secrets.get_gcloud_credential()

		# Set the credentials
		user_secrets.set_tensorflow_credential(user_credential)

		# Use a familiar call to get the GCS path of the dataset
		from kaggle_datasets import KaggleDatasets
		GCS_DS_PATH = KaggleDatasets().get_gcs_path()

		""")


if __name__ != "__main__":
	import os
	import tensorflow as tf
	from random import shuffle
	import glob
	import sys
	import cv2
	import numpy as np 
