.PHONY: get_data_from_s2orc uncompress_everything sort_and_bucketize subset_abstract create_s2fos_lookup augment_s2orc_with_s2fos
.SUFFIXES:

get_data_from_s2orc:
	# Update with personal script sent by Kyle Lo 
	sh presign_urls_dl_s2orc_20200705v1_full_urls_expires_20220907.sh

uncompress_everything: 20200705v1
	gunzip full/metadata/* && \
	gunzip full/pdf_parses/*

sort_and_bucketize: output/metadata_by_decade_all/
	python bucketized_metadata.py

subset_abstract: output/metadata_by_decade_all/metadata_*_all_simple_has_abstract.jsonl
	for i in $(seq 1950 10 2020); do python subset_metadata_by_decade.py --decade $i --parse abstract; done

create_s2fos_lookup: output/s2fos_lookup
	# Run on the Vacc
	for file in $(ls get_s2fos_lookup_vacc/*.sh); do sbatch $file; done;

augment_s2orc_with_s2fos:
	python augment_s2fos.py --decade 1950 --lookup 'metadata_195*'
	python augment_s2fos.py --decade 1960 --lookup 'metadata_196*'
	python augment_s2fos.py --decade 1970 --lookup 'metadata_197*'
	python augment_s2fos.py --decade 1980 --lookup 'metadata_198*'
	python augment_s2fos.py --decade 1990 --lookup 'metadata_199*'
	python augment_s2fos.py --decade 2000 --lookup 'metadata_200*'
	python augment_s2fos.py --decade 2010 --lookup 'metadata_201*'
	python augment_s2fos.py --decade 2020 --lookup 'metadata_202*'

query_s2searchAPI: output/s2search_data/*
	# done interactively with `s2searchAPI.py`

query_specterAPI: output/specterAPI
	# Run on the Vacc
	sh specterAPI_vacc.sh

 
	
