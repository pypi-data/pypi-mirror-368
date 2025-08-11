def convolutional_block(X, f, filters, stage, block, s=2):
    """
    Implementation of the convolutional block as defined in Figure 4
    Arguments:
        X: input tensor of shape (m, n_H_prev, n_W_prev, n_C_prev)
        f: integer, specifying the shape of the middle CONV's window for the main path
        filters: python list of integers, defining the number of filters in the CONV layers of the main path
        stage: integer, used to name the layers, depending on their position in the network
        block: string/character, used to name the layers, depending on their position in the network
        s: Integer, specifying the stride to be used
    Returns:
        X: output of the convolutional block, tensor of shape (n_H, n_W, n_C)
    """

    # defining name basis
    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    # Retrieve Filters
    F1, F2, F3 = filters

    # Save the input value
    X_shortcut = X

    """First component of main path"""
    # CONV2D
    X = Conv2D(filters=F1, kernel_size=(1, 1), strides=(s, s), padding='valid', name=conv_name_base + '2a', kernel_initializer=glorot_uniform(seed=0))(X)
    # Batch Norm
    X = BatchNormalization(axis=3, name=bn_name_base + '2a')(X)
    # ReLU
    X = Activation('relu')(X)

    """Second component of main path"""
    # CONV2D
    X = Conv2D(filters=F2, kernel_size=(f, f), strides=(1, 1), padding='same', name=conv_name_base + '2b', kernel_initializer=glorot_uniform(seed=0))(X)
    # Batch Norm
    X = BatchNormalization(axis=3, name=bn_name_base + '2b')(X)
    # ReLU
    X = Activation('relu')(X)

    """Third component of main path"""
    # CONV2D
    X = Conv2D(filters=F3, kernel_size=(1, 1), strides=(1, 1), padding='valid', name=conv_name_base + '2c', kernel_initializer=glorot_uniform(seed=0))(X)
    # Batch Norm
    X = BatchNormalization(axis=3, name=bn_name_base + '2c')(X)

    """Shortcut Path"""
    # Shortcut CONV2D
    X_shortcut = Conv2D(filters=F3, kernel_size=(1, 1), strides=(s, s), padding='valid', name=conv_name_base + '1', kernel_initializer=glorot_uniform(seed=0))(X_shortcut)
    # Shortcut Batch Norm
    X_shortcut = BatchNormalization(axis=3, name=bn_name_base + '1')(X_shortcut)

    """Final step: Add shortcut value to main path, and pass it through a RELU activation"""
    # Shortcut or Skip Connection
    X = Add()([X, X_shortcut])
    # ReLU
    X = Activation('relu')(X)

    return X

def identity_block(X, f, filters, stage, block):
    """
    Implementation of the identity block as defined in Figure 3
    Arguments:
        X: input tensor of shape (m, n_H_prev, n_W_prev, n_C_prev)
        f: integer, specifying the shape of the middle CONV's window for the main path
        filters: python list of integers, defining the number of filters in the CONV layers of the main path
        stage: integer, used to name the layers, depending on their position in the network
        block: string/character, used to name the layers, depending on their position in the network
    Returns:
        X: output of the identity block, tensor of shape (n_H, n_W, n_C)
    """

    # defining name basis
    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    # Retrieve Filters
    F1, F2, F3 = filters

    # Save the input value. You'll need this later to add back to the main path.
    X_shortcut = X

    """First component of main path"""
    # CONV2D
    X = Conv2D(filters=F1, kernel_size=(1, 1), strides=(1, 1), padding='valid', name=conv_name_base + '2a', kernel_initializer=glorot_uniform(seed=0))(X)
    # Batch Norm
    X = BatchNormalization(axis=3, name=bn_name_base + '2a')(X)
    # ReLU
    X = Activation('relu')(X)

    """Second component of main path"""
    # CONV2D
    X = Conv2D(filters=F2, kernel_size=(f, f), strides=(1, 1), padding='same', name=conv_name_base + '2b', kernel_initializer=glorot_uniform(seed=0))(X)
    # Batch Norm
    X = BatchNormalization(axis=3, name=bn_name_base + '2b')(X)
    # ReLU
    X = Activation('relu')(X)

    """Third component of main path"""
    # CONV2D
    X = Conv2D(filters=F3, kernel_size=(1, 1), strides=(1, 1), padding='valid', name=conv_name_base + '2c', kernel_initializer=glorot_uniform(seed=0))(X)
    # Batch Norm
    X = BatchNormalization(axis=3, name=bn_name_base + '2c')(X)

    """Final step: Add shortcut value to main path, and pass it through a RELU activation"""
    # SKIP Connection
    X = Add()([X, X_shortcut])
    # ReLU
    X = Activation('relu')(X)

    return X

