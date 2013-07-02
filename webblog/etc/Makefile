# $Id$

include ../../config.mk

BFTFILES = *.bft
BFTDIR = $(ETCDIR)/bibformat/format_templates
SUBDIRS = output_formats templates

all:
	@echo "Done."

test:
	@echo "Not implemented."

install:
	$(INSTALL) -m 664 $(BFTFILES) $(BFTDIR)
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
