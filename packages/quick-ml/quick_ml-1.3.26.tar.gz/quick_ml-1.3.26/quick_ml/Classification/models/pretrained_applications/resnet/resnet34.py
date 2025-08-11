import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import *

class Conv_Block(Model):
    def __init__(self, filters, strides = (2,2)):
        super(Conv_Block, self).__init__()
        filter1, filter2 = filters
        self.conv1_1 = tf.keras.layers.Conv2D(filter1, kernel_size = (3,3), strides = strides, padding = 'same')
        self.bn1_1 = tf.keras.layers.BatchNormalization(axis = 3)
        self.act1_1 = tf.keras.layers.Activation("relu")

        self.conv1_2 = tf.keras.layers.Conv2D(filter2, kernel_size = (3,3), padding = 'same')
        self.bn1_2 = tf.keras.layers.BatchNormalization(axis = 3)
        self.act1_2 = tf.keras.layers.Activation("relu")

        self.conv2_1 = tf.keras.layers.Conv2D(filter2, (1,1), strides = strides, padding = 'valid')
        self.bn2_1 = tf.keras.layers.BatchNormalization(axis = 3)

        self.act = tf.keras.layers.Activation("relu")

    def call(self, x):
        
        path1 = self.conv1_1(x)
        path1 = self.bn1_1(path1)
        path1 = self.act1_1(path1)

        path1 = self.conv1_2(path1)
        path1 = self.bn1_2(path1)
        path1 = self.act1_2(path1)

        path2 = self.conv2_1(x)
        path2 = self.bn2_1(path2)

        output = tf.keras.layers.add([path1, path2])
        output = self.act(output)

        return output


class Identity_Block(Model):
    def __init__(self, filters):
        super(Identity_Block, self).__init__()
        filter1, filter2 = filters
        self.conv1 = tf.keras.layers.Conv2D(filter1, (3,3), padding = 'same')
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.act1 = tf.keras.layers.Activation("relu")

        self.conv2 = tf.keras.layers.Conv2D(filter2, (3,3), padding = 'same')
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.act2 = tf.keras.layers.Activation("relu")

    def call(self, x):
        path1 = self.conv1(x)
        path1 = self.bn1(path1)
        path1 = self.act1(path1)

        path1 = self.conv2(path1)
        path1 = self.bn2(path1)
        path1 = self.act2(path1)

        return tf.keras.layers.add([path1, x])


class ResNet34(Model):

    def __init__(self, input_shape = (224, 224, 3), num_classes = 1000):

        super(ResNet34, self).__init__()

        self.input_shape = input_shape

        self.zero_pad1 = tf.keras.layers.ZeroPadding2D((3,3 ))
        self.conv7x7 = tf.keras.layers.Conv2D(filters = 64, kernel_size = (7,7), strides = (2, 2))
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.act1 = tf.keras.layers.Activation("relu")

        self.zero_pad2 = tf.keras.layers.ZeroPadding2D((1,1))
        self.max_pool1 = tf.keras.layers.MaxPool2D((3, 3), strides=  2)


        self.conv_block1 = Conv_Block([64,64], strides = (1,1))
        self.iden_block1_1 = Identity_Block([64,64])
        self.iden_block1_2 = Identity_Block([64,64])


        self.conv_block2 = Conv_Block([128,128])
        self.iden_block2_1 = Identity_Block([128,128])
        self.iden_block2_2 = Identity_Block([128,128])
        self.iden_block2_3 = Identity_Block([128,128])

        self.conv_block3 = Conv_Block([256, 256])
        self.iden_block3_1 = Identity_Block([256, 256])
        self.iden_block3_2 = Identity_Block([256,256])
        self.iden_block3_3 = Identity_Block([256,256])
        self.iden_block3_4 = Identity_Block([256,256])
        self.iden_block3_5 = Identity_Block([256,256])

        self.conv_block4 = Conv_Block([512,512])
        self.iden_block4_1 = Identity_Block([512,512])
        self.iden_block4_2 = Identity_Block([512,512])

        self.glob_pool = tf.keras.layers.GlobalAveragePooling2D()
        
        if num_classes > 2:
            self.fc = tf.keras.layers.Dense(1000, activation = 'softmax')
        else:
            self.fc = tf.keras.layers.Dense(1, activation = 'sigmoid')
        

    def call(self, x):

        x =  self.zero_pad1(x)
        x = self.conv7x7(x)
        x = self.bn1(x)

        x =  self.act1(x)

        x = self.zero_pad2(x)
        x = self.max_pool1(x)

        x = self.conv_block1(x)
        x = self.iden_block1_1(x)
        x = self.iden_block1_2(x)

        x = self.conv_block2(x)
        x = self.iden_block2_1(x)
        x = self.iden_block2_2(x)
        x = self.iden_block2_3(x)

        x = self.conv_block3(x)
        x = self.iden_block3_1(x)
        x = self.iden_block3_2(x)
        x = self.iden_block3_3(x)
        x = self.iden_block3_4(x)
        x = self.iden_block3_5(x)

        x = self.conv_block4(x)
        x = self.iden_block4_1(x)
        x = self.iden_block4_2(x)

        x = self.glob_pool(x)
        x = self.fc(x)

        return x

    def summary(self):

        x = Input(shape = self.input_shape)
        return Model(inputs = x, outputs = self.call(x)).summary()




