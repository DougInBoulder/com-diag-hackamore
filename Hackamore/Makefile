################################################################################
# Copyright 2014 by the Digital Aggregates Corporation, Colorado, USA
# Licensed under the terms in README.txt
# Chip Overclock <coverclock@diag.com>
# http://www.diag.com/navigation/downloads/Hackamore
# Hackamore is an application written in Python that receives events from
# one or more Asterisk PBXes via Asterisk Management Interface (AMI) sockets
# and from those events reconstructs the dynamic call states of those PBXes. 
################################################################################

PROJECT				=	hackamore
TITLE				=	Hackamore
SYMBOL				=	HACKAMORE

MAJOR				=	0
MINOR				=	0
BUILD				=	0

########## Variables

TIMESTAMP			=	$(shell date -u +%Y%m%d%H%M%S%N%Z)
DATESTAMP			=	$(shell date +%Y%m%d)

########## Locators

SVN_REPO			=	svn://graphite/$(PROJECT)
SVN_URL				=	$(SVN_REPO)/trunk/$(TITLE)
HTTP_URL			=	http://www.diag.com/navigation/downloads/$(TITLE).html
GIT_URL				=	https://github.com/coverclock/com-diag-$(PROJECT).git

########## Directories

CUR_DIR				:=	$(shell pwd)
SRC_DIR				=	src
TST_DIR				=	tst
TMP_DIR				=	/var/tmp
DOC_DIR				=	doc

########## Distribution

.PHONY:	distribution

distribution:
	rm -rf $(TMP_DIR)/$(PROJECT)-$(MAJOR).$(MINOR).$(BUILD)
	svn export $(SVN_URL) $(TMP_DIR)/$(PROJECT)-$(MAJOR).$(MINOR).$(BUILD)
	( cd $(TMP_DIR); tar cvzf - $(PROJECT)-$(MAJOR).$(MINOR).$(BUILD) ) > $(TMP_DIR)/$(PROJECT)-$(MAJOR).$(MINOR).$(BUILD).tgz

########## Backup

.PHONY:	backup

backup:	../$(PROJECT)-backup.tgz
	mv $(MVFLAGS) ../$(PROJECT)-backup.tgz ../$(PROJECT)-$(TIMESTAMP).tgz

../$(PROJECT)-backup.tgz:
	tar --exclude-vcs -cvzf - . > $@

########## Documentation

.PHONY:	documentation browse refman manpages

documentation:
	sed -e "s/\\\$$Name.*\\\$$/$(MAJOR).$(MINOR).$(BUILD)/" < doxygen.cf > doxygen-local.cf
	doxygen doxygen-local.cf
	test -d $(DOC_DIR)/pdf || mkdir -p $(DOC_DIR)/pdf
	( cd $(DOC_DIR)/latex; $(MAKE) refman.pdf; cp refman.pdf ../pdf )
	cat $(DOC_DIR)/man/man3/*.3 | groff -man -Tps - > $(DOC_DIR)/pdf/manpages.ps
	ps2pdf $(DOC_DIR)/pdf/manpages.ps $(DOC_DIR)/pdf/manpages.pdf

browse:
	$(BROWSER) file:doc/html/index.html

refman:
	$(BROWSER) file:doc/pdf/refman.pdf

manpages:
	$(BROWSER) file:doc/pdf/manpages.pdf

########## Unit Tests

.PHONY:	test

test:
	export PYTHONPATH=$(CUR_DIR)/$(SRC_DIR):$(CUR_DIR)/$(TST_DIR); \
	for S in $(TST_DIR); do \
		for F in $$S/com/diag/$(PROJECT)/Test*.py; do \
			D=`dirname $$F`; \
			B=`basename $$F`; \
			( cd $$D; python $$B; ) \
		done; \
	done

pythonpath:
	echo "export PYTHONPATH=$(CUR_DIR)/$(SRC_DIR):$(CUR_DIR)/$(TST_DIR)"

########## Housekeeping

.PHONY:	commit dcommit push init

commit:
	git commit .

dcommit:
	git svn dcommit

push:
	git push origin master

init:
	git svn show-ignore > .gitignore
	git add .gitignore
	git remote add origin $(GIT_URL)
