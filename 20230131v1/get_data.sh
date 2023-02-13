#!/bin/sh
while IFS=, read -r url short_url
do
  curl --header "x-api-key: 8mH99xWXoi60vMDfkSJtb6zVhSLiSgNP8ewg3nlZ" $url > $2/$short_url
done < $1