from tensorflow.keras.initializers import GlorotUniform as glorot_uniform
def ResNet152(input_shape=(224, 224, 3)):
    """
    Implementation of the popular ResNet50 the following architecture:
        CONV2D -> BATCHNORM -> RELU -> MAXPOOL -> CONVBLOCK -> IDBLOCK*2 -> CONVBLOCK -> IDBLOCK*3 -> CONVBLOCK -> IDBLOCK*5 -> CONVBLOCK -> IDBLOCK*2 -> AVGPOOL -> TOPLAYER
    Arguments:
        input_shape: shape of the images of the dataset
        classes: integer, number of classes
    Returns:
        model: a Model() instance in Keras
    """

    # Define the input as a tensor with shape input_shape
    X_input = Input(input_shape)

    # ZERO PAD
    X = ZeroPadding2D((3, 3))(X_input)


    """Stage 1"""
    # CONV
    X = Conv2D(64, (7, 7), strides=(2, 2), name='conv1', kernel_initializer=glorot_uniform(seed=0))(X)
    # Batch Norm
    X = BatchNormalization(axis=3, name='bn_conv1')(X)
    # ReLU
    X = Activation('relu')(X)
    # MAX POOL
    X = MaxPooling2D((3, 3), strides=(2, 2))(X)


    """Stage 2"""
    # CONV BLOCK
    X = convolutional_block(X, f=3, filters=[64, 64, 256], stage=2, block='a', s=1)
    # ID BLOCK x2
    X = identity_block(X, 3, [64, 64, 256], stage=2, block='b')
    X = identity_block(X, 3, [64, 64, 256], stage=2, block='c')



    """Stage 3"""
    # CONV BLOCK
    X = convolutional_block(X, f=3, filters=[128, 128, 512], stage=3, block='a', s=2)
    # ID BLOCK x3
    X = identity_block(X, 3, [128, 128, 512], stage=3, block='b')
    X = identity_block(X, 3, [128, 128, 512], stage=3, block='c')
    X = identity_block(X, 3, [128, 128, 512], stage=3, block='d')
    X = identity_block(X, 3, [128, 128, 512], stage=3, block='e')
    X = identity_block(X, 3, [128, 128, 512], stage=3, block='f')
    X = identity_block(X, 3, [128, 128, 512], stage=3, block='g')
    X = identity_block(X, 3, [128, 128, 512], stage = 3, block = 'h')


    """Stage 4"""
    # CONV BLOCK
    X = convolutional_block(X, f=3, filters=[256, 256, 1024], stage=4, block='a', s=2)
    # ID BLOCK x5
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='b')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='c')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='d')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='e')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='f')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='g')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='h')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='i')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='j')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='k')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='l')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='m')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='n')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='o')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='p')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='q')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='r')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='s')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='t')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='u')
    X = identity_block(X, 3, [256, 256, 1024], stage = 4, block = 'v')
    X = identity_block(X, 3, [256, 256, 1024], stage = 4, block = 'w')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='x')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='y')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='z')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='aa')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='ab')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='ac')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='ad')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='ae')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='af')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='ag')
    X = identity_block(X, 3, [256, 256, 1024], stage=4, block='ah')
    X = identity_block(X, 3, [256, 256, 1024], stage = 4, block = 'ai')
    X = identity_block(X, 3, [256, 256, 1024], stage = 4, block = 'aj')


    """Stage 5"""
    # CONV BLOCK
    X = convolutional_block(X, f=3, filters=[512, 512, 2048], stage=5, block='a', s=2)
    # ID BLOCK x2
    X = identity_block(X, 3, [512, 512, 2048], stage=5, block='b')
    X = identity_block(X, 3, [512, 512, 2048], stage=5, block='c')

    # AVGPOOL. Use "X = AveragePooling2D(...)(X)"
    #X = AveragePooling2D(pool_size=(2, 2), padding='same')(X)
    X = GlobalAveragePooling2D()(X)
    #X = tf.keras.layers.Flatten()(X)
    X = tf.keras.layers.Dense(1000, activation = 'softmax')(X)

    # Create Model
    model = Model(inputs=X_input, outputs=X, name='ResNet152')

    # return ResNet50 as model
    return model 
