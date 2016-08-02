#! /usr/bin/env python
# encoding: utf-8

from waflib.Configure import conf

@conf
def check_opencv(conf):
    # possible path to find headers
    includes_check = ['/usr/local/include/opencv2', '/usr/local/include/opencv2/core']
    libs_check = ['/usr/local/lib', '/usr/lib']
    try:
      conf.start_msg('Checking for opencv includes')
      include_files = ['opencv.hpp', 'mat.hpp']
      for file in include_files:
        conf.find_file(file, includes_check)
      conf.end_msg('got it!')
      conf.env.INCLUDES_OPENCV = includes_check

      conf.start_msg('Checking for opencv libs')
      lib_files = ['opencv_core','opencv_highgui','opencv_imgproc','opencv_calib3d','opencv_contrib','opencv_features2d','opencv_flann','opencv_gpu','opencv_legacy','opencv_objdetect','opencv_ocl','opencv_photo','opencv_stitching','opencv_superres','opencv_video','opencv_videostab']
      for file in lib_files:
        conf.find_file('lib'+file+'.so', libs_check)
        #print "Found file {}".format(file)
      conf.end_msg('got it!')
      conf.env.LIBPATH_OPENCV = libs_check
      conf.env.LIB_OPENCV = lib_files
    except:
      conf.fatal('opencv not found')
      return
