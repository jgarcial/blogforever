# $Id$

include ../../config.mk

IMGFILES = bull_BackContent.gif bull_leftMenuBackground.gif bull_middleBackground.gif drop_down_menu_arrow_down_g.gif bullet_toggle_minus.png bull_linetwopoints.gif bull_twopoints.gif drop_down_menu_arrow_down_lg.gif site_logo.gif bullet_toggle_plus.png bull_Logo-en.gif bull_twopointsline.gif header_background.gif site_logo_small.gif
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

