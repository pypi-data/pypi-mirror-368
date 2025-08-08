cmake_policy(PUSH)
cmake_policy(VERSION 2.6...3.20)

set(CMAKE_IMPORT_FILE_VERSION 1)

if(NOT TARGET cuquantum::cuquantum)
  add_library(cuquantum::cuquantum INTERFACE IMPORTED)

  set_target_properties(cuquantum::cuquantum PROPERTIES
       INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/."
  )


endif()

if(CMAKE_VERSION VERSION_LESS 3.0.0)
  message(FATAL_ERROR "This file relies on consumers using CMake 3.0.0 or greater.")
endif()

set(CMAKE_IMPORT_FILE_VERSION)
cmake_policy(POP)
