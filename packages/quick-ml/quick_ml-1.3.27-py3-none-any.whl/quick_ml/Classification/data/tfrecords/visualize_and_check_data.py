def plot_a_grid(columns, rows, img_batch, titles, figsize = (8,8)):
	import matplotlib.pyplot as plt
	try:
		fig=plt.figure(figsize=figsize)
		columns = columns
		rows = rows
		for i in range(1, columns*rows +1):
			img = img_batch[i-1]
			fig.add_subplot(rows, columns, i).title.set_text(titles[i-1])
			plt.imshow(img)
		plt.show()
	except IndexError as err:
		print("ERROR!")
		print(err.args)
		print("The value for rows & columns set wrong. Please ensure columns * rows must be equal to number of images.")

def check_one_image_and_label(tfrecord_filename):
	from quick_ml.Classification.begin_tpu import load_dataset
	labeleddata = load_dataset(tfrecord_filename, labeled = True)
	img = None
	label = None
	for data in labeleddata.take(1):
		img = data[0]
		label = data[1]

	import matplotlib.pyplot as plt 
	plt.imshow(img.numpy()); plt.show()

	print("Label of the Image -> ", label.numpy())

def check_one_image_and_label_dataset(labeleddata):
	img = None
	label = None
	for data in labeleddata.take(1):
		img = data[0]
		label = data[1]

	import matplotlib.pyplot as plt 
	plt.imshow(img.numpy()); plt.show()

	print("Label of the Image -> ", label.numpy())
	

def check_batch_and_labels(tfrecord_filename, n_examples, grid_rows, grid_columns, grid_size = (8,8)):
	from quick_ml.begin_tpu import load_dataset
	labeleddata = load_dataset(tfrecord_filename, labeled = True)
	
	img_batch = []
	labels = []
	for data in labeleddata.take(n_examples):
		img_batch.append(data[0].numpy())
		labels.append(data[1].numpy())
	plot_a_grid(grid_columns, grid_rows, img_batch, labels,  grid_size)


def check_batch_and_labels_dataset(labeleddata, n_examples, grid_rows, grid_columns, grid_size = (8,8)):
	img_batch = []
	labels = []
	for data in labeleddata.take(n_examples):
		img_batch.append(data[0].numpy())
		labels.append(data[1].numpy())
	plot_a_grid(grid_columns, grid_rows, img_batch, labels,  grid_size)

def check_one_image_and_id(tfrecord_filename):
	from quick_ml.begin_tpu import load_dataset
	import matplotlib.pyplot as plt

	unlabeleddata = load_dataset(tfrecord_filename, labeled = False)
	img = None
	id_ = None
	for data in unlabeleddata.take(1):
		img = data[0]
		id_ = data[1]

	plt.imshow(img.numpy()); plt.show()
	print("Id of this image is -> ", id_.numpy().decode())


def check_one_image_and_id_dataset(unlabeleddata):
	unlabeleddata = load_dataset(tfrecord_filename, labeled = False)
	img = None
	id_ = None
	for data in unlabeleddata.take(1):
		img = data[0]
		id_ = data[1]

	plt.imshow(img.numpy()); plt.show()
	print("Id of this image is -> ", id_.numpy().decode())


def check_batch_and_ids(tfrecord_filename, n_examples, grid_rows, grid_columns, grid_size = (8,8)):
	
	from quick_ml.begin_tpu import load_dataset
	unlabeleddata = load_dataset(tfrecord_filename, labeled = False)

	img_batch = []
	ids = []
	for data in unlabeleddata.take(n_examples):
		img_batch.append(data[0].numpy())
		ids.append(data[1].numpy().decode())
	plot_a_grid(grid_columns, grid_rows, img_batch, ids, grid_size)
	
	
def check_batch_and_ids_dataset(unlabeleddata, n_examples, grid_rows, grid_columns, grid_size = (8,8)):
	img_batch = []
	ids = []
	for data in unlabeleddata.take(n_examples):
		img_batch.append(data[0].numpy())
		ids.append(data[1].numpy().decode())
	plot_a_grid(grid_columns, grid_rows, img_batch, ids, grid_size)