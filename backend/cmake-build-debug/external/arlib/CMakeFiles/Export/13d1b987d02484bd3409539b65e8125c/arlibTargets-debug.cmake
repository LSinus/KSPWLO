#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "arlib::arlib" for configuration "Debug"
set_property(TARGET arlib::arlib APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(arlib::arlib PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "CXX"
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/libarlib.a"
  )

list(APPEND _cmake_import_check_targets arlib::arlib )
list(APPEND _cmake_import_check_files_for_arlib::arlib "${_IMPORT_PREFIX}/lib/libarlib.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
