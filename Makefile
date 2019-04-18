.PHONY: install uninstall

install:
	sudo python3 setup.py install --record .files.txt

uninstall:
	sudo xargs rm -rf < .files.txt