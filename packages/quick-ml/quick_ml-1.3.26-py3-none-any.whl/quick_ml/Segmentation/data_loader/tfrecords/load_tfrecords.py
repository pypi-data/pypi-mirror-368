import tensorflow as tf
#AUTOTUNE = tf.data.AUTOTUNE

class TFRecLoader:

	def __init__(self, filenames, feature_json):
		self.dataset = None
		#self.final_dataset = None
		self.filenames = filenames
		self.feature_json = feature_json

		import json
		with open(self.feature_json) as json_file:
			self.data = json.load(json_file)
		self.dictionary = {}

		for key in self.data.keys():
			if self.data[key] == 'FixedLenFeatureString':
				self.dictionary[key] = tf.io.FixedLenFeature([], tf.string)
		#self.dictionary = 

	def _decode_image(self, example):
		
		example = tf.io.parse_single_example(example, self.dictionary)

		image = example['image']
		image = tf.io.decode_jpeg(image, channels = 3)
		#image = tf.image.convert_image_dtype(image, dtype = tf.float32)  (no division by 255)
		# or
		image = tf.image.convert_image_dtype(image, dtype = tf.uint8)
		image = image / 255
		

		mask = example['mask']
		mask = tf.io.decode_png(mask, channels = 1)
		mask = tf.image.convert_image_dtype(mask, dtype = tf.uint8)
		#print(mask)
		mask = mask/255

		return image, mask

	def load(self, batch_size):

		self.dataset = tf.data.TFRecordDataset(filenames = tf.io.gfile.glob(self.filenames))

		self.dataset = self.dataset.map(self._decode_image)

		#self.final_dataset = self.dataset.cache()
		#self.final_dataset = self.final_dataset.prefetch(buffer_size = int(batch_size / 2))#self.final_dataset.prefetch(buffer_size = AUTOTUNE)

		final_dataset = self.dataset.batch(batch_size, drop_remainder = True)
		final_dataset = final_dataset.prefetch(tf.data.AUTOTUNE)		
		return final_dataset

	def get_dataset_length(self):

		count_iterator = self.dataset.as_numpy_iterator()
		num_images = sum(1 for _ in count_iterator)
		print("Number of images loaded:", num_images)
		
	def visualize_loaded(self, num_pairs = 3):
		from matplotlib import pyplot as plt 

		plt.figure(figsize = (15, 15))
		for n , (i,m ) in enumerate(self.dataset.take(num_pairs)):
			#print(i)
			plt.subplot(2, num_pairs, n + 1)
			plt.imshow(i * 255.0)

			plt.subplot(2, num_pairs, n + 1 + num_pairs)
			plt.imshow(m, cmap = 'gray')
			
	def visualize_batch(self, num_pairs = 3):
		
		from matplotlib import pyplot as plt 

		plt.figure(figsize = (15, 15))
		
		#print(self.dataset.take(1))
		
		for i_b, m_b in self.final_dataset.take(1):
			
			for n, (i,m) in enumerate(zip(i_b, m_b)):
				
			
				plt.subplot(2, num_pairs , n + 1)
				plt.imshow(i * 255.0)

				plt.subplot(2, num_pairs, n + 1 + num_pairs)
				plt.imshow(m, cmap = 'gray')
				
				if n + 1 == num_pairs:
					break

