import tensorflow as tf 
from tensorflow.keras.layers import *
from tensorflow.nn import relu

from ...experimental.utils.torch2tf.layers.conv import Convolution2D

#from ..unetpp import ConvBlock
#from unetpp import ConvBlock

class REBNCONV(tf.keras.Model):
	def __init__(self,in_ch=3,out_ch=3,dirate=1):
		super(REBNCONV,self).__init__()
		#self.conv_s1 = nn.Conv2d(in_ch,out_ch,3,padding=1*dirate,dilation=1*dirate)
		#self.bn_s1 = nn.BatchNorm2d(out_ch)
		#self.relu_s1 = nn.ReLU(inplace=True)
		#self.conv_s1 = Conv2D(out_ch, kernel_size = 3, padding = 'same', dilation_rate = dirate)
		self.conv_s1 = Convolution2D(out_ch, kernel_size = 3, padding = 1 * dirate, dilation = 1 * dirate)
		self.bn_s1 = BatchNormalization()
		self.relu_s1 = ReLU()

	def call(self,x, training = False):

		hx = x
		xout = self.relu_s1(self.bn_s1(self.conv_s1(hx), training = training))

		return xout

## upsample tensor 'src' to have the same spatial size with tensor 'tar'
def _upsample_like(src,tar):

	#src = F.upsample(src,size=tar.shape[2:],mode='bilinear')

	h_factor = tar.shape[1]/src.shape[1]
	#print("H Factor", h_factor)
	w_factor = tar.shape[2]/src.shape[2]
	#print("W Factor", w_factor)

	#src = UpSampling2D(size = (h_factor, w_factor), interpolation = 'bilinear')(src)
	#out = UpSampling2D(size = tf.convert_to_tensor([h_factor, w_factor]), interpolation = 'bilinear')(src)
	out = UpSampling2D(size = (int(h_factor), int(w_factor)), interpolation = 'bilinear')(src)

	return out

### RSU-7 ###
#class RSU7(nn.Module):#UNet07DRES(nn.Module):
class RSU7(tf.keras.Model):

	def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
		super(RSU7,self).__init__()

		self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)

		self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
		#self.pool1 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool1 = MaxPool2D(pool_size = (2,2), strides = 2) #)#, ceil_mode = True)


		self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool2 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool2 = MaxPool2D(pool_size = (2, 2), strides = 2)#, ceil_mode = True)


		self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool3 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool3 = MaxPool2D(pool_size = (2,2), strides = 2)#)#, ceil_mode = True)



		self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool4 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool4 = MaxPool2D(pool_size = (2, 2), strides = 2)#, ceil_mode = True)


		self.rebnconv5 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool5 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool5 = MaxPool2D(pool_size = (2,2), strides = 2)#, ceil_mode = True)


		self.rebnconv6 = REBNCONV(mid_ch,mid_ch,dirate=1)

		self.rebnconv7 = REBNCONV(mid_ch,mid_ch,dirate=2)

		self.rebnconv6d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv5d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv4d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)

	def call(self,x):

		hx = x
		hxin = self.rebnconvin(hx)

		hx1 = self.rebnconv1(hxin)
		hx = self.pool1(hx1)

		hx2 = self.rebnconv2(hx)
		hx = self.pool2(hx2)

		hx3 = self.rebnconv3(hx)
		hx = self.pool3(hx3)

		hx4 = self.rebnconv4(hx)
		hx = self.pool4(hx4)

		hx5 = self.rebnconv5(hx)
		hx = self.pool5(hx5)

		hx6 = self.rebnconv6(hx)

		hx7 = self.rebnconv7(hx6)

		#print("hxin.shape", hxin.shape)
		#hx6d =  self.rebnconv6d(torch.cat((hx7,hx6),1))
		hx6d = self.rebnconv6d(tf.concat([hx7, hx6], -1))
		#print(hx6d.shape)
		#print('----' * 10,"\n", hx5.shape)
		hx6dup = _upsample_like(hx6d,hx5)
		#print("hx6dup.shape", hx6dup.shape)

		#hx5d =  self.rebnconv5d(torch.cat((hx6dup,hx5),1))
		hx5d = self.rebnconv5d(tf.concat([hx6dup, hx5], -1))
		hx5dup = _upsample_like(hx5d,hx4)
		#print("hx5dup.shape", hx5dup.shape)

		#hx4d = self.rebnconv4d(torch.cat((hx5dup,hx4),1))
		hx4d = self.rebnconv4d(tf.concat([hx5dup, hx4], -1))
		hx4dup = _upsample_like(hx4d,hx3)
		#print("hx4dup.shape", hx4dup.shape)

		#hx3d = self.rebnconv3d(torch.cat((hx4dup,hx3),1))
		hx3d = self.rebnconv3d(tf.concat([hx4dup, hx3], -1))
		hx3dup = _upsample_like(hx3d,hx2)
		#print("hx3dup.shape", hx3dup.shape)

		#hx2d = self.rebnconv2d(torch.cat((hx3dup,hx2),1))
		hx2d = self.rebnconv2d(tf.concat([hx3dup, hx2], -1))
		hx2dup = _upsample_like(hx2d,hx1)
		#print("hx2dup.shape", hx2dup.shape)
		#print("hx1.shape", hx1.shape)
		
		#hx1d = self.rebnconv1d(torch.cat((hx2dup,hx1),1))
		hx1d = self.rebnconv1d(tf.concat([hx2dup, hx1], -1))
		#print("hx1d.shape", hx1d.shape)

		return hx1d + hxin

