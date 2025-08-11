import tensorflow as tf 

from glob import glob 


def image_dataset_from_directory(directory,
    labels='inferred',
    label_mode='int',
    class_names=None,
    color_mode='rgb',
    batch_size=32,
    image_size=(256, 256),
    shuffle=True,
    seed=None,
    validation_split=None,
    subset=None,
    interpolation='bilinear',
    follow_links=False,
    crop_to_aspect_ratio=False,
    pad_to_aspect_ratio=False,
    data_format=None,
    verbose=True):

	pass

	return tf.keras.utils.image_dataset_from_directory(labels, label_mode, class_names, color_mode, 
		batch_size, image_size, shuffle, seed, validation_split, subset, interpolation, follow_links, crop_to_aspect_ratio, 
		pad_to_aspect_ratio, data_format, verbose)

	

