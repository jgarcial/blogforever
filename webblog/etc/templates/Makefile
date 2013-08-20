# $Id$

include ../../../config.mk

TPLFILES = *.tpl *.html
TPLDIR = $(ETCLOCALDIR)/templates

SUBDIRS = format_templates

all:
	@echo "Done."

test:
	@echo "Not implemented."

install:
	$(INSTALL) -m 664 $(TPLFILES) $(TPLDIR)
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
