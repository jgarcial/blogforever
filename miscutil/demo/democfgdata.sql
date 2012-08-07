
-- create collections

INSERT INTO collection VALUES (2,'Blogs','collection:BLOG',NULL,NULL);
INSERT INTO collection VALUES (3,'Posts','collection:BLOGPOST',NULL,NULL);
INSERT INTO collection VALUES (4,'Comments','collection:COMMENT',NULL,NULL);
INSERT INTO collection VALUES (5,'Pages','collection:PAGE',NULL,NULL);
INSERT INTO collection VALUES (6,'Initial Blogs','collection:INITIALBLOG',NULL,NULL);

INSERT INTO collectionname VALUES (2,'en','ln','Blogs');
INSERT INTO collectionname VALUES (3,'en','ln','Posts');
INSERT INTO collectionname VALUES (4,'en','ln','Comments');
INSERT INTO collectionname VALUES (5,'en','ln','Pages');
INSERT INTO collectionname VALUES (6,'en','ln','Initial Blogs');

INSERT INTO collection_collection VALUES (1,2,'r',60);
INSERT INTO collection_collection VALUES (1,3,'r',40);
INSERT INTO collection_collection VALUES (1,4,'r',30);
INSERT INTO collection_collection VALUES (1,5,'r',20);
-- INSERT INTO collection_collection VALUES (1,6,'r',10);


-- set the 'websearch_instantbrowse_by_field' plugin up to
-- the blog posts collection to display them by publication date

-- INSERT INTO collection_instantbrowse VALUES (3, 'websearch_instantbrowse_by_field', '{"field": "269__c", "order": "d"}');


-- blogs submission form

