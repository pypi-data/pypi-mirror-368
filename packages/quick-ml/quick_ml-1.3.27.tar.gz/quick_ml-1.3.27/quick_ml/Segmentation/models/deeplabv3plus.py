class ConvolutionBlock(Model):

    def __init__(self, block_input= None, num_filters = 256, kernel_size = 3, dilation_rate = 1, use_bias = False):
        
        super().__init__()
        self.block_input = block_input
        self.num_filters = num_filters
        self.kernel_size = kernel_size
        self.dilation_rate = dilation_rate
        self.use_bias = use_bias

        ## Layers 

        self.conv1 = Conv2D(self.num_filters, kernel_size = self.kernel_size, dilation_rate = self.dilation_rate, 
            padding = 'same', use_bias = self.use_bias, kernel_initializer = tf.keras.initializers.HeNormal())

        self.bn1 = BatchNormalization()
        #self.relu = ops.nn.relu()
        

    def call(self, x):

        x = self.conv1(x)
        x = self.bn1(x)
        #x = self.relu(x)
        
        return ops.nn.relu(x)


class DilatedSpatialPyramidPooling(Model):

    def __init__(self):#, input_shape =  ((512, 512, 3))):
        super().__init__()
        #self.dspp_input = dspp_input
        #self.dims = dspp_input.shape
        #self.dims = input_shape

        #self.avgpool1 = AveragePooling2D(pool_size = (self.dims[-3], self.dims[-2]))
        self.conv_block1 = ConvolutionBlock( kernel_size = 1, use_bias= True)
       
        self.conv_block2 = ConvolutionBlock(kernel_size=1, dilation_rate=1)
        self.conv_block3 = ConvolutionBlock(kernel_size=3, dilation_rate=6)
        self.conv_block4 = ConvolutionBlock(kernel_size=3, dilation_rate=12)
        self.conv_block5 = ConvolutionBlock(kernel_size=3, dilation_rate=18)
        #self.up_1 = UpSampling2D(size = (self.dims[-3]// x.shape[1] , self.dims[-2] // x.shape[2]))
        self.conv_block_f = ConvolutionBlock(kernel_size = 1)

    def call(self, inputs):
        #x = self.avgpool1(inputs)
        dims = inputs.shape
        x = AveragePooling2D(pool_size = (dims[-3], dims[-2]))(inputs)
        x = self.conv_block1(x)
        outpool = UpSampling2D(size = (dims[-3]// x.shape[1] , dims[-2] // x.shape[2]))(x)

        out_1 = self.conv_block2(inputs)
        out_6 = self.conv_block3(inputs)
        out_12 = self.conv_block4(inputs)
        out_18 = self.conv_block5(inputs)

        x = Concatenate(axis = -1)([outpool, out_1, out_6, out_12, out_18])
        output = self.conv_block_f(x)
        return output


class DeeplabV3Plus(Model):

    def __init__(self, num_classes = 2, image_size = (512, 512, 3)):
        super().__init__()
        self.dims = image_size
        self.image_size = image_size
        model_input = tf.keras.Input(shape=image_size)
        self.preprocessed = tf.keras.applications.resnet50.preprocess_input(model_input)
        resnet50 = tf.keras.applications.ResNet50(
        weights="imagenet", include_top=False, input_tensor=self.preprocessed
        )
        self.conv4_block6_2_relu = resnet50.get_layer("conv4_block6_2_relu").output
        self.conv2_block3_2_relu = resnet50.get_layer("conv2_block3_2_relu").output
        self.dspp = DilatedSpatialPyramidPooling()
        self.conv_block1 = ConvolutionBlock(num_filters=48, kernel_size=1)
        self.conv_block2 = ConvolutionBlock()
        self.conv_block3 = ConvolutionBlock()
        if num_classes == 2 or num_classes == 1:
            self.last_conv = Conv2D(1, kernel_size = (1, 1), padding = 'same')
        else:
            self.last_conv = Conv2D(num_classes, kernel_size=(1, 1), padding="same")
        
    def call(self, inputs):
        
        x = self.conv4_block6_2_relu
        x = self.dspp(x)

        print(x.shape)
        
        input_a = UpSampling2D(
        size=(self.image_size[0] // 4 // x.shape[1], self.image_size[1] // 4 // x.shape[2]),
        interpolation="bilinear",
        )(x)

        input_b = self.conv2_block3_2_relu
        input_b = self.conv_block1(input_b)
        
        x = Concatenate(axis=-1)([input_a, input_b])
        
        x = self.conv_block2(x)
        x = self.conv_block3(x)
        
        x = UpSampling2D(
        size=(self.image_size[0] // x.shape[1], self.image_size[1] // x.shape[2]),
        interpolation="bilinear",
        )(x)

        model_output = self.last_conv(x)
        return model_output

    def summary(self):
        x = Input(shape = self.dims)
        return Model(inputs = [x], outputs = self.call(x)).summary()