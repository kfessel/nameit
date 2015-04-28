cmake_minimum_required(VERSION 2.8.3)
project(nameit)

find_package(catkin REQUIRED COMPONENTS rospy message_generation std_msgs sensor_msgs)

add_message_files(DIRECTORY msg FILES DescriptionTags.msg WordOccurrence.msg)
add_service_files(DIRECTORY srv FILES NameItGoogle.srv)

generate_messages(DEPENDENCIES std_msgs sensor_msgs)

catkin_package(CATKIN_DEPENDS message_runtime std_msgs)

#add_dependencies(${PROJECT_NAME} ${PROJECT_NAME}_genpy)

# do not wildcard install files since the root folder of the package will contain a debian folder for releasing
catkin_install_python(PROGRAMS
  nameit/google_sbi_tagit.py
  nameit/google_name_it
  nameit/nameit_client
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

# 
# if(CATKIN_ENABLE_TESTING)
#   find_package(rostest)
#   foreach(T
#       test/test-add-two-ints.launch
#       test/test-peer-subscribe-notify.launch
#       test/test-add-two-ints-with-roscpp-server.launch
#       test/test-talker-listener.launch
#       test/test-talker-listener-with-roscpp.launch
#       test/test-on-shutdown.launch
#       test/test-connection-header.launch)
#      add_rostest(${T})
#   endforeach()
# endif()
