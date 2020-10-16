#!/bin/bash

# removing line feed, harmonising all in \n
# in place, -p for loop over line like sed, -e one line program
# https://superuser.com/a/1472126
perl -i -pe 's/\R/\n/g' clean/*
