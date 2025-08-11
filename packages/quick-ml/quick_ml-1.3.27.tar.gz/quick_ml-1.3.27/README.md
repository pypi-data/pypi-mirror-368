# quick_ml&nbsp;&nbsp;&nbsp;&nbsp; :&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ML for everyone
[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger) [![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://gitlab.com/antoreep_jana/quick_ml/-/blob/master/LICENSE)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![quick_ml_logo](https://gitlab.com/antoreep_jana/quick_ml/-/raw/master/quick_ml_logo.png?inline=false)

<br><br>

## Official Website

<br>

**www.quickml.info**

<br><br>
**quick_ml** is a python package (pypi) which provides quick plug and plag prototypes to train Deep Learning Model(s) through optimized utilization of TPU computation power.

  - Speed up your Deep Learning Experimentation Workflow by x20 times.
  - No unncessary worrying about the details. Those have been taken care of by the library.
  - Obtain results of Deep Learning Models on your dataset using minimal lines of code.
  - Train Multiple Deep Learning Models in a go just by naming the model names. You need not to worry much about the internal working.
  - Full control over the Deep Learning workflow  & setting of parameters. All within a single or minimal function call(s).

# New Features!

  - Rapidly train about 24 Deep Learning Pretrained Models in one session using TPUs.
  - Quick & Easy TFRecords Dataset Maker. TFRecords expidite the training process. -  


### Why quick_ml?
  - Usual time taken to code & train a deep learning workflow for a single model is atleast 1.5 hrs to 2 hrs (given you are proficient in the field and you know what to code). Using quick_ml, you would be able to do this in less than 20 mins even if you are a beginner.
  - Fast experimentation. That's it. Experimenting what works and what doesn't is tedious and tiresome. 
 

## Specifications
 Support for __Kaggle Notebooks__ w/ __TPU enabled ON__.
 For best performance, import the pretrained weights dataset in the Kaggle Notebook. (https://www.kaggle.com/superficiallybot/tf-keras-pretrained-weights) <br>
 **Tensorflow version==2.4.0** <br>
 **Python 3.6+** <br>
 
 __Note__ -> Don't import tensorflow in the beginning. With the upcoming updates in the tensorflow, it might take some time to reflect the corresponding changes to the package. The package is built and tested on the most stable version of tensorflow mentioned in the Specifications.
 

### Few Words about the package

> The idea behind designing the package was to 
> reduce the unncessary training time for Deep Learning Models.
> The experimentation time if reduced can help the people concerned with
> the package to focus on the finer details which are often neglected. 
> In addition to this, there are several utility functions provided at a single
> place aimed at expediting the ML workflow. These utility functions have been designed
> with ease of use as the foremost priority and attempt has been made to 
> optimize the TPU computation as well as bring in most of the functionalities. Attempt has been made to reduce about 500-700 lines of code or even more (depending on what you are about to use) to less than 10 lines of code. Hope you like it!

***
## Table of Contents
***
***

* [Installation](#installation)
* [Getting Started](#getting-started)
    * [Making Custom Datasets (TFRecords)](#making-custom-datasets-tfrecords)
        * Labeled Data
        * Unlabeled Data
    * [Visualize & Check the Data](#visualize-check-the-data)
    * [Begin Working w/ TPU](#begin-working-w-tpu)
    * [Create Models Quickly](#create-model-quickly)
    * [Models Training Report](#models-training-report)
    * [Callbacks](#callbacks)
    * [Predictions](#predictions)
    * [K-Fold Training & Predictions](#k-fold-training-predictions)
* [Examples](#examples)
* [Feedback & Development](#feedback-development)
* [Upcoming Features!](#upcoming-features)
* [License](#license)


***
### Installation
***
***

You can quickly get started with the package using pip command.

```
!pip install quick-ml
```

Once you have installed quick_ml package, you can get started with your Deep Learning Workflow. <br> Quickly check whether the correct version of tenserflow has been installed and import tensorflow by the following statement.

<br>


```
import tensorflow as tf
import quick_ml
```

Check the output to know about the status of your installation.  Also add, <br>

<br>

***
# Getting Started
___
***
Let's begin exploring the package. 

## Making Custom Datasets (TFRecords)
---

To obtain the best performance using TPUs, the package accepts only TFRecords Dataset(s). 
Either you have ready-made TFRecords Dataset or you want to obtain TFRecords Dataset for your own image data. This section is devoted to explaining about how to obtain your own Image Dataset TFRecords. <br>
_Note_ -> To utilize the TFRecords dataset created, ensure that the dataset is public while uploading on Kaggle. <br>
_Note_ -> No need to have **TPU ON** for making TFRecords files. Making TFRecords is CPU computation. <br>
_Note_ -> It is better to make TFRecords dataset on Google Colab ( > 75 GB) as Kaggle Kernels have limited Disk Space( < 5 GB). Download the datasets after you are done. Upload them on Kaggle as public datasets. Input the data in the Kaggle Notebooks.

Let's get started with **tfrecords_maker** module of **quick_ml** package. <br>

<br>

**Labeled Data**

For Labeled Data, make sure that the dataset follows the following structure -> 

>/ Data
>>> -Class1 <br>
>>> -Class2 <br>
>>> -Class3 <br>
>>> -ClassN <br>

where Class1, Class2, .. , ClassN denote the folders of images as well the class of the images. These shall serve as the labels for classification.
<br> 
This is usually used for training and validation data. <br>
However, it can also be used to create labeled Test Data.
<br> <br>

To make labeled data, there are 2 options. <br>
* Convert entire image folder to tfrecords file.
 * Split the Image Dataset folder in a specified ratio & make tfrecords files.

<br>
A) Convert entire image folder to tfrecords file <br>

```
from quick_ml.tfrecords_maker import create_tfrecord_labeled
from quick_ml.tfrecords_maker import get_addrs_label
```

To create a tfrecords dataset file from this, the following would be the function call :- <br>

```
create_tfrecord_labeled(addrs, labels, output_filename, IMAGE_SIZE = (192,192))
```

<br>

However, you would need the address (**addrs**) and (**labels**) and shuffle them up. This has been implemented for you in the **get_addrs_label**. Follow the line of code below.<br>

```
addrs, labels = get_addrs_labels(DATA_DIR)
```

<br>
where DATA_DIR directs to the path of the Dataset with the structure mentioned in the beginning of Labeled Data TFRecords. <br>

Obtain the tfrecords file by giving a output_filename you would desire your output file to have using this line of code. <br>

```
create_tfrecord_labeled(addrs, labels, output_filename, IMAGE_SIZE = (192,192))
```

<br>
Ensure that you save the Labeled TFRecord Format somewhere as you would require it to read the data at a later stage. Preferred way of achieving this is through saving it in the Markdown cell below the above code cell. After uploading on Kaggle and making dataset public, adding the Labeled TFRecords Format in the Dataset Description. <br>

B) Split the Image Dataset Folder in a specified ratio & make tfrecords files. <br>

```
from quick_ml.tfrecords_maker import create_split_tfrecords_data
```

To create two tfrecords datasets from the Image Dataset Folder, use the following line of code :- <br>

```
create_split_tfrecords_data(DATA_DIR, outfile1name, outfile2name, split_size_ratio, IMAGE_SIZE = (192,192))
```

<br>

**_DESCRIPTION_** => 

<br>

&nbsp;&nbsp;&nbsp;&nbsp; **DATA_DIR** -> This refers to the Path to the Dataset Folder following the structure mentioned above. 
<br> &nbsp;&nbsp;&nbsp;&nbsp; **outfile1name** + **outfile2name** -> Give names to the corresponding output files obtained through the split of the dataset as _outfile1name_ & _outfile2name_. <br>
&nbsp;&nbsp;&nbsp;&nbsp; **split_size_ratio** -> Mention the split size ratio you would to divide your dataset into. <br>
&nbsp;&nbsp;&nbsp;&nbsp; **IMAGE_SIZE** -> The Image Size you would like to set all the images of your dataset in the tfrecords file.

<br>
<br>

<br>

**_RETURNS_** => <br>
Doesn't return anything. Stores the TFRecords file(s) to your disk. Ensure sufficient disk space.

**Unlabeled Data**

For unlabeled data, make sure to follow the following structure. <br>

> / Data
>>> file1 <br>
>>> file2 <br>
>>> file3 <br>
>>> file4 <br>
>>> fileN <br>

where file1, file2, file3, fileN denote the unlabeled, uncategorized image files. The filenames serve as the Id which is paired with the Images as an identification. <br>
This is usually used for test data creation(unknown, unclassified).
<br>  <br>
To make unlabeled TFRecords dataset, you would need **create_tfrecord_unlabeled** & **get_addrs_ids**.

```
from quick_ml.tfrecords_maker import create_tfrecord_unlabeled
from quick_ml.tfrecords_maker import get_addrs_ids
```

<br>

First, obtain the image addresses (**addrs**) and image ids (**ids**) using **get_addrs_ids** in the **tfrecords_maker** module. <br> 

```
addrs, ids = get_addrs_ids(Unlabeled_Data_Dir)
```

<br>
where, <br>
Unlabeled_Data_dir refers to the Dataset Folder which follows the structure of unlabeled dataset. <br>

After getting the addrs & ids, pass the right parameters for the function to make the TFRecords Dataset for you. <br>

```
unlabeled_dataset = create_tfrecord_unlabeled(out_filename, addrs, ids, IMAGE_SIZE = (192,192))
```

**_DESCRIPTION_** => <br>
&nbsp;&nbsp;&nbsp;&nbsp;**out_filename** - name of the tfrecords outputfile name. <br>
&nbsp;&nbsp;&nbsp;&nbsp;**addrs** - the addrs of the images in the data folder. (can be obtained using get_addrs_ids()) <br>
&nbsp;&nbsp;&nbsp;&nbsp;**ids** - the ids of the imahes in the data folder. (can be obtained using get_addrs_ids()) <br>
&nbsp;&nbsp;&nbsp;&nbsp;**IMAGE_SIZE** - The Image Size of each image you want to have in the TFRecords dataset. Default, (192,192). <br>


**_RETURNS_** => <br>
A TFRecords dataset with examples with 'image' as the first field & 'idnum' as the second field.  

<br>

## Visualize & Check the Data
---

After creating your TFRecords Dataset (labeled or unlabeled), you would like to check and glance through your dataset. For this import, **visualize_and_check_data** from **quick_ml**.
<br>
To get started, write the following line of code. :- <br>

```
from quick_ml.visualize_and_check_data import check_one_image_and_label, check_batch_and_labels, check_one_image_and_id, check_batch_and_ids
```

Available methods are :- 
<ol>
<li type = 'I'> check_one_image_and_label
<li type = 'I'> check_batch_and_labels
<li type = 'I'> check_one_image_and_id
<li type = 'I'> check_batch_and_ids
</ol>

<br>

**check_one_image_and_label** <br>

Use this for checking labeled TFRecords Dataset. It displays only one image along with its label when the labeled TFRecords dataset is passed as an argument. <br>

```
check_one_image_and_label(tfrecord_filename)
```

**_Description_** => <br>
Displays one image along with its label. <br>
Pass the tfrecord_filename as the argument. It will display one image along with its label from the tfrecords dataset. <br>

**check_batch_and_labels** <br>
Use this  for checking labeled TFRecords Dataset. It displays a grid of images along with their labels given the tfrecords dataset passed as an argument. <br>

```
check_batch_and_labels(tfrecord_filename, n_examples, grid_rows, grid_columns, grid_size = (8,8)
```

**_Description_** => <br>
Displays a grid of images along with their labels. <br>
Pass the tfrecord_filename, the number of examples to see (n_examples), divide the n_examples into product of rows (grid_rows) and columns (grid_columns) such that n_examples = grid_rows * grid_columns. Finally the grid_size as a tuple, Default (8,8) as an argument. It will display a grid of images along with their labels from the tfrecords dataset. <br>

**check_one_image_and_id** <br>

Use this for checking unlabeled TFRecords Dataset. It displays only one image along with its id when the unlabeled TFRecords dataset is passed as an argument. <br>

```
check_one_image_and_id(tfrecord_filename)
```

**_Description_** => <br>
Displays one image along with its id. <br>
Pass the tfrecord_filename as the argument. It will display one image along with its id from the tfrecords dataset. <br>

**check_batch_and_ids** <br>
Use this  for checking unlabeled TFRecords Dataset. It displays a grid of images along with their ids given the tfrecords dataset passed as an argument. <br>

```
check_batch_and_ids(tfrecord_filename, n_examples, grid_rows, grid_columns, grid_size = (8,8)
```

**_Description_** => <br>
Displays a grid of images along with their ids. <br>
Pass the tfrecord_filename, the number of examples to see (n_examples), divide the n_examples into product of rows (grid_rows) and columns (grid_columns) such that n_examples = grid_rows * grid_columns. Finally the grid_size as a tuple, Default (8,8) as an argument. It will display a grid of images along with their ids from the tfrecords dataset. <br>

<br>

## Begin working w/ TPU
---

This helps you to get the TPU instance, TPU strategy, load the training dataset, validation dataset & test dataset from their TFRecords file & GCS_DS_PATH. <br>

To get all the required utilities, use the following line of code. <br>

```
from quick_ml.begin_tpu import define_tpu_strategy, get_training_dataset, get_validation_dataset, get_test_dataset
```

**_Available Methods & Functionalities_** => <br>

<ol>
<li> define_tpu_strategy
<li> get_training_dataset
<li> get_validation_dataset
<li> get_test_dataset
</ol>

**define_tpu_strategy** <br>
This returns the tpu instance and the tpu strategy. <br>

```
strategy, tpu = define_tpu_strategy()
```

**get_training_dataset** <br>
Helps you load the tfrecords file (TRAINING DATASET). <br>

```
train_dataset = get_training_dataset(GCS_DS_PATH, train_tfrec_path, BATCH_SIZE)
```

**_Description_** => <br>
&nbsp;&nbsp;&nbsp;&nbsp; **GCS_DS_PATH** - The GCS Bucket Path of the tfrecords dataset. <br>
&nbsp;&nbsp;&nbsp;&nbsp; **train_tfrec_path** - the train tfrecords filename path. eg. '/train.tfrecords' <br>
&nbsp;&nbsp;&nbsp;&nbsp; **BATCH_SIZE** - Select the batch size for the images to load in the training dataset instance. <br>

<br>

**_Returns_** => <br>
A tfrecords dataset instance which can be fed to model training as the training dataset.

<br>

**get_validation_dataset** <br>
Helps you load the tfrecords file (VALIDATION DATASET).

```
val_dataset = get_validation_dataset(GCS_DS_PATH, val_tfrec_path, BATCH_SIZE)
```

**_Description_** => <br>
&nbsp;&nbsp;&nbsp;&nbsp; **GCS_DS_PATH** - The GCS Bucket Path of the tfrecords dataset. <br>
&nbsp;&nbsp;&nbsp;&nbsp; **val_tfrec_path** - the validation tfrecords filename path. eg. '/val.tfrecords' <br>
&nbsp;&nbsp;&nbsp;&nbsp; **BATCH_SIZE** - Select the batch size for the images to load in the validation dataset instance. <br>

<br>

**_Returns_** => <br>
A tfrecords dataset instance which can be fed to model training as the validation dataset.

<br>

**get_test_dataset** <br>
Helps you load the tfrecords file (TEST DATASET).

```
test_dataset = get_test_dataset(GCS_DS_PATH, test_tfrec_path, BATCH_SIZE)
```

**_Description_** => <br>
&nbsp;&nbsp;&nbsp;&nbsp; **GCS_DS_PATH** - The GCS Bucket Path of the tfrecords dataset. <br>
&nbsp;&nbsp;&nbsp;&nbsp; **test_tfrec_path** - the test tfrecords filename path. eg. '/test.tfrecords' <br>
&nbsp;&nbsp;&nbsp;&nbsp; **BATCH_SIZE** - Select the batch size for the images to load in the test dataset instance. <br>

<br>

**_Returns_** => <br>
A tfrecords dataset instance which can be used for prediction as test dataset.

<br>



## Create Model Quickly
---

This helps you to create a model ready for training all in a single line of code. <br>
This includes loading the pretrained model along with the weights, addition of the the classification model on top of pretrained model and the compilation of the model. All in a single line of code. <br>
The function is situated in the **load_models_quick** module of **quick_ml** package. <br>
```
from quick_ml.load_models_quick import create_model
```
<br>

**create_model()** function parameters/arguments :- <br>

```
model = create_model(classes, model_name = 'VGG16', classification_model = 'default', freeze = False, input_shape = [512, 512,3], activation  = 'softmax', weights= "imagenet", optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = 'sparse_categorical_accuracy')
```

**_Arguemnts Description_** => <br>
&nbsp;&nbsp;&nbsp;&nbsp;**classes** - Number of classes for classification. <br>
&nbsp;&nbsp;&nbsp;&nbsp;**model_name** - Name of the model. Default, VGG16. <br>
Available models -> <br>
MODELS -> 'VGG16', 'VGG19',  <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    'Xception', <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    'DenseNet121', 'DenseNet169', 'DenseNet201', <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    'ResNet50', 'ResNet101', 'ResNet152', 'ResNet50V2', 'ResNet101V2', 'ResNet152V2', <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    'MobileNet', 'MobileNetV2', <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    'InceptionV3', 'InceptionResNetV2', <br> 
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    'EfficientNetB0', 'EfficientNetB1', 'EfficientNetB2', 'EfficientNetB3', 'EfficientNetB4',  'EfficientNetB5', 'EfficientNetB6', 'EfficientNetB7'
<br>

&nbsp;&nbsp;&nbsp;&nbsp;**classification_model** - The classification model which you want to attach as the top to the pretrained model. The 'default' classification model has a Global Average Pooling2D followed by Dense layer with output nodes same as the number of classes for classification. <br>
You can define your own classification_model (Sequential Model) and pass the model as an argument to the classification model. <br>
```
class_model = tf.keras.Sequential([
tf.keras.layers(),
tf.keras.layers()
])

get_models_training_report(models, tpu, n_class, traindata, steps_per_epoch, epochs, val_data, classification_model = class_model)
```

<br>

&nbsp;&nbsp;&nbsp;&nbsp;**freeze** - True or False. Whether or not to freeze the pretrained model weights while training the model. Default, False.<br>
&nbsp;&nbsp;&nbsp;&nbsp;**input_shape** - Input shape of the images of the TFRecords Dataset. Default, [512,512,3] <br>
&nbsp;&nbsp;&nbsp;&nbsp;**activation** - The activation function to be used for the final layer of the classification model put on top of the pretrained model. For Binary Classification, use 'sigmoid'. For multi-class classification, use 'softmax'. Default, 'softmax'. <br> 
&nbsp;&nbsp;&nbsp;&nbsp;**weights** - What kind of weights to use for the pretrained model you have decided as your model backbone. Default, 'imagenet'. Options, 'imagenet' & None. In case you are using 'imagenet' weights, ensure you have loaded [TF Keras pretrained weights](https://www.kaggle.com/superficiallybot/tf-keras-pretrained-weights) in your Kaggle Notebook. <br>
&nbsp;&nbsp;&nbsp;&nbsp;**optimizer** - The optimizer to be used for converging the model while training. Default, 'adam'.<br>
&nbsp;&nbsp;&nbsp;&nbsp;**loss** - Loss function for the model while training. Default, 'sparse_categorical_crossentropy'. Options, 'binary_crossentropy' or 'sparse_categorical_crossentropy'. Use 'binary_crossentropy' for Binary Classifications. Use 'sparse_categorical_crossentropy' for multi-class classifications. Support for 'categorical_crossentropy' is not provided as it is computationally expensive. Both sparse & categorical cross entropy serve the same purpose.<br>
&nbsp;&nbsp;&nbsp;&nbsp;**metrics** - The metrics for gauging your model's training performance. Default, 'sparse_categorical_accuracy'. Options, 'sparse_categorical_accuracy' & 'accuracy'. For Binary Classifications, use 'accuracy'. For Multi-class classifications, use 'sparse_categorical_accuracy'. <br>

<br>

**_Returns_** => <br>
A tf.keras.Sequential **compiled** Model with base model as the pretrained model architecture name specified along with the classification model attached. This model is **_ready for training_** via model.fit(). <br>

## Models Training Report
---

This utility function is designed for getting to know which models are the best for the dataset at hand. Manually training models one by one is troublesome as well as cumbersome. A smart and quick way of achieving this is by using the **get_models_training_report()** from **quick_ml.training_predictions**. <br>
To get started, import the **training_predictions** module from **quick_ml** <br>
```
from quick_ml.training_predictions import get_models_training_report
```
<br>

After passing in the arguments for get_models_training_report, you will obtain a pandas dataframe. However, before getting into the details of the output and what are the parameters to be passed to the function, let's take a quick view of the table output format. <br>

### Output Table Overview 
Table Preview of the Pandas DataFrame that is return upon calling the function to obtain training_report. <br>

| Model Name | Train_top1_Accuracy | Train_top3_Accuracy | Val_top1_Accuracy | Val_top3_Accuracy |
| ------ | ------ | ------ | ------ | ------ |
| Model_1 | 97.1 | 96| 94| 93.1|
| Model_2 |  96.2 | 92 | 93| 91|
| Model_3 |  98| 96| 97.1| 96|
| Model_4 |  90| 87| 85| 83|
| Model_5 |  70| 61|  55| 51|
| Model_6 |  91| 86| 90| 88|

<br>
Table Description :- <br>
1) Model Name -> Name of the model trained on the dataset <br>
2) Top 1 Accuracy -> The last accuracy score on training dataset <br>
3) Top 3 Accuracy -> The average of the last 3 accuracy scores on training dataset<br>
4) Val Top 1 Accuracy -> The last validation accuracy score on validation dataset <br>
5) Val Top 3 Accuracy -> The average of the last 3 validation accuracy scores on validation dataset <br>
<br>

#### Using Models Training Report

Once you have successfully imported **get_models_training_report**, pass the arguments as per your requirement. The function returns a pandas dataframe with a table similar to above. The arguemnts are - <br>

```
get_models_training_report(models, tpu, n_class, traindata, steps_per_epoch, epochs, val_data, classification_model = 'default', freeze = False, input_shape = [512,512,3], activation = 'softmax', weights = 'imagenet', optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = 'sparse_categorical_accuracy', plot = False)
```

_**Arguments Description**_ -> <br>
&nbsp;&nbsp;&nbsp;&nbsp;**models** - list of models to obtain the training report on. eg.
``` models = ['VGG16', 'EfficientNetB7', 'InceptionV3', 'ResNet50'] ``` <br>
&nbsp;&nbsp;&nbsp;&nbsp;**tpu** - The TPU instance <br>
&nbsp;&nbsp;&nbsp;&nbsp;**n_class** - number of classes in the Dataset <br>
&nbsp;&nbsp;&nbsp;&nbsp;**traindata** - The training dataset (In TFRecords Dataset) <br>
&nbsp;&nbsp;&nbsp;&nbsp;**steps_per_epoch** - number of steps to be taken per epoch. Ideally, it should be number of training images // BATCH_SIZE <br>
&nbsp;&nbsp;&nbsp;&nbsp;**epochs** - Number of epochs for which models are to be trained. <br>
&nbsp;&nbsp;&nbsp;&nbsp;**val_data** - The validation dataset (In TFRecords Dataset) <br>
&nbsp;&nbsp;&nbsp;&nbsp;**classification_model** - The classification model which you want to attach as the top to the pretrained model. The 'default' classification model has a Global Average Pooling2D followed by Dense layer with output nodes same as the number of classes for classification. <br>
You can define your own classification_model (Sequential Model) and pass the model as an argument to the classification model. <br>
```
class_model = tf.keras.Sequential([
tf.keras.layers(),
tf.keras.layers()
])

get_models_training_report(models, tpu, n_class, traindata, steps_per_epoch, epochs, val_data, classification_model = class_model)
```

&nbsp;&nbsp;&nbsp;&nbsp;**freeze** - Whether or not you want to freeze the pretrained model weights. Default, False. <br>
input_shape - Defines the input_shape of the images of the dataset. Default, [512,512,3] <br>
&nbsp;&nbsp;&nbsp;&nbsp;**activation** - The activation function for the final Dense layer of your Classification model. Default, 'softmax'. For binary classification, change to 'sigmoid' with n_class = 1.<br>
&nbsp;&nbsp;&nbsp;&nbsp;**weights** - The pretrained Model weights to be taken for consideration. Default, 'imagenet'. Support for 'noisy-student' coming soon. <br>
optimizer - The optimizer for the model to converge while training. Default, 'adam' <br>
&nbsp;&nbsp;&nbsp;&nbsp;**loss** - loss function to consider while training your deep learning model. Two options supported. 'Sparse Categorical CrossEntropy' & 'Binary Cross Entropy'. Default, 'Sparse Categorical CrossEntropy'. <br>
&nbsp;&nbsp;&nbsp;&nbsp;**metrics** - The metric to be taken under consideration while training your deep learning model. Two options available. 'accuracy' & 'sparse_categorical_accuracy'. Use 'accuracy' as a metric while doing Binary Classification else 'sparse_categorical_accuracy'. Default, 'sparse_categorical_accuracy'. <br>
&nbsp;&nbsp;&nbsp;&nbsp;**plot** - Plot the training curves of all the models for quick visualization. Feature Coming soon. <br>
<br>
**_Returns_** => <br>
A Pandas Dataframe with a table output as shown above. You can save the function output in a variable and save the dataframe to your disk using .to_csv() method. <br>

## Callbacks
---

In case, the classes of your dataset contain high similarity index, in such cases, it is imperative to have callbacks necessary for your model training and convergence. For obtaining such a model, callbacks are often used. 
This utility aims at providing callbacks which are oftenly used while training deep learning models and returns a list of callbacks. Pass this as an argument while training deep learning models. <br>

```
from quick_ml.callbacks import callbacks
```

##### Learning Rate Scheduler 

There are 3 different types of learning rate schedulers. <br>
    <ol><li> RAMPUP Learning Rate Scheduler
    <li> Simple Learning Rate Scheduler
    <li> Step-wise Learning Rate Scheduler
    </ol>

##### Early Stopping Callback

Use Early Stopping Callback as a measure to prevent the model from overfitting. The default callback setting is as follows <br>
  monitor : 'val_loss', min_delta = 0, patience = 0, verbose = 0, <br>
  mode = 'auto', baseline = None, restore_best_weights = False.
  <br><br>
  
To use the default settings of Early Stopping Callback, pass
```
callbacks = callbacks(early_stopping = "default")
```


  

##### Readuce LR On Plateau

Prevent your model from getting stuck at local minima using ReduceLROnPlataeu callback. The default implementation has the following parameter settings =>  <br>
 'monitor' : 'val_loss', 'factor' : 0.1, 'patience' : 10, 'verbose' : 0, mode = 'auto', min_delta = 0.0001, cooldown = 0, min_lr = 0
 <br> <br>
 
 _**Combine Multiple  callbacks**_ <br>
 ```
 callbacks = callbacks(lr_scheduler = 'rampup', early_stopping = 'default', reduce_lr_on_plateau = 'default' )
 ```
 
 ## Predictions
 ---
 
 The package supports multlipe options to obtain predictions on your testDataset (only TFRecords Format Dataset). <br><br>
 
 Supported Methods for obtaining predictions -> <br>
 - get_predictions
 - ensemble_predictions
    - Model Averaging
    - Model Weighted
    - Train K-Fold (Coming Soon)
    - Test Time Augmentatios (Coming Soon)
    
 ##### Get Predictions

 Obtain predictions on the **TEST TFRECORDS Data Format** using get_predictions(). <br>
 Two call types have been defined for get_predictions(). <br>
 Import the predictions function. <br>
 ```
 from quick_ml.predictions import get_predictions
 ```
 
 First Definition -> <br>
 Use this function definition when you have the GCS_DS_PATH, test_tfrec_path, BATCH_SIZE. <br>
 This is usually helpful when you have a trained model weights from a different session and want to obtain predictions in a different session. Usually beneficial if there are multiple models from whom predictions are to be obtained. Training of multiple models using get_models_training_report() from quick_ml.training_predictions in one session. Saving the best model weights in the same session using create_model() from quick_ml.load_models_quickly. Testing/Predictions in a different session for multiple models using this function definition. This is the best way to deal with multiple models. <br>
 ```
 predictions = get_predictions(GCS_DS_PATH, test_tfrec_path, BATCH_SIZE, model)
 ```

Second Definition <br>
Use this function when you have testTFDataset and model. <br>
This function definition is usually the best option when you have one model and want to obtain the predictions in the same session. For this, you must have loaded the datasets before. However, you are free to explore better possibilites with the above two functions.
```
prediction = get_predictions(testTFdataset, model)
```

<br>

## K-Fold Training & Predictions
---

<br>

K-Fold Cross Validation is usually performed to verify that the selected model's good performance isn't due to data bias. <br>
This would be highly beneficial after obtaining Training Report of the models and you have selected your model architecture you would be working with. <br>

To get started with K-Fold Cross Validation & Predictions, <br>

```
from quick_ml.k_fold_training import train_k_fold_predict
```

<br>
Function Definition :- <br>

```
train_k_fold_predict(k, tpu, train_tfrecs, val_tfrecs, test_tfrecs, GCS_DS_PATH, BATCH_SIZE)
```

<br>

**_Description_** => <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **k** -> The number of folds. Usually, 5 or 10. <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **tpu** -> the tpu instance. To be obtained from get_strategy()<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **train_tfrecs** -> The complete path location of the tfrecord files of training dataset. <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **val_tfrecs** -> The complete path location of the tfrecord files of the validation dataset. <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **test_tfrecs** -> The complete path location of the tfrecord files of the test dataset. <br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **GCS_DS_PATH** -> The Google Cloud Bucket Service Location of the Dataset.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **BATCH_SIZE** -> Select the batch size of the training dataset. Usually, the value should be a multiple of 128 for efficient utilization of TPUs. <br>



<br> <br>
**_Returns_** => <br>
Doesn't return anything. Saves an output file with the result of each fold training along with its validation result. <br>


<br>

## Examples
***

Following are few Kaggle Notebooks showing the working of **quick_ml** python package. <br>
<br>
TFRecords Dataset Making -> [Notebook 1](https://www.kaggle.com/superficiallybot/quick-ml-tfrecords-maker?scriptVersionId=41133131) <br>
Binary Classification -> [Notebook 2](https://www.kaggle.com/superficiallybot/) <br>
Multi-Class Classification -> [Notebook 3](https://www.kaggle.com/superficiallybot/quick-ml-multiclass-classification-tpu?scriptVersionId=41169786) <br>

## Feedback & Development
***

__Want to contribute? Great!__ <br>
Send your ideas to antoreepjana@gmail.com and ensure the format of the subject of the mail as 
[quick_ml Contribute] -> [Your Subject]


__Want to suggest an improvement or a feature? Most Welcome!__ <br>
Send your ideas to antoreepjana@gmail.com and ensure the format of the subject of the mail as [quick_ml Suggestion] -> [Your Subject]


__Want to share errors or complaint something which you didn't like? That's how it improves ;)__ <br>
Send your grievances to antoreepjana@gmail.com and ensure the format of the subject of the mail as [quick_ml Grievances] -> [Your Subject]


__Want to send love, thanks and appreciation? I'd love to hear from you!__ <br>
Send your love to antoreepjana@gmail.com and ensure the format of the subject of the mail as [quick_ml Feedback] -> [Your Subject]



## Upcoming Features!
***

 - Data Augmentations on TPU.
 - Support for Hyper-Parameter Tuning

## License
***

MIT


**Free Software, Hell Yeah!**
