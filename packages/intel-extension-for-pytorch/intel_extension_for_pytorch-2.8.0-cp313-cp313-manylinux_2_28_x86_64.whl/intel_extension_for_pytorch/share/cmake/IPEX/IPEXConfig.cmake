# FindIPEX
# -------
#
# Finds the Torch IPEX library
#
# This will define the following variables:
#
#   IPEX_FOUND              -- True if the system has the Torch IPEX library
#   IPEX_INCLUDE_DIRS       -- The include directories for torch
#   IPEX_LIBRARIES          -- Libraries to link against
#   IPEX_CXX_FLAGS          -- Additional (required) compiler flags
#
#   TORCH_IPEX_INCLUDE_DIRS -- TORCH_INCLUDE_DIRS + IPEX_INCLUDE_DIRS
#   TORCH_IPEX_LIBRARIES    -- TORCH_LIBRARIES + IPEX_LIBRARIES
#   TORCH_IPEX_CXX_FLAGS    -- TORCH_CXX_FLAGS + IPEX_CXX_FLAGS
#
# and the following imported targets:
#
#   intel-ext-pt-cpu
#   intel-ext-pt-gpu

include(FindPackageHandleStandardArgs)

if(DEFINED ENV{IPEX_INSTALL_PREFIX})
  set(IPEX_INSTALL_PREFIX $ENV{IPEX_INSTALL_PREFIX})
else()
  # Assume we are in <install-prefix>/share/cmake/IPEX/IPEXConfig.cmake
  get_filename_component(CMAKE_CURRENT_LIST_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)
  get_filename_component(IPEX_INSTALL_PREFIX "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)
endif()

# Include directories.
if(EXISTS "${IPEX_INSTALL_PREFIX}/include")
  list(APPEND IPEX_INCLUDE_DIRS ${IPEX_INSTALL_PREFIX}/include)
endif()

# Library dependencies.
if(ON)
  find_library(IPEX_CPU_CORE_LIBRARY intel-ext-pt-cpu PATHS "${IPEX_INSTALL_PREFIX}/lib")
  list(APPEND IPEX_LIBRARIES_PRINT ${IPEX_CPU_CORE_LIBRARY})
  list(APPEND IPEX_LIBRARIES intel-ext-pt-cpu)
endif()

if(OFF)
  find_library(IPEX_GPU_CORE_LIBRARY intel-ext-pt-gpu PATHS "${IPEX_INSTALL_PREFIX}/lib")
  list(APPEND IPEX_LIBRARIES_PRINT ${IPEX_GPU_CORE_LIBRARY})
  list(APPEND IPEX_LIBRARIES intel-ext-pt-gpu)
endif()

if(ON)
  add_library(intel-ext-pt-cpu INTERFACE IMPORTED)
  set_target_properties(intel-ext-pt-cpu PROPERTIES
      IMPORTED_LOCATION "${IPEX_CPU_CORE_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${IPEX_INCLUDE_DIRS}"
      INTERFACE_LINK_LIBRARIES "-Wl,--no-as-needed,\"${IPEX_CPU_CORE_LIBRARY}\""
      CXX_STANDARD 14
  )
  if(IPEX_CXX_FLAGS)
    set_property(TARGET intel-ext-pt-cpu PROPERTY INTERFACE_COMPILE_OPTIONS "${IPEX_CXX_FLAGS}")
  endif()
  set(IPEX_WITH_CPU ON)
endif()

if(OFF)
  add_library(intel-ext-pt-gpu INTERFACE IMPORTED)
  set_target_properties(intel-ext-pt-gpu PROPERTIES
      IMPORTED_LOCATION "${IPEX_GPU_CORE_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${IPEX_INCLUDE_DIRS}"
      INTERFACE_LINK_LIBRARIES "-Wl,--no-as-needed,\"${IPEX_GPU_CORE_LIBRARY}\""
      CXX_STANDARD 17
  )
  if(IPEX_CXX_FLAGS)
    set_property(TARGET intel-ext-pt-gpu PROPERTY INTERFACE_COMPILE_OPTIONS "${IPEX_CXX_FLAGS}")
  endif()
  set(IPEX_WITH_XPU ON)
endif()

# Import Torch to simplify usage
FIND_PACKAGE(Torch REQUIRED)
if(TORCH_LIBRARIES)
  list(APPEND TORCH_IPEX_LIBRARIES ${TORCH_LIBRARIES})
  if(IPEX_LIBRARIES)
      list(APPEND TORCH_IPEX_LIBRARIES ${IPEX_LIBRARIES})
  endif()
endif()

find_package_handle_standard_args(IPEX DEFAULT_MSG IPEX_LIBRARIES_PRINT IPEX_INCLUDE_DIRS)
