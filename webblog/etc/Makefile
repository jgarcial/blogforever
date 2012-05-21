# $Id$

include ../../config.mk

BFTFILES = *.bft
#XSLFILES = *.xsl
BFTDIR = $(ETCDIR)/bibformat/format_templates
SUBDIRS = output_formats
all:
	@echo "Done."

test:
	@echo "Not implemented."

install:
	$(INSTALL) -m 664 $(BFTFILES) $(BFTDIR)
#        $(INSTALL) -m 664 $(XSLFILES) $(BFTDIR)
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
