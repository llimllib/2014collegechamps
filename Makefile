notebook: requirements
	ipython notebook --notebook-dir=.

requirements:
	pip install -r requirements.txt

.PHONY: notebook requirements
