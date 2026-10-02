cmake_minimum_required(VERSION 3.25)
project(vtr_pon_atem_addon VERSION 0.3.0 LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT WIN32 OR NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
  message(FATAL_ERROR "This add-on supports Windows x64 only.")
endif()
set(VTRPON_ATEM_SDK_DIR "" CACHE PATH "Blackmagic ATEM Switchers SDK Windows directory")
set(_sdk_include "${VTRPON_ATEM_SDK_DIR}/include")
if(NOT EXISTS "${_sdk_include}/BMDSwitcherAPI.idl")
  message(FATAL_ERROR "Set VTRPON_ATEM_SDK_DIR to the ATEM SDK Windows directory.")
endif()
find_program(MIDL_EXECUTABLE midl REQUIRED)
set(_generated "${CMAKE_CURRENT_BINARY_DIR}/generated")
file(GLOB _idl_dependencies CONFIGURE_DEPENDS
  "${_sdk_include}/*.idl" "${_sdk_include}/Legacy/*.idl")
add_custom_command(
  OUTPUT "${_generated}/BMDSwitcherAPI.h"
         "${_generated}/BMDSwitcherAPI_i.c"
         "${_generated}/BMDSwitcherAPI.tlb"
  COMMAND "${CMAKE_COMMAND}" -E make_directory "${_generated}"
  COMMAND "${MIDL_EXECUTABLE}" /nologo /env x64 /out "${_generated}"
          /h BMDSwitcherAPI.h /iid BMDSwitcherAPI_i.c
          /tlb BMDSwitcherAPI.tlb "${_sdk_include}/BMDSwitcherAPI.idl"
  DEPENDS ${_idl_dependencies}
  WORKING_DIRECTORY "${_sdk_include}"
  VERBATIM)
set_source_files_properties("${_generated}/BMDSwitcherAPI_i.c" PROPERTIES
  GENERATED TRUE LANGUAGE CXX)
add_library(vtr-pon-atem-addon SHARED
  src/vtrpon_atem_switcher_addon.cpp
  "${_generated}/BMDSwitcherAPI_i.c")
target_include_directories(vtr-pon-atem-addon PRIVATE include "${_generated}")
target_compile_definitions(vtr-pon-atem-addon PRIVATE
  NOMINMAX WIN32_LEAN_AND_MEAN VTRPON_SWITCHER_ADDON_BUILD=1)
target_link_libraries(vtr-pon-atem-addon PRIVATE ole32 oleaut32)
if(MSVC)
  target_compile_options(vtr-pon-atem-addon PRIVATE /utf-8)
endif()
set_target_properties(vtr-pon-atem-addon PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/switcher-addons")
install(TARGETS vtr-pon-atem-addon RUNTIME DESTINATION switcher-addons)
