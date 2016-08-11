all: test

init:
	@pip install -r requirements.txt

lint:
	@flake8 .

unit:
	@python -m unittest

coverage:
	@coverage run --omit='*/**/tests/*,*/**/bitstring.py' -m unittest
	@coverage report

test: lint unit
