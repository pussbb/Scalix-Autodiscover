#!/bin/bash

RPM_BUILD=$(type -p rpmbuild)
CURRENT_DIR="$(realpath `dirname "$0"`)"
BUILD_DIR="$CURRENT_DIR/build/"
SOURCE_ARCHIVE="$BUILD_DIR/SOURCES/scalix-autodiscover.tar.gz"

if [ -d "$BUILD_DIR" ] ; then
    rm -rf "$BUILD_DIR"
fi

mkdir -p "$BUILD_DIR/SOURCES/scalix-autodiscover"

cp -r "$CURRENT_DIR/dist_template/." "$BUILD_DIR/SOURCES/scalix-autodiscover/"
cp "$CURRENT_DIR/autodiscover.py" "$BUILD_DIR/SOURCES/scalix-autodiscover/opt/scalix-autodiscover/cgi/"
tar -czvf "$SOURCE_ARCHIVE" -C "$BUILD_DIR/SOURCES/scalix-autodiscover/" .

if [ -n "$RPM_BUILD" ]; then
    $RPM_BUILD -ba --define "_topdir $BUILD_DIR" "$CURRENT_DIR/scalix-autodiscover.spec"
    find "$BUILD_DIR/RPMS/" -name "scalix-*.rpm" -exec cp -fL {} "$CURRENT_DIR/"  \;
else
    echo "rpm command not found . Can not build rpm file"
fi

DPKG_DEB=$(type -p dpkg-deb)
if [ -n "$RPM_BUILD" ]; then
    cp -r ./DEBIAN/ "$BUILD_DIR/SOURCES/scalix-autodiscover/"
    $DPKG_DEB -b "$BUILD_DIR/SOURCES/scalix-autodiscover/" ./
else
    echo "dpkg-deb command not found . Can not build deb file"
fi
