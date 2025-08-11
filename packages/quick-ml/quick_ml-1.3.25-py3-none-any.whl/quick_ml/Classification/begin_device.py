def define_strategy(mixed_precision = False, xla_accelerate = False):
	try:
		tpu = tf.distribute.cluster_resolver.TPUClusterResolver(tpu = 'local')
		print('Running on TPU ', tpu.master())
	
	except ValueError:
		print("TPU not activated. Please check the settings. Settings -> Accelerator -> TPU v3-8\n")
		tpu = None
	
	
	if tpu != None:
		tf.config.experimental_connect_to_cluster(tpu)
		tf.tpu.experimental.initialize_tpu_system(tpu)
		#strategy = tf.distribute.experimental.TPUStrategy(tpu)
		strategy = tf.distribute.TPUStrategy(tpu)
	else:
		strategy = tf.distribute.get_strategy()

	if mixed_precision:
		from tensorflow.keras.mixed_precision import experimental as mixed_precision 
		if tpu: 
			policy = tf.keras.mixed_precision.experimental.Policy('mixed_bfloat16')
		else:
			policy = tf.keras.mixed_precision.experimental.Policy('mixed_float16')
		mixed_precision.set_policy(policy)
		print("Mixed precision enabled")
	else:
		print("Mixed precision disabled")
	if xla_accelerate:
		tf.config.optimizer.set_jit(True)
		print("Accelerated Linear Algebra enabled")
	else:
		print("Accelerated Linear Algebra disabled")
	
	return strategy, tpu


############### DATASET SETUP  ###################


def decode_image(image_data, IMAGE_SIZE):
	
	image = tf.io.decode_raw(image_data, tf.uint8)
	
	image = tf.cast(image, tf.float32) / 255.0
	

	# how would I obtain Image_Size 
	image = tf.reshape(image, [*IMAGE_SIZE, 3])
	return image

def read_labeled_tfrecord(example):
	
	global dictionary_labeled
	global IMAGE_SIZE
	global tmp_d_l
	global tmp_img_sz
	
	tmp_d_l = dictionary_labeled
	tmp_img_sz = IMAGE_SIZE
	
	if dictionary_labeled is None:
		print("Enter the dictionary of Labeled_TFREC_FORMAT\n")
		dictionary = eval(input())
	else:
		dictionary = eval(dictionary_labeled)
	
	if IMAGE_SIZE is None:
		print("Enter Image Size; Example Format ->  192,192  (w/o brackets)\n\n")
		IMAGE_SIZE = input()
		
	IMAGE_SIZE = [int(IMAGE_SIZE.split(',')[0]), int(IMAGE_SIZE.split(',')[1])]
	example = tf.io.parse_single_example(example, dictionary)
	image = decode_image(example[list(dictionary.keys())[0]], IMAGE_SIZE)
	label = tf.cast(example[list(dictionary.keys())[1]], tf.int32)
	
	dictionary_labeled = tmp_d_l
	IMAGE_SIZE = tmp_img_sz
	
	return image, label

def read_unlabeled_tfrecord(example):
	
	global dictionary_unlabeled
	global IMAGE_SIZE
	global tmp_d_ul
	global tmp_img_sz
	
	tmp_d_ul = dictionary_unlabeled
	tmp_img_sz = IMAGE_SIZE
	
	
	if dictionary_unlabeled is None:
		print("Enter the dictionary of the UnLabeled_TFREC_FORMAT\n")
		dictionary = eval(input())
	else:
		dictionary = eval(dictionary_unlabeled)
	
	if IMAGE_SIZE is None:
		print("Enter Image Size; Example Format ->  192,192  (w/o brackets)\n\n")
		IMAGE_SIZE = input()
	IMAGE_SIZE = [int(IMAGE_SIZE.split(',')[0]), int(IMAGE_SIZE.split(',')[1])]
	example = tf.io.parse_single_example(example, dictionary)
	image = decode_image(example[list(dictionary.keys())[0]], IMAGE_SIZE)
	idnum = example[list(dictionary.keys())[1]]
	dictionary_unlabeled = tmp_d_ul
	IMAGE_SIZE = tmp_img_sz
	
	return image, idnum


def load_dataset(filenames, labeled = True, ordered = False):
	ignore_order = tf.data.Options()
	if not ordered:
		ignore_order.experimental_deterministic = False
		
	dataset = tf.data.TFRecordDataset(filenames, num_parallel_reads = tf.data.experimental.AUTOTUNE) # can add AUTO if multiple files need to be read in a go.
	dataset = dataset.with_options(ignore_order)
	dataset = dataset.map(read_labeled_tfrecord if labeled else read_unlabeled_tfrecord)
	return dataset


