#!/bin/bash

# Functions to override in bpt-rules

bpt_download() {
    true
}

bpt_unpack() {
    true
}

bpt_build() {
    echo 'Unimplemented bpt_build!'
    false
}

bpt_unittest() {
    true
}

bpt_clean() {
    true
}

bpt_deepclean() {
    true
}

# Utility functions that can be used in bpt-rules

bpt_get() {
    SERVER_URL="$1"
    FILENAME="$2"
    MD5SUM="$3"

    if [ ! -e "$FILENAME" ]
    then
        wget "$SERVER_URL/$FILENAME"
    else
        echo "$FILENAME already downloaded"
    fi

    # Check MD5
    if [ "x$MD5SUM" != "x" ] 
    then 
        if (! (echo "$MD5SUM  $FILENAME" | md5sum -c))
        then 
            echo Failed checksum for "$FILENAME". Try removing it
            exit 1
        fi
    fi
}


