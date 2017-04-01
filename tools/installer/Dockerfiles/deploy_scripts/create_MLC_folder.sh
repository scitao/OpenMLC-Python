#!/bin/bash
MLC_PATH="/tmp/MLC-$RELEASE"
# Create the containing folder
mkdir -p $MLC_PATH/tools
ENTRYPOINT ["/tmp/deploy_scripts/create_MLC_folder.sh"]

# Download the MLC code from Github
wget "https://github.com/Ezetowers/MLC/archive/v$RELEASE.tar.gz"
tar xzvf v$RELEASE.tar.gz -C $MLC_PATH
rm -rf /tmp/v$RELEASE.tar.gz

# Add the mlc_python
cp -r /opt/mlc-python-2.7.11 $MLC_PATH/mlc_python

# Add project scripts
cp -r /tmp/deploy_scripts/mlc.sh.in $MLC_PATH/mlc.sh
sed -i "s/^\([^@]*\)@\([^@]*\)@$/\1$RELEASE/" $MLC_PATH/mlc.sh
cp -r /tmp/deploy_scripts/install_matlab_engine.sh $MLC_PATH/tools

# Create symbolic links to mlc_python and mlc_ipython
cd $MLC_PATH
ln -s mlc_python/bin/mlc_python mlc_python.sh
ln -s mlc_python/bin/mlc_ipython mlc_ipython.sh
ln -s mlc_python/bin/mlc_pip mlc_pip.sh

# Clean unnecesary files in the MLC package
find $MLC_PATH/mlc_python -name "*.pyc" | xargs rm -rf
find $MLC_PATH/mlc_python -name "*.pyo" | xargs rm -rf
find $MLC_PATH/mlc_python -name "*.pyd" | xargs rm -rf
find $MLC_PATH/mlc_python -name "test" | xargs rm -rf
rm -rf $MLC_PATH/Qt-5.7.1/docs
rm -rf $MLC_PATH/Qt-5.7.1/include
rm -rf $MLC_PATH/Qt-5.7.1/mkspecs

# Create the MLC Package
tar cJvpf /tmp/MLC-$RELEASE-$OS_VERSION.tar.xz -C /tmp MLC-$RELEASE
fpm -s dir -t $PACKAGE_TYPE -v $RELEASE -n mlc-python-$OS_VERSION /opt/mlc-python-2.7.11
bash