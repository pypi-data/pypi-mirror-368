cmake_minimum_required(VERSION 3.22.1)

#for building the python module. Should be similar to the one in the android project

#TODO: this file needs work

if(NOT DEFINED SKBUILD)
    set(SKBUILD_PROJECT_NAME "zrod")
    set(MODULE_NAME ${SKBUILD_PROJECT_NAME})
endif()


project(${SKBUILD_PROJECT_NAME})
set(MODULE_NAME ${SKBUILD_PROJECT_NAME})
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
#set(CMAKE_C_COMPILER /usr/bin/cc)
#set(CMAKE_CXX_COMPILER /usr/bin/c++)

set(CMAKE_CXX_STANDARD 20)

#set(CMAKE_CXX_VISIBILITY_PRESET hidden)
#set(CMAKE_VISIBILITY_INLINES_HIDDEN YES)

# Preventing writes to package registry by default
#set(CMAKE_EXPORT_NO_PACKAGE_REGISTRY YES)




if(NOT WIN32)
    string(ASCII 27 Esc)
    set(ColorReset "${Esc}[m")
    set(ColorBold  "${Esc}[1m")
    set(Red         "${Esc}[31m")
    set(Green       "${Esc}[32m")
    set(Yellow      "${Esc}[33m")
    set(Blue        "${Esc}[34m")
    set(Magenta     "${Esc}[35m")
    set(Cyan        "${Esc}[36m")
    set(White       "${Esc}[37m")
    set(BoldRed     "${Esc}[1;31m")
    set(BoldGreen   "${Esc}[1;32m")
    set(BoldYellow  "${Esc}[1;33m")
    set(BoldBlue    "${Esc}[1;34m")
    set(BoldMagenta "${Esc}[1;35m")
    set(BoldCyan    "${Esc}[1;36m")
    set(BoldWhite   "${Esc}[1;37m")
endif()


#use to toggle the AWS code in zrod.cpp
add_definitions(
    -DUSE_AWS_SDK #TODO: this should be eliminated once the aws code is fully implemented and stable
    -DJWT_DISABLE_PICOJSON
    -DSQLITE_CORE
)

message(STATUS "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx CMAKE PYTHON BUILD CONTENTS")


if(WIN32)
    #set_target_properties(zrod PROPERTIES LINK_FLAGS "/WHOLEARCHIVE")
    message(STATUS "${Red} Only building for WINDOWS ${ColorReset}")

    set(INCOPENSSL_PATH c:/Users/walter/GitRepos/wansco-aws-sdk-cpp/dist/windows/Release/include)

    set(INCCURL_PATH c:/Users/walter/GitRepos/wansco-aws-sdk-cpp/dist/windows/Release/include)
    set(LIBCURL_PATH c:/Users/walter/GitRepos/wansco-aws-sdk-cpp/dist/windows/Release/lib)

    set(INCAWS_PATH c:/Users/walter/GitRepos/wansco-aws-sdk-cpp/dist/windows/Release/include)
    set(LIBAWS_PATH c:/Users/walter/GitRepos/wansco-aws-sdk-cpp/dist/windows/Release/lib)

    #set(CMAKE_PREFIX_PATH "${LIBAWS_PATH}/lib/cmake")
elseif(APPLE)
    message(STATUS "${Red} Only building for ARM Macs ${ColorReset}")

    #TODO: move the includes to "apple" or some other folder
    set(INCOPENSSL_PATH $ENV{HOME}/GitRepos/wansco-aws-sdk-cpp/dist/macosx/include)

    set(INCCURL_PATH $ENV{HOME}/GitRepos/wansco-aws-sdk-cpp/dist/macosx/include)
    set(LIBCURL_PATH $ENV{HOME}/GitRepos/wansco-aws-sdk-cpp/dist/macosx/lib)

    set(INCAWS_PATH $ENV{HOME}/GitRepos/wansco-aws-sdk-cpp/dist/macosx/include)
    set(LIBAWS_PATH $ENV{HOME}/GitRepos/wansco-aws-sdk-cpp/dist/macosx/lib)

    #set(CMAKE_C_COMPILER "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang")
    #set(CMAKE_CXX_COMPILER "/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang++")

    #set(CMAKE_PREFIX_PATH "${LIBAWS_PATH}/lib/cmake")
else() #Linux
    message(STATUS "${Red} Only building for Linux ${ColorReset}")

    #TODO: switch this to the aws build of curl
    #set(INCCURL_PATH $ENV{HOME}/GitRepos/curl/include)
    #set(LIBCURL_PATH $ENV{HOME}/GitRepos/curl/artifacts/lib)

    set(INCAWS_PATH $ENV{HOME}/GitRepos/wansco-aws-sdk-cpp/dist/linux/include)
    set(LIBAWS_PATH $ENV{HOME}/GitRepos/wansco-aws-sdk-cpp/dist/linux/lib)

    #not sure why s2n is only on linux
    set(s2n_DIR "${LIBAWS_PATH}/s2n/cmake")
    find_package(s2n REQUIRED)
endif()


