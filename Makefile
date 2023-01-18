.PHONY: clean 20200705v1 data/metadata_by_decade parse_abstract data/s2FOS_lookup augment_s2orc_with_s2fos data/specterAPI/computational-%.json
.SUFFIXES:

raw_metadata_files := $(wildcard 20200705v1/full/metadata/*.jsonl)
metadata_by_decade_dir = "data/metadata_by_decade"
s2fields_todo = 'Agricultural and Food Sciences' 'Materials Science'
specter_dir = "data/specterAPI"
s2search_dir = "data/s2search_data"


clean:
	rm -rf data/metadata_by_decade data/s2FOS_lookup

20200705v1:
	# Update with personal script sent by Kyle Lo 
	sh presign_urls_dl_s2orc_20200705v1_full_urls_expires_20220907.sh
	gunzip 20200705v1/full/metadata/* && gunzip 20200705v1/full/pdf_parses/

data/metadata_by_decade: 
	for file in $(raw_metadata_files); do \
		python src/bucketize.py --input_file $$file --output_dir $@; \
	done

parse_abstract: data/metadata_by_decade/*all.jsonl
	for i in $$(seq 1950 10 2020); do \
		python src/subset_metadata_by_decade.py --input_dir $(metadata_by_decade_dir) \
												--decade $$i \
												--parse abstract; \
	done

data/s2FOS_lookup:
	cd src && \
	python get_s2fos_lookup2vac.py --input_path ../data/metadata_by_decade --batch_size 75000 --destfile tmp && \
	for file in $$(ls tmp/*.sh); do sh $$file; done; 
	rm -rf src/tmp

augment_s2orc_with_s2fos:
	for file in $$(ls data/metadata_by_decade/*_all.jsonl); do \
		python src/augment_s2fos.py --input_file $$file 
									--lookup_dir data/s2FOS_lookup; \
	done

# Quantifying computational works ------------------------------------------------------------------------

data/s2search_data:
	for fOS in $(s2fields_todo); do \
		python src/query_s2searchAPI/s2searchAPI.py -q computational --fOS $$fOS --output_dir $@; \
		sleep 300; \
	done


# $(specter_dir)/computational-%.json: $(s2search_dir)/computational-%.pqt 
# 	python src/query_s2searchAPI/specterAPI2vacc.py --fname $< -o '.'
# sbatch run_specter_on_vacc.sh

# for file in $$(ls data/s2search_data/*.pqt); do \
# 	python src/query_specterAPI/specterAPI2vacc.py --fname $$file; \
# 	sbatch tmp.sh; \
# done 
# rm run_specter_on_vacc.sh


# query_specterAPI: output/specterAPI
# 	# Run on the Vacc
# 	sh specterAPI_vacc.sh

 
	
