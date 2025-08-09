from typing import Optional

from pydantic import BaseModel

from deeploy.models.reference_json import (
    BlobReference,
    DockerReference,
    TransformerReference,
)


class CreateTransformerReference(BaseModel):
    """Class that contains the options for creating a reference.json for a transformer"""

    docker: Optional[DockerReference] = None
    """DockerReference: docker configuration object of the transformer"""
    blob: Optional[BlobReference] = None
    """BlobReference: blob configuration object of the transformer"""

    def get_reference(self) -> TransformerReference:
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
        else:
            raise ValueError("Please provide a valid option")

        return reference
