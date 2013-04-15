# $Id$

include ../../config.mk

IMGFILES = blogforever_logo.png header_background.gif site_logo_small.gif sample1.png sample2.png sample3.png sample4.png bf1-screenshot.jpg bf3-screenshot.jpg  blogforever-logo.png
IMGDIR = $(PREFIX)/var/www/img/

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Not implemented."

install:
	$(INSTALL) $(IMGFILES) $(IMGDIR)
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
