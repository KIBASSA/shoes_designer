from azureml.core.webservice import AciWebservice, AksWebservice, LocalWebservice
from azureml.core import Environment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.model import InferenceConfig, Model
from azureml.exceptions import WebserviceException
from azureml.core.compute import AksCompute
import json
from aiopslibs import __version__

class WebServiceDeployer:
    def __init__(self, ws):
        self.ws = ws

        self.DEPLOY_SERVICE_NAME = "SHOES_DESIGNER_SERVICE"
        self.MODEL_NAME = "SHOES_DESIGNER_MODEL"
        
    def deploy(self):

        try:
            AciWebservice(self.ws, self.DEPLOY_SERVICE_NAME).delete()
            print("webservice deleted")
        except WebserviceException:
            pass

        conda_dep = CondaDependencies()                                        
        conda_dep.add_pip_package("joblib")
        conda_dep.add_pip_package("torch")
        conda_dep.add_pip_package("torchvision")
        conda_dep.add_pip_package("azureml-sdk")
        conda_dep.add_pip_package("azure-storage-blob")
        conda_dep.add_pip_package("PyYAML")
        conda_dep.add_pip_package("scikit-learn")
        conda_dep.add_pip_package("matplotlib")
        conda_dep.add_pip_package("opencensus-ext-azure")
        
        
        shoes_designer_env_file = "shoes_designer_env.yml"
        with open(shoes_designer_env_file,"w") as f:
            f.write(conda_dep.serialize_to_string())

        shoes_designer_env = Environment.from_conda_specification(name="shoes_designer_env", file_path=shoes_designer_env_file)

        inference_config = InferenceConfig(entry_script="score.py", environment=shoes_designer_env)

        aciconfig = AciWebservice.deploy_configuration(cpu_cores=1, 
                                                    memory_gb=2, 
                                                    tags={"method" : "torch"}, 
                                                    description='Generate shoes with torch')

        model = self.ws.models[self.MODEL_NAME]

        service = Model.deploy(workspace=self.ws, 
                            name=self.DEPLOY_SERVICE_NAME, 
                            models=[model], 
                            inference_config=inference_config, 
                            deployment_config=aciconfig,
                            overwrite=True)
        service.wait_for_deployment(show_output=True)

        print("success deployement")        

        return service
    
    def deploy_local(self):

        try:
            LocalWebservice(self.ws, "test").delete()
            print("webservice deleted")
        except WebserviceException:
            pass

        shoes_designer_env = Environment('shoes_designer_env')
        shoes_designer_env.python.conda_dependencies.add_pip_package("joblib")
        shoes_designer_env.python.conda_dependencies.add_pip_package("torch")
        shoes_designer_env.python.conda_dependencies.add_pip_package("torchvision")
        shoes_designer_env.python.conda_dependencies.add_pip_package("azure-storage-blob")
        shoes_designer_env.python.conda_dependencies.add_pip_package("azureml-sdk")
        shoes_designer_env.python.conda_dependencies.add_pip_package("PyYAML")
        shoes_designer_env.python.conda_dependencies.add_pip_package("scikit-learn")
        shoes_designer_env.python.conda_dependencies.add_pip_package("matplotlib")
        conda_dep.add_pip_package("opencensus-ext-azure")

        # explicitly set base_image to None when setting base_dockerfile
        shoes_designer_env.docker.base_image = None
        shoes_designer_env.docker.base_dockerfile = "FROM mcr.microsoft.com/azureml/base:intelmpi2018.3-ubuntu16.04\nRUN echo \"this is test\""
        shoes_designer_env.inferencing_stack_version = "latest"

        inference_config = InferenceConfig(entry_script="score.py",environment=shoes_designer_env)
        
        model = self.ws.models[self.MODEL_NAME]

        # This is optional, if not provided Docker will choose a random unused port.
        deployment_config = LocalWebservice.deploy_configuration(port=6789)

        local_service = Model.deploy(self.ws, "test", [model], inference_config, deployment_config)

        local_service.wait_for_deployment()
        print("success deployement")
        
        return local_service