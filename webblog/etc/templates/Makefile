# $Id$

include ../../../config.mk

SUBDIRS = format_templates
all:
	@echo "Done."

test:
	@echo "Not implemented."

install:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
