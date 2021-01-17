
import glob
import torch
from torch import nn
from tqdm.auto import tqdm
from torchvision import transforms
from torchvision.utils import make_grid
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from PIL import Image
torch.manual_seed(0)
from torch.utils.data import Dataset
from classes import ContractingBlock, ExpandingBlock, FeatureMapBlock, UNet, Discriminator, show_tensor_images
import numpy as np
import torch.nn.functional as F

# New parameters
adv_criterion = nn.BCEWithLogitsLoss() 
recon_criterion = nn.L1Loss() 
lambda_recon = 200

n_epochs = 40
input_dim = 1 # for edge image (1, 512, 512 )
real_dim = 3
display_step = 200
batch_size = 4
lr = 0.0002
target_shape = 512
device = 'cpu'
#device = 'cuda'
#if not torch.cuda.is_available():
#    device = "cpu"


class CropImage(object):
    def __call__(self, image):
        _,w, h = image.size()
        diff = (w - h)//2
        image = image[:,diff: h + diff,:]
        return image

#credit source : https://discuss.pytorch.org/t/how-make-customised-dataset-for-semantic-segmentation/30881/5
class CustomDataset(Dataset):
    def __init__(self, image_paths, target_paths, train=True):   # initial logic happens like transform
        self.image_paths = image_paths
        self.target_paths = target_paths

        self.transforms = transforms.Compose([transforms.ToTensor(),CropImage(), transforms.Resize((target_shape,target_shape))])

        #self.transforms = transforms.ToTensor()
        #self.transforms = transforms.Scale((256,256))

    def __getitem__(self, index):
        image = Image.open(self.image_paths[index])
        
        mask = Image.open(self.target_paths[index])
        
        t_image = self.transforms(image)
        mask = self.transforms(mask)
        return t_image, mask

    def __len__(self):  # return count of sample we have

        return len(self.image_paths)


#device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

"""You will then pre-process the images of the dataset to make sure they're all the same size and that the size change due to U-Net layers is accounted for.
"""

transform = transforms.Compose([
    transforms.ToTensor(),
])

import torchvision
#dataset = torchvision.datasets.ImageFolder("maps", transform=transform)

"""Next, you can initialize your generator (U-Net) and discriminator, as well as their optimizers. Finally, you will also load your pre-trained model.
"""

gen = UNet(input_dim, real_dim).to(device)
gen_opt = torch.optim.Adam(gen.parameters(), lr=lr)
disc = Discriminator(input_dim + real_dim).to(device)
disc_opt = torch.optim.Adam(disc.parameters(), lr=lr)

def weights_init(m):
    if isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
        torch.nn.init.normal_(m.weight, 0.0, 0.02)
    if isinstance(m, nn.BatchNorm2d):
        torch.nn.init.normal_(m.weight, 0.0, 0.02)
        torch.nn.init.constant_(m.bias, 0)

# Feel free to change pretrained to False if you're training the model from scratch
pretrained = True
if pretrained:
    loaded_state = torch.load("pix2pix_black_briant_high_resolution7600.pth")
    gen.load_state_dict(loaded_state["gen"])
    gen_opt.load_state_dict(loaded_state["gen_opt"])
    disc.load_state_dict(loaded_state["disc"])
    disc_opt.load_state_dict(loaded_state["disc_opt"])
else:
    gen = gen.apply(weights_init)
    disc = disc.apply(weights_init)

"""While there are some changes to the U-Net architecture for Pix2Pix, the most important distinguishing feature of Pix2Pix is its adversarial loss. You will be implementing that here!
"""
# UNQ_C2 (UNIQUE CELL IDENTIFIER, DO NOT EDIT)
# GRADED CLASS: get_gen_loss
def get_gen_loss(gen, disc, real, condition, adv_criterion, recon_criterion, lambda_recon):
    '''
    Return the loss of the generator given inputs.
    Parameters:
        gen: the generator; takes the condition and returns potential images
        disc: the discriminator; takes images and the condition and
          returns real/fake prediction matrices
        real: the real images (e.g. maps) to be used to evaluate the reconstruction
        condition: the source images (e.g. satellite imagery) which are used to produce the real images
        adv_criterion: the adversarial loss function; takes the discriminator 
                  predictions and the true labels and returns a adversarial 
                  loss (which you aim to minimize)
        recon_criterion: the reconstruction loss function; takes the generator 
                    outputs and the real images and returns a reconstructuion 
                    loss (which you aim to minimize)
        lambda_recon: the degree to which the reconstruction loss should be weighted in the sum
    '''
    # Steps: 1) Generate the fake images, based on the conditions.
    #        2) Evaluate the fake images and the condition with the discriminator.
    #        3) Calculate the adversarial and reconstruction losses.
    #        4) Add the two losses, weighting the reconstruction loss appropriately.
    #### START CODE HERE ####
    fake_image = gen(condition)
    disc_fake = disc(fake_image, condition)
    gen_adv_loss = adv_criterion(disc_fake, torch.ones_like(disc_fake))
    gen_recon_loss = recon_criterion(real, fake_image)
    gen_loss = gen_adv_loss + lambda_recon * gen_recon_loss
    #### END CODE HERE ####
    return gen_loss


