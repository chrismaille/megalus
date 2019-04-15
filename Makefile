test:
	pytest
ci:
	pytest --docstyle --pep8 --cov=megalus --mypy
changelog:
	echo "TODO"
release:
	echo "TODO"
deploy:
	rm -rf dist/
	rm -rf build/
	python setup.py sdist bdist_wheel
	twine upload dist/*
