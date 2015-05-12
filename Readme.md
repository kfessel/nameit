#NameIt

Nameit contains a Google search by image (sbi) interface written in Python. It contains a standalone version or may be used as a Python module. This is used by the included ROS-Service.

The web-page-results are parsed using regular expressions which makes the module sensitive to changes on Google servers since no API is used.

It uploads the picture to Google sbi searches the result for Tags which would be used for a Google search regarding the Image and searches the similar Image Pages parsing their Descriptions for words and bigrams counting them and returning the most common.

Google accepts many image formats (e.g. png jpeg bmp gif webm) for incompatible formats the module just gives no results (no error to try fetch).

The ROS Package may be build and installed using catkin.