import glob
import shutil

class ImageMixer(object):
    def mixe(self, folder_src, folder_dst):
        for file in glob.glob(folder_src, recursive=True):
            shutil.copy(file, folder_dst)




