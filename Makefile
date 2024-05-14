.PHONY: clean clean-test clean-pyc clean-build docs help update-ngrams

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

update-ngrams:
	python .generate_sh.py
	for file in *sh; do sbatch $$file; done;
	sh .check_nodes.sh
	rm slurm-*