"""Pix2Pix Training
Finally, you can train the model and see some of your maps!
"""
from skimage import color
import numpy as np

def train(model_name, dir, save_model=True):
    mean_generator_loss = 0
    mean_discriminator_loss = 0
    print("save_model :", save_model)
    #dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # get all the image and mask path and number of images
    #100627.255_hed_
    folder_data = glob.glob(dir + "/**/*_real_.jpg")
    folder_mask = glob.glob(dir + "/**/*_hed_.jpg")
    # split these path using a certain percentage
    len_data = len(folder_data)
    print(len_data)
    train_size = 0.8

    train_image_paths = folder_data[:int(len_data * train_size)]
    test_image_paths = folder_data[int(len_data * train_size):]

    train_mask_paths = folder_mask[:int(len_data * train_size)]
    test_mask_paths = folder_mask[int(len_data * train_size):]

    train_dataset = CustomDataset(train_image_paths, train_mask_paths, train=True)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=4, shuffle=True)

    test_dataset = CustomDataset(test_image_paths, test_mask_paths, train=False)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=4, shuffle=False)

    #print("iciiiiiiiiii")
    #dataiter = iter(train_loader)
    #_images, _labels = dataiter.next()
    #raise Exception("aie aie aie")

    cur_step = 0
    
    """"""
    for epoch in range(n_epochs):
        # Dataloader returns the batches
        for image, mask in tqdm(train_loader):

            #image_width = image.shape[3]
            #condition = image[:, :, :, :image_width // 2]
            #condition = nn.functional.interpolate(condition, size=target_shape)
            #real = image[:, :, :, image_width // 2:]
            #real = nn.functional.interpolate(real, size=target_shape)
            #cur_batch_size = len(condition)
            #condition = condition.to(device)
            #real = real.to(device)

            condition = mask # c'est sont les images en mode dessin 
            condition = nn.functional.interpolate(condition, size=target_shape)
            condition = condition.to(device)
            real = image # c'est des images réel
            real = nn.functional.interpolate(real, size=target_shape)
            real = real.to(device)


            ### Update discriminator ###
            disc_opt.zero_grad() # Zero out the gradient before backpropagation
            with torch.no_grad():
                fake = gen(condition)
            disc_fake_hat = disc(fake.detach(), condition) # Detach generator
            disc_fake_loss = adv_criterion(disc_fake_hat, torch.zeros_like(disc_fake_hat))
            disc_real_hat = disc(real, condition)
            disc_real_loss = adv_criterion(disc_real_hat, torch.ones_like(disc_real_hat))
            disc_loss = (disc_fake_loss + disc_real_loss) / 2
            disc_loss.backward(retain_graph=True) # Update gradients
            disc_opt.step() # Update optimizer

            ### Update generator ###
            gen_opt.zero_grad()
            gen_loss = get_gen_loss(gen, disc, real, condition, adv_criterion, recon_criterion, lambda_recon)
            gen_loss.backward() # Update gradients
            gen_opt.step() # Update optimizer

            # Keep track of the average discriminator loss
            mean_discriminator_loss += disc_loss.item() / display_step
            # Keep track of the average generator loss
            mean_generator_loss += gen_loss.item() / display_step

            ### Visualization code ###
            if cur_step % display_step == 0:
                if cur_step > 0:
                    print(f"Epoch {epoch}: Step {cur_step}: Generator (U-Net) loss: {mean_generator_loss}, Discriminator loss: {mean_discriminator_loss}")
                else:
                    print("Pretrained initial state")
                show_tensor_images(condition, size=(input_dim, target_shape, target_shape))
                show_tensor_images(real, size=(real_dim, target_shape, target_shape))
                show_tensor_images(fake, size=(real_dim, target_shape, target_shape))
                mean_generator_loss = 0
                mean_discriminator_loss = 0
                # You can change save_model to True if you'd like to save the model
                if save_model:
                    torch.save({'gen': gen.state_dict(),
                        'gen_opt': gen_opt.state_dict(),
                        'disc': disc.state_dict(),
                        'disc_opt': disc_opt.state_dict()
                    }, f"{model_name}{cur_step}.pth")
            cur_step += 1
#train()


