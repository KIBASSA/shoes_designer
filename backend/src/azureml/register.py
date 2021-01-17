
import sys
sys.path.append("../pix2pixs")
import torch
from classes import UNet
from azureml.core import Workspace,Experiment
from deployer import WebServiceDeployer
from azureml.core import Model


if __name__ == "__main__":

    ws = Workspace.get(name="ShoesDesigner",
               subscription_id='e112014e-a856-4c71-8fc1-4836d72b7c4c',
               resource_group='ShoesDesigner')

    model_name = os.path.join(model_folder, "pix2pix_black_briant_high_resolution7600.pth")

    Model.register(workspace=ws,
                    model_path = model_name,
                    model_name = "SHOES_DESIGNER",
                    tags={'Register context':'Pipeline'})

    deployer = WebServiceDeployer(ws)
    deployer.deploy_local()
    #deployer.deploy()
