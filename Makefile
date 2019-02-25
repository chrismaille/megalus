test:
	pytest --docstyle --pep8 --cov=megalus --mypy
changelog:
	echo "TODO"
release:
	echo "TODO"
deploy:
	rm -rf dist/
	python setup.py sdist bdist_wheel
	twine upload dist/*
