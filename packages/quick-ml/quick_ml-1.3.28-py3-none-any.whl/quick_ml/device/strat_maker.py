import re
import tensorflow as tf 

class StrategyMaker:

	def __init__(self, device = 'cpu'):
		self.device = device.lower() ## one among : 'cpu', 'gpu', 'mgpu', 'tpu'
		self.strategy = None

	def initialize(self):

		if self.device == 'tpu':
			resolver = tf.distribute.cluster_resolver.TPUClusterResolver()
			tf.config.experimental_connect_to_cluster(resolver)
			tf.tpu.experimental.initialize_tpu_system(resolver)
			self.strategy = tf.distribute.TPUStrategy(resolver)

		elif "mgpu" in self.device:
			if self.device == 'mgpu[all]':
				self.strategy = tf.distribute.MirroredStrategy()
			else:
				gpus = re.findall('\[(.*)\]', self.device)[0].split(',')
				g_devices = []
				for g in gpus:
					g_devices.append(f"/gpu:{str(g)}")
				self.strategy = tf.distribute.MirroredStrategy(devices = g_devices)

		elif self.device == 'gpu' or self.device == 'cpu':
			self.strategy = tf.distribute.MirroredStrategy()

		#return self.strategy

	def get_batch_size(self):

		return 8 * self.strategy.num_replicas_in_sync



