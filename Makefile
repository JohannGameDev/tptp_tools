# prerequisites
PYTHON=python3
PIP=pip3

# project directories
BIN=./bin

default: all

all:
	pip3 install .
	mkdir -p $(BIN)
	echo "#!$(PYTHON)" > $(BIN)/system_on_tptp
	cat ./tptp_tools/system_on_tptp.py >> $(BIN)/system_on_tptp
	chmod +x $(BIN)/system_on_tptp

clean:
	rm -Rf $(BIN)
	pip3 uninstall -y tptp_tools