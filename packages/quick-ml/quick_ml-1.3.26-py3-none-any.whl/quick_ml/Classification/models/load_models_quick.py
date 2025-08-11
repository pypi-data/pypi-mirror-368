def create_model(classes, model_name = 'VGG16', classification_model = 'default', freeze = False, input_shape = [512, 512,3], activation  = 'softmax', weights= "imagenet", optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = 'sparse_categorical_accuracy'):
	"""
	
	MODELS -> 'VGG16', 'VGG19',  
	'Xception',
	'DenseNet121', 'DenseNet169', 'DenseNet201', 
	'ResNet50', 'ResNet101', 'ResNet152', 'ResNet50V2', 'ResNet101V2', 'ResNet152V2', 
	'MobileNet', 'MobileNetV2',
	'InceptionV3', 'InceptionResNetV2', 
	'EfficientNetB0', 'EfficientNetB1', 'EfficientNetB2', 'EfficientNetB3', 'EfficientNetB4', 'EfficientNetB5', 'EfficientNetB6', 'EfficientNetB7'

	How to use ->
	
	1) For Effnet & Other than Effnet Models
	   a) with default classification model

	  from load_models_quick import create_model
	  model = create_model(classes = n_classes, model_name = "VGG19")
	   
	   
	   b) With Custom Classification Model
	   
	   from load_models_quick import create_model 
	   class_model = tf.keras.Sequential([
		  tf.keras.lkeras.layers.GlobalAveragePooling2D(),
		  tf.keras.layers.Dense(n_classes, activation = 'softmax') ])
	   model = create_model(classes = n_classes, model_name = 'VGG19', classification_model = 
		class_model)
		
		
	Load multiple models in a go. 
	
	model_names = ['VGG16', 'InceptionV3', 'DenseNet201', "EfficientNetB7"]
	models = []
	for model in model_names:
		models.append(create_model(classes = n_classes, model_name = model))
	
	
	"""
	weights_dict = {
	'DenseNet121' : '/kaggle/input/tf-keras-pretrained-weights/No Top/densenet121_weights_tf_dim_ordering_tf_kernels_notop.h5',
	'DenseNet169' : '/kaggle/input/tf-keras-pretrained-weights/No Top/densenet169_weights_tf_dim_ordering_tf_kernels_notop.h5', 
	'DenseNet201' : '/kaggle/input/tf-keras-pretrained-weights/No Top/densenet201_weights_tf_dim_ordering_tf_kernels_notop.h5',
	'EfficientNetB0' : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b0_weights_tf_dim_ordering_tf_kernels_autoaugment_notop.h5',
	'EfficientNetB1' : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b1_weights_tf_dim_ordering_tf_kernels_autoaugment_notop.h5',
	'EfficientNetB2' : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b2_weights_tf_dim_ordering_tf_kernels_autoaugment_notop.h5',
	'EfficientNetB3' : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b3_weights_tf_dim_ordering_tf_kernels_autoaugment_notop.h5',
	'EfficientNetB4' : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b4_weights_tf_dim_ordering_tf_kernels_autoaugment_notop.h5',
	'EfficientNetB5' : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b5_weights_tf_dim_ordering_tf_kernels_autoaugment_notop.h5',
	'EfficientNetB6' : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b6_weights_tf_dim_ordering_tf_kernels_autoaugment_notop.h5' ,
	'EfficientNetB7' : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b7_weights_tf_dim_ordering_tf_kernels_autoaugment_notop.h5',
	'InceptionResNetV2' : '/kaggle/input/tf-keras-pretrained-weights/No Top/inception_resnet_v2_weights_tf_dim_ordering_tf_kernels_notop.h5' ,
	'InceptionV3' : '/kaggle/input/tf-keras-pretrained-weights/No Top/inception_v3_weights_tf_dim_ordering_tf_kernels_notop.h5',
	"MobileNet" : '/kaggle/input/tf-keras-pretrained-weights/No Top/mobilenet_1_0_192_tf_no_top.h5',
	"MobileNetV2" : '/kaggle/input/tf-keras-pretrained-weights/No Top/mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_192_no_top.h5',
	"ResNet101" : '/kaggle/input/tf-keras-pretrained-weights/No Top/resnet101_weights_tf_dim_ordering_tf_kernels_notop.h5',
	"ResNet101V2" : '/kaggle/input/tf-keras-pretrained-weights/No Top/resnet101v2_weights_tf_dim_ordering_tf_kernels_notop.h5',
	"ResNet152" : '/kaggle/input/tf-keras-pretrained-weights/No Top/resnet152_weights_tf_dim_ordering_tf_kernels_notop.h5',
	"ResNet152V2" : '/kaggle/input/tf-keras-pretrained-weights/No Top/resnet152v2_weights_tf_dim_ordering_tf_kernels_notop.h5',
	"ResNet50" : '/kaggle/input/tf-keras-pretrained-weights/No Top/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5' ,
	"ResNet50V2" : '/kaggle/input/tf-keras-pretrained-weights/No Top/resnet50v2_weights_tf_dim_ordering_tf_kernels_notop.h5',
	"VGG16" : '/kaggle/input/tf-keras-pretrained-weights/No Top/vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5',
	"VGG19" : '/kaggle/input/tf-keras-pretrained-weights/No Top/vgg19_weights_tf_dim_ordering_tf_kernels_notop.h5',
	"Xception" : '/kaggle/input/tf-keras-pretrained-weights/No Top/xception_weights_tf_dim_ordering_tf_kernels_notop.h5'
	}
	
	noisy_weights = {
	"EfficientNetB0" : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b0_noisy-student_notop.h5',
	"EfficientNetB1" : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b1_noisy-student_notop.h5',
	"EfficientNetB2" : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b2_noisy-student_notop.h5',
	"EfficientNetB3" : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b3_noisy-student_notop.h5',
	"EfficientNetB4" : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b4_noisy-student_notop.h5',
	"EfficientNetB5" : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b5_noisy-student_notop.h5',
	"EfficientNetB6" : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b6_noisy-student_notop.h5',
	"EfficientNetB7" : '/kaggle/input/tf-keras-pretrained-weights/No Top/efficientnet-b7_noisy-student_notop.h5'
	}
	import os
	
	params = {"input_shape" : input_shape, "weights" : weights, "include_top" : False}
	
	weights_dir_present = False
	if os.path.isdir('/kaggle/input/tf-keras-pretrained-weights/No Top'):
		params = {"input_shape" : input_shape, "include_top" : False}
		weights_dir_present = True
	elif os.path.isdir('/content/No Top'):
		params = {'input_shape' : input_shape, 'include_top' : False}
		weights_dir_present = True
		
	
	if classification_model != 'default':
		print("""
		Make Sure that the classification model consists of layers of tf.keras.layers only else it won't work.
			
		""")
	
	import os
	if model_name.startswith("EfficientNet"):
		import os
		os.system("pip install git+https://github.com/qubvel/segmentation_models")
		#import keras
		import tensorflow as tf
	else:
		import tensorflow as tf
		from tensorflow.keras.applications import VGG16, VGG19,  Xception,DenseNet121, DenseNet169, DenseNet201, ResNet50, ResNet101, ResNet152, ResNet50V2, ResNet101V2, ResNet152V2, MobileNet, MobileNetV2, InceptionV3, InceptionResNetV2
		#import keras
	
	
	#tf.keras.backend.clear_session() # error pops
	if model_name == "VGG16":
		if weights_dir_present:
			try:
				pretrained_model = VGG16(weights = weights_dict['VGG16'], **params)
			except:
				pretrained_model = VGG16(weights = os.path.join('/content', '/'.join(weights_dict['VGG16'].split('/')[4:])), **params)
		else:
			pretrained_model = VGG16(**params)
	elif model_name == "VGG19":
		if weights_dir_present:
			
			try:
				pretrained_model = VGG19(weights = weights_dict['VGG19'], **params)
			except:
				pretrained_model = VGG19(weights = os.path.join('/content', '/'.join(weights_dict['VGG19'].split('/')[4:])), **params)
		else:
			pretrained_model = VGG19(**params)
	elif model_name == 'Xception':
		if weights_dir_present:
			try:
				pretrained_model = Xception(weights = weights_dict['Xception'], **params)
			except:
				pretrained_model = Xception(weights = os.path.join('/content', '/'.join(weights_dict['Xception'].split('/')[4:])), **params)
		else:
			pretrained_model = Xception(**params)
	elif model_name == "DenseNet121":
		if weights_dir_present:
			try:
				pretrained_model = DenseNet121(weights = weights_dict['DenseNet121'], **params)
			except:
				pretrained_model = DenseNet121(weights = os.path.join('/content', '/'.join(weights_dict['DenseNet121'].split('/')[4:])), **params)
		else:
			pretrained_model = DenseNet121(**params)
	elif model_name == "DenseNet169":
		if weights_dir_present:
			try:
				pretrained_model = DenseNet169(weights = weights_dict['DenseNet169'], **params)
			except:
				pretrained_model = DenseNet169(weights = os.path.join('/content', '/'.join(weights_dict['DenseNet169'].split('/')[4:])), **params)
		else:
			pretrained_model = DenseNet169(**params)
	elif model_name == "DenseNet201":
		if weights_dir_present:
			try:
				pretrained_model = DenseNet201(weights = weights_dict['DenseNet201'], **params)
			except:
				pretrained_model = DenseNet201(weights = os.path.join('/content', '/'.join(weights_dict['DenseNet201'].split('/')[4:])), **params)
		else:
			pretrained_model = DenseNet201(**params)
	elif model_name == 'EfficientNetB7':
		#import os 
		#os.system("pip install tensorflow==2.1")
		#os.system("pip install keras==2.3.1")
		#os.system("pip install git+https://github.com/qubvel/segmentation_models")
		import efficientnet.tfkeras as efn   
		if weights_dir_present:
				
			try:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB7(weights = noisy_weights['EfficientNetB7'], **params)
				else:
					pretrained_model = efn.EfficientNetB7(weights = weights_dict['EfficientNetB7'], **params)
			except:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB7(weights = os.path.join('/content', '/'.join(noisy_weights['EfficientNetB7'].split('/')[4:])), **params)
				else:
					pretrained_model = efn.EfficientNetB7(weights = os.path.join('/content', '/'.join(weights_dict['EfficientNetB7'].split('/')[4:])), **params)
		else:
			pretrained_model = efn.EfficientNetB7(**params)
		
	elif model_name == 'EfficientNetB6':
		
		#os.system("!pip install -q efficientnet")
		#import efficientnet.tfkeras as efficientnet
		#pretrained_model = efficientnet.EfficientNetB6(**params)
		
		import efficientnet.tfkeras as efn  
		if weights_dir_present:
		
			
			try:
			
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB6(weights = noisy_weights['EfficientNetB6'], **params)
				else:
					pretrained_model = efn.EfficientNetB6(weights = weights_dict['EfficientNetB6'], **params)
					
			except:
				
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB6(weights = os.path.join('/content', '/'.join(noisy_weights['EfficientNetB6'].split('/')[4:])), **params)
				else:
					pretrained_model = efn.EfficientNetB6(weights = os.path.join('/content', '/'.join(weights_dict['EfficientNetB6'].split('/')[4:])), **params)
		else:
			pretrained_model = efn.EfficientNetB6(**params)
		
	elif model_name == 'EfficientNetB5':
		#os.system("!pip install -q efficientnet")
		#import efficientnet.tfkeras as efficientnet
		#pretrained_model = efficientnet.EfficientNetB5(**params)
		
		import efficientnet.tfkeras as efn   
		
		if weights_dir_present:
			try:
				
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB5(weights = noisy_weights['EfficientNetB5'], **params)
				else:
					pretrained_model = efn.EfficientNetB5(weights = weights_dict['EfficientNetB5'], **params)
			except:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB5(weights = os.path.join('/content', '/'.join(noisy_weights['EfficientNetB5'].split('/')[4:])), **params)
				else:
					pretrained_model = efn.EfficientNetB5(weights = os.path.join('/content', '/'.join(weights_dict['EfficientNetB5'].split('/')[4:])), **params)
		else:
			pretrained_model = efn.EfficientNetB5(**params)
		
	elif model_name == 'EfficientNetB4':
		#os.system("!pip install -q efficientnet")
		#import efficientnet.tfkeras as efficientnet
		#pretrained_model = efficientnet.EfficientNetB4(**params)
		
		import efficientnet.tfkeras as efn
		
		if weights_dir_present:
			try:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB4(weights = noisy_weights['EfficientNetB4'], **params)
				else:
					pretrained_model = efn.EfficientNetB4(weights = weights_dict['EfficientNetB4'], **params)
			except:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB4(weights = os.path.join('/content', '/'.join(noisy_weights['EfficientNetB4'].split('/')[4:])), **params)
				else:
					pretrained_model = efn.EfficientNetB4(weights = os.path.join('/content', '/'.join(weights_dict['EfficientNetB4'].split('/')[4:])), **params)
		else:
			pretrained_model = efn.EfficientNetB4(**params)
		
	elif model_name == 'EfficientNetB3':
		#os.system("!pip install -q efficientnet")
		#import efficientnet.tfkeras as efficientnet
		#pretrained_model = efficientnet.EfficientNetB3(**params)
		
		import efficientnet.tfkeras as efn  
		
		if weights_dir_present:
			try:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB3(weights = noisy_weights['EfficientNetB3'], **params)
				else:
					pretrained_model = efn.EfficientNetB3(weights = weights_dict['EfficientNetB3'], **params)
			except:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB3(weights = os.path.join('/content', '/'.join(noisy_weights['EfficientNetB3'].split('/')[4:])), **params)
				else:
					pretrained_model = efn.EfficientNetB3(weights = os.path.join('/content', '/'.join(weights_dict['EfficientNetB3'].split('/')[4:])), **params)
		else:
			pretrained_model = efn.EfficientNetB3(**params)
		
	elif model_name == 'EfficientNetB2':
		#os.system("!pip install -q efficientnet")
		#import efficientnet.tfkeras as efficientnet
		#pretrained_model = efficientnet.EfficientNetB2(**params)
		
		import efficientnet.tfkeras as efn 
		
		if weights_dir_present:
			try:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB2(weights = noisy_weights['EfficientNetB2'], **params)
				else:
					pretrained_model = efn.EfficientNetB2(weights = weights_dict['EfficientNetB2'], **params)
			except:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB2(weights = os.path.join('/content', '/'.join(noisy_weights['EfficientNetB2'].split('/')[4:])), **params)
				else:
					pretrained_model = efn.EfficientNetB2(weights = os.path.join('/content', '/'.join(weights_dict['EfficientNetB2'].split('/')[4:])), **params)
		else:
			pretrained_model = efn.EfficientNetB2(**params)
		
	elif model_name == 'EfficientNetB1':
		#os.system("!pip install -q efficientnet")
		#import efficientnet.tfkeras as efficientnet
		#pretrained_model = efficientnet.EfficientNetB1(**params)
		
		import efficientnet.tfkeras as efn  
		
		if weights_dir_present:
			try:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB1(weights = noisy_weights['EfficientNetB1'], **params)
				else:
					pretrained_model = efn.EfficientNetB1(weights = weights_dict['EfficientNetB1'], **params)
			except:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB1(weights = os.path.join('/content', '/'.join(noisy_weights['EfficientNetB1'].split('/')[4:])), **params)
				else:
					pretrained_model = efn.EfficientNetB1(weights = os.path.join('/content', '/'.join(weights_dict['EfficientNetB1'].split('/')[4:])), **params)
		else:
			pretrained_model = efn.EfficientNetB1(**params)
		
	elif model_name == 'EfficientNetB0':
		#os.system("!pip install -q efficientnet")
		#import efficientnet.tfkeras as efficientnet
		#pretrained_model = efficientnet.EfficientNetB0(**params)
		
		import efficientnet.tfkeras as efn 
		
		if weights_dir_present:
			try:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB0(weights = noisy_weights['EfficientNetB0'], **params)
				else:
					pretrained_model = efn.EfficientNetB0(weights = weights_dict['EfficientNetB0'], **params)
			except:
				if weights == 'noisy-student':
					pretrained_model = efn.EfficientNetB0(weights = os.path.join('/content', '/'.join(noisy_weights['EfficientNetB0'].split('/')[4:])), **params)
				else:
					pretrained_model = efn.EfficientNetB0(weights = os.path.join('/content', '/'.join(weights_dict['EfficientNetB0'].split('/')[4:])), **params)
		else:
			pretrained_model = efn.EfficientNetB0(**params)
		
	elif model_name == "InceptionV3":
		
		if weights_dir_present:
			try:
				pretrained_model = InceptionV3(weights = weights_dict['InceptionV3'], **params)
			except:
				pretrained_model = InceptionV3(weights = os.path.join('/content', '/'.join(weights_dict['InceptionV3'].split('/')[4:])), **params)
		else:
			pretrained_model = InceptionV3(**params)
	elif model_name == "ResNet50":
		if weights_dir_present:
			try:
				pretrained_model = ResNet50(weights = weights_dict['ResNet50'], **params)
			except:
				pretrained_model = ResNet50(weights = os.path.join('/content', '/'.join(weights_dict['ResNet50'].split('/')[4:])), **params)
		else:
			pretrained_model = ResNet50(**params)
	elif model_name == "ResNet101":
		if weights_dir_present:
			try:
				pretrained_model = ResNet101(weights = weights_dict['ResNet101'], **params)
			except:
				pretrained_model = ResNet101(weights = os.path.join('/content', '/'.join(weights_dict['ResNet101'].split('/')[4:])), **params)
		else:
			pretrained_model = ResNet101(**params)
	elif model_name == "ResNet152":
		
		if weights_dir_present:
			try:
				pretrained_model = ResNet152(weights = weights_dict['ResNet152'], **params)
			except:
				pretrained_model = ResNet152(weights = os.path.join('/content', '/'.join(weights_dict['ResNet152'].split('/')[4:])), **params)
		else:
			pretrained_model = ResNet152(**params)
	elif model_name == "ResNet50V2":
		
		if weights_dir_present:
			try:
				pretrained_model = ResNet50V2(weights = weights_dict['ResNet50V2'], **params)
			except:
				pretrained_model = ResNet50V2(weights = os.path.join('/content', '/'.join(weights_dict['ResNet50V2'].split('/')[4:])), **params)
		else:
			pretrained_model = ResNet50V2(**params)
	elif model_name == "ResNet101V2":
		
		if weights_dir_present:
			try:
				pretrained_model = ResNet101V2(weights = weights_dict['ResNet101V2'], **params)
			except:
				pretrained_model = ResNet101V2(weights = os.path.join('/content', '/'.join(weights_dict['ResNet101V2'].split('/')[4:])), **params)
		else:
			pretrained_model = ResNet101V2(**params)
			
	elif model_name == "ResNet152V2":
		
		if weights_dir_present:
			try:
				pretrained_model = ResNet152V2(weights = weights_dict['ResNet152V2'], **params)
			except:
				pretrained_model = ResNet152V2(weights = os.path.join('/content', '/'.join(weights_dict['ResNet152V2'].split('/')[4:])), **params)
		else:
			pretrained_model = ResNet152V2(**params)
	elif model_name == 'MobileNet':
		
		if weights_dir_present:
			try:
				pretrained_model = MobileNet(weights = weights_dict['MobileNet'], **params)
			except:
				pretrained_model = MobileNet(weights = os.path.join('/content', '/'.join(weights_dict['MobileNet'].split('/')[4:])), **params)
		else:
			pretrained_model = MobileNet(**params)    
	elif model_name == 'MobileNetV2':
		
		if weights_dir_present:
			try:
				pretrained_model = MobileNetV2(weights = weights_dict['MobileNetV2'], **params)
			except:
				pretrained_model = MobileNetV2(weights = os.path.join('/content', '/'.join(weights_dict['MobileNetV2'].split('/')[4:])), **params)
		else:
			pretrained_model = MobileNetV2(**params)
			
	elif model_name == "InceptionResNetV2":
		
		if weights_dir_present:
			try:
				pretrained_model = InceptionResNetV2(weights = weights_dict['InceptionResNetV2'], **params)
			except:
				pretrained_model = InceptionResNetV2(weights = os.path.join('/content', '/'.join(weights_dict['InceptionResNetV2'].split('/')[4:])), **params)
		else:
			pretrained_model = InceptionResNetV2(**params)

	else:
		print("model not among known models... exiting...")
		return
	
	if freeze:
		pretrained_model.trainable = False
	else:
		#pretrained_model.trainable = True
		for layer in pretrained_model.layers:
			if not isinstance(layer, tf.keras.layers.BatchNormalization):
				layer.trainable = True
			else:
				layer.trainable = False
	
	if model_name.startswith("EfficientNet"):
		
		if classification_model == 'default':
			#tf.keras.backend.clear_session()
			model = tf.keras.Sequential([
			pretrained_model,
			tf.keras.layers.GlobalAveragePooling2D(),
			tf.keras.layers.Dense(classes, activation = activation)
			])
		else:
			#tf.keras.backend.clear_session()
			new_model = tf.keras.Sequential()
			new_model.add(pretrained_model)
			for layer in classification_model.layers:
				new_model.add(layer)
			new_model.compile(optimizer = optimizer, loss = loss, metrics = [metrics])
			return new_model
	else:
		
		if classification_model == 'default':
			#tf.keras.backend.clear_session()
			model = tf.keras.Sequential([
			pretrained_model,
			tf.keras.layers.GlobalAveragePooling2D(),
			tf.keras.layers.Dense(classes, activation =activation)
			])
		else:
			#tf.keras.backend.clear_session()
			new_model = tf.keras.Sequential()
			new_model.add(pretrained_model)
			for layer in classification_model.layers:
				new_model.add(layer)
			new_model.compile(optimizer = optimizer, loss = loss, metrics = [metrics])
			return new_model
				
	
	model.compile(optimizer = optimizer, loss = loss, metrics = [metrics])
	
	return model    

if __name__ != "__main__":
	#print("Please refer to help(create_model) to know about how to use.\n")
	#import os
	#print("Installing the reqd libraries...\n")
	#os.system("pip install tensorflow==2.2.0")
	#os.system("pip install keras==2.4.3")
	import tensorflow as tf
