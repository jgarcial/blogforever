

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

-- submission form

DELETE FROM sbmFUNDESC WHERE function LIKE 'BSI%';
DELETE FROM sbmFIELD WHERE subname LIKE '%BSI';
DELETE FROM sbmFIELDDESC WHERE name LIKE 'BSI%';
DELETE FROM sbmALLFUNCDESCR WHERE function LIKE 'BSI%';
DELETE FROM sbmDOCTYPE WHERE sdocname='BSI';
DELETE FROM sbmCATEGORIES WHERE doctype ='BSI';
DELETE FROM sbmFUNCTIONS WHERE doctype='BSI';
DELETE FROM sbmIMPLEMENT WHERE docname='BSI';
DELETE FROM sbmPARAMETERS WHERE doctype='BSI';
INSERT INTO sbmDOCTYPE VALUES ('Blog Submission Interface','BSI','2012-05-23','2012-05-23','Blog Submission Interface');
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,1,'BSI_TITLE','<table style=\"font-family: Verdana, Arial, Helvetica, sans-serif;font-size: 16px;width: 400px;height:380px;background:#E8F9EC;border-spacing: 4px 4px;padding-left:10px;\" align=\"center\" cellspacing=\"2\" cellpadding=\"2\">\r\n<tr>\r\n<td style=\"text-align: left\"><br />\r\n<span style=\"font-weight: bold;\">Submit blog metadata:</span><br /><br />\r\n<span>Blog title:</span><br />','M','Blog title','','2012-05-23','2012-05-29',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,2,'BSI_URL','<br /><br />\r\n<span style=\"color: red;\">* </span>Blog URL:<br />','M','Blog URL','','2012-05-23','2012-05-24',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,3,'BSI_TOPIC','<br /><br /><span style=\"color: red;\">* </span>Topic:<br />','M','Topic','','2012-05-23','2012-05-23',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,4,'BSI_LICENSE','<br /><br /><span style=\"color: red;\">* </span>License:<br />','M','License','','2012-05-23','2012-05-23',NULL,NULL);
INSERT INTO sbmFIELD VALUES ('SBIBSI',1,5,'BSI_END','<br /><br /></td></tr></table><br />','O','','','2012-05-23','2012-05-23',NULL,NULL);
INSERT INTO sbmFIELDDESC VALUES ('BSI_END',NULL,'','D',NULL,NULL,NULL,NULL,NULL,'<div align=\"center\">\r\n<INPUT TYPE=\"button\" class=\"adminbutton\" name=\"endS\" width=\"400\" height=\"50\" value=\"Finish Submission\" onclick=\"finish();\">\r\n</div>','2012-05-23','2012-05-23',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BSI_LICENSE',NULL,'542__f','R',NULL,NULL,NULL,NULL,NULL,'text = \'<select name=\"BSI_LICENSE\"> <option>- select -</option>\'\r\n# FIXME: retrieve from the database\r\n# from invenio.dbquery import run_sql\r\n# license_names = run_sql(\"select name from license\")\r\nlicense_names = [\'License1\', \'License2\', \'License3\']\r\n\r\nfor license_name in license_names:\r\n    text += \'<option value=\"%s\"> %s </option>\' % (license_name, license_name)\r\n    \r\ntext += \"</select>\"','2012-05-23','2012-05-24',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BSI_TITLE',NULL,'245__a','I',40,NULL,NULL,NULL,NULL,'Blog Title','2012-05-23','2012-05-23',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BSI_TOPIC',NULL,'654__a','R',NULL,NULL,NULL,NULL,NULL,'text = \'<select name=\"BSI_TOPIC\"> <option>- select -</option>\'\r\n# FIXME: retrieve from the database\r\n# from invenio.dbquery import run_sql\r\n# topic_names = run_sql(\"select name from topic\")\r\ntopic_names = [\'Topic1\', \'Topic2\', \'Topic3\']\r\n\r\nfor topic_name in topic_names:\r\n    text += \'<option value=\"%s\"> %s </option>\' % (topic_name, topic_name)\r\n    \r\ntext += \"</select>\"\r\n','2012-05-23','2012-05-24',NULL,NULL,0);
INSERT INTO sbmFIELDDESC VALUES ('BSI_URL',NULL,'520__u','I',40,NULL,NULL,NULL,NULL,'Blog URL','2012-05-23','2012-05-24',NULL,NULL,0);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Check_URL',10,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Create_Recid',20,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Insert_Record',50,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Mail_Submitter',70,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Make_Record',40,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Move_to_Done',80,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Print_Success',60,1);
INSERT INTO sbmFUNCTIONS VALUES ('SBI','BSI','Report_Number_Generation',30,1);
INSERT INTO sbmIMPLEMENT VALUES ('BSI','SBI','Y','SBIBSI',1,'2012-05-23','2012-06-21',NULL,'','',0,0,'');
INSERT INTO sbmPARAMETERS VALUES ('BSI','autorngen','Y');
INSERT INTO sbmPARAMETERS VALUES ('BSI','counterpath','lastid_BLOG_<PA>yy</PA>	');
INSERT INTO sbmPARAMETERS VALUES ('BSI','createTemplate','BSIcreate.tpl');
INSERT INTO sbmPARAMETERS VALUES ('BSI','edsrn','BSI_RN');
INSERT INTO sbmPARAMETERS VALUES ('BSI','emailFile','SuE');
INSERT INTO sbmPARAMETERS VALUES ('BSI','rnformat','BLOG-<PA>yy</PA>');
INSERT INTO sbmPARAMETERS VALUES ('BSI','sourceTemplate','BSI.tpl');
INSERT INTO sbmPARAMETERS VALUES ('BSI','status','ADDED');
INSERT INTO sbmPARAMETERS VALUES ('BSI','titleFile','BSI_TITLE');
INSERT INTO sbmPARAMETERS VALUES ('BSI','url','BSI_URL');
INSERT INTO sbmPARAMETERS VALUES ('BSI','yeargen','AUTO');

-- end of file
