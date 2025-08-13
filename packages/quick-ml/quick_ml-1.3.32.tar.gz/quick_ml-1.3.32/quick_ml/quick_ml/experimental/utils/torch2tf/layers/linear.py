import tensorflow as tf
import numpy as np

class LinearDense(tf.keras.Layer):

    def __init__(self, out_features, bias = True, activation = None, 
        kernel_initializer='glorot_uniform',
    bias_initializer='zeros',
    kernel_regularizer=None,
    bias_regularizer=None,
    activity_regularizer=None,
    kernel_constraint=None,
    bias_constraint=None,
    lora_rank=None,**kwargs):
        
        super(LinearDense, self).__init__()
        
        self.linear = tf.keras.layers.Dense(out_features, use_bias = bias, activation = activation, 
                                                    kernel_initializer='glorot_uniform',
                                                    bias_initializer='zeros',
                                                    kernel_regularizer=None,
                                                    bias_regularizer=None,
                                                    activity_regularizer=None,
                                                    kernel_constraint=None,
                                                    bias_constraint=None,
                                                    lora_rank=None)

    def load_torch_weights(self, layer, inp_size):

        linear_weights_torch = layer.weight.detach().cpu().numpy()

        linear_weights_tf = linear_weights_torch.T

        linear_bias_tf = layer.bias.detach().cpu().numpy()

        self.linear.build(input_shape = (None, inp_size))
        self.linear.set_weights([linear_weights_tf, linear_bias_tf])
        
    def call(self, x):
        return self.linear(x) 
 
