DATA_DIR=./data
DATA_DIR_S2=$(DATA_DIR)/semantic_scholar/data # s2 data
DATA_DIR_S2ORC=$(DATA_DIR)/s2orc 
DATA_DIR_OA=$(DATA_DIR)/openalex-snapshot/data 

SRC_DIR=./src

.PHONY: clean clean-test clean-pyc clean-build docs help

.DEFAULT_GOAL := help

help:
	grep '\#\#' Makefile

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr dist/

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	find . -name '.coverage' -exec rm -fr {} +
	find . -name 'htmlcov' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +

lint: ## check style
	tox -e lint

test: ## run tests on one version of Python
	tox -e py

tox:  ## run tests on all available versions of Python
	tox

dist: clean ## builds source and wheel package
	flit build
	ls -l dist

install: ## install in editable mode
	pip install -e .

#################
# UPDATING OA   #
#################

uncompress-oa-vacc:
	source ~/myconda.sh && conda activate catDB &&	\
	sbatch --partition=week \
	       --nodes=1 \
	       --mem=10G \
	       --time=167:00:00 \
	       --job-name=uncompress_oa \
	       --wrap="source ~/myconda.sh && conda activate catDB && gzip -dr $(DATA_DIR_OA)"
	
update-works-oa-vacc:
	source ~/myconda.sh && conda activate catDB &&	\
	sbatch --partition=week \
	       --nodes=1 \
	       --mem=10G \
	       --time=167:00:00 \
	       --job-name=add_works_to_scisciDB \
	       --wrap="source ~/myconda.sh && conda activate catDB && python src/oa_push_db.py -i $(DATA_DIR_OA)/works/ -c works_oa"

####################
# UPDATING S2ORC   #
####################

update-papers-s2-vacc:
	source ~/myconda.sh && conda activate catDB &&	\
	python src/s2_import.py papers && \
	gunzip -d $(DATA_DIR_S2)/papers/*.gz && \
	sbatch --partition=week \
	       --nodes=1 \
	       --mem=10G \
	       --time=167:00:00 \
	       --job-name=add_papers_to_scisciDB \
	       --wrap="source ~/myconda.sh && conda activate catDB && python src/oa_push_db.py -i $(DATA_DIR_S2)/papers/ -c papers"

###############################
# AUGMENT PAPERS WITH WORKS_OA   #
###############################

augment-papers-with-s2orc-vacc:
	source ~/myconda.sh && conda activate catDB &&	\
	sbatch --partition=week \
	       --nodes=5 \
	       --mem=60G \
	       --time=167:00:00 \
	       --job-name=augment_papers_with_s2orc_parsed \
	       --wrap="source ~/myconda.sh && conda activate catDB && python -c "import sos; sos_db=sos.api.sosDB(); sos_db.augment_papers_with_s2orc_bool()"
