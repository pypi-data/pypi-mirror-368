from glob import glob
from tqdm import tqdm

from multiprocessing import Process
import multiprocessing
import tensorflow as tf

class TFRecordMaker:

	def __init__(self, img_files, mask_files):

		self.img_files = img_files
		self.mask_files = mask_files

		self.imgs = glob(self.img_files)
		self.masks = glob(self.mask_files)
		
		self.imgs.sort()
		self.masks.sort()

		if len(self.imgs) > 0 and len(self.masks) > 0:
			if len(self.imgs) == len(self.masks):
				print(f"Received {len(self.imgs)} images & {len(self.masks)} masks")
			else:
				print("Images unequal!")
				print(f"Received {len(self.imgs)} images & {len(self.masks)} masks")

		else:
			print("Loaded 0 images for either images or masks.")

		self.training_dataset = list(zip(self.imgs, self.masks))



	def _bytes_feature(self, value):
		return tf.train.Feature(bytes_list = tf.train.BytesList(value = [value]))

	def _float_feature(self, value):
		return tf.train.Feature(float_list = tf.train.FloatList(value = [value]))

	def _int64_feature(self, value):
		return tf.train.Feature(int64_list = tf.train.Int64List(value = [value]))

	def serialize_example(self, image, mask):

		feature = {
		'image' : self._bytes_feature(image),
		'mask' : self._bytes_feature(mask)
		}

		example_proto = tf.train.Example(features = tf.train.Features(feature = feature))

		return example_proto.SerializeToString()

	def write_tfrecord_unit(self, training_files, filename, verbose = 0):

		writer = tf.io.TFRecordWriter(filename)

		for i, m in tqdm(training_files, ncols = 100):

			image = tf.io.read_file(i)
			image = tf.io.decode_jpeg(image)

			mask = tf.io.read_file(m)
			mask = tf.io.decode_png(mask)

			example = self.serialize_example(tf.io.encode_jpeg(image).numpy(), tf.io.encode_png(mask).numpy())
			writer.write(example)
		writer.close()

		print(f"Completed {filename}")



	def write_tfrecords(self, filename, split = True):

		procs = []

		cpu_count = multiprocessing.cpu_count()

		if cpu_count >=10:
			cpu_count = 10
		unit = int(len(self.training_dataset) / cpu_count)
		#for i in range(multiprocessing.cpu_count()):

		if split:
			
			for i in range(cpu_count):
				if i == cpu_count - 1 :
					procs.append(Process(target = self.write_tfrecord_unit, args = (self.training_dataset[i * unit :], filename.split('.')[0] + f"_{i}.tfrecord"),))
				else:
					procs.append(Process(target = self.write_tfrecord_unit, args = (self.training_dataset[ i * unit : (i + 1) * unit], filename.split('.')[0] + f"_{i}.tfrecord"), ))

			for proc in procs:
				proc.start()

			for proc in procs:
				proc.join()

		else:

			self.write_tfrecord_unit(self.training_dataset, filename)

		dictionary = {
		'image' : 'FixedLenFeatureString',
		'mask' : "FixedLenFeatureString"
		}

		import json 
		with open('feature.json', 'w') as fp:
			json.dump(dictionary, fp)









