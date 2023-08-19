# Set the base path of the satellite model
# set(BASE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/src/satellite/model)
# set(DATA_PATH ${BASE_PATH}/data)

# Compiler flags (Assuming C++11 standard)
# set(CMAKE_CXX_STANDARD 11)
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")

# Build the executable for constants-gen.cc
# add_executable(cgen ${DATA_PATH}/constants-gen.cc)

# Add custom target to generate header and source files
#add_custom_target(GenerateHeaderSource
#  COMMAND ${CMAKE_COMMAND} -E make_directory ${BASE_PATH}
#  COMMAND ${CMAKE_COMMAND} -E echo "Generating header and source files..."
#  COMMAND ./cgen header ${BASE_PATH}
#  COMMAND ./cgen source ${BASE_PATH}
#  WORKING_DIRECTORY ${DATA_PATH}
#  DEPENDS cgen
#)

# Include directories
set(header_files
    model/iers-data.h
    model/julian-date.h
    model/satellite.h
    model/satellite-position-helper.h
    model/satellite-position-mobility-model.h
    model/sgp4ext.h
    model/sgp4io.h
    model/sgp4unit.h
    model/vector-extensions.h
)
# List of source files for the satellite module
set(source_files
    model/iers-data.cc
    model/julian-date.cc
    model/satellite.cc
    model/satellite-position-helper.cc
    model/satellite-position-mobility-model.cc
    model/sgp4ext.cpp
    model/sgp4io.cpp
    model/sgp4unit.cpp
    model/vector-extensions.cc
)
build_lib(
    LIBNAME satellite
    SOURCE_FILES ${source_files}
    HEADER_FILES ${header_files}
    LIBRARIES_TO_LINK
        ${libcore}
        ${libmobility}
)
# Create the satellite module library
# add_library(${PROJECT_NAME} MODULE ${SOURCE_FILES})

# Add dependency on GenerateHeaderSource target before building the library
# add_dependencies(${PROJECT_NAME} GenerateHeaderSource)

# Link the satellite module library with NS3 core and mobility libraries
# target_link_libraries(${PROJECT_NAME} PUBLIC ns3::core ns3::mobility)