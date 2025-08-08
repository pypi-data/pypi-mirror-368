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


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was mindquantumConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

if(TARGET mindquantum::mqbackend)
  # Protect against double definitions due to previous call or add_subdirectory()
  return()
endif()

# ==============================================================================

if(FALSE) # if(MQ_INSTALL_IN_BUILD_DIR)
  list(PREPEND CMAKE_MODULE_PATH "/Users/jenkins3/agent-working-dir/workspace/executor0/mindquantum/cmake/commands" "/Users/jenkins3/agent-working-dir/workspace/executor0/mindquantum/cmake/Modules"
       "/Users/jenkins3/agent-working-dir/workspace/executor0/mindquantum/cmake" "${CMAKE_CURRENT_LIST_DIR}")
else()
  list(PREPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/commands" "${CMAKE_CURRENT_LIST_DIR}/Modules"
       "${CMAKE_CURRENT_LIST_DIR}")
endif()

include(to_cmake_path)
include(find_python_module)
include(mq_config_macros)

# ---------------------------------------

mq_set(MQ_PACKAGE_PREFIX_DIR "${PACKAGE_PREFIX_DIR}")

mq_set(USE_OPENMP "ON")
mq_set(USE_PARALLEL_STL "OFF")
mq_set(PYTHON_EXECUTABLE "")

# ---------------------------------------

if(ENABLE_CUDA)
  enable_language(CUDA)
endif()

include(packages)

# ==============================================================================

include(mindquantumTargetsExternal)

include(mindquantumTargets)
if(EXISTS mindquantumPythonTargets)
  include(mindquantumPythonTargets)
endif()

# ------------------------------------------------------------------------------

check_required_components(mindquantum)

# ==============================================================================

mq_unset_auto()

list(POP_FRONT CMAKE_MODULE_PATH)
list(POP_FRONT CMAKE_MODULE_PATH)
list(POP_FRONT CMAKE_MODULE_PATH)
if(FALSE) # if(MQ_INSTALL_IN_BUILD_DIR)
  list(POP_FRONT CMAKE_MODULE_PATH)
endif()

# ==============================================================================
