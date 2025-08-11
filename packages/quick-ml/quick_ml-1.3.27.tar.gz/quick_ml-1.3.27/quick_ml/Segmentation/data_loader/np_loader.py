from glob import glob
from tqdm import tqdm 
import cv2

class NumpyDataLoader(FileLoader):
    def __init__(self, img_dir, mask_dir):
        super().__init__(img_dir, mask_dir)

    def __read_img(self, img, img_size):
        img = cv2.imread(img)
        img = cv2.resize(img, img_size)
        img = img/255.0
        img = img.astype(np.float32)
        return img

    def __read_mask(self, mask, img_size):
        mask = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)
        mask = cv2.resize(mask, img_size)
        mask = np.expand_dims(mask, axis =2)
        mask = mask/255.0
        mask = mask.astype(dtype = np.float32)
        
        return mask

    def load_data_on_ram(self, fraction = 1.0):

        img_data = []
        till_ = len(self.imgs) * fraction

        for img in tqdm(self.imgs[:till_]):
            img = cv2.imread(img)
            img = img/255.0
            img = img.astype(np.float32)
            img_data.append(img)

        mask_data = []

        for mask in tqdm(self.masks * fraction):
            mask = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)
            mask = np.expand_dims(mask, axis = 2)
            mask = mask/255.0
            mask = mask.astype(np.uint8)
            mask_data.append(mask)

        return np.array(img_data), np.array(mask_data)

    def merge_data(self, img_data, mask_data):
        training_data = []
        for img, mask in zip(img_data, mask_data):
            training_data.append(img_data, mask_data)

        return np.array(training_data)

    def __augment(self, image, mask):
        if self.horizontal_flip:
            if np.random.choice([0,1]):
                image = cv2.flip(image, 1)
                mask = cv2.flip(mask, 1)
                if len(mask.shape) == 2:
                    mask = np.expand_dims(mask, axis = 2)
             
        if self.vertical_flip:
            if np.random.choice([0, 1]):
                image = cv2.flip(image, 0)
                mask = cv2.flip(mask, 0)

                if len(mask.shape) == 2:
                    mask = np.expand_dims(mask, axis = 2)
                
        return image, mask
        
    def define_augmentations(self, horizontal_flip = False, vertical_flip = False):
        self.horizontal_flip = horizontal_flip
        self.vertical_flip = vertical_flip

    def training_data_generator(self,img_size = (512, 512), batch_size = 8, shuffle = False,
                               validation = False, training_subset = True, validation_split = 0.0
                               ):

        if shuffle:
            self.train_imgs = zip(self.imgs, self.masks)
            np.random.shuffle(self.train_imgs)

            self.imgs.clear()
            self.masks.clear()
            
            for i,m in self.train_imgs:
                self.imgs.append(i)
                self.masks.append(m)

        while True:

            if validation:
                if !training_subset:
                    val_imgs = int(len(self.imgs) * validation_split)
                    while True:
                        for i in range(len(self.imgs) - val_imgs, len(self.imgs), batch_size):
                            if i + batch_size <= len(self.imgs):
                                x_batch = []
                                y_batch = []
    
                                for j in range(i, i + batch_size):
                                    im = self.__read_img(self.imgs[j], img_size)
                                    msk = self.__read_mask(self.masks[j], img_size)
    
                                    im, msk = self.__augment(im, msk)
                                    x_batch.append(im)
                                    y_batch.append(msk)
                            else:
                                continue
                        yield np.array(x_batch), np.array(y_batch)
                else:
                    train_imgs = int(len(self.imgs) * (1 - validation_split))
                    while True:
                        for i in range(0, train_imgs, batch_size):
                            if i + batch_size <= len(self.imgs):
                                x_batch = []
                                y_batch = []

                                for j in range(i , i + batch_size):
                                    im = self.__read_img(self.imgs[j], img_size)
                                    msk = self.__read_mask(self.masks[j], img_size)

                                    im, msk = self.__augment(im, msk)
                                    x_batch.append(im)
                                    y_batch.append(msk)
                            else:
                                continue
                        yield np.array(x_batch), np.array(y_batch)


            else:
                ## traverse for 1 epoch
                for i in range(0, len(self.imgs), batch_size):
                    if i + batch_size <= len(self.imgs):
        
                        x_batch = []
                        y_batch = []
    
                        for j in range(i, i + batch_size):
    
                            im = self.__read_img(self.imgs[j], img_size)
                            msk = self.__read_mask(self.masks[j], img_size)
                            
                            im, msk = self.__augment(im, msk)
                            x_batch.append(im)
                            y_batch.append(msk)
    
                    else:
                        continue
                    
                    yield np.array(x_batch), np.array(y_batch)
                
                