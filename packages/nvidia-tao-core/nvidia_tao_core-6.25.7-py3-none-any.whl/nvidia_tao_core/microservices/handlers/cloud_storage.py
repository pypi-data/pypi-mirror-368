# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Cloud storage Apache client"""
import os
import io
import copy
import time
import functools
import fnmatch
import logging

from nvidia_tao_core.microservices.handlers.encrypt import NVVaultEncryption
from nvidia_tao_core.distributed.decorators import master_node_only

from libcloud.storage.types import Provider
from libcloud.storage.providers import get_driver
from libcloud.common.types import LibcloudError
from libcloud.storage.types import ObjectDoesNotExistError

NUM_RETRY = 5

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry_method(func):
    """Retry Cloud storage methods for NUM_RETRY times"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(NUM_RETRY):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log or handle the exception as needed
                logger.error("Exception in %s: %s", func.__name__, e)
            time.sleep(30)
        # If all retries fail, raise an exception or handle it accordingly
        raise ValueError(f"Failed to execute {func.__name__} after multiple retries")
    return wrapper


def create_cs_instance_with_decrypted_metadata(decrypted_metadata):
    """Create a Cloud storage instance based on decrypted metadata"""
    handler_metadata_copy = copy.deepcopy(decrypted_metadata)
    cloud_type = handler_metadata_copy.get("cloud_type")
    cloud_specific_details = handler_metadata_copy.get("cloud_specific_details")
    cloud_region = cloud_specific_details.get("cloud_region")
    cloud_bucket_name = cloud_specific_details.get("cloud_bucket_name")

    cs_instance = None
    if cloud_specific_details and cloud_bucket_name:
        if cloud_type == "aws" and cloud_region:
            cs_instance = CloudStorage(
                "aws",
                cloud_bucket_name,
                region=cloud_region,
                access_key=cloud_specific_details.get("access_key"),
                secret_key=cloud_specific_details.get("secret_key")
            )
        elif cloud_type == "azure":
            cs_instance = CloudStorage(
                "azure",
                cloud_bucket_name,
                access_key=cloud_specific_details.get("account_name"),
                secret_key=cloud_specific_details.get("access_key")
            )
    return cs_instance, cloud_specific_details


def create_cs_instance(handler_metadata):
    """Create a Cloud Storage instance based on handler metadata details"""
    handler_metadata_copy = copy.deepcopy(handler_metadata)
    cloud_type = handler_metadata_copy.get("cloud_type")
    cloud_specific_details = handler_metadata_copy.get("cloud_specific_details")

    # Decrypt cloud details
    config_path = os.getenv("VAULT_SECRET_PATH", None)
    if config_path:
        encryption = NVVaultEncryption(config_path)
        for key, encrypted_value in cloud_specific_details.items():
            if encryption.check_config()[0]:
                cloud_specific_details[key] = encryption.decrypt(encrypted_value)

    cloud_region = cloud_specific_details.get("cloud_region")
    cloud_bucket_name = cloud_specific_details.get("cloud_bucket_name")

    cs_instance = None
    if cloud_specific_details:
        if cloud_type == "aws":
            cs_instance = CloudStorage(
                "aws",
                cloud_bucket_name,
                region=cloud_region,
                access_key=cloud_specific_details.get("access_key"),
                secret_key=cloud_specific_details.get("secret_key")
            )
        elif cloud_type == "azure":
            cs_instance = CloudStorage(
                "azure",
                cloud_bucket_name,
                access_key=cloud_specific_details.get("account_name"),
                secret_key=cloud_specific_details.get("access_key")
            )
    return cs_instance, cloud_specific_details


class CloudStorage:
    """Class for CRUD Cloud storage operations."""

    @retry_method
    def __init__(self, cloud_type, bucket_name, region="us-west-1", access_key=None, secret_key=None):
        """Initialize the CloudStorage object.

        cloud_type: Type of cloud storage ("aws" or "azure").
        bucket_name: Name of the bucket/container.
        region: Region for the cloud storage provider.
        access_key: Access key for authentication.
        secret_key: Secret key for authentication.
        """
        self.cloud_type = cloud_type
        self.bucket_name = bucket_name
        self.region = region

        if cloud_type == "aws":
            cls = get_driver(Provider.S3)
        elif cloud_type == "azure":
            cls = get_driver(Provider.AZURE_BLOBS)
        else:
            raise ValueError("Invalid cloud_type. Supported values: 'aws' or 'azure'.")

        self.driver = cls(access_key, secret_key, region=self.region)
        self.container = self.driver.get_container(container_name=self.bucket_name)

    """GET Operations"""

    @retry_method
    def is_file(self, cloud_path):
        """Check if the given cloud path represents a file.

        :param cloud_path: Cloud path to be checked.
        :return: True if the path represents a file, False otherwise.
        """
        try:
            self.driver.get_object(container_name=self.bucket_name, object_name=cloud_path)
        except (LibcloudError, ObjectDoesNotExistError):
            logger.error("File %s doesn't exist in cloud storage", cloud_path)
            return False
        except Exception as e:
            logger.error("Error checking cloud path: %s", e)
            return False
        return True

    @retry_method
    def is_folder(self, cloud_path):
        """Check if the given cloud path represents a folder.

        :param cloud_path: Cloud path to be checked.
        :return: True if the path represents a folder, False otherwise.
        """
        try:
            prefix = cloud_path.rstrip('/') + '/'

            # List objects with the specified prefix
            objects = self.driver.list_container_objects(container=self.container, ex_prefix=prefix)

            # Check if there are any objects with the specified prefix
            return any(objects)
        except Exception as e:
            raise e

    @retry_method
    def glob_files(self, pattern):
        """Search for files in the bucket that match the specified pattern.

        pattern: File pattern to match, e.g., "*.mp4".
        Returns:
            List of matching file names.
        """
        all_files = self.driver.list_container_objects(self.container)
        matching_files = [obj.name for obj in all_files if fnmatch.fnmatch(obj.name, pattern)]
        return matching_files

    @retry_method
    def list_files_in_folder(self, folder):
        """List files in the specified folder in the cloud storage bucket.

        folder: Cloud folder path.
        :return: List of cloud storage objects in the specified folder.
        """
        try:
            folder = folder + '/' if not folder.endswith('/') else folder
            file_objects = self.driver.list_container_objects(container=self.container, ex_prefix=folder)
            file_names = [file_object.name for file_object in file_objects]
            return file_names, file_objects
        except Exception as e:
            raise e

    @retry_method
    def download_file(self, cloud_file_path, local_destination):
        """Download a file from the cloud storage bucket.

        cloud_file_path: Cloud file path to be downloaded.
        local_destination: Local path to save the downloaded file.
        """
        if not self.is_file(cloud_file_path):
            logger.error("Cloud file %s trying to download doesn't exist", cloud_file_path)
            return
        try:
            base_path = os.path.dirname(local_destination)
            if not os.path.exists(base_path):
                os.makedirs(base_path)

            obj = self.driver.get_object(container_name=self.bucket_name, object_name=cloud_file_path)
            logger.info("Downloading file %s to %s", cloud_file_path, local_destination)
            chunk_size = 1024 * 1024 * 10  # 10MB
            with open(local_destination, 'wb') as f:
                for chunk in obj.as_stream(chunk_size=chunk_size):
                    f.write(chunk)
            logger.info("File %s downloaded successfully", cloud_file_path)
        except Exception as e:
            raise e

    @retry_method
    def download_folder(self, cloud_folder, local_destination, maintain_src_folder_structure=False):
        """Download all files in a cloud folder to a local destination.

        cloud_folder: Cloud folder path to be downloaded.
        local_destination: Local folder path to save the downloaded files.
        """
        _, objects = self.list_files_in_folder(cloud_folder)
        for obj in objects:
            if maintain_src_folder_structure:
                local_dest_wo_parent_root = f"/{obj.name}"
                if local_dest_wo_parent_root.endswith("/"):
                    local_dest_wo_parent_root = local_dest_wo_parent_root[:-1]
            else:
                relative_path = obj.name.replace(cloud_folder, "")
                if relative_path.startswith("/"):
                    relative_path = relative_path[1:]
                local_dest_wo_parent_root = os.path.join(local_destination, relative_path)
            self.download_file(obj.name, local_dest_wo_parent_root)

    """CREATE Operations"""

    @retry_method
    @master_node_only
    def create_folder_in_bucket(self, folder):
        """Create a folder in the cloud storage bucket.

        Args:
            folder (str): Folder path to be created in the cloud storage bucket.
        """
        try:
            # Ensure the folder path ends with a trailing slash
            if not folder.endswith('/'):
                folder += '/'

            # Upload an empty object to represent the folder
            empty_data = io.BytesIO(b'')
            self.driver.upload_object_via_stream(empty_data, container=self.container, object_name=folder)
        except Exception as e:
            raise e

    @retry_method
    @master_node_only
    def upload_file(self, local_file_path, cloud_file_path):
        """Upload a file from a local path to a specified path in the cloud storage bucket.

        :local_file_path: Local file path to be uploaded.
        :cloud_file_path: Destination path in the cloud storage bucket.
        """
        try:
            cloud_file_path = cloud_file_path.strip("/")
            # Upload the file to cloud storage
            if os.path.exists(local_file_path):
                with open(local_file_path, 'rb') as file_stream:
                    self.driver.upload_object_via_stream(
                        file_stream,
                        container=self.container,
                        object_name=cloud_file_path
                    )
                if self.is_file(cloud_file_path):
                    logger.info("File %s was uploaded successfully", cloud_file_path)
                else:
                    raise ValueError(f"File {cloud_file_path} was not uploaded successfully")
        except Exception as e:
            raise e

    @retry_method
    @master_node_only
    def upload_folder(self, local_folder, cloud_subfolder):
        """Upload files from a local folder to a specified subfolder in the cloud storage bucket.

        local_folder: Local folder path.
        cloud_subfolder: Target subfolder in the cloud storage bucket.
        """
        try:
            # Remove leading/trailing slashes from cloud_subfolder
            cloud_subfolder = cloud_subfolder.strip("/")

            for root, _, files in os.walk(local_folder):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, local_folder)

                    # Construct the cloud object name without a leading slash
                    cloud_object_name = f"{cloud_subfolder}/{relative_path.replace(os.path.sep, '/')}"

                    # Upload the file to cloud storage
                    with open(local_file_path, 'rb') as file_stream:
                        self.driver.upload_object_via_stream(
                            file_stream,
                            container=self.container,
                            object_name=cloud_object_name
                        )
        except Exception as e:
            raise e

    """DELETE Operations"""

    @retry_method
    @master_node_only
    def delete_folder(self, folder):
        """Delete a folder and its contents from the cloud storage bucket.

        folder: Cloud folder path to be deleted.
        """
        try:
            _, objects = self.list_files_in_folder(folder)
            for obj in objects:
                self.driver.delete_object(obj)
        except Exception as e:
            raise e

    @retry_method
    @master_node_only
    def delete_file(self, file_path):
        """Delete a file from the cloud storage bucket.

        file_path: Cloud file path to be deleted.
        """
        try:
            if self.is_file(file_path):
                obj = self.driver.get_object(container_name=self.bucket_name, object_name=file_path)
                self.driver.delete_object(obj)
            else:
                logger.info("File %s doesn't exist", file_path)
        except Exception as e:
            raise e

    """UPDATE Operations"""

    @retry_method
    @master_node_only
    def move_file(self, source_path, destination_path):
        """Move a file within the cloud storage bucket.

        :param source_path: Source path of the file to be moved.
        :param destination_path: Destination path for the file.
        """
        if not self.is_file(source_path):
            raise ValueError("Source path must represent a file.")

        self.copy_file(source_path, destination_path)
        self.delete_file(source_path)

    @retry_method
    @master_node_only
    def move_folder(self, source_path, destination_path):
        """Move a folder within the cloud storage bucket.

        :param source_path: Source path of the folder to be moved.
        :param destination_path: Destination path for the folder.
        """
        if not self.is_folder(source_path):
            raise ValueError("Source path must represent a folder.")

        # Ensure the destination folder exists
        self.create_folder_in_bucket(destination_path)

        _, objects = self.list_files_in_folder(source_path)
        for obj in objects:
            relative_path = os.path.relpath(obj.name, source_path)
            destination_object_name = f"{destination_path}/{relative_path.replace(os.path.sep, '/')}"

            self.copy_file(obj.name, destination_object_name)
            self.delete_file(obj.name)

    @retry_method
    @master_node_only
    def copy_file(self, source_object_name, destination_object_name):
        """Copy a file within the cloud storage bucket.

        :param source_path: Source path of the file to be copied.
        :param destination_path: Destination path for the copied file.
        """
        if self.is_file(source_object_name):
            # Get the source object
            source_object = self.driver.get_object(container_name=self.bucket_name, object_name=source_object_name)

            # Upload the source object to the destination object path
            try:
                self.driver.upload_object_via_stream(
                    source_object.as_stream(),
                    container=self.container,
                    object_name=destination_object_name
                )
                logger.info("Object copied successfully: %s -> %s", source_object_name, destination_object_name)
            except Exception as e:
                logger.error("Error copying object %s: %s", source_object_name, e)
                raise ValueError(f"Error copying object {source_object_name}") from e

    @retry_method
    @master_node_only
    def copy_folder(self, source_path, destination_path):
        """Copy a folder within the cloud storage bucket.

        :param source_path: Source path of the folder to be copied.
        :param destination_path: Destination path for the copied folder.
        """
        if not self.is_folder(source_path):
            raise ValueError("Source path must represent a folder.")

        # Ensure the destination folder exists
        self.create_folder_in_bucket(destination_path)

        _, objects = self.list_files_in_folder(source_path)
        for obj in objects:
            relative_path = os.path.relpath(obj.name, source_path)
            destination_object_name = f"{destination_path}/{relative_path.replace(os.path.sep, '/')}"

            self.copy_file(obj.name, destination_object_name)
