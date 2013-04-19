# $Id$

include config.mk

SUBDIRS = miscutil webaccess webblog websearch webstyle websubmit

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	@echo "Done.  Please run make test now."

test:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make test && cd .. ;)
	@echo "Done.  Please run make install now."

install:
	mkdir -p $(ETCLOCALDIR)/templates
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to restart Apache now."

install-yes-i-know:
	@echo "If you are really sure you want to install *all* then launch \"make install-yes-i-know\""
