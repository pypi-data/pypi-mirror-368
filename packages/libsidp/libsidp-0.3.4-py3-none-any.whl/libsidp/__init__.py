import io
import requests
import os
import random
import json
import zipfile
import base64


from time import sleep
from typing import Dict, Optional, Union
from pydantic import BaseModel, Field


def random_char(y: int) -> str:
    """
    Generates a random str of "y" chars
    """
    return "".join(chr(random.randrange(97, 97 + 26)) for x in range(y))


class SidpHemeraOptions(BaseModel):
    ai_gen_assistant: bool = Field(
        default=False, description="Enable AI generation assistant"
    )
    install_mssql: bool = Field(
        default=False, description="Install Microsoft SQL Server"
    )
    install_oracle: bool = Field(default=False, description="Install Oracle Database")
    install_mariadb: bool = Field(default=False, description="Install MariaDB")
    install_psql: bool = Field(default=False, description="Install PostgreSQL")
    install_sftp: bool = Field(default=False, description="Install SFTP")
    trusted_ips: str = Field(default="0.0.0.0/0", description="Whitelisted IP adresses")

    def to_dict(self) -> Dict[str, bool]:
        """
        Convert the model to a dictionary representation.

        :return: Dictionary of Hemera options
        """
        return {
            "ai_gen_assistant": self.ai_gen_assistant,
            "install_mssql": self.install_mssql,
            "install_oracle": self.install_oracle,
            "install_mariadb": self.install_mariadb,
            "install_psql": self.install_psql,
            "install_sftp": self.install_sftp,
            "trusted_ips": self.trusted_ips,
        }


class SidpExtraOptions(BaseModel):
    provision: bool = Field(
        default=False, description="Provision cluster with dummy data"
    )
    provisioning_job: str = Field(
        default="init_platform", description="Select provisioning data set"
    )
    no_hemera_deploy: bool = Field(
        default=False, description="Whether to install Hemera or not"
    )

    def to_dict(self) -> Dict[str, bool]:
        """
        Convert the model to a dictionary representation.

        :return: Dictionary of Extra options
        """
        return {
            "provision": self.provision,
            "no_hemera_deploy": self.no_hemera_deploy,
            "provisioning_job": self.provisioning_job,
        }


class SidpConfigurator(BaseModel):
    clusterName: str = Field(default="", description="Name of the cluster")
    kubeVersion: Optional[str] = Field(default=None, description="Kubernetes version")
    sourceBranch: Optional[str] = Field(default=None, description="Source branch")
    clusterOwner: Optional[str] = Field(
        default=None, description="Owner of the resource"
    )
    hemeraOptions: SidpHemeraOptions = Field(
        default_factory=SidpHemeraOptions, description="Hemera-specific options"
    )
    extraOptions: SidpExtraOptions = Field(
        default_factory=SidpExtraOptions, description="Additional configuration options"
    )

    def validate(self) -> bool:
        """
        Validate the configurator.

        :return: True if valid, False otherwise
        """
        return bool(self.clusterName)


