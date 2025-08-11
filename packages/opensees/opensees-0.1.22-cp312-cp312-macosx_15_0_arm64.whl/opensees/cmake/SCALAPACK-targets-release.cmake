#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SCALAPACK::BLACS" for configuration "Release"
set_property(TARGET SCALAPACK::BLACS APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(SCALAPACK::BLACS PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libblacs.a"
  )

list(APPEND _cmake_import_check_targets SCALAPACK::BLACS )
list(APPEND _cmake_import_check_files_for_SCALAPACK::BLACS "${_IMPORT_PREFIX}/lib/libblacs.a" )

# Import target "SCALAPACK::SCALAPACK" for configuration "Release"
set_property(TARGET SCALAPACK::SCALAPACK APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(SCALAPACK::SCALAPACK PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C;Fortran"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libscalapack.a"
  )

list(APPEND _cmake_import_check_targets SCALAPACK::SCALAPACK )
list(APPEND _cmake_import_check_files_for_SCALAPACK::SCALAPACK "${_IMPORT_PREFIX}/lib/libscalapack.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