def get_training_dataset(GCS_DS_PATH, train_tfrec_path, BATCH_SIZE, augmentation = False):
	
	if not augmentation:
		print(""" Make Sure to
		Define how to read LABELED tfrecord data as per the LABELED_TFRECORD_FORMAT
		Rest of the helper functions are implemented.
		""")
	dataset = load_dataset(tf.io.gfile.glob(GCS_DS_PATH  + train_tfrec_path), labeled = True)
	if augmentation:
		from quick_ml.augments import augmentations
		dataset = dataset.map(augmentations, num_parallel_calls = tf.data.experimental.AUTOTUNE)
	cnt = 0
	for data in dataset:
		cnt += 1
	if not augmentation:
		print(f"Loaded {train_tfrec_path} with {cnt} examples")
	dataset = dataset.repeat()
	dataset = dataset.shuffle(2048)
	dataset = dataset.batch(BATCH_SIZE)
	dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)
	return dataset


def get_validation_dataset(GCS_DS_PATH,val_tfrec_path, BATCH_SIZE , augmentation = False):
	
	
	if not augmentation:
		print(""" Make Sure to
		Define how to read LABELED tfrecord data as per the LABELED_TFRECORD_FORMAT
		Rest of the helper functions are implemented.
		""")
	
	dataset = load_dataset(tf.io.gfile.glob(GCS_DS_PATH + val_tfrec_path), labeled = True, ordered = False)
	
	if augmentation:
		from quick_ml.augments import augmentations
		dataset = dataset.map(augmentations, num_parallel_calls = tf.data.experimental.AUTOTUNE)
	cnt = 0
	for data in dataset:
		cnt += 1
	if not augmentation:
		print(f"Loaded {val_tfrec_path} with {cnt} examples")
	dataset = dataset.batch(BATCH_SIZE)
	dataset = dataset.cache()
	dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)
	
	return dataset


def get_test_dataset(GCS_DS_PATH, test_tfrec_path, BATCH_SIZE):
	
	print(""" Make Sure to
	Define how to read UNLABELED tfrecord data as per the UNLABELED_TFRECORD_FORMAT
	Rest of the helper functions are implemented.
	""")

	dataset = load_dataset(tf.io.gfile.glob(GCS_DS_PATH + test_tfrec_path), labeled = False, ordered = True)
	cnt = 0
	for data in dataset:
		cnt += 1
	print(f"Loaded {test_tfrec_path} with {cnt} examples")
	dataset = dataset.batch(BATCH_SIZE)
	return dataset


def count_num_examples(tfrecordfile, labeled = True):
	
	tfdataset = load_dataset(tfrecordfile, labeled)
	cnt = 0
	for data in tfdataset:
		cnt += 1
	print(f"{tfrecordfile} contains {cnt} Examples")

def get_labeled_tfrecord_format(dict, img_size):
	global dictionary_labeled
	global IMAGE_SIZE
	
	dictionary_labeled = dict
	IMAGE_SIZE = img_size
	
def get_unlabeled_tfrecord_format(dict, img_size):
	global dictionary_unlabeled
	global IMAGE_SIZE
	
	dictionary_unlabeled = dict
	IMAGE_SIZE = img_size

## later	
def set_parameters(epochs, batch_size_base, GCS_PATH):
	from kaggle_datasets import KaggleDatasets
	GCS_DS_PATH = KaggleDatasets().get_gcs_path(GCS_PATH)
	print(f'GCS_DS_PATH ->  {GCS_DS_PATH}')
	
	STEPS_PER_EPOCH = None

if __name__ != "__main__":
	import tensorflow as tf
	




def define_strategy(mixed_precision = False, xla_accelerate = False, device = 'tpu'):
	tpu = None
	if device == 'tpu':
		try:
			tpu = tf.distribute.cluster_resolver.TPUClusterResolver(tpu = 'local')
			tf.config.experimental_connect_to_cluster(tpu)
			tf.tpu.experimental.initialize_tpu_system(tpu)
			#strategy = tf.distribute.experimental.TPUStrategy(tpu)
			strategy = tf.distribute.TPUStrategy(tpu)
			print('Running on TPU ', tpu.master())
	
		except ValueError:
			print("TPU not activated. Please check the settings. Settings -> Accelerator -> TPU v3-8\n")
			tpu = None
	else:
		strategy = tf.distribute.get_strategy()

	if mixed_precision:
		from tensorflow.keras.mixed_precision import experimental as mixed_precision 
		if tpu: 
			policy = tf.keras.mixed_precision.experimental.Policy('mixed_bfloat16')
		else:
			policy = tf.keras.mixed_precision.experimental.Policy('mixed_float16')
		mixed_precision.set_policy(policy)
		print("Mixed precision enabled")
	else:
		print("Mixed precision disabled")
	if xla_accelerate:
		tf.config.optimizer.set_jit(True)
		print("Accelerated Linear Algebra enabled")
	else:
		print("Accelerated Linear Algebra disabled")
	
	return strategy, tpu