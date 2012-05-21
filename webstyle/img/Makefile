# $Id$

include ../../config.mk

IMGFILES = header_background.gif site_logo.gif site_logo_small.gif 

IMGDIR = $(PREFIX)/var/www/img/

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Not implemented."

install:
	$(INSTALL) $(IMGFILES) $(IMGDIR)
#	$(INSTALL) favicon.ico $(PREFIX)/var/www/
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)