#set(AWSSDK_ROOT_DIR "${LIBAWS_PATH}/cmake")
set(CMAKE_PREFIX_PATH "${CMAKE_PREFIX_PATH}" "${LIBAWS_PATH}/cmake")

#set(CMAKE_FIND_DEBUG_MODE TRUE)
find_package(AWSSDK REQUIRED COMPONENTS s3 dynamodb cognito-identity cognito-idp)
#set(CMAKE_FIND_DEBUG_MODE FALSE)
#message(FATAL_ERROR "You did something wrong!")

#set(CMAKE_PREFIX_PATH "$ENV{HOME}/GitRepos/curl/CMake")
#find_package(curl REQUIRED)

#set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fvisibility=hidden")

if(DEFINED SKBUILD)
    message(STATUS "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxThe project is built using scikit-build")
    #find_package(PythonExtensions REQUIRED)
    find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
endif()



if(WIN32)
    set(SRC_PATH c:/Users/walter/GitRepos/zrodapp/zrodapp/ios/zrod/cpp)
else() #everything else
    #add_subdirectory($ENV{HOME}/GitRepos/zrodapp/zrodapp/ios/zrod/cpp)
    set(SRC_PATH $ENV{HOME}/GitRepos/zrodapp/zrodapp/ios/zrod/cpp)
endif()


include_directories(
    ${INCAWS_PATH}
    ${INCOPENSSL_PATH}
    ${SRC_PATH} #needed this for #include <sqlite3ext.h>
    #${Python3_INCLUDE_DIRS}
)


message("==================================")
#message($ENV{HOME})
#message(${SRC_PATH})
#set(CMAKE_C_COMPILER "clang")
#set(CMAKE_CXX_COMPILER "clang++")
#set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-rpath='$ORIGIN'")

#set(CMAKE_CXX_MODULE_STD 1)
#set(CMAKE_CXX_FLAGS "-stdlib=libc++")


find_package(ZLIB)
#find_package(CURL)
#find_package(CURL)
#find_package(openssl)
#find_package(crypto)
#find_package(aws-cpp-sdk-core CONFIG REQUIRED)
#find_package(aws-c-auth CONFIG REQUIRED)
#find_package(aws-c-common CONFIG REQUIRED)
#find_package(aws-cpp-sdk-core CONFIG REQUIRED)
#find_package(aws-crt-cpp CONFIG REQUIRED)
#find_package(aws-c-s3 CONFIG REQUIRED)
#find_package(aws-cpp-sdk-s3 CONFIG REQUIRED)
#find_package(aws-cpp-sdk-dynamodb CONFIG REQUIRED)
#find_package(aws-cpp-sdk-cognito-identity CONFIG REQUIRED)
#find_package(aws-cpp-sdk-cognito-idp CONFIG REQUIRED)


if(WIN32)
    #set_target_properties(zrod PROPERTIES LINK_FLAGS "/WHOLEARCHIVE")
elseif(APPLE)
    #set_target_properties(zrod PROPERTIES LINK_FLAGS "-Wl,-all_load")
else() #Linux
    #set_target_properties(zrod PROPERTIES LINK_FLAGS "-Wl,--whole-archive")
endif()
#set(CMAKE_SHARED_LINKER_FLAGS "-Wl,--export-all-symbols")


if(DEFINED SKBUILD)
    #python_extension_module(libzrod)
    python_add_library(${MODULE_NAME} MODULE
        ${SRC_PATH}/zrod.cpp
        ${SRC_PATH}/pugixml.cpp
        ${SRC_PATH}/RodData.cpp
        ${SRC_PATH}/PumpingUnitData.cpp
        ${SRC_PATH}/awslink.cpp
        ${SRC_PATH}/csv.c
        ${SRC_PATH}/sqlite3.c
        WITH_SOABI
        ${FILENAME}
        #libzrod.so
    )
else()
    add_library(${MODULE_NAME} SHARED
        ${SRC_PATH}/zrod.cpp
        ${SRC_PATH}/pugixml.cpp
        ${SRC_PATH}/RodData.cpp
        ${SRC_PATH}/PumpingUnitData.cpp
        ${SRC_PATH}/awslink.cpp
        ${SRC_PATH}/csv.c
        ${SRC_PATH}/sqlite3.c
    )
endif()




target_link_libraries(${MODULE_NAME} PRIVATE
    -L${LIBAWS_PATH}
    #aws-c-auth
    #aws-c-cal
    #aws-c-common
    #aws-c-compression
    #aws-c-event-stream
    #aws-c-http
    #aws-c-io
    #aws-c-mqtt
    #aws-c-s3
    #aws-c-sdkutils
    #aws-checksums

    #aws-cpp-sdk-core
    #aws-crt-cpp
    #aws-cpp-sdk-s3

    aws-cpp-sdk-dynamodb
    aws-cpp-sdk-cognito-identity
    aws-cpp-sdk-cognito-idp
)


#install(TARGETS zrod LIBRARY DESTINATION libzrod)
install(TARGETS ${MODULE_NAME} DESTINATION ${SKBUILD_PROJECT_NAME})


#[===[

]===]
