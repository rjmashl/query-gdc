#!/bin/bash

# Manifest with a column of file ids
FILE=$1

TOKEN=/home/rmashl/tokens/mytoken.txt

# Apply CLI tools to extract file ids
#for f in $(tail -n +2   $FILE  | cut -f1); do
for f in $(cat  $FILE | grep -v ^gdc_file_id | grep -v ^# | cut -f1 ); do
    echo $f

    # default server per config file
    #./gdc-client download --config ./gdc-client.conf                                          -t $TOKEN $f

    # override default server
    ./gdc-client download --config ./gdc-client.conf  -s https://api.awg.gdc.cancer.gov      -t $TOKEN $f
done
