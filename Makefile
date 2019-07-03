install:
	pipenv install --dev
test:
	pytest
lint:
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -f .coverage
	pipenv run pytest --cov=megalus --cov-fail-under=90 --docstyle --pep8 --mypy
changelog:
	echo "TODO"
release:
	echo "TODO"
deploy:
	rm -rf dist/
	rm -rf build/
	python setup.py sdist bdist_wheel
	twine upload dist/*
