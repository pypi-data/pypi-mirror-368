from typing import Optional

from pydantic import BaseModel

from deeploy.models.reference_json import (
    AzureMLReference,
    BlobReference,
    DatabricksReference,
    DockerReference,
    MLFlowReference,
    ModelReference,
)


class CreateModelReference(BaseModel):
    """Class that contains the options for creating a reference.json for a model"""

    docker: Optional[DockerReference] = None
    """DockerReference: docker configuration object of the model"""
    blob: Optional[BlobReference] = None
    """BlobReference: blob configuration object of the model"""
    mlflow: Optional[MLFlowReference] = None
    """MLFlowReference: mlflow configuration object of the model"""
    azure_ml: Optional[AzureMLReference] = None
    """AzureMLReference: azure machine learning configuration object of the model"""
    databricks: Optional[DatabricksReference] = None
    """DatabricksReference: databricks unity catalog configuration object of the model"""

    def get_reference(self) -> ModelReference:
        if self.docker:
            reference = {
                "docker": {
                    "image": self.docker.image,
                    "uri": self.docker.uri,
                    "port": self.docker.port,
                }
            }
        elif self.blob:
            reference = {
                "blob": {
                    "url": self.blob.url,
                    "region": self.blob.region,
                }
            }
        elif self.mlflow:
            reference = {
                "mlflow": {
                    "model": self.mlflow.model,
                    "version": self.mlflow.version,
                    "stage": self.mlflow.stage,
                    "alias": self.mlflow.alias,
                }
            }

            if self.mlflow.blob and self.mlflow.blob.region:
                reference["mlflow"]["blob"] = {"region": self.mlflow.blob.region}
        elif self.azure_ml:
            reference = {
                "azureML": {
                    "image": self.azure_ml.image,
                    "uri": self.azure_ml.uri,
                    "port": self.azure_ml.port,
                    "readinessPath": self.azure_ml.readiness_path,
                    "livenessPath": self.azure_ml.liveness_path,
                    "model": self.azure_ml.model,
                    "version": self.azure_ml.version,
                }
            }
        elif self.databricks:
            reference = {
                "databricks": {
                    "model": self.databricks.model,
                    "version": self.databricks.version,
                    "alias": self.databricks.alias,
                }
            }
        else:
            raise ValueError("Please provide a valid option")

        return reference
