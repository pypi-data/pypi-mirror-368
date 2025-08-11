import tensorflow as tf
from typing import Tuple  # Import Tuple for type hinting

from tensorflow.keras.layers import Conv2D

class Convolution2D(tf.keras.layers.Layer):
    def __init__(self, filters, kernel_size, strides = (1,1), padding = 'valid', use_bias = True, **kwargs):
        super(Convolution2D, self).__init__()
        """
        padding tuple of 4 ints => left, right, top & bottom
        """

        self.filters = filters
        self.kernel_size = kernel_size

        if isinstance(strides, int):
            self.strides = (strides, strides)
        elif isinstance(strides, tuple):
            self.strides = strides
        else:
            raise TypeError('Invalid Input type. Only int or tuple (int, int) allowed')
        #self.strides = strides
        self.use_bias = use_bias

        #self.padding = padding
        # self.conv = tf.keras.layers.Conv2D(
        #     filters = filters, 
        #     kernel_size = kernel_size, 
        #     strides = strides, 
        #     padding = 'valid',
        #         **kwargs
        # )

        if padding in ['valid', 'same']:
            self.padding = padding
            self.conv = Conv2D(filters = self.filters, kernel_size = self.kernel_size, 
                              strides = self.strides, padding = self.padding, use_bias = self.use_bias)
            
        #MaxPooling2D(pool_size = self.pool_size, strides = self.strides, padding = self.padding)   
        else:
            #self.maxpool2d = MaxPooling2D(pool_size = self.pool_size, strides = self.strides, padding = 'valid')
            self.conv = Conv2D(filters = self.filters, kernel_size = self.kernel_size, 
                              strides = self.strides, padding = 'valid', use_bias = self.use_bias)
            if isinstance(padding, int):
                self.padding = ((0,0), (padding, padding), (padding, padding), (0,0))
            elif isinstance(padding, tuple):
                self.padding = ((0,0), (padding[0], padding[0]), (padding[1], padding[1]), (0,0))
            else:
                raise TypeError('Invalid Input type. Only int or tuple (int, int) allowed')
        #print("padding", self.padding)
        

    def call(self, x):
        #top, bottom, left, right = self.padding
        #padded = tf.pad(x, paddings = [[0,0], [top, bottom], [left, right], [0,0]])
        #print(type(self.padding))
        if isinstance(self.padding, tuple):
            x = tf.pad(x, self.padding)
        return self.conv(x)   

    def load_torch_weights(self, torch_layer, img_size : Tuple[int, int, int]) -> None:

        weights_torch = torch_layer.weight.detach().cpu().numpy()

        weights_tf = np.transpose(weights_torch, (2,3,1,0))
        self.conv(np.random.rand(1, img_size[0], img_size[1], img_size[2]))

        if self.use_bias:
            bias_torch = torch_layer.bias.detach().cpu().numpy()
            self.conv.set_weights([weights_tf, bias_torch])

        else:
            self.conv.set_weights([weights_tf])
        