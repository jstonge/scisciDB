#!/bin/bash
source=$1
corpus=$2

# Pull data from relevant source

# get_data() {
#   while IFS=, read -r url short_url; do
#       curl --header "x-api-key: 8mH99xWXoi60vMDfkSJtb6zVhSLiSgNP8ewg3nlZ" $url > 20230131v1/$corpus/$short_url
#     done < 20230131v1/$corpus/2023-01-31_$corpus.csv
# }

# if [ $source = "s2" ]
# then
#   echo "Doing s2"
#   echo "Grabbing data urls"
#   python pull_data.py $corpus
#   nb_urls_to_do=`cat 20230131v1/$corpus/2023-01-31_$corpus.csv | wc -l`
#   echo "We have $nb_urls_to_do urls to do"

#   while [ $nb_urls_to_do -gt 0 ]
#   do
#   get_data 
#   echo "unzipping..." 
#   gzip -d 20230131v1/$corpus/*gz 
#   # Remove files who failed to be unzipped
#   rm 20230131v1/$corpus/*gz
#   # Get the urls left
#   python pull_data.py $corpus
#   nb_urls_to_do=`cat 20230131v1/$corpus/2023-01-31_$corpus.csv | wc -l`
#   echo "We have $nb_urls_to_do urls to do"
#   done
# else
#   echo "pull data from openalex"
#   # if first time
#   # aws s3 sync "s3://openalex" "openalex-snapshot" --no-sign-request
#   # else 
#   # aws s3 sync --delete "s3://openalex" "openalex-snapshot" --no-sign-request
# fi

# Push data mongoDB

echo "Uploading data to mongoDB"
python push_mongoDB.py -s $source -c $corpus