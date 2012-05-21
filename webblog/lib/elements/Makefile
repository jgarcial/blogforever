# $Id$

include ../../../config.mk

PYFILES = *.py
PYFILESDIR = $(PREFIX)/lib/python/invenio/bibformat_elements


all:
	@echo "Done.  Please run make test now."

test:
	@echo "Done.  Please run make install now."

install:
	$(INSTALL) -m 664 $(PYFILES) $(PYFILESDIR)
	@echo "Done.  You may want to restart Apache now."
