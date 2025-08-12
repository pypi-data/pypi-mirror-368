help:
	@echo available commands: clean, env, format, lint, run, test, wip

remove_env:
	rm -rf env/

create_env:
	python3 -m venv env
	env/bin/pip install --upgrade pip
	env/bin/pip install -r requirements.txt
	env/bin/pip install -e .
	rm -rf *.egg-info
	@echo done!

upgrade_env:
	env/bin/pip install -r requirements.txt --upgrade

env: remove_env create_env

create_reqs:
	pipreqs

run:
	python3 scripts/clf_train.py
	pyclean . -q

# todo: add docker commands

mlflow:
	open http://127.0.0.1:5000/#/

mlflow-clean:
	rm -rf mlruns

lab_add_env:
	python -m pip install ipykernel
	python -m ipykernel install --name=env

lab_list_env:
	jupyter kernelspec list

lab_uninstall_env:
	jupyter kernelspec uninstall env

lab:
	jupyter lab

clean:
	pyclean . -q

clean-project: clean
	rm -rf build/
	rm -rf logs/
	rm -rf mlruns/
	rm -rf out/

clean-mlflow:
	rm -rf mlruns

format:
	black scripts/ -q
	black src/ -q
	black tests/ -q
	isort scripts/ -q
	isort src/ -q
	isort tests/ -q

lint:
	flake8 scripts/*.py
	flake8 src/*.py

test:
	pytest . -v -x --cov=src --cov-fail-under=0
	rm -rf .pytest_cache

wip: format test
	git add .
	git commit -m wip
	git push
