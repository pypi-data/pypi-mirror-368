from tensorflow.keras.models import Model

from tensorflow.keras.layers import ReLU
from tensorflow.keras.layers import Input, Flatten

from .....experimental.utils.torch2tf.layers.conv import Convolution2D
from .....experimental.utils.torch2tf.layers.pooling import MAXPOOL2D, AdaptiveAvgpooling2D

import tensorflow as tf
import numpy as np

class FeaturesAlex(tf.keras.Model):

    
    def __init__(self): #, weights, conv_layers):
        super(FeaturesAlex, self).__init__()

        
        self.conv1 = Convolution2D(filters = 64, kernel_size = (11,11), strides = (4,4), padding = (2,2))
        self.act1 = ReLU()
        
        ###  complete implementation
        self.maxpool1 = MAXPOOL2D(pool_size = (3,3), strides = 2, padding =  0, dilation = 1)

        self.conv2 = Convolution2D(filters = 192, kernel_size = (5,5), strides = (1,1), padding = (2,2))
        self.act2 = ReLU()
        self.maxpool2 = MAXPOOL2D(pool_size = (3,3), strides = 2, padding = 0, dilation = 1)

        self.conv3 = Convolution2D(384, kernel_size = (3,3), strides = (1,1), padding = (1,1))
        self.act3 = ReLU()
        self.conv4 = Convolution2D(256, kernel_size = (3,3), strides =(1, 1), padding=(1, 1) )
        self.act4 = ReLU()
        self.conv5 = Convolution2D(256, kernel_size = (3,3), strides = (1,1), padding = (1,1))
        self.act5 = ReLU()

        self.maxpool3 = MAXPOOL2D(pool_size = (3,3), strides = 2, padding = 0, dilation = 1)

        # if weights == 'imagenet':
            
        #     self.conv1.load_torch_weights(conv_layers[0], (224,224, 3))
        #     self.conv2.load_torch_weights(conv_layers[1], (27, 27, 64))
        #     self.conv3.load_torch_weights(conv_layers[2], (13,13, 192))
        #     self.conv4.load_torch_weights(conv_layers[3], (13,13,384))
        #     self.conv5.load_torch_weights(conv_layers[4], (13,13,256))
        # elif weights == None:
        #     pass
        # else:
        #     raise ValueError("Invalid weight argument. Choose between None and 'imagenet'")

    def call(self, x):
        #print("Conv 1 X shape", x.shape)
        x = self.conv1(x)
        x = self.act1(x)
        x = self.maxpool1(x)
        #print(" Conv 2 X shape", x.shape)
        x = self.conv2(x)
        x = self.act2(x)
        x = self.maxpool2(x)
        #print(" Conv 3 X shape", x.shape)
        x = self.conv3(x)
        x = self.act3(x)

        #print("Conv 4 X shape", x.shape)
        x = self.conv4(x)
        x = self.act4(x)


        #print("Conv 5 X shape", x.shape)
        x = self.conv5(x)
        x = self.act5(x)

        x = self.maxpool3(x)
        

        return x

from tensorflow.keras.layers import Dropout, Dense

class ClassifierAlex(tf.keras.Model):

    def __init__(self, num_classes): #, weights):

        super(ClassifierAlex, self).__init__()
        self.flatten = Flatten()
        self.dropout1 = Dropout(0.5)
        self.linear1 = Dense(4096)
        self.act6 = ReLU()

        self.dropout2 = Dropout(0.5)
        self.linear2 = Dense(4096)
        self.act7 = ReLU()

        if num_classes == 2:
            self.linear3 = Dense(1, activation = 'sigmoid')
        else:
            self.linear3 = Dense(num_classes, activation = 'softmax')


        # if weights == 'imagenet':
            
        #     linear1_weights_torch = self.alex_model.classifier[1].weight.detach().cpu().numpy()
        #     linear1_bias_torch = self.alex_model.classifier[1].bias.detach().cpu().numpy()
        #     linear1_weights_tf = linear1_weights_torch.T#np.transpose(linear1_weights_torch, (2,3,1,0))
        #     self.linear1.build(input_shape = (None, 9216))
        #     self.linear1.set_weights([linear1_weights_tf, linear1_bias_torch])
    
        #     linear2_weights_torch = self.alex_model.classifier[4].weight.detach().cpu().numpy()
        #     linear2_bias_torch = self.alex_model.classifier[4].bias.detach().cpu().numpy()
        #     linear2_weights_tf = linear2_weights_torch.T#np.transpose(linear1_weights_torch, (2,3,1,0))
        #     self.linear2.build(input_shape = (None, 4096))
        #     self.linear2.set_weights([linear2_weights_tf, linear2_bias_torch])
    
        #     linear3_weights_torch = self.alex_model.classifier[-1].weight.detach().cpu().numpy()
        #     linear3_bias_torch = self.alex_model.classifier[-1].bias.detach().cpu().numpy()
        #     linear3_weights_tf = linear3_weights_torch.T#np.transpose(linear1_weights_torch, (2,3,1,0))
        #     self.linear3.build(input_shape = (None, 4096))
        #     self.linear3.set_weights([linear3_weights_tf, linear3_bias_torch])
        # elif weights == None:
        #     pass

        # else:
        #     raise ValueError("Invalid weights argument. Choose between 'imagenet' and None")

    
    def call(self, x, training = True):

        x = tf.transpose(x, [0, 3, 1, 2])
        x = self.flatten(x)
        x = self.dropout1(x, training = training)
        x = self.linear1(x)
        x = self.act6(x)

        x = self.dropout2(x, training = training)
        x = self.linear2(x)
        x = self.act7(x)
        x = self.linear3(x)
        return x

class AlexNet(tf.keras.Model):

    def __init__(self, input_shape = (224,224,3), num_classes = 1000, weights = None):

        super(AlexNet, self).__init__()
        self.input_shape = input_shape
        self.num_classes = num_classes
        #self.weights = weights


        self.features = FeaturesAlex()
        self.avgpool = AdaptiveAvgpooling2D(output_size = (6,6))
        self.classifier = ClassifierAlex(num_classes)

        if weights == 'imagenet':
            # from torchvision.models import alexnet
            # self.alex_model = alexnet(pretrained = True)
            # self.conv_layers = [self.alex_model.features[0], self.alex_model.features[3], self.alex_model.features[6], self.alex_model.features[8], self.alex_model.features[10]]
            #self.load_weights('.alexnet.keras')
            #self.build((None, 224, 224, 3))
            x = np.random.rand(1, 224, 224, 3)#Input(shape = self.input_shape)
            self.build((None, 224, 224, 3))
            self.call(x, training = False)

            ## Weights sourced from PyTorch's Official Torchvision AlexNet Model IMAGENET1K_V1
            
            #self.load_weights('alexnet.keras')
            from ..download_model_weights import download_model_weights
            self.load_weights(download_model_weights('alexnet', True))

    def call(self, x, training = True):

        x = self.features(x)
        x = self.avgpool(x)
        x = self.classifier(x, training = training)

        return x

    def summary(self):
        x = Input(shape = self.input_shape)
        return Model(inputs = x, outputs = self.call(x, training = False)).summary()

# model_tf = AlexNet((224, 224, 3), weights = None)
# model_tf.summary()
# model_tf.save('alexnet.keras')