### RSU-6 ###
#class RSU6(nn.Module):#UNet06DRES(nn.Module):
class RSU6(tf.keras.Model):

	def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
		super(RSU6,self).__init__()

		self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)

		self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
		#self.pool1 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool1 = MaxPool2D(2, strides = 2)

		self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool2 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool2 = MaxPool2D(2, strides = 2)

		self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool3 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool3 = MaxPool2D(2, strides = 2)

		self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool4 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool4 = MaxPool2D(2, strides = 2)

		self.rebnconv5 = REBNCONV(mid_ch,mid_ch,dirate=1)

		self.rebnconv6 = REBNCONV(mid_ch,mid_ch,dirate=2)

		self.rebnconv5d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv4d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)

	def call(self,x):

		hx = x

		hxin = self.rebnconvin(hx)

		hx1 = self.rebnconv1(hxin)
		hx = self.pool1(hx1)

		hx2 = self.rebnconv2(hx)
		hx = self.pool2(hx2)

		hx3 = self.rebnconv3(hx)
		hx = self.pool3(hx3)

		hx4 = self.rebnconv4(hx)
		hx = self.pool4(hx4)

		hx5 = self.rebnconv5(hx)

		hx6 = self.rebnconv6(hx5)


		#hx5d =  self.rebnconv5d(torch.cat((hx6,hx5),1))
		hx5d = self.rebnconv5d(tf.concat([hx6, hx5], -1))
		hx5dup = _upsample_like(hx5d,hx4)

		#hx4d = self.rebnconv4d(torch.cat((hx5dup,hx4),1))
		hx4d = self.rebnconv4d(tf.concat([hx5dup, hx4], -1))
		hx4dup = _upsample_like(hx4d,hx3)

		#hx3d = self.rebnconv3d(torch.cat((hx4dup,hx3),1))
		hx3d = self.rebnconv3d(tf.concat([hx4dup, hx3], -1))
		hx3dup = _upsample_like(hx3d,hx2)

		#hx2d = self.rebnconv2d(torch.cat((hx3dup,hx2),1))
		hx2d = self.rebnconv2d(tf.concat([hx3dup, hx2], -1))
		hx2dup = _upsample_like(hx2d,hx1)

		#hx1d = self.rebnconv1d(torch.cat((hx2dup,hx1),1))
		hx1d = self.rebnconv1d(tf.concat([hx2dup, hx1], -1))

		return hx1d + hxin

