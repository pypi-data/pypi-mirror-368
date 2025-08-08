# ==============================================================================
#
# Copyright 2022 <Huawei Technologies Co., Ltd>
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
#
# ==============================================================================



# fmt (local)
find_package(fmt
             10.2.1
             CONFIG
             NO_DEFAULT_PATH
             PATHS
             C:/Users/jenkins/.mslib/fmt_10.2.1_a95fb89c55065ede818c0342669f9637
             REQUIRED)
if(TARGET fmt::fmt-header-only AND NOT TARGET mindquantum::fmt)
  add_library(mindquantum::fmt ALIAS fmt::fmt-header-only)
endif()

# pybind11 (system)
find_package(pybind11
             2.10.0
             REQUIRED)
if(TARGET pybind11::headers AND NOT TARGET mindquantum::pybind11_headers)
  add_library(mindquantum::pybind11_headers ALIAS pybind11::headers)
endif()
if(TARGET pybind11::module AND NOT TARGET mindquantum::pybind11_module)
  add_library(mindquantum::pybind11_module ALIAS pybind11::module)
endif()
if(TARGET pybind11::lto AND NOT TARGET mindquantum::pybind11_lto)
  add_library(mindquantum::pybind11_lto ALIAS pybind11::lto)
endif()
if(TARGET pybind11::windows_extras AND NOT TARGET mindquantum::windows_extra)
  add_library(mindquantum::windows_extra ALIAS pybind11::windows_extras)
endif()

# nlohmann_json (local)
find_package(nlohmann_json
             3.11.2
             CONFIG
             NO_DEFAULT_PATH
             PATHS
             C:/Users/jenkins/.mslib/nlohmann_json_3.11.2_0d10904793224beceb27eddcdc104c9e
             REQUIRED)
if(TARGET nlohmann_json::nlohmann_json AND NOT TARGET mindquantum::json)
  add_library(mindquantum::json ALIAS nlohmann_json::nlohmann_json)
endif()
