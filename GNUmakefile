SHELL                                   := /bin/bash
PWD                                     ?= pwd_unknown
TIME                                    := $(shell date +%s)
export TIME

OS                                      :=$(shell uname -s)
export OS
OS_VERSION                              :=$(shell uname -r)
export OS_VERSION
ARCH                                    :=$(shell uname -m)
export ARCH
ifeq ($(ARCH),x86_64)
TRIPLET                                 :=x86_64-linux-gnu
export TRIPLET
endif
ifeq ($(ARCH),arm64)
TRIPLET                                 :=aarch64-linux-gnu
export TRIPLET
endif
ifeq ($(ARCH),arm64)
TRIPLET                                 :=aarch64-linux-gnu
export TRIPLET
endif

HOMEBREW                                := $(shell type -P brew)
export HOMEBREW

PYTHON                                  := $(shell which python)
export PYTHON
PYTHON2                                 := $(shell which python2)
export PYTHON2
PYTHON3                                 := $(shell which python3)
export PYTHON3

PIP                                     := $(notdir $(shell which pip))
export PIP
PIP2                                    := $(notdir $(shell which pip2))
export PIP2
PIP3                                    := $(notdir $(shell which pip3))
export PIP3

ifeq ($(PYTHON3),/usr/local/bin/python3)
PIP                                    := pip
PIP3                                   := pip
export PIP
export PIP3
endif

PYTHON_VENV                             := $(shell python -c "import sys; sys.stdout.write('1') if hasattr(sys, 'base_prefix') else sys.stdout.write('0')")
PYTHON3_VENV                            := $(shell python3 -c "import sys; sys.stdout.write('1') if hasattr(sys, 'real_prefix') else sys.stdout.write('0')")
export PYTHON_VENV
export PYTHON3_VENV
ifeq ($(PYTHON_VENV),0)
USER_FLAG                               :=--user
else
USER_FLAG                               :=
endif

ifeq ($(project),)
PROJECT_NAME                            := $(notdir $(PWD))
else
PROJECT_NAME                            := $(project)
endif
export PROJECT_NAME

ifeq ($(mk3-version),)
MK3_VERSION                                 := 2023-06-26T1241-v4.1.9-coldcard.dfu
else
MK3_VERSION                                 := $(mk3-version)
endif
export MK3_VERSION
ifeq ($(mk4-version),)
MK4_VERSION                                 := 2023-04-07T1330-v5.1.2-mk4-coldcard.dfu
else
MK4_VERSION                                 := $(mk4-version)
endif
export MK4_VERSION
ifeq ($(q1-version),)
Q1_VERSION                                 := 2024-05-09T1529-v1.2.1Q-q1-coldcard.dfu
else
Q1_VERSION                                 := $(mk4-version)
endif
export MK4_VERSION

GIT_USER_NAME                           := $(shell git config user.name || echo $(PROJECT_NAME))
export GIT_USER_NAME
GH_USER_NAME                            := $(shell git config user.name || echo $(PROJECT_NAME))
GH_USER_REPO                            := $(GH_USER_NAME).github.io
GH_USER_SPECIAL_REPO                    := $(GH_USER_NAME)
KB_USER_REPO                            := $(GH_USER_NAME).keybase.pub
ifneq ($(ghuser),)
GH_USER_NAME := $(ghuser)
GH_USER_SPECIAL_REPO := $(ghuser)/$(ghuser)
endif
export GIT_USER_NAME
export GH_USER_REPO
export GH_USER_SPECIAL_REPO

GIT_USER_EMAIL                          := $(shell git config user.email || echo $(PROJECT_NAME))
export GIT_USER_EMAIL
GIT_SERVER                              := https://github.com
export GIT_SERVER
GIT_SSH_SERVER                          := git@github.com
export GIT_SSH_SERVER
GIT_PROFILE                             := $(shell git config user.name || echo $(PROJECT_NAME))
export GIT_PROFILE
GIT_BRANCH                              := $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null || echo $(PROJECT_NAME))
export GIT_BRANCH
GIT_HASH                                := $(shell git rev-parse --short HEAD 2>/dev/null || echo $(PROJECT_NAME))
export GIT_HASH
GIT_PREVIOUS_HASH                       := $(shell git rev-parse --short master@{1} 2>/dev/null || echo $(PROJECT_NAME))
export GIT_PREVIOUS_HASH
GIT_REPO_ORIGIN                         := $(shell git remote get-url origin 2>/dev/null || echo $(PROJECT_NAME))
export GIT_REPO_ORIGIN
GIT_REPO_NAME                           := $(PROJECT_NAME)
export GIT_REPO_NAME
GIT_REPO_PATH                           := $(HOME)/$(GIT_REPO_NAME)
export GIT_REPO_PATH

