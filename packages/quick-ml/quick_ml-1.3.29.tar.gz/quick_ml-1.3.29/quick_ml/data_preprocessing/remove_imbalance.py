## script to remove class imbalances
## Use this script if there is any imbalance among the classes else don't

## Direct Mode (yet to be written)
# def upsample():
#     pass

# def downsample():


#     pass


# def check_transformations(func):
#     acceptable = ['random_crop', 'flip_left_right', 'flip_up_down',
#     'random_hue', 'random_contrast', 'brightness', 
#     'random_saturation', 'zoom', 'rotation']
    
#     def inner(lst):

#         for i in lst:
#             if i not in acceptable:
#                 raise Exception(f"Error! Couldn't understand the transformation -> {i}. \n Check help(define_transformations) to know supported transformations.")

#         func(lst)

#     return inner



# @check_transformations
# def define_transformations(lst):
#     """
#     Supported Transformations -> 
#     'random_crop', 'flip_left_right', 'flip_up_down',
#     'random_hue', 'random_contrast', 'brightness', 
#     'random_saturation', 'zoom', 'rotation', 'mixup', 'cutmix'
#     """
#     global transformations_list

#     if len(lst) > 0:
#         transformations_list = lst
#     else:
#         raise Exception("Error! No transformation defined...")





