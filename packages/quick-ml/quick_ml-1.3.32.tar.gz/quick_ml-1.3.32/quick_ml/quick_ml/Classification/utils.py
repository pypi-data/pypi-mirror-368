def grad_cam(input_model, image, cls, layer_name, H=320, W = 320):
	"""GradCAM method for visualizing input saliency."""

	y_c = input_model.output[0, cls]
	conv_output = input_model.get_layer(layer_name).output
	grads = K.gradients(y_c, conv_output)



	gradient_function = K.function([input_model.input], )





def compute_gradcam(model, img, image_dir, df, labels, selected_labels, layer_name = 'bn'):
	preprocessed_input = load_image(img, image_dir, df)

	predictions = model.predict(preprocessed_input)

	print("Loading original image...")
	plt.figure(figsize = (15,10))
	plt.subplot(151)
	plt.title("Original....")
	plt.axis("off")
	plt.imshow(load_image(img, image_dir, df, preprocess = False), cmap = 'grey')

	j = 1

	for i in range(len(labels)):

		if labels[i] in selected_labels:

			print(f"Generating gradcam for class {labels[i]}")
			gradcam = grad_cam(model, preprocessed_input, i, layer_name)
			plt.subplot(151 + j)
			plt.title(f"{labels[i]}: p={predictions[0][i]:.3f}")
            plt.axis('off')
            plt.imshow(load_image(img, image_dir, df, preprocess=False),
                       cmap='gray')
            plt.imshow(gradcam, cmap='jet', alpha=min(0.5, predictions[0][i]))
            j += 1



def get_roc_curve(labels, predicted_vals, generator):
	auc_roc_vals = []

	for i in range(len(labels)):
		try:
			pass	
		except Exception as e:
			print(f"Error in generating ROC Curve values for {labels[i]}")

	plt.show()
	return auc_roc_vals




def get_weighted_loss(pos_weights, neg_weights, epsilon = 1e-7):

	def weighted_loss(y_true, y_pred):

		loss = 0.0


		for i in range(len(pos_weights)):

			loss += -1 * K.mean((pos_weights[i] * y_true[:, i] * K.log(y_pred[:,i] + epsilon)))





if __name__ != "__main__":
	import random
	import cv2
	import matplotlib.pyplot as plt 
	from keras import backend as K 
	from keras.preprocessing import image 
	from sklearn.metrics import roc_auc_score, roc_curve 
	from tensorflow.compat.v1.logging import INFO, set_verbosity


### https://www.kaggle.com/rftexas/implementing-gradcam-with-keras-for-error-analysis