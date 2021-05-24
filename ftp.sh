#!/usr/bin/bash


ftp ftp.ngdc.noaa.gov
cd /ionosonde/data/WI937/individual/2021/001/scaled/
ls *.EDP

get WI937_2021001000000.EDP
mget *.EDP

# https://tecadmin.net/download-upload-files-using-ftp-command-line/