### Interactive Mode
class Class_Balancer():
    def __init__(self, training_data_path, output_path = None, use_multiprocessing = True):
        self.balanced = False
        self.max_class_samples = None
        self.training_data_path = training_data_path
        self.classes = None
        self.output_path = output_path
        self.multiprocessing = use_multiprocessing

        if self.__check_imbalance(training_data_path):
            self.balanced = True

        if not self.balanced:  
            print("\nThe dataset is imbalanced. Please mention the set of transformations to be applied.")
            self.transformations_list = ['random_crop', 'flip_left_right', 'flip_up_down',
            'random_hue', 'random_contrast', 'random_brightness', 
            'random_saturation', 'random_zoom', 'random_rotation']#, 'mixup', 'cutmix']
            self.bool_transformations = ['flip_left_right', 'flip_up_down'] # mixup, cutmix
            #self.input_values = {'random_crop' : [crop_height, crop_width, channels], 'random_hue' : [0, 0.5), 'random_contrast' : [lower, upper], 'brightness' : [+max_delta], 'random_saturation' : [lower, upper], 'random_zoom' : [(height, width), fill_mode], 'random_rotation' : [rg, fill_mode]}
            #self.values_constraints = {'random_crop' : }
            self.input_value_parameters = {'random_crop' : ['crop_height', 'crop_width', 'channels'], 'random_hue' : ['max_delta'], 'random_contrast' : ['lower', 'upper'], 'random_brightness' : ['max_delta'], 'random_saturation' : ['lower', 'upper'], 'random_zoom' : ['height', 'width', 'fill_mode'], 'random_rotation' : ['rg', 'fill_mode']}
            self.user_transformations = {}
            self.user_selections = []

            for i in self.transformations_list:
                print('\n', i, " : ")
                response = input('Please enter in yes/no \n')
                self.user_transformations[i] = []
                self.user_transformations[i].append(True if response.lower()[0] == 'y' else False)
                if self.user_transformations[i][0] and (i not in self.bool_transformations):
                    for param in self.input_value_parameters[i]:
                        self.user_transformations[i].append(input(f"\nPlease enter the value for {i} parameter {param} : \n"))

            for item in self.user_transformations.items():
                if item[1][0]:
                    self.user_selections.append(item[0])

            if not any(list(self.user_transformations.values())):
                raise Exception("Please mention atleast one of the transformations to be applied...")


    @staticmethod
    def augment_class():
        pass

    def __check_imbalance(self, training_data_path):
        """
        Helps you to visualize the class imbalance by plotting the number of data points
        per class.
        """
        classes = os.listdir(training_data_path)
        #self.classes = classes
        class_dist = {}
        for class_ in classes:
            class_dist[class_] = len(glob(training_data_path + '/' + class_ + "/*.jpg"))
        
        self.classes = class_dist
        self.max_class_samples = max(list(class_dist.values()))
        #print(class_dist)
        plt.figure(figsize = (20,20))
        sns.barplot(x = list(class_dist.keys()), y = list(class_dist.values()))
        plt.xticks(rotation = 90)
        plt.show()
        keys = list(class_dist.keys())
        set_values = set()
        for k in keys:
            set_values.add(class_dist[k])
        return len(set_values) == 1

    def __transformations_func(self, img, transform):
        if transform == "random_crop":
            crop1 = int(self.user_transformations[transform][1])
            crop2 = int(self.user_transformations[transform][2])
            crop3 = int(self.user_transformations[transform][3])
            if img.shape[0] < crop1 :
                crop1 = img.shape[0]
            if img.shape[1] < crop2 : 
                crop2 = img.shape[1]
            
            return tf.image.random_crop(img, [crop1,crop2,crop3] )
            #return tf.image.random_crop(img, [int(self.user_transformations[transform][1]), int(self.user_transformations[transform][2]), int(self.user_transformations[transform][3])])
        elif transform == "random_zoom":
            zoom1 = float(self.user_transformations[transform][1])
            zoom2 = float(self.user_transformations[transform][2])

            if img.shape[0] > zoom1:
                zoom1 = img.shape[0]
            if img.shape[1] > zoom2:
                zoom2 = img.shape[1]
            
            return tf.keras.preprocessing.image.random_zoom(img, (zoom1, zoom2), fill_mode = self.user_transformations[transform][3])
            
            #return tf.keras.preprocessing.image.random_zoom(img, (float(self.user_transformations[transform][1]), float(self.user_transformations[transform][2])), fill_mode = self.user_transformations[transform][3])
        elif transform == "flip_left_right":
            return tf.image.flip_left_right(img)
        elif transform == "flip_up_down":
            return tf.image.flip_up_down(img)
        elif transform == "random_brightness":
            return tf.image.random_brightness(img, float(self.user_transformations[transform][1]))
        elif transform == "random_contrast":
            return tf.image.random_contrast(img, float(self.user_transformations[transform][1]), float(self.user_transformations[transform][2]))
        elif transform == "random_hue":
            return tf.image.random_hue(img, float(self.user_transformations[transform][1]))
        elif transform == "random_saturation":
            return tf.image.random_saturation(img, float(self.user_transformations[transform][1]), float(self.user_transformations[transform][2]))
        elif transform == "random_rotation":
            return tf.keras.preprocessing.image.random_rotation(img, float(self.user_transformations[transform][1]), fill_mode = self.user_transformations[transform][2], row_axis = 0, col_axis = 1, channel_axis = 2,)
      

    def __augment_multi_classes(self, class_lst, path, verbose):
        for class_ in class_lst:
            self.__augment_class_samples(class_, path, verbose)

    def __augment_class_samples(self, class_, path, verbose):
        diff = self.max_class_samples - len(glob( path + '/' + class_ + '/*.jpg'))
        augmentations_to_be_applied = np.random.choice(self.user_selections, replace = True, size = diff)
        indices = np.random.choice( range(len(glob( path + '/' + class_ + "/*.jpg"))),replace = True, size = diff)
        images_ = glob( path + '/' + class_ + '/*.jpg')
        
        #if verbose:
        print(f"Augmenting for class {class_}")
        for cnt, i in enumerate(tqdm(augmentations_to_be_applied)):
            img = cv2.imread(images_[indices[cnt]])
            #print(img.shape)
            temp_img = self.__transformations_func(img, i)
            temp_img = np.array(temp_img)
            #temp_img.save(os.path.join(path , images_[cnt] + '.jpg'))
            if verbose:
                print(images_[indices[cnt]], " | transform | ", i)
            save_name = images_[indices[cnt]].split('//')[-1].split('.')[0] + "_" + str(cnt) + '.jpg'
            cv2.imwrite( save_name, temp_img)
    


    def __augment_class_numbers(class_, path, num_samples):
        "Method under making..."
        pass 

    def balance_classes(self, inplace = True, output_directory = None, verbose = True):
        save_path = None
        if inplace is False:
            assert output_directory is not None
            save_path = output_directory
        else:
            save_path = self.training_data_path


        mode = int(input("\nPlease specify the mode of class balancing... -> \n1. Class Wise Balance \n2. Certain number of Samples Balance\n Please Choose between (1 or 2)\n"))
        if mode == 1:
          
            if self.multiprocessing:

                inp_classes = list(self.classes.keys())

                p1 = Process(target = self.__augment_multi_classes, args = (inp_classes[:len(inp_classes)//4], save_path,verbose))
                p2 = Process(target = self.__augment_multi_classes, args = (inp_classes[len(inp_classes)//4 : 2 * (len(inp_classes)//4)], save_path, verbose))
                p3 = Process(target = self.__augment_multi_classes, args = (inp_classes[2 * (len(inp_classes)//4) : 3 * (len(inp_classes) // 4)], save_path, verbose))
                p4 = Process(target = self.__augment_multi_classes, args = (inp_classes[3 * (len(inp_classes) // 4) : ], save_path, verbose))

                p1.start()
                p2.start()
                p3.start()
                p4.start()

                p1.join()
                p2.join()
                p3.join()
                p4.join()

            else:
                for class_ in list(self.classes.keys()):
                    self.__augment_class_samples(class_, save_path, verbose)

          
            print("Data Balancing complete...")        

        else:
            num_samples = int(input("\nPlease enter the number of samples (> max_samples in any class)\n"))
            assert num_samples > self.max_class_samples

            for class_ in list(self.classes.keys()):
                self.__augment_class_numbers(class_, save_path, num_samples)
            print("Data balancing complete...")
        self.balanced = True


    def csv_to_folder(self):
        print("Method under making...")
        pass

    def make_tfrecords(self):
        print("Method under making...")
        if self.balanced:
            pass
        else:
            raise Exception("Dataset path not yet balanced. Please balance the dataset by invoking balance_classes method of the class instance.")



if __name__ != "__main__":
    import tensorflow as tf 
    import os
    import seaborn as sns 
    import matplotlib.pyplot as plt
    import numpy as np
    import cv2
    from tqdm import tqdm
    from PIL import Image
    from glob import glob
    from multiprocessing import Process 
     
    sns.set_style('darkgrid')
    if tf.__version__ != '2.4.0':
        raise Exception("Tensorflow version mismatch!")

    global class_dist

