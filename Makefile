install:
	pipenv install --dev
test:
	pipenv run pytest
lint:
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -f .coverage
	pipenv run pytest --cov=megalus --cov-fail-under=90 --docstyle --pep8 --mypy --black
changelog:
	echo "TODO"
release:
	echo "TODO"
deploy:
	rm -rf dist/
	rm -rf build/
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/*
format:
	pipenv run black megalus