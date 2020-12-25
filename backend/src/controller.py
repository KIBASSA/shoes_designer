import os
import cv2
from edge_detector import EdgeTransformer
import glob
import shutil
class Controller(object):
    #EdgeTransformer
    def process(self, folder_src, folder_dest, edge_transformer):

        if not os.path.isdir(folder_dest):
            os.makedirs(folder_dest)
        
        for file in glob.glob(folder_src + '/**/*.jpg', recursive=True):
            filename = os.path.basename(file)
            filename_arr = os.path.splitext(filename)
            print("process for : ",filename)
            filename_dir = os.path.join(folder_dest, filename_arr[0])
            if not os.path.isdir(filename_dir):
                os.makedirs(filename_dir)
            #copy the first element of the pair

            filename_real = filename_arr[0] + "_real_" + filename_arr[1] 
            filename_real = os.path.join(filename_dir, filename_real)
            shutil.copy(file, filename_real)    
            canny, hed = edge_transformer.transform(file)
            
            filename_hed = filename_arr[0] + "_hed_" + filename_arr[1]
            cv2.imwrite(os.path.join(filename_dir, filename_hed), hed)

            filename_canny = filename_arr[0] + "_canny_" + filename_arr[1]
            cv2.imwrite(os.path.join(filename_dir, filename_canny), canny)
        
        #begin GANs traning


if __name__ == "__main__":
    folder_src = "../data/zap50k/"
    folder_dest = "../data/zap50k_pair"
    edge_models_path = "../models/hed_model"

    edge_transformer = EdgeTransformer(edge_models_path)
    controller = Controller()
    controller.process(folder_src, folder_dest, edge_transformer)

        
        
        

