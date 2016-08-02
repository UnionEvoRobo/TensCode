#! /usr/bin/env python

import limbo

import opencv

def configure(conf):
    conf.load('opencv')
    conf.check_opencv()
    print("LOADED OPENCV")

def options(opt):
    pass

def build(bld):
    bld(features='cxx cxxprogram',
        source='main.cpp serial.cpp tracker.cpp',
        includes='. ../../src',
        target='tens',
        uselib='BOOST EIGEN TBB LIBCMAES NLOPT OPENCV',
        use='limbo OPENCV')

    bld(features='cxx cxxprogram',
        source='test-controller.cpp serial.cpp',
        includes='. ../../src',
        uselib='BOOST EIGEN',
        target='test-tens')
