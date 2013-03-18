# $Id$

include ../../config.mk

FONTFILES = fontawesome-webfont.eot fontawesome-webfont.svg fontawesome-webfont.ttf fontawesome-webfont.woff
FONTDIR = $(PREFIX)/var/www/font/

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Not implemented."

install:
	mkdir -p ${PREFIX}/var/www/font
	$(INSTALL) $(FONTFILES) $(FONTDIR)
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
