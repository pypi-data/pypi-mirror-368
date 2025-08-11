from tensorflow.keras.layers import * 
from tensorflow.keras import Model
import tensorflow as tf 


class ConvBlock(Model):

    def __init__(self, num_filters):

        super().__init__()

        self.conv_1_1 = tf.keras.layers.Conv2D(num_filters, 3, padding='same')
        self.bn_1_1 = tf.keras.layers.BatchNormalization()
        self.act_1_1 = tf.keras.layers.Activation('relu')

        self.conv_1_2 = tf.keras.layers.Conv2D(num_filters, 3, padding = 'same')
        self.bn_1_2 = tf.keras.layers.BatchNormalization()
        self.act_1_2 = tf.keras.layers.Activation('relu')

    def call(self, inputs):

        conv1 = self.conv_1_1(inputs)
        conv1 = self.bn_1_1(conv1)
        conv1 = self.act_1_1(conv1)
        conv1 = self.conv_1_2(conv1)
        conv1 = self.bn_1_2(conv1)
        conv1 = self.act_1_2(conv1)
        return conv1

    
class UnetPlusPlus(Model):

    def __init__(self, input_shape=(256, 256, 3), num_classes=1, deep_supervision=True):
        super().__init__()
        self.input_size = input_shape
        self.num_classes = num_classes 
        self.deep_supervision = deep_supervision


        ## Conv Block with 64 filters
        self.conv_block1 = ConvBlock(64)

        self.max_pool_1 = tf.keras.layers.MaxPooling2D()

        ## Conv BLock 2
        self.conv_block2 = ConvBlock(128)
        self.max_pool_2 = tf.keras.layers.MaxPooling2D()

        ## Conv Block 3
        self.conv_block3 = ConvBlock(256)
        self.max_pool_3 = tf.keras.layers.MaxPooling2D()


        ## Conv Block 4
        self.conv_block4 = ConvBlock(512)
        self.max_pool_4 = tf.keras.layers.MaxPooling2D()

        ## Conv Block 5
        self.conv_block5 = ConvBlock(1024)
        self.max_pool_5 = tf.keras.layers.MaxPooling2D()

        ########### Nested  ###############
        
        self.up_1 = tf.keras.layers.UpSampling2D()
        ## Nested Conv Block 1 [6]
        self.conv_block6 = ConvBlock(64)

        ## Nested Conv Block 2 [7]

        self.up_2 = tf.keras.layers.UpSampling2D()
        self.conv_block7 = ConvBlock(128)

        ## Nested Conv Block 3 [8]

        self.up_3 = tf.keras.layers.UpSampling2D()
        self.conv_block8 = ConvBlock(256)

        ## Nested Conv Block 4 [9]

        self.up_4 = tf.keras.layers.UpSampling2D()
        self.conv_block9 = ConvBlock(512)

        ### Double Concats
        ## Nested Conv Block 5 [10]

        self.up_5 = tf.keras.layers.UpSampling2D()
        self.conv_block10 = ConvBlock(64)


        ## Nested Conv Block 6 [11]
        self.up_6 = tf.keras.layers.UpSampling2D()
        self.conv_block11 = ConvBlock(128)

        ## Nested Conv Block 7 [12]
        self.up_7 = tf.keras.layers.UpSampling2D()
        self.conv_block12 = ConvBlock(256)

        ### Triple Concats
        ## Nested Conv Block 8 [13]
        self.up_8 = tf.keras.layers.UpSampling2D()
        self.conv_block13 = ConvBlock(64)

        ## Nested Conv Block 9 [14]
        self.up_9 = tf.keras.layers.UpSampling2D()
        self.conv_block14 = ConvBlock(128)

        ## Nested Conv Block 10 [15]
        self.up_10 = tf.keras.layers.UpSampling2D()
        self.conv_block15 = ConvBlock(64)
        
        
        if num_classes == 1 or num_classes == 2:
            self.last_conv = tf.keras.layers.Conv2D(1, 1)
        else:
            self.last_conv = tf.keras.layers.Conv2D(num_classes, 1)
    
    def call(self, inputs):


        ###
        # Encoder Network
        ###
        
        ## Conv Block 1
        x_00 = self.conv_block1(inputs)
        x_00 = self.max_pool_1(x_00)

        ## Conv Block 2
        x_10 = self.conv_block2(x_00)
        x_10 = self.max_pool_2(x_10)

        ## Conv Block 3
        x_20 = self.conv_block3(x_10)
        x_20 = self.max_pool_3(x_20)

        ## Conv Block 4
        
        x_30 = self.conv_block4(x_20)
        x_30 = self.max_pool_4(x_30)

        ## Conv Block 5
        
        x_40 = self.conv_block5(x_30)
        x_40 = self.max_pool_5(x_40)

        # Nested Decoding Path

        ## Nest 1
        x_10_up = self.up_1(x_10)
        x_00_10up_merged = tf.keras.layers.concatenate([x_00, x_10_up])#self.concat1([x_00, x_10_up])
        x_01 = self.conv_block6(x_00_10up_merged)

        ## Nest 2
        x_20_up = self.up_2(x_20)
        x_10_20up_merged = tf.keras.layers.concatenate([x_10, x_20_up])
        x_11 = self.conv_block7(x_10_20up_merged)


        ## Nest 3
        
        x_30_up = self.up_3(x_30)
        x_20_30up_merged = tf.keras.layers.concatenate([x_20, x_30_up])
        x_21 = self.conv_block8(x_20_30up_merged)        
        
        
        ## Nest 4
        x_40_up = self.up_4(x_40)
        x_30_40up_merged = tf.keras.layers.concatenate([x_30, x_40_up])
        x_31 = self.conv_block9(x_30_40up_merged)


        ### Double Concats
        ## Nest 5
        x_11_up = self.up_5(x_11)
        x_00_01_11up_merged = tf.keras.layers.concatenate([x_00, x_01, x_11_up])
        x_02 = self.conv_block10(x_00_01_11up_merged)

        ### ------
        ## Nest 6
        x_21_up = self.up_6(x_21)
        x_10_11_21up_merged = tf.keras.layers.concatenate([x_10, x_11, x_21_up])
        x_12 = self.conv_block11(x_10_11_21up_merged)
        ## Nest 7
        x_31_up = self.up_7(x_31)
        x_20_21_31up_merged = tf.keras.layers.concatenate([x_20, x_21, x_31_up])
        x_22 = self.conv_block12(x_20_21_31up_merged)
        
        ### Triple Concats
        
        ## Nest 8
        x_12_up = self.up_8(x_12)
        x_00_01_02_12up_merged = tf.keras.layers.concatenate([x_00, x_01, x_02, x_12_up])
        x_03 = self.conv_block13(x_00_01_02_12up_merged)

        ## Nest 9
        x_22_up = self.up_9(x_22)
        x_10_11_12_22up_merged = tf.keras.layers.concatenate([x_10, x_11, x_12, x_22_up])
        x_13 = self.conv_block14(x_10_11_12_22up_merged)

        ### 4 concats
        ## Nest 10
        
        x_13_up = self.up_10(x_13)
        x_00_01_02_03_13up_merged = tf.keras.layers.concatenate([x_00, x_01, x_02, x_03, x_13_up])
        x_04 = self.conv_block15(x_00_01_02_03_13up_merged)
        
        outputs = self.last_conv(x_04)#tf.keras.layers.Conv2D(num_classes, 1)(x_04)
                
        return outputs

    def summary(self):
        x = Input(shape = self.input_size)
        return Model(inputs = [x], outputs = self.call(x)).summary()
        
    