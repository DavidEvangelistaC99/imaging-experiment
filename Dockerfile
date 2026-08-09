FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /root

# Install base packages
RUN apt-get update && \
    apt-get install -y \
        git curl sudo wget build-essential checkinstall cmake pkg-config yasm \
        gfortran python2-minimal python-dev python-cairo python-tk mencoder \
        libtiff5-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev \
        libdc1394-22-dev libxine2-dev libv4l-dev libgtk2.0-dev libtbb-dev \
        qt5-default libatlas-base-dev libfaac-dev libmp3lame-dev libtheora-dev \
        libvorbis-dev libxvidcore-dev libopencore-amrnb-dev libopencore-amrwb-dev \
        libavresample-dev x264 v4l-utils ffmpeg libgphoto2-dev libeigen3-dev \
        libhdf5-dev doxygen plplot-driver-cairo libopencv-dev python3-opencv \
        ubuntu-restricted-extras libavcodec58 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Fix header file link
RUN ln -s -f /usr/include/libv4l1-videodev.h /usr/include/linux/videodev.h

# Install pip2
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py && \
    python2 get-pip.py && \
    rm get-pip.py

# Install Python2 packages
RUN pip2 install \
        h5py==2.8.0 numpy==1.16.6 scipy==0.12.0 setuptools==38.2.5 \
        Cython version-utils matplotlib 

#swig

# Clone Imaging repository
RUN git clone https://github.com/joabAM/Imaging.git

# Clone and build plplot
# RUN git clone git://git.code.sf.net/p/plplot/plplot plplot.git && \
#     cd plplot.git && \
#     mkdir build_dir

ARG PLPLOT_VERSION=5.13.0

RUN git clone \
    --branch plplot-${PLPLOT_VERSION} \
    --depth 1 \
    https://github.com/PLplot/PLplot.git \
    plplot.git && \
    cd plplot.git && \
    mkdir build_dir

# Install Swig
RUN sudo apt-get update && apt-get install nano
RUN sudo apt update && sudo apt install -y swig


# --- HARDCODED ---
# You must modify plplot.git/cmake/modules/python.cmake to:
# option(FORCE_PYTHON2 "Force Python2 even when Python 3 is present" OFF)
# → change OFF to ON
# RUN sed -i 's/option(FORCE_PYTHON2 "Force Python2 even when Python 3 is present" OFF)/option(FORCE_PYTHON2 "Force Python2 even when Python 3 is present" ON)/' plplot.git/cmake/modules/python.cmake


# Build and install plplot
WORKDIR /root/plplot.git/build_dir
# RUN cmake -DCMAKE_INSTALL_PREFIX=/usr/local .. > cmake.out && \
#     make -j$(nproc) VERBOSE=1 > make.out && \
#     make install VERBOSE=1 > make_install.out

RUN cmake \
    -DCMAKE_INSTALL_PREFIX=/usr/local \
    -DFORCE_PYTHON2=ON \
    .. > cmake.out && \
    make -j$(nproc) VERBOSE=1 > make.out && \
    make install VERBOSE=1 > make_install.out

# Final installation step for Imaging
WORKDIR /root/Imaging
RUN bash ./installImaging

# Set default command
CMD ["/bin/bash"]

