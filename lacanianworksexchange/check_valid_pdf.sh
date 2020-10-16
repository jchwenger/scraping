#!/bin/bash

# https://superuser.com/a/580895

for i in pdf/*
do
  if ! pdfinfo "$i" &> /dev/null
  then
    echo "$i is broken, removing"
    rm "$i"
  fi
done

