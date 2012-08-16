# $Id$

include ../../../config.mk

LIBFILES = Check_URL.py Get_Recid.py Get_Recid_Number.py Make_Delete_Records.py \
		   Create_Modify_Interface.py \
		   Shared_Functions.py \
		   Move_to_Pending.py Move_From_Pending.py \
		   DBI_Mail_Approval_Request_to_Referee.py DBI_Mail_Notification_to_User.py DBI_Print_Success.py \
		   DPI_Mail_Approval_Request_to_Referee.py DPI_Mail_Notification_to_User.py DPI_Print_Success.py \
		   SBI_Mail_Approval_Request_to_Referee.py SBI_Mail_Notification_to_User.py SBI_Print_Success.py \
		   MBI_Mail_Approval_Request_to_Referee.py MBI_Mail_Notification_to_User.py MBI_Print_Success.py \
		   APP_Mail_Final_Decision_to_User.py APS_Mail_Final_Decision_to_User.py \
		   APO_Mail_Final_Decision_to_User.py APM_Mail_Final_Decision_to_User.py \
		   APP_Print_Success.py APS_Print_Success.py APO_Print_Success.py APM_Print_Success.py \
		   Update_Approval_DB.py DBI_Mail_Blog_Deleted_to_User.py DPI_Mail_Post_Deleted_to_User.py \
		   SBI_Mail_Blog_Submitted_to_User.py MBI_Mail_Blog_Modified_to_User.py \
		   Make_Modify_Record.py Insert_Modify_Record.py

all:
	$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make all && cd .. ;)
	#@echo "Done.  Please run make test now."

test:
	@echo "Done.  Please run make install now."

install:
	$(INSTALL) $(LIBFILES) $(LIBDIR)/python/invenio/websubmit_functions
	#$(foreach SUBDIR, $(SUBDIRS), cd $(SUBDIR) && make install && cd .. ;)
	@echo "Done.  You may want to restart Apache now."