### RSU-5 ###
#class RSU5(nn.Module):#UNet05DRES(nn.Module):
class RSU5(tf.keras.Model):

	def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
		super(RSU5,self).__init__()

		self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)

		self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
		#self.pool1 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool1 = MaxPool2D(2, strides = 2)#, ceil_mode = True)


		self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool2 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool2 = MaxPool2D(2, strides = 2)#, ceil_mode = True)


		self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool3 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool3 = MaxPool2D(2, strides = 2)#, ceil_mode = True)


		self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=1)

		self.rebnconv5 = REBNCONV(mid_ch,mid_ch,dirate=2)

		self.rebnconv4d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)


	def call(self,x):
		hx = x
		hxin = self.rebnconvin(hx)

		hx1 = self.rebnconv1(hxin)
		hx = self.pool1(hx1)

		hx2 = self.rebnconv2(hx)
		hx = self.pool2(hx2)

		hx3 = self.rebnconv3(hx)
		hx = self.pool3(hx3)

		hx4 = self.rebnconv4(hx)

		hx5 = self.rebnconv5(hx4)

		#hx4d = self.rebnconv4d(torch.cat((hx5,hx4),1))
		hx4d = self.rebnconv4d(tf.concat([hx5, hx4], -1))
		hx4dup = _upsample_like(hx4d,hx3)

		#hx3d = self.rebnconv3d(torch.cat((hx4dup,hx3),1))
		hx3d = self.rebnconv3d(tf.concat([hx4dup, hx3], -1))
		hx3dup = _upsample_like(hx3d,hx2)

		#hx2d = self.rebnconv2d(torch.cat((hx3dup,hx2),1))
		hx2d = self.rebnconv2d(tf.concat([hx3dup, hx2], -1))
		hx2dup = _upsample_like(hx2d,hx1)

		#hx1d = self.rebnconv1d(torch.cat((hx2dup,hx1),1))
		hx1d = self.rebnconv1d(tf.concat([hx2dup, hx1], -1))

		return hx1d + hxin

### RSU-4 ###
#class RSU4(nn.Module):#UNet04DRES(nn.Module):
class RSU4(tf.keras.Model):

	def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
		super(RSU4,self).__init__()

		self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)

		self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
		#self.pool1 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool1 = MaxPool2D(2, strides = 2)

		self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=1)
		#self.pool2 = nn.MaxPool2d(2,stride=2)#,ceil_mode=True)
		self.pool2 = MaxPool2D(2, strides = 2)

		self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=1)

		self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=2)

		self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=1)
		self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)

	def call(self,x):

		hx = x

		hxin = self.rebnconvin(hx)

		hx1 = self.rebnconv1(hxin)
		hx = self.pool1(hx1)

		hx2 = self.rebnconv2(hx)
		hx = self.pool2(hx2)

		hx3 = self.rebnconv3(hx)

		hx4 = self.rebnconv4(hx3)

		#hx3d = self.rebnconv3d(torch.cat((hx4,hx3),1))
		hx3d = self.rebnconv3d(tf.concat([hx4, hx3], -1))
		hx3dup = _upsample_like(hx3d,hx2)

		#hx2d = self.rebnconv2d(torch.cat((hx3dup,hx2),1))
		hx2d = self.rebnconv2d(tf.concat([hx3dup, hx2], -1))
		hx2dup = _upsample_like(hx2d,hx1)

		#hx1d = self.rebnconv1d(torch.cat((hx2dup,hx1),1))
		hx1d = self.rebnconv1d(tf.concat([hx2dup, hx1], -1))

		return hx1d + hxin

### RSU-4F ###
#class RSU4F(nn.Module):#UNet04FRES(nn.Module):
class RSU4F(tf.keras.Model):

	def __init__(self, in_ch=3, mid_ch=12, out_ch=3):
		super(RSU4F,self).__init__()

		self.rebnconvin = REBNCONV(in_ch,out_ch,dirate=1)

		self.rebnconv1 = REBNCONV(out_ch,mid_ch,dirate=1)
		self.rebnconv2 = REBNCONV(mid_ch,mid_ch,dirate=2)
		self.rebnconv3 = REBNCONV(mid_ch,mid_ch,dirate=4)

		self.rebnconv4 = REBNCONV(mid_ch,mid_ch,dirate=8)

		self.rebnconv3d = REBNCONV(mid_ch*2,mid_ch,dirate=4)
		self.rebnconv2d = REBNCONV(mid_ch*2,mid_ch,dirate=2)
		self.rebnconv1d = REBNCONV(mid_ch*2,out_ch,dirate=1)

	def call(self,x):

		hx = x

		hxin = self.rebnconvin(hx)

		hx1 = self.rebnconv1(hxin)
		hx2 = self.rebnconv2(hx1)
		hx3 = self.rebnconv3(hx2)

		hx4 = self.rebnconv4(hx3)

		#hx3d = self.rebnconv3d(torch.cat((hx4,hx3),1))
		hx3d = self.rebnconv3d(tf.concat([hx4, hx3], -1))
		#hx2d = self.rebnconv2d(torch.cat((hx3d,hx2),1))
		hx2d = self.rebnconv2d(tf.concat([hx3d, hx2], -1))
		#hx1d = self.rebnconv1d(torch.cat((hx2d,hx1),1))
		hx1d = self.rebnconv1d(tf.concat([hx2d, hx1], -1))

		return hx1d + hxin


