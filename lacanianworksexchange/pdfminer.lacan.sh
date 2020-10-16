#!/bin/bash

if [[ ! -d pdf ]]
then
  echo "pdf/ dir not found, please scrape first"
  exit 1
fi

if [[ ! -d miner ]]
then
  mkdir miner
  echo "creating dir miner/"
fi

echo "----------------------------------------"
for i in pdf/*.pdf
do
  if [[ ! -f $i ]]
  then
    echo "processing: ${i#pdf\/}"
    pdf2txt.py $i -t text -o miner/$(basename ${i/.pdf/.txt})
  else
    echo "found $i"
  fi
done
echo "----------------------------------------"
