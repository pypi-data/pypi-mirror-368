import tensorflow as tf
from matplotlib import pyplot as plt

class Visualizer:

	def __init__(self, json_path):
		self.json_path = json_path

		import json
		with open(self.json_path) as json_file:
			self.data = json.load(json_file)

	def _decode_image(self, example):
		

		dictionary = {}
		for key in self.data.keys():
			if self.data[key] == 'FixedLenFeatureString':
				dictionary[key] = tf.io.FixedLenFeature([], tf.string)

		example = tf.io.parse_single_example(example, dictionary)

		image = example['image']
		mask = example['mask']

		image = tf.image.decode_jpeg(image, channels = 3)
		image = tf.image.convert_image_dtype(image, dtype = tf.float32)
		image = image/255.0

		mask = tf.image.decode_png(mask, channels = 1)
		mask = tf.image.convert_image_dtype(mask, dtype = tf.float32)
		mask = mask / 255.0

		return image, mask

	def visualize(self, filenames, num_image_pairs):
		dataset = tf.data.TFRecordDataset(filenames = filenames)

		dataset = dataset.map(self._decode_image)

		plt.figure(figsize = (15, 6))

		for n, (i,m) in enumerate(dataset.take(num_image_pairs)):
			plt.subplot(2, num_image_pairs, n + 1)

			plt.imshow(i * 255.0)

			plt.subplot(2, num_image_pairs, n + 1 + num_image_pairs)
			plt.imshow(m.numpy(), cmap = 'gray')

		plt.show()

	def print_numpy_array(self, filenames, num_image_pairs):
		dataset = tf.data.TFRecordDataset(filenames = filenames)

		dataset = map(self.decode_image)

		for i, m in dataset.take(num_image_pairs):
			print(i.numpy())
			print('-' * 10)
			print(m.numpy())










		