cmake_minimum_required( VERSION 3.5 )
project( backend )

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
#set(CMAKE_CXX_EXTENSIONS OFF)
# Add ARLib directory
add_subdirectory(external/arlib)

add_executable(main main.cpp engine.cpp network.cpp message.cpp utils.cpp)
target_link_libraries(main PUBLIC arlib)

