# recursive, no directories, save in pdf/, no-clobber (no re-downloading if file already present, accepting pdf format
wget \
  --recursive \
  --no-clobber \
  --no-directories \
  --directory-prefix pdf \
  --accept pdf \
  https://www.lacanianworksexchange.net/lacan