class SIDPClient:
    def __init__(self, base_url: str, config: SidpConfigurator):
        """
        Initialize the SIDP API Client

        :param base_url: Base URL of the SIDP API (e.g., 'http://localhost:3000')
        """
        self.base_url = base_url.rstrip("/")
        self._config = config

        if os.environ.get("SIDP_API_ENDPOINT_USERNAME") and os.environ.get(
            "SIDP_API_ENDPOINT_PASSWORD"
        ):
            self.auth = requests.auth.HTTPBasicAuth(
                os.environ.get("SIDP_API_ENDPOINT_USERNAME"),
                os.environ.get("SIDP_API_ENDPOINT_PASSWORD"),
            )
        else:
            self.auth = None

    def create_cluster(self) -> Dict[str, Union[str, int]]:
        """
        Create a new cluster using a SidpConfigurator

        :return: Dictionary with command output and task_id
        """
        response = requests.post(
            f"{self.base_url}/api/create",
            json=self._config.model_dump(),
            auth=self.auth,
        )
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id: str) -> Dict[str, str]:
        """
        Check the status of a task

        :return: Dictionary with command output
        """
        response = requests.get(
            f"{self.base_url}/api/task_status/{task_id}", auth=self.auth
        )
        response.raise_for_status()
        return response.json()

    def delete_cluster(self) -> Dict[str, str]:
        """
        Delete a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(
            f"{self.base_url}/api/delete", json=payload, auth=self.auth
        )
        response.raise_for_status()
        return response.json()

    def get_cluster_info(self) -> Dict[str, Union[str, Dict]]:
        """
        Get information about a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(
            f"{self.base_url}/api/info", json=payload, auth=self.auth
        )
        response.raise_for_status()
        return response.json()

    def get_kubeconfig(self) -> Dict[str, str]:
        """
        Retrieve kubeconfig for a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(
            f"{self.base_url}/api/get-kubeconf", json=payload, auth=self.auth
        )
        response.raise_for_status()
        return response.json()

    def resume_cluster(self) -> Dict[str, Union[str, Dict]]:
        """
        Resume a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(
            f"{self.base_url}/api/resume", json=payload, auth=self.auth
        )
        response.raise_for_status()
        return response.json()

    def pause_cluster(self) -> Dict[str, Union[str, Dict]]:
        """
        Pause a cluster

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(
            f"{self.base_url}/api/pause", json=payload, auth=self.auth
        )
        response.raise_for_status()
        return response.json()

    def list_cluster(self) -> Dict[str, Union[str, Dict]]:
        """
        List all clusters

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(
            f"{self.base_url}/api/list", json=payload, auth=self.auth
        )
        response.raise_for_status()
        return response.json()

    def list_tags(self) -> Dict[str, Union[str, Dict]]:
        """
        List Hemera tags

        :return: Dictionary with command output
        """
        payload = {"clusterName": self._config.clusterName}
        response = requests.post(
            f"{self.base_url}/api/list-tags", json=payload, auth=self.auth
        )
        response.raise_for_status()
        return response.json()

    @property
    def config(self) -> SidpConfigurator:
        """
        Output current SidpConfigurator object

        :return: Dictionary with kubeconfig contents
        """
        return self._config

    class TestInfo(object):
        def __init__(self):
            self._GITLAB_HEADERS = {
                "PRIVATE-TOKEN": os.environ.get("SIDP_GITLAB_TOKEN")
            }
            self.DEPLOY_PROJECT_ID = "41447556"
            self._artifact_urls = str()

        def format_json_error(self, success: bool, message: str) -> str:
            return json.dumps({"success": success, "reason": message})

        @property
        def getArtifactUrl(self) -> str:
            return self._artifact_urls

        def get_provisioning_job_status(self, uuid: str, branch: str) -> dict:
            """
            Long running function that will wait for pipeline to end and return job status details downloaded from job artifacts
            Returns:
                {
                  "success": bool,
                  "reason": str
                }
            """
            # Get Gitlab pipeline ID
            pipeline_id = self.get_last_pipeline_id(branch)
            if not pipeline_id:
                return self.format_json_error(
                    False, "pipeline not found or pipeline too old."
                )

            # Wait for pipeline to be finished
            success, reason = self.wait_pipeline(pipeline_id)
            if not success:
                return self.format_json_error(False, reason)

            # Get job ID
            job_id = self.get_provisioning_job_id(pipeline_id)
            if not job_id:
                return self.format_json_error(
                    False, f"job provisioning not found in pipeline {pipeline_id}"
                )

            # Get artifact and return results
            result = self.get_job_result_json(job_id, uuid)
            return self.format_json_error(result["success"], str(result["errors"]))

        def get_last_pipeline_id(self, branch: str) -> str:
            pipelines = requests.get(
                f"https://gitlab.com/api/v4/projects/{self.DEPLOY_PROJECT_ID}/pipelines",
                headers=self._GITLAB_HEADERS,
            )
            if not pipelines.ok:
                print(
                    "reason: " + pipelines.reason, "exit code: " + pipelines.status_code
                )
                return
            pipeline_id = str()
            for p in pipelines.json():
                if p["ref"] == branch:
                    pipeline_id = p["id"]
                    break  # There may be more than one, we are exiting on first found as pipeline are already sorted from newest to oldest
            return pipeline_id

        def get_provisioning_job_id(self, pipeline_id: str) -> str:
            PROVISIONING_JOB_NAME = "provisioning"
            jobs = requests.get(
                f"https://gitlab.com/api/v4/projects/{self.DEPLOY_PROJECT_ID}/pipelines/{pipeline_id}/jobs",
                headers=self._GITLAB_HEADERS,
            )
            if not jobs.ok:
                print("reason: " + jobs.reason, "exit code: " + jobs.status_code)
                return
            for j in jobs.json():
                if j["name"] == PROVISIONING_JOB_NAME:
                    return j["id"]
            return str()

        def get_job_result_json(self, job_id: str, uuid: str) -> dict:
            raw = self.get_raw_artifact(job_id)
            result = self.extract_gitlab_artifacts(raw)
            # Parse all files in zip and extract file named $uuid.json. This will raise IndexError if file is missing.
            filename = [x for x in result.keys() if uuid + ".json" in x][0]
            return json.loads(result[filename])

        def get_raw_artifact(self, job_id: str) -> str:
            self._artifact_urls = f"https://gitlab.com/api/v4/projects/{self.DEPLOY_PROJECT_ID}/jobs/{job_id}/artifacts"
            data = requests.get(
                self._artifact_urls,
                headers=self._GITLAB_HEADERS,
            )
            if not data.ok:
                print("reason: " + data.reason, "exit code: " + data.status_code)
            return data.content

        def wait_pipeline(self, pipeline_id: str) -> tuple[bool, str]:
            """
            Wait for pipeline to end and return True if successful, False for any other state. With reason of failure.
            """
            timeout = int(
                os.environ.get("SIDP_PROVISIONING_TIMEOUT", 3600)
            )  # Fetch from env var or 1h
            while timeout > 0:
                timeout = timeout - 5
                response = requests.get(
                    f"https://gitlab.com/api/v4/projects/{self.DEPLOY_PROJECT_ID}/pipelines/{pipeline_id}",
                    headers=self._GITLAB_HEADERS,
                )
                if not response.ok:
                    print(
                        "reason: " + response.reason,
                        "exit code: " + response.status_code,
                    )
                match response.json()["status"]:
                    case "success":
                        return True, str()
                    case "failed":
                        return False, "pipeline failed"
                    case "canceled":
                        return False, "pipeline canceled"
                sleep(5)
                print(f"Waiting for pipeline {pipeline_id}. Timeout in {timeout}")
            return False, "Time out waiting for provisioning to finish"

        def extract_gitlab_artifacts(self, zip_content):
            """
            Extract content from GitLab artifacts zip bytes

            Args:
                zip_content: The raw bytes of the ZIP file

            Returns:
                Dict containing the files in the artifacts zip
            """
            # Make sure we're working with bytes
            if not isinstance(zip_content, bytes):
                if isinstance(zip_content, str) and (
                    zip_content.startswith("b'") or zip_content.startswith('b"')
                ):
                    # It's a string representation of bytes
                    import ast

                    zip_content = ast.literal_eval(zip_content)
                else:
                    zip_content = bytes(zip_content, "latin1")

            # Process the ZIP content
            result = {}
            try:
                with io.BytesIO(zip_content) as zip_buffer:
                    with zipfile.ZipFile(zip_buffer) as zip_ref:
                        for file_name in zip_ref.namelist():
                            with zip_ref.open(file_name) as file:
                                content = file.read()
                                # Try to decode as text if it makes sense
                                try:
                                    result[file_name] = content.decode("utf-8")
                                except UnicodeDecodeError:
                                    # Keep as binary if it can't be decoded
                                    result[file_name] = content
                return result
            except zipfile.BadZipFile as e:
                # Additional debugging information
                print(f"Bad ZIP file error: {e}")
                print(f"First 20 bytes: {zip_content[:20]}")
                raise
