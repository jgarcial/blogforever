# $Id$

include ../../../config.mk

templatesdir = $(ETCLOCALDIR)/templates
templates_DATA = webaccount_login.html webaccount_register.html
EXTRA_DIST = $(templates_DATA)
CLEANFILES = *~ *.tmp


all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	@echo "Not implemented."

install:
	$(INSTALL) $(templates_DATA) $(templatesdir)
	@echo "Done.  You may want to restart Apache now."