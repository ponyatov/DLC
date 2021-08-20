# \ var
# detect module/project name by current directory
MODULE  = $(notdir $(CURDIR))
# detect OS name (only Linux in view)
OS      = $(shell uname -s)
# current date in the `ddmmyy` format
NOW     = $(shell date +%d%m%y)
# release hash: four hex digits (for snapshots)
REL     = $(shell git rev-parse --short=4 HEAD)
# current branch
BRANCH  = $(shell git rev-parse --abbrev-ref HEAD)
# number of CPU cores (for parallel builds)
CORES   = $(shell grep processor /proc/cpuinfo| wc -l)
# / var

# \ dir
# current (project) directory
CWD     = $(CURDIR)
# compiled/executable files (target dir)
BIN     = $(CWD)/bin
# documentation & external manuals download
DOC     = $(CWD)/doc
# libraries / scripts
LIB     = $(CWD)/lib
# source code (not for all languages, Rust/C included)
SRC     = $(CWD)/src
# temporary/generated files
TMP     = $(CWD)/tmp
# / dir

# \ tool
# http/ftp download tool
CURL    = curl -L -o
PY      = bin/python3
PIP     = bin/pip3
PEP     = bin/autopep8
PYT     = bin/pytest
# / tool

# \ src
P += config.py
Y += $(MODULE).py test_$(MODULE).py
S += $(Y)
# / src

# \ all

.PHONY: all
all: $(PY) $(MODULE).py
	$(MAKE) test format
	$^ $@

.PHONY: repl
repl: $(PY) $(MODULE).py
	$(PY) -i $(MODULE).py $@

.PHONY: test
test: $(PYT) test_$(MODULE).py
	$^

.PHONY: format
format: tmp/format
tmp/format: $(Y)
	$(PEP) --ignore=E26,E302,E305,E401,E402,E701,E702 -i $?
	touch $@

# / all

# \ doc
.PHONY: doc
doc:
# / doc

# \ install
.PHONY: install update
install: $(OS)_install doc
	$(MAKE) $(PIP)
	$(MAKE)   update
update: $(OS)_update
	$(PIP) install -U    pytest autopep8
	$(PIP) install -U -r requirements.txt

.PHONY: Linux_install Linux_update
Linux_install Linux_update:
	sudo apt update
	sudo apt install -u `cat apt.txt apt.dev`

$(PY) $(PIP) $(PYT) $(PEP):
	python3 -m venv .
	$(MAKE) update
# / install

# \ merge
MERGE  = Makefile README.md apt.* .gitignore $(S)
MERGE += .vscode bin doc lib src tmp

.PHONY: dev
dev:
	git push -v
	git checkout $@
	git pull -v
	git checkout ponymuck -- $(MERGE)

.PHONY: ponymuck
ponymuck:
	git push -v
	git checkout $@
	git pull -v

.PHONY: release
release:
	git tag $(NOW)-$(REL)
	git push -v --tags
	$(MAKE) ponymuck

.PHONY: zip
zip:
	git archive \
		--format zip \
		--output $(TMP)/$(MODULE)_$(BRANCH)_$(NOW)_$(REL).src.zip \
	HEAD
# / merge
