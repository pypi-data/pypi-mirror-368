from __future__ import absolute_import

import enum
import errno
import hashlib
import json
import mimetypes
import os
import tempfile
from concurrent import futures
from os import listdir, makedirs
from os.path import isdir, join
from shutil import rmtree, copyfile

import six

from rapyuta_io.utils import RestClient, InvalidParameterException, ConfigNotFoundException
from rapyuta_io.utils.error import InvalidJSONError, InvalidYAMLError, UploadError
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.settings import PARAMSERVER_API_TREE_PATH, PARAMSERVER_API_TREEBLOBS_PATH, \
    PARAMSERVER_API_FILENODE_PATH
from rapyuta_io.utils.utils import (
    create_auth_header,
    prepend_bearer_to_auth_token,
    get_api_response_data,
    validate_list_of_strings,
    parse_json,
    parse_yaml
)


class _Node(str, enum.Enum):

    def __str__(self):
        return str(self.value)

    File = 'FileNode'
    Value = 'ValueNode'
    Attribute = 'AttributeNode'
    Folder = 'FolderNode'


class _ParamserverClient:
    """
    Internal client for paramserver. Not for public use.
    """
    yaml_content_type = 'text/yaml'
    json_content_type = 'application/json'
    default_binary_content_type = "application/octet-stream"
    max_non_binary_size = 128 * 1024

    def __init__(self, auth_token, project, core_api_host):
        self._auth_token = auth_token
        self._headers = create_auth_header(prepend_bearer_to_auth_token(auth_token), project)
        self._core_api_host = core_api_host

    def set_project(self, project_guid):
        self._headers = create_auth_header(prepend_bearer_to_auth_token(self._auth_token), project_guid)

    @staticmethod
    def get_md5_checksum(data):
        md5_hash = hashlib.md5()
        md5_hash.update(data)
        return md5_hash.hexdigest()

    def create_file(self, tree_path, filedata, retry_limit=0, content_type=None):
        content_type = content_type if content_type else self.yaml_content_type
        url = self._core_api_host + PARAMSERVER_API_TREE_PATH + tree_path
        payload = {'type': _Node.File, 'data': filedata, 'contentType': content_type}
        response = RestClient(url).method(HttpMethod.PUT).headers(self._headers).retry(retry_limit).execute(payload)
        return get_api_response_data(response, parse_full=True)

    def create_binary_file(self, tree_path, file_path, retry_limit=0):
        url = self._core_api_host + PARAMSERVER_API_FILENODE_PATH + tree_path
        content_type = self.default_binary_content_type
        headers = self._headers.copy()
        guessed_content_type = mimetypes.MimeTypes().guess_type(file_path)
        if len(guessed_content_type) != 0:
            if guessed_content_type[0]:
                content_type = guessed_content_type[0]
            if guessed_content_type[1]:
                headers['Content-Encoding'] = guessed_content_type[1]

        # Override Content-Type for JSON and YAML to allow creating Binary files.
        # This is required for large YAML/JSON files.
        if content_type in (self.json_content_type, self.yaml_content_type):
            content_type = self.default_binary_content_type

        headers.update({'X-Rapyuta-Params-Version': "0",
                        'Content-Type': content_type})

        with open(file_path, 'rb') as f:
            headers.update({'Checksum': self.get_md5_checksum(f.read())})
            f.seek(0)
            response = RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=f, raw=True)

        try:
            return get_api_response_data(response, parse_full=True)
        except Exception as e:
            raise UploadError(file_path=file_path, msg=e)

    def create_value(self, tree_path, retry_limit=0):
        url = self._core_api_host + PARAMSERVER_API_TREE_PATH + tree_path
        payload = {'type': _Node.Value}
        response = RestClient(url).method(HttpMethod.PUT).headers(self._headers).retry(retry_limit).execute(payload)
        return get_api_response_data(response, parse_full=True)

    def create_folder(self, tree_path, retry_limit=0):
        url = self._core_api_host + PARAMSERVER_API_TREE_PATH + tree_path
        payload = {'type': _Node.Folder}
        response = RestClient(url).method(HttpMethod.PUT).headers(self._headers).retry(retry_limit).execute(payload)
        return get_api_response_data(response, parse_full=True)

    def create_attribute(self, tree_path, retry_limit=0):
        url = self._core_api_host + PARAMSERVER_API_TREE_PATH + tree_path
        payload = {'type': _Node.Attribute}
        response = RestClient(url).method(HttpMethod.PUT).headers(self._headers).retry(retry_limit).execute(payload)
        return get_api_response_data(response, parse_full=True)

    def create_tree(self, tree_name, delete_existing, retry_limit=0):
        if delete_existing:
            url = self._core_api_host + PARAMSERVER_API_TREE_PATH + tree_name
            response = RestClient(url).method(HttpMethod.DELETE).headers(self._headers).retry(retry_limit).execute()
            get_api_response_data(response, parse_full=True)  # validate 200 response
        return self.create_value(tree_name)

    def process_root_dir(self, executor, rootdir, tree_names, delete_existing_trees):
        listdir_names = listdir(rootdir)
        if tree_names:
            listdir_names = [name for name in listdir_names if name in tree_names]
        dir_futures = {}
        for name in listdir_names:
            if isdir(join(rootdir, name)):
                future = executor.submit(self.create_tree, name, delete_existing_trees)
                dir_futures[future] = (name, 1)
        for future in futures.as_completed(dir_futures):
            exc = future.exception()
            if exc is not None:
                exc.tree_path = dir_futures[future][0]
                raise exc
        return dir_futures

    def process_dir(self, executor, rootdir, tree_path, level, dir_futures, file_futures):
        in_attribute_dir = level % 2 == 0
        for name in listdir(join(rootdir, tree_path)):
            full_path = join(rootdir, tree_path, name)
            new_tree_path = join(tree_path, name)
            if isdir(full_path):
                func = self.create_value if in_attribute_dir else self.create_attribute
                future = executor.submit(func, new_tree_path)
                dir_futures[future] = (new_tree_path, level + 1)
            elif not in_attribute_dir:  # ignore files in attribute directories
                file_stat = os.stat(full_path)
                file_name = os.path.basename(full_path)
                if file_stat.st_size > self.max_non_binary_size:
                    future = executor.submit(self.create_binary_file, new_tree_path, full_path)
                if file_name.endswith('.yaml'):
                    data = parse_yaml(full_path)
                    if self.should_upload_as_binary(data, self.yaml_content_type):
                        future = executor.submit(self.create_binary_file, new_tree_path, full_path)
                    else:
                        future = executor.submit(self.create_file, new_tree_path, data)
                elif file_name.endswith('.json'):
                    data = parse_json(full_path)
                    if self.should_upload_as_binary(data, self.json_content_type):
                        future = executor.submit(self.create_binary_file, new_tree_path, full_path)
                    else:
                        future = executor.submit(self.create_file, new_tree_path, data, content_type=self.json_content_type)
                else:
                    future = executor.submit(self.create_binary_file, new_tree_path, full_path)
                file_futures[future] = new_tree_path
        return dir_futures, file_futures

    def process_folder(self, executor, rootdir, tree_path, level, dir_futures, file_futures):
        for name in listdir(join(rootdir, tree_path)):
            full_path = join(rootdir, tree_path, name)
            new_tree_path = join(tree_path, name)
            if isdir(full_path):
                future = executor.submit(self.create_folder, new_tree_path)
                dir_futures[future] = (new_tree_path, level + 1)
                continue
            file_stat = os.stat(full_path)
            file_name = os.path.basename(full_path)
            if file_stat.st_size > self.max_non_binary_size:
                future = executor.submit(self.create_binary_file, new_tree_path, full_path)
            elif file_name.endswith('.yaml'):
                data = parse_yaml(full_path)
                if self.should_upload_as_binary(data, self.yaml_content_type):
                    future = executor.submit(self.create_binary_file, new_tree_path, full_path)
                else:
                    future = executor.submit(self.create_file, new_tree_path, data)
            elif file_name.endswith('.json'):
                data = parse_json(full_path)
                if self.should_upload_as_binary(data, self.json_content_type):
                    future = executor.submit(self.create_binary_file, new_tree_path, full_path)
                else:
                    future = executor.submit(self.create_file, new_tree_path, data, content_type=self.json_content_type)
            else:
                future = executor.submit(self.create_binary_file, new_tree_path, full_path)
            file_futures[future] = new_tree_path

        return dir_futures, file_futures

    def should_upload_as_binary(self, filedata, content_type):
        """Determines if the file should be uploaded as binary based on the file size

        While the file data may be less than the supported limit, the combined size of
        the API payload is what is stored by paramserver. This method calculates the
        size of the payload and determines if it exceeds the supported limit. If it does,
        the file is uploaded as a binary to the blob store.

        We cannot entirely rely on the file stat result since the file data is sent as
        a string in the API payload and the final size inflates when json.dumps is
        performed on the final payload.
        """
        metadata_size_buffer = 200  # In bytes
        payload = {'type': _Node.File, 'data': filedata, 'contentType': content_type}
        return len(json.dumps(payload)) + metadata_size_buffer > self.max_non_binary_size

    def upload_configurations(self, rootdir, tree_names, delete_existing_trees, as_folder=False):
        self.validate_args(rootdir, tree_names, delete_existing_trees, as_folder)
        with futures.ThreadPoolExecutor(max_workers=15) as executor:
            dir_futures = self.process_root_dir(executor, rootdir, tree_names, delete_existing_trees)
            file_futures = {}
            done = futures.wait(dir_futures, return_when=futures.FIRST_COMPLETED).done
            future = done.pop() if len(done) else None
            while future is not None:
                tree_path, level = dir_futures[future]
                del dir_futures[future]
                exc = future.exception()
                if exc is not None:
                    exc.tree_path = tree_path
                    raise exc

                processor_func = self.process_dir if not as_folder else self.process_folder
                dir_futures, file_futures = processor_func(executor, rootdir, tree_path, level, dir_futures,
                                                           file_futures)
                done = futures.wait(dir_futures, return_when=futures.FIRST_COMPLETED).done
                future = done.pop() if len(done) else None

            for future in futures.as_completed(file_futures):
                exc = future.exception()
                if exc is not None:
                    exc.tree_path = file_futures[future]
                    raise exc

    @staticmethod
    def _safe_makedirs(path):
        """makedirs if not exists"""
        try:
            makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def create_node_on_filesystem(self, node, dirprefix, blob_dir):
        path = join(dirprefix, node['name'])
        if node['type'] == _Node.File:
            if node.get('blobRefId'):
                blob_path = join(blob_dir, node['blobRefId'])
                copyfile(blob_path, path)
            else:
                with open(path, 'w') as f:
                    f.write(node.get('data', ''))
        else:
            self._safe_makedirs(path)
            for child in node.get('children', []):
                self.create_node_on_filesystem(child, path, blob_dir)

    def download_tree(self, tree_name, rootdir, delete_existing, blob_temp_dir):
        if delete_existing:
            try:
                rmtree(join(rootdir, tree_name))
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise

        url = self._core_api_host + PARAMSERVER_API_TREE_PATH + tree_name
        response = RestClient(url).method(HttpMethod.GET).headers(self._headers).retry(0).execute()
        tree_root = get_api_response_data(response, parse_full=True).get('data', {})
        self.create_node_on_filesystem(tree_root, rootdir, blob_temp_dir)

    def get_blob_data(self, tree_names):
        url = self._core_api_host + PARAMSERVER_API_TREEBLOBS_PATH
        response = RestClient(url).method(HttpMethod.GET).query_param({'treeNames': tree_names}).headers(
            self._headers).retry(0).execute()
        blob_data = get_api_response_data(response, parse_full=True).get('data', {})
        return blob_data

    @staticmethod
    def download_blob_file(blob, blob_temp_dir):
        response = RestClient(blob['signedUrl']).method(HttpMethod.GET).execute()
        path = os.path.join(blob_temp_dir, str(blob['ID']))
        with open(path, 'wb') as f:
            for chunk in response.iter_content(1024 * 1024):
                f.write(chunk)

    @staticmethod
    def validate_args(rootdir, tree_names, delete_existing_trees, as_folder=False):
        if not isinstance(rootdir, six.string_types):
            raise InvalidParameterException('rootdir must be a string')
        if tree_names:
            validate_list_of_strings(tree_names, 'tree_names')
        if not isinstance(delete_existing_trees, bool):
            raise InvalidParameterException('delete_existing_trees must be a boolean')
        if not isinstance(as_folder, bool):
            raise InvalidParameterException('as_folder must be a boolean')

    def download_configurations(self, rootdir, tree_names, delete_existing_trees):
        self.validate_args(rootdir, tree_names, delete_existing_trees)
        self._safe_makedirs(rootdir)

        try:
            url = self._core_api_host + PARAMSERVER_API_TREE_PATH.rstrip('/')
            response = RestClient(url).method(HttpMethod.GET).headers(self._headers).retry(0).execute()
            api_tree_names = get_api_response_data(response, parse_full=True).get('data', [])
        except Exception as e:
            e.tree_path = ''
            raise

        if tree_names:
            api_tree_names = [tree_name for tree_name in api_tree_names if tree_name in tree_names]

        if not api_tree_names:
            raise ConfigNotFoundException('One or more trees not found')

        blob_temp_dir = tempfile.mkdtemp()

        blob_files = self.get_blob_data(api_tree_names)
        with futures.ThreadPoolExecutor(max_workers=15) as executor:
            blobs = blob_files.pop('blobRefs')
            blob_futures = {}
            for blob in blobs:
                if blob['signedUrl']:
                    future = executor.submit(self.download_blob_file, blob, blob_temp_dir)
                    blob_futures[future] = blob['ID']

            for future in futures.as_completed(blob_futures):
                exc = future.exception()
                if exc is not None:
                    # it is set to None for backward compatibility,
                    # the blob_files doesnt have any information abt tree
                    exc.tree_path = None
                    raise exc

        with futures.ThreadPoolExecutor(max_workers=15) as executor:
            tree_futures = {}
            for tree_name in api_tree_names:
                future = executor.submit(self.download_tree, tree_name, rootdir, delete_existing_trees, blob_temp_dir)
                tree_futures[future] = tree_name

            for future in futures.as_completed(tree_futures):
                exc = future.exception()
                if exc is not None:
                    exc.tree_path = tree_futures[future]
                    raise exc

        rmtree(blob_temp_dir)
