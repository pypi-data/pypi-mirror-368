#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mindquantum::mq_base" for configuration "Release"
set_property(TARGET mindquantum::mq_base APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mindquantum::mq_base PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/mindquantum/libmq_base.a"
  )

list(APPEND _cmake_import_check_targets mindquantum::mq_base )
list(APPEND _cmake_import_check_files_for_mindquantum::mq_base "${_IMPORT_PREFIX}/lib/mindquantum/libmq_base.a" )

# Import target "mindquantum::mqsim_common" for configuration "Release"
set_property(TARGET mindquantum::mqsim_common APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mindquantum::mqsim_common PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/mindquantum/libmqsim_common.a"
  )

list(APPEND _cmake_import_check_targets mindquantum::mqsim_common )
list(APPEND _cmake_import_check_files_for_mindquantum::mqsim_common "${_IMPORT_PREFIX}/lib/mindquantum/libmqsim_common.a" )

# Import target "mindquantum::mqsim_vector_cpu" for configuration "Release"
set_property(TARGET mindquantum::mqsim_vector_cpu APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mindquantum::mqsim_vector_cpu PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/mindquantum/libmqsim_vector_cpu.a"
  )

list(APPEND _cmake_import_check_targets mindquantum::mqsim_vector_cpu )
list(APPEND _cmake_import_check_files_for_mindquantum::mqsim_vector_cpu "${_IMPORT_PREFIX}/lib/mindquantum/libmqsim_vector_cpu.a" )

# Import target "mindquantum::mqrt" for configuration "Release"
set_property(TARGET mindquantum::mqrt APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mindquantum::mqrt PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/mqrt.exe"
  )

list(APPEND _cmake_import_check_targets mindquantum::mqrt )
list(APPEND _cmake_import_check_files_for_mindquantum::mqrt "${_IMPORT_PREFIX}/bin/mqrt.exe" )

# Import target "mindquantum::mqsim_densitymatrix_cpu" for configuration "Release"
set_property(TARGET mindquantum::mqsim_densitymatrix_cpu APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mindquantum::mqsim_densitymatrix_cpu PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/mindquantum/libmqsim_densitymatrix_cpu.a"
  )

list(APPEND _cmake_import_check_targets mindquantum::mqsim_densitymatrix_cpu )
list(APPEND _cmake_import_check_files_for_mindquantum::mqsim_densitymatrix_cpu "${_IMPORT_PREFIX}/lib/mindquantum/libmqsim_densitymatrix_cpu.a" )

# Import target "mindquantum::mqsim_stabilizer" for configuration "Release"
set_property(TARGET mindquantum::mqsim_stabilizer APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mindquantum::mqsim_stabilizer PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/mindquantum/libmqsim_stabilizer.a"
  )

list(APPEND _cmake_import_check_targets mindquantum::mqsim_stabilizer )
list(APPEND _cmake_import_check_files_for_mindquantum::mqsim_stabilizer "${_IMPORT_PREFIX}/lib/mindquantum/libmqsim_stabilizer.a" )

# Import target "mindquantum::mqchem_cpu" for configuration "Release"
set_property(TARGET mindquantum::mqchem_cpu APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mindquantum::mqchem_cpu PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/mindquantum/libmqchem_cpu.a"
  )

list(APPEND _cmake_import_check_targets mindquantum::mqchem_cpu )
list(APPEND _cmake_import_check_files_for_mindquantum::mqchem_cpu "${_IMPORT_PREFIX}/lib/mindquantum/libmqchem_cpu.a" )

# Import target "mindquantum::mq_math" for configuration "Release"
set_property(TARGET mindquantum::mq_math APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mindquantum::mq_math PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/mindquantum/libmq_math.a"
  )

list(APPEND _cmake_import_check_targets mindquantum::mq_math )
list(APPEND _cmake_import_check_files_for_mindquantum::mq_math "${_IMPORT_PREFIX}/lib/mindquantum/libmq_math.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
