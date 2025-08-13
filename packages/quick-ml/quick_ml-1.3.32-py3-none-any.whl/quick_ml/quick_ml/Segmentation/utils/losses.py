"""
Semantic Segmentation Loss Functions : 

	a) Focal Loss
	b) Dice Loss
	c) IoU -balanced Loss
	d) Boundary Loss
	e) Weighted Cross-Entropy
	f) Lovasz-Softmax Loss


"""

import tensorflow as tf

def dice_coef(y_true, y_pred):

	smooth = 1.
	y_true_f = K.flatten(y_true)
	y_pred_f = K.flatten(y_pred)
	intersection = K.sum(y_true_f * y_pred_f)
	return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)


def bce_dice_loss(y_true, y_pred):

	return 0.5 * tf.keras.losses.binary_crossentropy(y_true, y_pred) 



class DiceLoss(tf.keras.losses.Loss):

	def __init__(self, smooth = 1e-6, gama = 2):
		super(DiceLoss, self).__init__(name = 'dice_loss')

		#self.name = 'NDL'
		self.smooth = smooth
		self.gamma = gama 

	def call(self, y_true, y_pred):
		y_true, y_pred = tf.cast(
			y_true, dtype = tf.float32
			), tf.cast(y_pred, tf.float32)

		nominator = 2 * \
		tf.reduce_sum(tf.multiply(y_pred, y_true)) + self.smooth

		denominator = tf.reduce_sum(
			y_pred ** self.gamma) + tf.reduce_sum(y_true ** self.gamma) + self.smooth
		result = 1 - tf.divide(nominator, denominator)
		return result
