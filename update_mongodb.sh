#!/bin/bash
#SBATCH --partition=bluemoon
#SBATCH --nodes=1
#SBATCH --time=29:59:59
#SBATCH --job-name=get_data
source=$1
corpus=$2

# Pull data from relevant source --------------------------------------------

get_data() {
  while IFS=, read -r url short_url; do
      curl --header "x-api-key: 8mH99xWXoi60vMDfkSJtb6zVhSLiSgNP8ewg3nlZ" $url > $corpus/$short_url
    done < $corpus/2023-01-31_$corpus.csv
}

if [ $source = "s2" ]
then
  echo "Doing s2"
  echo "Grabbing data urls"
  python pull_data.py $corpus
  nb_urls_to_do=`cat $corpus/2023-01-31_$corpus.csv | wc -l`
  echo "We have $nb_urls_to_do urls to do"

  while [ $nb_urls_to_do -gt 0 ]
  do
  get_data 
  echo "unzipping..." 
  gzip -d $corpus/*gz 
  # Remove files who failed to be unzipped
  rm $corpus/*gz
  # Get the urls left
  python grab_data_urls.py $corpus
  nb_urls_to_do=`cat $corpus/2023-01-31_$corpus.csv | wc -l`
  echo "We have $nb_urls_to_do urls to do"
  done
else
  echo "pull data from openalex"
  # if first time
  # aws s3 sync "s3://openalex" "openalex-snapshot" --no-sign-request
  # else 
  # aws s3 sync --delete "s3://openalex" "openalex-snapshot" --no-sign-request
fi

# Push data mongoDB ----------------------------------------------------

echo "Uploading data to mongoDB"
python push_mongoDB.py -s $source -c $corpus