import tensorflow as tf
import numpy as np

class BatchNorm2D(tf.keras.Layer):

    def __init__(self, eps = 1e-05, momentum = 0.1, affine = True, track_running_stats = True):
        
        super(BatchNorm2D, self).__init__()
        self.momentum = 1 - momentum

        self.bn = tf.keras.layers.BatchNormalization(
            axis = -1, momentum = self.momentum, 
            epsilon = eps, center = affine, scale = affine
        )

    def load_torch_weights(self, layer, inp_size):

        dummy_input = np.zeros((1, 112, 112, 64), dtype=np.float32)
        _ = self.call(dummy_input, training = False)
        self.set_weights([layer.weight.detach().numpy(), layer.bias.detach().numpy(), layer.running_mean.detach().numpy(), layer.running_var.detach().numpy()])
        
    def call(self, x, training = True):
        return self.bn(x, training = training) 
