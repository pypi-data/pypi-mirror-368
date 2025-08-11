from glob import glob 
import tensorflow as tf
from matplotlib import pyplot as plt 

class DataPipeMaker:
    
    def __init__(self, img_path, mask_path = None):
        
        self._img_path = img_path
        self._mask_path = mask_path
        
        self._images = glob(self._img_path)
        self._dataset_size = len(self._images)
        if self._mask_path != None:
            self._masks = glob(self._mask_path)
            self._masks.sort()
            self.mask_ds = tf.data.Dataset.list_files(self._masks, shuffle = False)
            self.mask_ds = self.mask_ds.map(self._parse_mask)
        
        self._images.sort()
        
        self.image_ds = tf.data.Dataset.list_files(self._images, shuffle = False)
        self.image_ds = self.image_ds.map(self._parse_image)
                
    def _parse_image(self, filename):
        
        image = tf.io.read_file(filename)
        image = tf.io.decode_jpeg(image)
        #image = tf.io.decode_image(image, channels = 3)
        image = tf.image.convert_image_dtype(image, tf.uint8)
        image = tf.image.resize(image, (512, 512))
        image = image/255.0
        
        return image
    
    def _parse_mask(self, filename):
        
        mask = tf.io.read_file(filename)
        mask = tf.io.decode_png(mask)
        #mask = tf.io.decode_image(mask, channels = 1)
        mask = tf.image.convert_image_dtype(mask, tf.uint8)
        mask = tf.image.resize(mask, (512, 512))
        
        mask = mask /255.0
        
        return mask
    
    def get_training_dataset(self, batch_size = 32, val_split = 0):
        
        #training_dataset = tf.data.Dataset.zip((self.image_ds, self.mask_ds))
        #training_dataset = training_dataset.batch(batch_size, drop_remainder = True)
        dataset = tf.data.Dataset.zip((self.image_ds, self.mask_ds))
        
        
        #dataset = dataset.batch(batch_size, drop_remainder = True)
        
        #training_dataset = training_dataset.cache()
        #training_dataset = training_dataset.shuffle(1)
        #training_dataset = training_dataset.prefetch(1)
        #training_dataset = training_dataset.repeat()
        
        #training_dataset = training_dataset.prefetch(tf.data.AUTOTUNE)
        #dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        if val_split:
            val_size = int(self._dataset_size * val_split)
            print(f"Making a split of : Val -> {val_size} & Training -> {self._dataset_size - val_size}")
            validation_dataset = dataset.take(int(self._dataset_size * val_split))
            validation_dataset = validation_dataset.batch(1, drop_remainder = True)
            validation_dataset = validation_dataset.prefetch(tf.data.AUTOTUNE)
            
            training_dataset = dataset.skip(int(self._dataset_size * val_split))
            training_dataset = training_dataset.batch(batch_size, drop_remainder = True)
            training_dataset = training_dataset.prefetch(tf.data.AUTOTUNE)
            return validation_dataset, training_dataset
        else:
            dataset = dataset.batch(batch_size, drop_remainder = True)
            dataset = dataset.prefetch(tf.data.AUTOTUNE)
            return dataset
       
    def apply_mask_threshold(self, ds, threshold = 0.5):
        def mask_threshold(img, mask):
            mask = tf.where(mask >= threshold, 1.0, 0.0)
            return img, mask 
        ds = ds.map(mask_threshold)
        return ds
        
    def get_test_dataset(self, img_path, batch_size = 128):
        
        test_imgs = glob(img_path)
        test_imgs.sort()
        
        testing_dataset = tf.data.Dataset.list_files(test_imgs, shuffle = False)
        testing_dataset = testing_dataset.map(self._parse_image)
        testing_dataset = testing_dataset.batch(batch_size)
        return testing_dataset

    def get_validation_dataset(self, img_path, mask_path, batch_size = 32):
        images = glob(img_path)
        images.sort()
        masks = glob(mask_path)
        masks.sort()
        
        image_ds = tf.data.Dataset.list_files(images, shuffle = False)
        mask_ds = tf.data.Dataset.list_files(masks, shuffle = False)
        
        image_ds = image_ds.map(self._parse_image)
        mask_ds = mask_ds.map(self._parse_mask)
        
        val_dataset = zip(image_ds, mask_ds)
        val_dataset = val_dataset.batch(batch_size, drop_remainder = True)
        val_dataset = val_dataset.prefetch(tf.data.AUTOTUNE)
        return val_dataset
        
    def visualize_dataset(self, ds):

        plt.figure(figsize = (30, 10))
        count = 1
        for i,m in ds.take(5):
            plt.subplot(2, 5, count)
            plt.imshow(i[0].numpy())

            plt.subplot(2, 5, count + 5)
            plt.imshow(m[0].numpy())
            count += 1