class Conv2D_P(tf.keras.layers.Layer):

	def __init__(self, filters, kernel_size, strides = 1, padding = 'valid', **kwargs):
		super(Conv2D_P, self).__init__(**kwargs)
		self.conv = tf.keras.layers.Conv2D(
			filters = filters, 
			kernel_size = kernel_size, 
			strides = strides, 
			padding = padding
			)

	def call(self, inputs):
		return self.conv(inputs)



class MaxPool2DP(tf.keras.layers.Layer):

	def __init__(self, pool_size = 2, strides = 2, padding = 'valid', **kwargs):
		super(MaxPool2DP, self).__init__(**kwargs)
		self.pool = tf.keras.layers.MaxPooling2D(
			pool_size = pool_size, 
			strides = strides, 
			padding = padding)

	def call(self, inputs):
		return self.pool(inputs)


##### U^2-Net ####
#class U2NET(nn.Module):
class U2NET(tf.keras.Model):

	def __init__(self,in_ch=3,out_ch=1):

		
		super(U2NET,self).__init__()

		self.loss_tracker = tf.keras.metrics.Mean(name="loss")
		self.mae_metric = tf.keras.metrics.Accuracy()#dice_coef#()

        
		self.loss_fn = tf.keras.losses.Dice()#bce_dice_loss#()

		self.stage1 = RSU7(in_ch,32,64)
		self.pool12 = MaxPool2D(2,strides=2)#)#,ceil_mode=True)

		self.stage2 = RSU6(64,32,128)
		self.pool23 = MaxPool2D(2,strides=2)#,ceil_mode=True)

		self.stage3 = RSU5(128,64,256)
		self.pool34 = MaxPool2D(2,strides=2)#,ceil_mode=True)

		self.stage4 = RSU4(256,128,512)
		self.pool45 = MaxPool2D(2,strides=2)#,ceil_mode=True)

		self.stage5 = RSU4F(512,256,512)
		self.pool56 = MaxPool2D(2,strides=2)#,ceil_mode=True)

		self.stage6 = RSU4F(512,256,512)

		# decoder
		self.stage5d = RSU4F(1024,256,512)
		self.stage4d = RSU4(1024,128,256)
		self.stage3d = RSU5(512,64,128)
		self.stage2d = RSU6(256,32,64)
		self.stage1d = RSU7(128,16,64)

		#self.side1 = nn.Conv2d(64,out_ch,3,padding=1)
		self.side1 = Conv2D(out_ch, 3, padding = 'same')
		#self.side1 = Conv2D_P(out_ch, 3, padding = 'same')

		# self.side2 = nn.Conv2d(64,out_ch,3,padding=1)
		# self.side3 = nn.Conv2d(128,out_ch,3,padding=1)
		# self.side4 = nn.Conv2d(256,out_ch,3,padding=1)
		# self.side5 = nn.Conv2d(512,out_ch,3,padding=1)
		# self.side6 = nn.Conv2d(512,out_ch,3,padding=1)
		self.side2 = Conv2D(out_ch, 3, padding = 'same')
		#self.side2 = Conv2D_P()
		self.side3 = Conv2D(out_ch, 3, padding = 'same')
		self.side4 = Conv2D(out_ch, 3, padding = 'same')
		self.side5 = Conv2D(out_ch, 3, padding = 'same')
		self.side6 = Conv2D(out_ch, 3, padding = 'same')

		#self.outconv = nn.Conv2d(6*out_ch,out_ch,1)
		self.outconv = Conv2D(out_ch, 1)

	def call(self,x):

		hx = x

		#stage 1
		hx1 = self.stage1(hx)
		hx = self.pool12(hx1)

		#stage 2
		hx2 = self.stage2(hx)
		hx = self.pool23(hx2)

		#stage 3
		hx3 = self.stage3(hx)
		hx = self.pool34(hx3)

		#stage 4
		hx4 = self.stage4(hx)
		hx = self.pool45(hx4)

		#stage 5
		hx5 = self.stage5(hx)
		hx = self.pool56(hx5)

		#stage 6
		hx6 = self.stage6(hx)
		hx6up = _upsample_like(hx6,hx5)

		#-------------------- decoder --------------------
		#hx5d = self.stage5d(torch.cat((hx6up,hx5),1))
		#hx5d = self.stage5d(tf.concat([hx6up, hx5], -1))
		hx5d = self.stage5d(tf.keras.layers.Concatenate(
    								axis=-1)([hx6up, hx5]))
		hx5dup = _upsample_like(hx5d,hx4)

		#hx4d = self.stage4d(torch.cat((hx5dup,hx4),1))
		#hx4d = self.stage4d(tf.concat([hx5dup, hx4], -1))
		hx4d = self.stage4d(tf.keras.layers.Concatenate(axis = -1)([hx5dup, hx4]))
		hx4dup = _upsample_like(hx4d,hx3)

		#hx3d = self.stage3d(torch.cat((hx4dup,hx3),1))
		#hx3d = self.stage3d(tf.concat([hx4dup, hx3], -1))
		hx3d = self.stage3d(tf.keras.layers.Concatenate(axis = -1)([hx4dup, hx3]))
		hx3dup = _upsample_like(hx3d,hx2)

		#hx2d = self.stage2d(torch.cat((hx3dup,hx2),1))
		#hx2d = self.stage2d(tf.concat([hx3dup, hx2], -1))
		hx2d = self.stage2d(tf.keras.layers.Concatenate(axis = -1)([hx3dup, hx2]))
		hx2dup = _upsample_like(hx2d,hx1)

		#hx1d = self.stage1d(torch.cat((hx2dup,hx1),1))
		#hx1d = self.stage1d(tf.concat([hx2dup, hx1], -1))
		hx1d = self.stage1d(tf.keras.layers.Concatenate(axis = -1)([hx2dup, hx1]))


		#side output
		d1 = self.side1(hx1d)

		d2 = self.side2(hx2d)
		d2 = _upsample_like(d2,d1)

		d3 = self.side3(hx3d)
		d3 = _upsample_like(d3,d1)

		d4 = self.side4(hx4d)
		d4 = _upsample_like(d4,d1)

		d5 = self.side5(hx5d)
		d5 = _upsample_like(d5,d1)

		d6 = self.side6(hx6)
		d6 = _upsample_like(d6,d1)

		#d0 = self.outconv(torch.cat((d1,d2,d3,d4,d5,d6),1))
		#d0 = self.outconv(tf.concat([d1, d2, d3, d4, d5, d6], -1))
		d0 = self.outconv(tf.keras.layers.Concatenate(axis = -1)([d1, d2, d3, d4, d5, d6]))

		#return F.sigmoid(d0), F.sigmoid(d1), F.sigmoid(d2), F.sigmoid(d3), F.sigmoid(d4), F.sigmoid(d5), F.sigmoid(d6)
		#return tf.math.sigmoid(d0), tf.math.sigmoid(d1), tf.math.sigmoid(d2), tf.math.sigmoid(d3), tf.math.sigmoid(d4), tf.math.sigmoid(d5), tf.math.sigmoid(d6)
		return d0, d1, d2, d3, d4, d5, d6
		#return tf.math.sigmoid(d0)

	def summary(self):

		x = Input(shape = (224, 224, 3))
		return tf.keras.Model(inputs = [x], outputs = self.call(x)).summary()

model = U2NET()

model.summary()

"""

    def train_step(self, data):

		x, y = data

		with tf.GradientTape() as tape:
			y_pred = self(x, training = True)

			loss0 = self.loss_fn(y, y_pred[0])
			loss1 = self.loss_fn(y, y_pred[1])
			loss2 = self.loss_fn(y, y_pred[2])
			loss3 = self.loss_fn(y, y_pred[3])
			loss4 = self.loss_fn(y, y_pred[4])
			loss5 = self.loss_fn(y, y_pred[5])
			loss6 = self.loss_fn(y, y_pred[6])
			loss = loss0 + loss1 + loss2 + loss3 + loss4 + loss5 + loss6

		trainable_vars = self.trainable_variables
		gradients = tape.gradient(loss, trainable_vars)

		## update vars
		self.optimizer.apply(gradients, trainable_vars)

		# compute own metrics
		self.loss_tracker.update_state(loss)
		#self.mae_metric.update_state(y, y_pred)

		return {
			"loss" : self.loss_tracker.result(),
			#"dice_coef" : self.mae_metric.result()
		}
    """

	# @property
	# def metrics(self):
	# 	return [self.loss_tracker, self.mae_metric]