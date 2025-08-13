def rampup_lrfn(epoch):

	"""
	Fine Tune the pretrained model weights in a better and smooth manner.
	Use this as a callback feature during the model training.
	"""
	
	if epoch < LR_RAMPUP_EPOCHS:
		lr = (LR_MAX - LR_START) / LR_RAMPUP_EPOCHS * epoch + LR_START
	elif epoch < LR_RAMPUP_EPOCHS + LR_SUSTAIN_EPOCHS : 
		lr = LR_MAX
	else:
		lr = (LR_MAX - LR_MIN) + LR_EXP_DECAY**(epoch - LR_RAMPUP_EPOCHS - LR_SUSTAIN_EPOCHS) + LR_MIN

	return lr

def stepped_lrfn(epoch):
	return 1e-4 * (0.75 ** np.floor(epoch / 2))

def step_decay(epoch):
	initAlpha = 0.01
	factor = 0.25
	dropEvery = 5
	
	alpha = initAlpha * (factor ** np.floor((1+epoch) / dropEvery))
	return float(alpha)

def simple_lrfn(epoch):

	if epoch < 6:
		return 0.001
	elif 6 < epoch < 12 : 
		return 0.0005
	elif 12 < epoch < 18 : 
		return 0.00008
	else:
		return 0.000006

	return

def plot_lrfn(lr_type = 'rampup'):

	EPOCHS = 20
	import matplotlib.pyplot as plt
	rng = [ i for i in range(EPOCHS)]	
	if lr_type == 'rampup':
		y = [rampup_lrfn(x) for x in range(EPOCHS)]
	elif lr_type == 'simple':
		y = [simple_lrfn(x) for x in range(EPOCHS)]
	elif lr_type == 'stepped':
		y = [stepped_lrfn(x) for x in range(EPOCHS)]
	elif lr_type == 'step_decay':
		y = [step_decay(x) for x in range(EPOCHS)]
	else:
		print("lr_type not among known LRs. If it's a valid LR scheduler method, drop a mail @ antoreepjana@gmail.com and check the developments section of the documentation of quick_ml. https://gitlab.com/antoreep_jana/quick_ml/-/blob/master/README.md")
		return 
		
	print("Learning Rate Schedule => ")
	plt.plot(rng, y); plt.show()
	

def get_callbacks(lr_scheduler = None, early_stopping = None, reduce_lr_on_plateau = None):
	callbacks = []

	#### Learning Rate Scheduler

	if lr_scheduler == 'simple':
		lr_callback = tf.keras.callbacks.LearningRateScheduler(simple_lrfn, verbose = False)

	elif lr_scheduler == 'rampup':
		lr_callback = tf.keras.callbacks.LearningRateScheduler(rampup_lrfn, verbose = False)
	
	elif lr_scheduler == 'stepped':
		lr_callback = tf.keras.callbacks.LearningRateScheduler(stepped_lrfn, verbose = False)
	elif lr_scheduler == 'step_decay':
		lr_callback = tf.keras.callbacks.LearningRateScheduler(step_decay, verbose = False)
	# more callbacks in upcoming versions...
	if lr_callback is not None:
		callbacks.append(lr_callback)

	####  Early Stopping	
	if early_stopping == 'default':
		es_callback = tf.keras.callbacks.EarlyStopping(
				monitor = 'val_loss',
				min_delta = 0,
				patience = 0,
				verbose = 0, 
				mode = 'auto',
				baseline = None,
				restore_best_weights = False
			)
	elif early_stopping is None:
		es_callback = None
	elif isinstance(early_stopping, dict):
		es_callback = tf.keras.callbacks.EarlyStopping(**early_stopping)

	if es_callback is not None:
		callbacks.append(es_callback)



	#### Reduce LR On Plateau
	if reduce_lr_on_plateau == 'default':
		rlop_callback = tf.keras.callbacks.ReduceLROnPlateau(
			monitor = 'val_loss', 
			factor = 0.1, 
			patience = 10, 
			mode = 'auto',
			min_delta = 0.0001, 
			cooldown = 0,
			min_lr = 0)
	elif reduce_lr_on_plateau is None:
		rlop_callback = None
	elif isinstance(reduce_lr_on_plateau, dict):
		rlop_callback = tf.keras.callbacks.ReduceLROnPlateau(**reduce_lr_on_plateau)

	if rlop_callback is not None:
		callbacks.append(rlop_callback)

	return callbacks
		

if __name__ != "__main__":
	global LR_MAX
	global LR_MIN
	global LR_RAMPUP_EPOCHS
	global LR_SUSTAIN_EPOCHS
	global LR_EXP_DEC
	global LR_START
	
	import tensorflow as tf
	import numpy as np
	LR_MAX = 0.00005 * 8
	LR_MIN = 0.00001
	LR_RAMPUP_EPOCHS = 5
	LR_SUSTAIN_EPOCHS = 0
	LR_EXP_DECAY = 0.8
	LR_START = 0.00001
