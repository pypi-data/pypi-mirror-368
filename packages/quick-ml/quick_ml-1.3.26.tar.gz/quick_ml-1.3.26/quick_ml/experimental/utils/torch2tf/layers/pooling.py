
import math

import tensorflow as tf

class MAXPOOL2D(tf.keras.layers.Layer):

    def __init__(self, pool_size = (2,2), strides = None, padding = 'valid', dilation = 1, **kwargs):
        super(MAXPOOL2D, self).__init__()
        self.pool_size = pool_size

        if isinstance(strides, int):
            self.strides = (strides, strides)
        elif isinstance(strides, tuple):
            self.strides = strides
        else:
            raise TypeError('Invalid Input type. Only int or tuple (int, int) allowed')
        #self.strides = strides
        self.dilation = dilation
        
        if padding in ['valid', 'same']:
            self.padding = padding
            #self.maxpool2d = MaxPooling2D(pool_size = self.pool_size, strides = self.strides, padding = self.padding)   
        else:
            #self.maxpool2d = MaxPooling2D(pool_size = self.pool_size, strides = self.strides, padding = 'valid')
            if isinstance(padding, int):
                self.padding = ((0,0), (padding, padding), (padding, padding), (0,0))
            elif isinstance(padding, tuple):
                self.padding = ((0,0), (padding[0], padding[0]), (padding[1], padding[1]), (0,0))
            else:
                raise TypeError('Invalid Input type. Only int or tuple (int, int) allowed')
            

    def call(self, x):
        
        return tf.nn.pool(x, window_shape = self.pool_size, pooling_type = 'MAX', strides = self.strides, padding = self.padding, dilations =[self.dilation, self.dilation])


class AdaptiveAvgpooling2D(tf.keras.layers.Layer):

    def __init__(self, output_size , **kwargs):

        super(AdaptiveAvgpooling2D, self).__init__()

        if isinstance(output_size, int):
            self.output_size = (output_size, output_size)
        else:
            self.output_size = output_size

        
    def call(self, x):

        self.stride = math.floor(x.shape[1]/self.output_size[0])
        self.strides = (self.stride, self.stride)

        self.kernel = x.shape[1] - (self.output_size[0] - 1) * self.stride

        self.pool_size = (self.kernel, self.kernel)
        
        return tf.nn.pool(x, window_shape = self.pool_size, pooling_type = 'AVG', strides = self.strides, padding = 'VALID', dilations =[1,1])