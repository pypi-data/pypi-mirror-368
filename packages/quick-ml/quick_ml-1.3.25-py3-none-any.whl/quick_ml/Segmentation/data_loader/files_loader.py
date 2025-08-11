from glob import glob 

class FileLoader:

    def __init__(self, img_dir, mask_dir):

        self.imgs = None
        self.masks = None

        if img_dir.endswith('/*'):
            self.imgs = glob(img_dir)
        elif img_dir.endswith('/'):
            self.imgs = glob(img_dir + '*')
        else:
            self.imgs = glob(img_dir + '/*')


        if mask_dir.endswith('/*'):
            self.masks = glob(mask_dir)
        elif mask_dir.endswith('/'):
            self.masks = glob(mask_dir + "*")
        else:
            self.masks = glob(mask_dir + "/*")

        self.imgs.sort()
        self.masks.sort()


    def read_img(self, img, img_size):
        img = cv2.imread(img)
        img = cv2.resize(img, img_size)
        img = img/255.0
        img = img.astype(np.float32)
        return img

    def read_mask(self, mask, img_size):
        mask = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)
        mask = cv2.resize(mask, img_size)
        mask = np.expand_dims(mask, axis =2)
        mask = mask/255.0
        mask = mask.astype(dtype = np.float32)
        
        return mask