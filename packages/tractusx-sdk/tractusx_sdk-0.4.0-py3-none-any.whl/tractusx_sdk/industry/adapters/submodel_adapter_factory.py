#################################################################################
# Eclipse Tractus-X - Software Development KIT
#
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the
# License for the specific language govern in permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0
#################################################################################

from enum import Enum
from importlib import import_module

class SubmodelAdapterType(Enum):
    """
    Enum for different adapter types. Each adapter type corresponds to a specific implementation,
    and must correspond exactly to the prefix of the adapter class it is associated with.
    """
    FILE_SYSTEM = "FileSystem"

class SubmodelAdapterFactory:

    @staticmethod
    def _get_adapter_builder(
            adapter_type: SubmodelAdapterType,
    ):
        adapter_module = ".".join(__name__.split(".")[0:-1])
        module_name = f"{adapter_module}.submodel_adapters"
        adapter_class_name = f"{adapter_type.value}Adapter"

        try:
            module = import_module(module_name)
            adapter_class = getattr(module, adapter_class_name)
            return adapter_class.builder()
        except AttributeError as attr_exception:
            raise AttributeError(
                f"Failed to import adapter class {adapter_class_name} for module {module_name}"
            ) from attr_exception
        except ImportError as import_exception:
            raise ImportError(
                f"Failed to import module {module_name}. Ensure that the required packages are installed and the PYTHONPATH is set correctly."
            ) from import_exception
    
    @staticmethod
    def get_file_system(root_path: str = "./submodel"):
        builder = SubmodelAdapterFactory._get_adapter_builder(
            adapter_type=SubmodelAdapterType.FILE_SYSTEM,
        )
        builder.root_path(root_path)
        return builder.build()
