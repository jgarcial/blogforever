# $Id$

include ../../../config.mk

LIBFILES = Check_URL.py Get_Recid.py Get_Report_Number.py Make_Delete_Records.py \
		   Print_Success_DEL.py Print_Success_MBI.py Print_Success.py \
		   Create_Modify_Interface.py Mail_Submitter.py \
		   Shared_Functions.py

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	#@echo "Done.  Please run make test now."

test:
	@echo "Done.  Please run make install now."

install:
	$(INSTALL) $(LIBFILES) $(LIBDIR)/python/invenio/websubmit_functions
	#$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to restart Apache now."
