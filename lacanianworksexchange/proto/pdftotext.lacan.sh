#!bin/bash

if [[ ! -d txt ]]
then
  echo "creating dir txt/"
  mkdir txt
fi

echo "----------------------------------------"
for i in pdf/*.pdf;
do
  fname=$(basename ${i%pdf}txt)
  if [ ! -f txt/$fname ]
  then
    echo "converting $i"
    pdftotext $i
    mv ${i%pdf}txt txt
  else
    echo "found $fname, no need to convert"
  fi
done
echo "----------------------------------------"