DELETE sbmALLFUNCDESCR.* FROM sbmALLFUNCDESCR, sbmFUNCTIONS WHERE sbmALLFUNCDESCR.function=sbmFUNCTIONS.function and sbmFUNCTIONS.doctype='BSI';
DELETE sbmFUNDESC.* FROM sbmFUNDESC, sbmFUNCTIONS WHERE sbmFUNDESC.function=sbmFUNCTIONS.function and sbmFUNCTIONS.doctype='BSI';
DELETE sbmFIELDDESC.* FROM sbmFIELDDESC, sbmFIELD, sbmIMPLEMENT WHERE sbmFIELD.fidesc=sbmFIELDDESC.name AND sbmFIELD.subname=sbmIMPLEMENT.subname AND sbmIMPLEMENT.docname='BSI';
DELETE sbmFIELD.* FROM sbmFIELD, sbmIMPLEMENT WHERE sbmFIELD.subname=sbmIMPLEMENT.subname AND sbmIMPLEMENT.docname='BSI';
DELETE FROM sbmDOCTYPE WHERE sdocname='BSI';
DELETE FROM sbmCATEGORIES WHERE doctype ='BSI';
DELETE FROM sbmFUNCTIONS WHERE doctype='BSI';
DELETE FROM sbmIMPLEMENT WHERE docname='BSI';
DELETE FROM sbmPARAMETERS WHERE doctype='BSI';
INSERT INTO sbmALLFUNCDESCR VALUES ('Check_URL',NULL);
INSERT INTO sbmALLFUNCDESCR VALUES ('Make_Delete_Records','');
INSERT INTO sbmDOCTYPE VALUES ('Blog Submission Interface','BSI','2012-05-23','2012-05-23','Blog Submission Interface');
INSERT INTO sbmFIELD VALUES ('DBIBSI',1,1,'BSI_URL','<table style=\"font-family: Verdana, Arial, Helvetica, sans-serif;font-size: 16px;width: 400px;height:380px;background:#E8F9EC;border-spacing: 4px 4px;padding-left:10px;\" align=\"center\" cellspacing=\"2\" cellpadding=\"2\"><tr> 
<td style="text-align: left"> <span style="font-weight: bold; color:red">WARNING: Note that is just possible to delete the whole blog, i.e., you are going to delete all the comments and blog posts of the given blog!!</span> <tr> <td style=\"text-align: left\"> <span style=\"font-weight: bold;\">Delete a blog:</span><br /><br /> <span>Insert the URL of the blog you wish to delete: <br /> (e.g: \"http://blogforever.eu\")</span><br /><br />','M','Blog URL','','2012-07-26','2012-08-10',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('DBIBSI',1,2,'DBI_END','<br /><br /></td></tr></td></tr></table><br />','O','Delete end bottom','','2012-08-10','2012-08-10',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('MBIBSI',1,1,'BSI_URL','<table style=\"font-family: Verdana, Arial, Helvetica, sans-serif;font-size: 16px;width: 400px;height:380px;background:#E8F9EC;border-spacing: 4px 4px;padding-left:10px;\" align=\"center\" cellspacing=\"2\" cellpadding=\"2\">\r\n<tr>\r\n<td style=\"text-align: left\"><br />\r\n<span style=\"font-weight: bold;\">Modify blog metadata:</span><br /><br />\r\n<span>Blog URL:</span><br />','M','Blog URL','','2012-07-26','2012-07-26',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('MBIBSI',1,2,'MBI_SELECT','<br /><br /><span style=\"color: red;\">*</span>Choose the fields to be modified:<br />','M','Fields to modify','','2012-07-26','2012-07-26',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('MBIBSI',1,3,'MBI_CONT','<br /><br /></td></tr></table><br />','O','','','2012-07-26','2012-08-07',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,1,'BSI_TITLE','<table style=\"font-family: Verdana, Arial, Helvetica, sans-serif;font-size: 16px;width: 400px;height:380px;background:#E8F9EC;border-spacing: 4px 4px;padding-left:10px;\" align=\"center\" cellspacing=\"2\" cellpadding=\"2\">\r\n<tr>\r\n<td style=\"text-align: left\"><br />\r\n<span style=\"font-weight: bold;\">Submit blog metadata:</span><br /><br />\r\n<span>Blog title:</span><br />','O','Blog title','','2012-05-23','2012-05-29',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,2,'BSI_URL','<br /><br />\r\n<span style=\"color: red;\">* </span>Blog URL:<br />','M','Blog URL','','2012-05-23','2012-06-21',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,3,'BSI_TOPIC','<br /><br /><span style=\"color: red;\">* </span>Topic:<br />','M','Topic','','2012-05-23','2012-05-23',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,4,'BSI_LICENSE','<br /><br /><span style=\"color: red;\">* </span>License:<br />','M','License','','2012-05-23','2012-05-23',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,5,'BSI_END','<br /><br /></td></tr></table><br />','O','','','2012-05-23','2012-08-06',NULL,NULL);
INSERT INTO sbmFIELDDESC VALUES ('BSI_END',NULL,'','D',NULL,NULL,NULL,NULL,NULL,'<div align=\"center\">\r\n<INPUT TYPE=\"button\" class=\"adminbutton\" name=\"endS\" width=\"400\" height=\"50\" value=\"Finish Submission\" onclick=\"finish();\">\r\n</div>','2012-05-23','2012-08-10',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BSI_LICENSE',NULL,'542__a','R',NULL,NULL,NULL,NULL,NULL,'text = \'<select name=\"BSI_LICENSE\"> <option>- select -</option>\'\r\n# FIXME: retrieve from the database\r\n# from invenio.dbquery import run_sql\r\n# license_names = run_sql(\"select name from license\")\r\nlicense_names = [\'License1\', \'License2\', \'License3\']\r\n\r\nfor license_name in license_names:\r\n    text += \'<option value=\"%s\"> %s </option>\' % (license_name, license_name)\r\n    \r\ntext += \"</select>\"','2012-05-23','2012-07-26',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BSI_TITLE',NULL,'245__a','I',40,NULL,NULL,NULL,NULL,'Blog Title','2012-05-23','2012-05-23',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BSI_TOPIC',NULL,'65014a','R',NULL,NULL,NULL,NULL,NULL,'text = \'<select name=\"BSI_TOPIC\"> <option>- select -</option>\'\r\n# FIXME: retrieve from the database\r\n# from invenio.dbquery import run_sql\r\n# topic_names = run_sql(\"select name from topic\")\r\ntopic_names = [\'Topic1\', \'Topic2\', \'Topic3\']\r\n\r\nfor topic_name in topic_names:\r\n    text += \'<option value=\"%s\"> %s </option>\' % (topic_name, topic_name)\r\n    \r\ntext += \"</select>\"\r\n','2012-05-23','2012-07-26',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BSI_URL',NULL,'520__u','I',40,NULL,NULL,NULL,NULL,'Blog URL','2012-05-23','2012-05-24',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('DBI_END',NULL,'','D',NULL,NULL,NULL,NULL,NULL,'<div align=\"center\">\r\n<INPUT TYPE=\"button\" class=\"adminbutton\" name=\"endS\" width=\"400\" height=\"50\" value=\"Delete blog\" onclick=\"finish();\">\r\n</div>','2012-08-10','2012-08-10',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('MBI_CONT',NULL,'','D',NULL,NULL,NULL,NULL,NULL,'<div align=\"center\">\r\n<input type=\"button\" class=\"adminbutton\" width=\"400\" height=\"50\" name=\"endS\" value=\"Continue\" onclick=\"finish();\" />\r\n</div>','2012-07-26','2012-07-26',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('MBI_SELECT',NULL,'','S',NULL,NULL,NULL,NULL,NULL,'<select name=\"MBI_SELECT[]\" size=\"4\" multiple>\r\n <option value=\"Select:\">Select:</option>\r\n <option value=\"BSI_TITLE\">Title</option>\r\n <option value=\"BSI_TOPIC\">Topic</option>\r\n <option value=\"BSI_LICENSE\">License</option>\r\n</select>','2012-07-26','2012-07-26',NULL,NULL,0);
INSERT INTO sbmACTION VALUES ('Delete a Blog', 'DBI', 'delete', '2012-08-10', '2012-08-10', '', 'Delete a Blog');
UPDATE sbmACTION SET lactname='Submit a Blog', statustext='Submit a Blog' WHERE sactname='SBI';
UPDATE sbmACTION SET lactname='Modify Information', statustext='Modify Information' WHERE sactname='MBI';
INSERT INTO sbmFUNCTIONS VALUES ('DBI','BSI','Get_Recid',20,1);
INSERT INTO sbmFUNCTIONS VALUES ('DBI','BSI','Get_Report_Number',10,1);
INSERT INTO sbmFUNCTIONS VALUES ('DBI','BSI','Is_Original_Submitter',40,1);
INSERT INTO sbmFUNCTIONS VALUES ('DBI','BSI','Make_Delete_Records',30,1);
INSERT INTO sbmFUNCTIONS VALUES ('DBI','BSI','Move_to_Done',70,1);
INSERT INTO sbmFUNCTIONS VALUES ('DBI','BSI','Print_Success_DEL',60,1);
INSERT INTO sbmFUNCTIONS VALUES ('DBI','BSI','Send_Delete_Mail',50,1);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Create_Modify_Interface',40,1);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Get_Recid',20,1);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Get_Recid',20,2);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Get_Report_Number',10,1);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Get_Report_Number',10,2);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Insert_Modify_Record',50,2);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Is_Original_Submitter',30,1);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Is_Original_Submitter',30,2);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Make_Modify_Record',40,2);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Move_to_Done',80,2);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Print_Success_MBI',60,2);
INSERT INTO sbmFUNCTIONS VALUES ('MBI','BSI','Send_Modify_Mail',70,2);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Check_URL',10,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Create_Recid',20,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Insert_Record',50,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Mail_Submitter',70,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Make_Record',40,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Move_to_Done',80,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Print_Success',60,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Report_Number_Generation',30,1);
INSERT INTO sbmFUNDESC VALUES ('Check_URL','url');
INSERT INTO sbmFUNDESC VALUES ('Create_Modify_Interface','fieldnameMBI');
INSERT INTO sbmFUNDESC VALUES ('Get_Recid','record_search_pattern');
INSERT INTO sbmFUNDESC VALUES ('Get_Report_Number','edsrn');
INSERT INTO sbmFUNDESC VALUES ('Mail_Submitter','authorfile');
INSERT INTO sbmFUNDESC VALUES ('Mail_Submitter','edsrn');
INSERT INTO sbmFUNDESC VALUES ('Mail_Submitter','emailFile');
INSERT INTO sbmFUNDESC VALUES ('Mail_Submitter','newrnin');
INSERT INTO sbmFUNDESC VALUES ('Mail_Submitter','status');
INSERT INTO sbmFUNDESC VALUES ('Mail_Submitter','titleFile');
INSERT INTO sbmFUNDESC VALUES ('Make_Modify_Record','modifyTemplate');
INSERT INTO sbmFUNDESC VALUES ('Make_Modify_Record','sourceTemplate');
INSERT INTO sbmFUNDESC VALUES ('Make_Record','createTemplate');
INSERT INTO sbmFUNDESC VALUES ('Make_Record','sourceTemplate');
INSERT INTO sbmFUNDESC VALUES ('Print_Success','edsrn');
INSERT INTO sbmFUNDESC VALUES ('Print_Success','newrnin');
INSERT INTO sbmFUNDESC VALUES ('Print_Success','status');
INSERT INTO sbmFUNDESC VALUES ('Report_Number_Generation','autorngen');
INSERT INTO sbmFUNDESC VALUES ('Report_Number_Generation','counterpath');
INSERT INTO sbmFUNDESC VALUES ('Report_Number_Generation','edsrn');
INSERT INTO sbmFUNDESC VALUES ('Report_Number_Generation','nblength');
INSERT INTO sbmFUNDESC VALUES ('Report_Number_Generation','rnformat');
INSERT INTO sbmFUNDESC VALUES ('Report_Number_Generation','rnin');
INSERT INTO sbmFUNDESC VALUES ('Report_Number_Generation','yeargen');
INSERT INTO sbmFUNDESC VALUES ('Send_Delete_Mail','edsrn');
INSERT INTO sbmFUNDESC VALUES ('Send_Delete_Mail','record_managers');
INSERT INTO sbmFUNDESC VALUES ('Send_Modify_Mail','addressesMBI');
INSERT INTO sbmFUNDESC VALUES ('Send_Modify_Mail','emailFile');
INSERT INTO sbmFUNDESC VALUES ('Send_Modify_Mail','fieldnameMBI');
INSERT INTO sbmFUNDESC VALUES ('Send_Modify_Mail','sourceDoc');
INSERT INTO sbmIMPLEMENT VALUES ('BSI','DBI','Y','DBIBSI',1,'2012-07-26','2012-08-10',3,'','',0,0,'');
INSERT INTO sbmIMPLEMENT VALUES ('BSI','MBI','Y','MBIBSI',1,'2012-07-25','2012-08-07',2,'','',0,0,'');
INSERT INTO sbmIMPLEMENT VALUES ('BSI','SBI','Y','SBIBSI',1,'2012-05-23','2012-08-10',1,'','',0,0,'');
INSERT INTO sbmPARAMETERS VALUES ('BSI','authorfile','');
INSERT INTO sbmPARAMETERS VALUES ('BSI','autorngen','Y');
INSERT INTO sbmPARAMETERS VALUES ('BSI','counterpath','lastid_BLOG_<PA>yy</PA>	');
INSERT INTO sbmPARAMETERS VALUES ('BSI','createTemplate','BSIcreate.tpl');
INSERT INTO sbmPARAMETERS VALUES ('BSI','edsrn','BSI_URL');
INSERT INTO sbmPARAMETERS VALUES ('BSI','emailFile','SuE');
INSERT INTO sbmPARAMETERS VALUES ('BSI','fieldnameMBI','MBI_SELECT');
INSERT INTO sbmPARAMETERS VALUES ('BSI','modifyTemplate','MSImodify.tpl');
INSERT INTO sbmPARAMETERS VALUES ('BSI','rnformat','BLOG-<PA>yy</PA>');
INSERT INTO sbmPARAMETERS VALUES ('BSI','sourceTemplate','BSI.tpl');
INSERT INTO sbmPARAMETERS VALUES ('BSI','status','ADDED');
INSERT INTO sbmPARAMETERS VALUES ('BSI','titleFile','BSI_TITLE');
INSERT INTO sbmPARAMETERS VALUES ('BSI','url','BSI_URL');
INSERT INTO sbmPARAMETERS VALUES ('BSI','yeargen','AUTO');

-- end of file
