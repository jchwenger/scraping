#!/bin/bash
# Found here:
# https://www.exratione.com/2014/11/how-to-politely-download-all-english-language-text-format-files-from-project-gutenberg/
#
# Download the complete archive of text format files from Project Gutenberg.
#
# Estimated size in Q2 2014: 7G in zipfiles which unzip to about 21G in text
# files. So have 30G spare if you run this.
#
# Note that as written here this is a 36 to 48 hour process on a fast
# connection, with pauses between downloads. This minimizes impact on the
# Project Gutenberg servers.
#
# You'll only have to do this once, however, and this script will pick up from
# where it left off if it fails or is stopped.
#

# ------------------------------------------------------------------------
# Preliminaries
# ------------------------------------------------------------------------

if [ $# -lt 1 ]; then
  echo "please choose a language, e.g. 'en', 'fr', etc."
  exit 1
fi

set -o nounset
set -o errexit

# Restrict downloads to this file format.
FORMAT=txt
# Restrict downloads to this language.
LANG=$1

# The directory in which this file exists.
DIR="$( cd "$( dirname "$0" )" && pwd)"
# File containing the list of zipfile URLs.
ZIP_LIST="${DIR}/links-zipfile.txt"
# A subdirectory in which to store the zipfiles.
ZIP_DIR="${DIR}/zipfiles"
# A directory in which to store the unzipped files.
UNZIP_DIR="${DIR}/files"

mkdir -p "${ZIP_DIR}"
mkdir -p "${UNZIP_DIR}"


# ------------------------------------------------------------------------
# Obtain URLs to download.
# ------------------------------------------------------------------------

# This step downloads ~700 html files containing ~38,000 zip file links. This
# will take about 30 minutes.

echo "-------------------------------------------------------------------------"
echo "Harvesting zipfile URLs for format [$FORMAT] in language [$LANG]."
echo "-------------------------------------------------------------------------"

# Only do this if it hasn't been done already.
if [ ! -f "${ZIP_LIST}" ] ; then

  echo "downloading list of zip files into '$ZIP_DIR'"
  echo ""

  # The --mirror mode of wget spiders through files listing links.
  # The two second delay is to play nice and not get banned.
  wget \
    --continue \
    --no-verbose \
    --wait=0.5 \
    --mirror \
    "http://www.gutenberg.org/robot/harvest?filetypes[]=${FORMAT}&langs[]=${LANG}"

  # Process the downloaded HTML link lists into a single sorted file of zipfile
  # URLs, one per line.
  grep -oh 'http://[a-zA-Z0-9./\-]*.zip' "${DIR}/www.gutenberg.org/robot/harvest"* | \
    sort | \
    uniq > "${ZIP_LIST}"

  # Get rid of the downloaded harvest files now that we have what we want.
  rm -Rf "${DIR}/www.gutenberg.org"

else
  echo "${ZIP_LIST} already exists. Skipping harvest."
fi


# ------------------------------------------------------------------------
# Download the zipfiles.
# ------------------------------------------------------------------------

# This will take a while: 36 to 48 hours. Just let it run. Project Gutenberg is
# a non-profit with a noble goal, so don't crush their servers, and it isn't as
# though you'll need to do this more than once.

echo "-------------------------------------------------------------------------"
echo "Downloading zipfiles. Starting with utf-8 encoding."
echo "See here: file types, cf. here: https://www.gutenberg.org/files/"
echo "-------------------------------------------------------------------------"
echo "Starting with -0"
echo "-------------------------------------------------------------------------"

for URL in $(cat "${ZIP_LIST}"| grep '\-0')
do
  echo "- ${URL##*/}"
  ZIP_FILE="${ZIP_DIR}/${URL##*/}" # only the very end, e.g. '8224.zip'
  # Only download it if it hasn't already been downloaded in a past run.
  wget \
    --no-verbose \
    --continue \
    --directory-prefix="${ZIP_DIR}" "${URL}"
  # # Play nice with a delay.
  # sleep 0.5
done

echo "-------------------------------------------------------------------------"
echo "Now to files with -8"
echo "-------------------------------------------------------------------------"

for URL in $(cat "${ZIP_LIST}"| grep '\-8')
do
  echo $URL
  ZIP_FILE="${ZIP_DIR}/${URL##*/}"
  ZIP_FILE_0=${ZIP_FILE%-8*}-0.zip
  exit 1
  # Only download it if it hasn't already been downloaded in a past run.
  if [ ! -f "${ZIP_FILE_0}" ] ; then
    wget \
      --no-verbose \
      --continue \
      --directory-prefix="${ZIP_DIR}" "${URL}"
    # # Play nice with a delay.
    # sleep 0.5
  else
    echo "A version of ${ZIP_FILE##*/} already exists. Skipping download."
  fi
done

echo "-------------------------------------------------------------------------"
echo "Finally, files with neither -0 nor -8."
echo "-------------------------------------------------------------------------"

for URL in $(cat "${ZIP_LIST}"| grep -P '(?<!\-[80])\.zip')
do
  echo $URL
  ZIP_FILE="${ZIP_DIR}/${URL##*/}"
  ZIP_FILE_0=${ZIP_FILE}-0.zip
  ZIP_FILE_8=${ZIP_FILE}-8.zip
  exit 1
  # Only download it if it hasn't already been downloaded in a past run.
  if [ ! -f "${ZIP_FILE_0}" ] && [ ! -f "${ZIP_FILE_8}" ]; then
    wget \
      --no-verbose \
      --continue \
      --directory-prefix="${ZIP_DIR}" "${URL}"
    # # Play nice with a delay.
    # sleep 0.5
  else
    echo "A version of ${ZIP_FILE##*/} already exists. Skipping download."
  fi
done

# ------------------------------------------------------------------------
# Unzip the zipfiles.
# ------------------------------------------------------------------------

echo "-------------------------------------------------------------------------"
echo "Unzipping files."
echo "-------------------------------------------------------------------------"

for ZIP_FILE in $(find ${ZIP_DIR} -name '*.zip')
do
  UNZIP_FILE=$(basename ${ZIP_FILE} .zip)
  UNZIP_FILE="${UNZIP_DIR}/${UNZIP_FILE}.txt"
  # Only unzip if not already unzipped. This check assumes that x.zip unzips to
  # x.txt, which so far seems to be the case.
  if [ ! -f "${UNZIP_FILE}" ] ; then
    unzip -o "${ZIP_FILE}" -d "${UNZIP_DIR}"
  else
    echo "${ZIP_FILE##*/} already unzipped. Skipping."
  fi
done
