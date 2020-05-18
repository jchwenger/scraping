if [ $# -lt 1 ]; then
  echo $#
  echo "please choose a language code from the following:"
  curl -is https://oscar-corpus.com/ | grep -Po "(?<=/)[a-z]+(?=\.txt\.gz)" | sort | uniq
  echo "---"
  echo "Cf. here: https://traces1.inria.fr/oscar/"
  exit 1
fi

DL_DIR="oscar"
if [ ! -d $DL_DIR ]; then
  mkdir $DL_DIR
fi

LANG=$1
echo "downloading the OSCAR dataset (deduplicated) in '$LANG' into $DL_DIR."
echo "from: https://traces1.inria.fr/oscar/"
echo "(this will probably take hours...)"
echo "---------------------"
echo ""

wget \
  --continue \
  --directory-prefix $DL_DIR \
  https://traces1.inria.fr/oscar/files/Compressed/${LANG}_dedup.txt.gz