BASENAME := $(shell basename -s .git `git config --get remote.origin.url` || echo $(PROJECT_NAME))
export BASENAME

NODE_VERSION                            :=v14.21.3
export NODE_VERSION
NODE_ALIAS                              :=v14.21.0
export NODE_ALIAS
NVM_DIR                                 :=$(HOME)/.nvm
export NVM_DIR
PACKAGE_MANAGER                         :=yarn
export PACKAGE_MANAGER
PACKAGE_INSTALL                         :=add
export PACKAGE_INSTALL

SPHINXOPTS                               =
SPHINXBUILD                              = sphinx-build
PAPER                                    =
BUILDDIR                                 = _build
PRIVATE_BUILDDIR                         = _private_build

PAPEROPT_a4                              = -D latex_paper_size=a4
PAPEROPT_letter                          = -D latex_paper_size=letter
ALLSPHINXOPTS                            = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
PRIVATE_ALLSPHINXOPTS                    = -d $(PRIVATE_BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
I18NSPHINXOPTS                           = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

-:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
## help

.PHONY: init
.ONESHELL:
init:initialize venv##	initialize venv
	@echo $(PYTHON)
	@echo $(PYTHON2)
	@echo $(PYTHON3)
	@echo $(PIP)
	@echo $(PIP2)
	@echo $(PIP3)
	@echo PATH=$(PATH):/usr/local/opt/python@3.10/Frameworks/Python.framework/Versions/3.10/bin
	@echo PATH=$(PATH):$(HOME)/Library/Python/3.10/bin
	test -d .venv || $(PYTHON3) -m virtualenv .venv
	( \
	   source .venv/bin/activate; pip install -q -r requirements.txt; \
	   $(PYTHON3) -m pip install $(USER_FLAG) --upgrade pip; \
	   $(PYTHON3) -m pip install $(USER_FLAG) -r requirements.txt; \
	   $(PYTHON3) -m pip install -q omegaconf \
	   pip install -q --upgrade pip; \
	);
	( \
	    while ! docker system info > /dev/null 2>&1; do\
	    echo 'Waiting for docker to start...';\
	    if [[ '$(OS)' == 'Linux' ]]; then\
	     systemctl restart docker.service;\
	    fi;\
	    if [[ '$(OS)' == 'Darwin' ]]; then\
	     open --background -a /./Applications/Docker.app/Contents/MacOS/Docker;\
	    fi;\
	sleep 1;\
	done\
	)
	@bash -c ". .venv/bin/activate &"

help:## 	verbose help
	@sed -n 's/^## //p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'


.PHONY: report
report:## 	report
	@echo ''
	@echo '[ENV VARIABLES]	'
	@echo ''
	@echo 'TIME=${TIME}'
	@echo 'BASENAME=${BASENAME}'
	@echo 'PROJECT_NAME=${PROJECT_NAME}'
	@echo 'MK3_VERSION=${MK3_VERSION}'
	@echo 'MK4_VERSION=${MK4_VERSION}'
	@echo 'Q1_VERSION=${Q1_VERSION}'
	@echo 'PYTHON_VENV=${PYTHON_VENV}'
	@echo 'PYTHON3_VENV=${PYTHON3_VENV}'
	@echo 'HOMEBREW=${HOMEBREW}'
	@echo ''
	@echo 'GIT_USER_NAME=${GIT_USER_NAME}'
	@echo 'GH_USER_REPO=${GH_USER_REPO}'
	@echo 'GH_USER_SPECIAL_REPO=${GH_USER_SPECIAL_REPO}'
	@echo 'GIT_USER_EMAIL=${GIT_USER_EMAIL}'
	@echo 'GIT_SERVER=${GIT_SERVER}'
	@echo 'GIT_PROFILE=${GIT_PROFILE}'
	@echo 'GIT_BRANCH=${GIT_BRANCH}'
	@echo 'GIT_HASH=${GIT_HASH}'
	@echo 'GIT_PREVIOUS_HASH=${GIT_PREVIOUS_HASH}'
	@echo 'GIT_REPO_ORIGIN=${GIT_REPO_ORIGIN}'
	@echo 'GIT_REPO_NAME=${GIT_REPO_NAME}'
	@echo 'GIT_REPO_PATH=${GIT_REPO_PATH}'

.PHONY: super
.ONESHELL:
super:
ifneq ($(shell id -u),0)
	@echo switch to superuser
	@echo cd $(TARGET_DIR)
	sudo -s
endif

checkbrew:
ifeq ($(HOMEBREW),)
	@/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
	@type -P brew
endif

submodules: checkbrew## 	submodules
	git submodule update --init --recursive
	git submodule foreach --recursive "git submodule update --init --recursive"

.ONESHELL:
docker-start:
	touch requirements.txt
	test -d .venv || $(PYTHON3) -m virtualenv .venv
	( \
	   source .venv/bin/activate; pip install -q -r requirements.txt; \
	   pip install -q --upgrade pip; \
	);
	( \
	    while ! docker system info > /dev/null 2>&1; do\
	    echo 'Waiting for docker to start...';\
	    if [[ '$(OS)' == 'Linux' ]]; then\
	     systemctl restart docker.service;\
	    fi;\
	    if [[ '$(OS)' == 'Darwin' ]]; then\
	     open --background -a /./Applications/Docker.app/Contents/MacOS/Docker;\
	    fi;\
	sleep 1;\
	done\
	)

initialize:## 	initialize
	@[[ '$(shell uname -m)' == 'x86_64' ]] && [[ '$(shell uname -s)' == 'Darwin' ]] && echo "is_Darwin/x86_64" || echo "not_Darwin/x86_64"
	@[[ '$(shell uname -m)' == 'x86_64' ]] && [[ '$(shell uname -s)' == 'Linux' ]] && echo "is_Linux/x86_64" || echo "not_Linux/x86_64"

repro-mk-three: clean submodules## 	repro-mk-three
## 	repro-mk-three
## 	:additional help
#@echo $(git describe --match "20*" --abbrev=0)
## https://coldcard.com/downloads/2023-06-19T1627-v4.1.8-coldcard.dfu
	@touch releases/$(MK3_VERSION)
	@[[ ! -f releases/$(MK3_VERSION) ]]; curl https://coldcard.com/downloads/$(MK3_VERSION) > releases/$(MK3_VERSION)
	@cd stm32 && make -f MK3-Makefile repro

repro-mk-four: clean submodules## 	repro-mk-four
## 	repro-mk-four
## 	:additional help
#@echo $(git describe --match "20*" --abbrev=0)
	@touch releases/$(MK4_VERSION)
	@[[ ! -f releases/$(MK4_VERSION) ]]; curl https://coldcard.com/downloads/$(MK4_VERSION) > releases/$(MK4_VERSION)
	@cd stm32 && make -f MK4-Makefile repro

repro-q-one: clean submodules## 	repro-q-one
## 	repro-q-one
## 	:additional help
#@echo $(git describe --match "20*" --abbrev=0)
	@touch releases/$(Q1_VERSION)
	@[[ ! -f releases/$(Q1_VERSION) ]]; curl https://coldcard.com/downloads/$(Q1_VERSION) > releases/$(Q1_VERSION)
	@cd stm32 && make -f Q1-Makefile repro

.PHONY: failure
failure:
	@-/usr/bin/false && ([ $$? -eq 0 ] && echo "success!") || echo "failure!"
.PHONY: success
success:
	@-/usr/bin/true && ([ $$? -eq 0 ] && echo "success!") || echo "failure!"

venv:submodules## 	python3.10 virtualenv
	$(MAKE) -f $(PWD)/venv.mk venv-3-10
venv-test:submodules## 	venv-3-10-test
	$(MAKE) -f $(PWD)/venv.mk venv-3-10-test

tag:## 	tag
	@git tag $(OS)-$(OS_VERSION)-$(ARCH)-$(shell date +%s)
	@git push -f --tags

clean:## 	clean
	@mkdir -p $(PWD)/external/micropython
	@mkdir -p $(PWD)/external/libngu
	@mkdir -p $(PWD)/external/mpy-qr
	@if [[  -z $(PWd)/external/micropython ]]; then \
		rm -rf $(PWD)/external/mpy-qr; \
		rm -rf $(PWD)/external/libngu; \
		rm -rf $(PWD)/external/micropython; \
		fi;
	@mkdir -p $(PWD)/stm32/built
	@if [[ -d $(PWD)/stm32/built ]]; then \
		rm -rf $(PWD)/stm32/built/**.bin; \
		fi;
	$(MAKE) submodules

-include venv.mk
-include act.mk&
