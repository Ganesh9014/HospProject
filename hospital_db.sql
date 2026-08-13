-- ============================================================
-- SQL Server INSERT script — Hospital Database
-- Generated automatically from live database
-- Run AFTER: python manage.py migrate
-- Open in SSMS and execute (F5)
-- ============================================================

SET NOCOUNT ON;
BEGIN TRANSACTION;

-- ---- [employee]  (1 rows) ----
INSERT INTO `employee` (`id`, `emp_id`, `emp_name`, `designation`, `age`, `doj`, `address`, `phone`, `createdby`, `createddate`, `updatedby`, `updatedtime`, `active`, `empid`, `empname`, `empdesig`) VALUES (1, 'MH01', 'Admin', 'AdminRole', 28, '2026-05-26', 'HYderabad', 8787888787, 'admin', NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- ---- [tblroles]  (1 rows) ----
INSERT INTO `tblroles` (`RoleId`, `RoleName`, `RolePages`, `mainrole`, `roletables`) VALUES (1, 'AdminRole', 'Admin,Employee Registration,Permission,Change Password,Admission Charges,Department Master,Floors Master,Room Type Master,Rooms Master,Beds Master,Auto Services,PRO Master,State Master,District Master,City Master,Doctor Master,Ref Doc Master,Speciality Master,Service Type Master,Case Type Master,OT Master,Operation Master,Machine Equipment Master,Investigation Master,Investigation Details,InvestigationDetailsMaster,Resource Master,Roles Master,OtherCharges Master,Machine Eqp Master,Package Master,Invest Department,Expenditure Master,PRO Report,lab packages,Inv Group Master,Discharge Master,Payee Master,New Buttons Master,Front Office,Registration,Consultation,IP Registration,OP Modify,Patient Infomation,Print Pages,Advances,Expendature,Ambulance charge,IP,IP Consultation,IP Investigations,IP Procedures,IP Services,IP Operations,IP Bed Transfer,IP Machine Equipment,IP Miscellnaous,Other Charges,Discharge Form,IP Cancellation,IP Modify,IP Refund,Payments,Final Bill,Revoke ip,IP Concession,ipblock,New Discharge Summary,IP Invest Indent,IP Pharmacy Indent,OP,OP Cancellation,OP Procedures,OP Investigations,OP Concession,OP Refund,OP Payments,Lab,Lab Entry,Lab Modify,Lab Reports,Reports,Collection Report,Concession Report,Patient Information,Cancellation Report,PRO Report,Discharge Type Report,DayWise Doctor Report,CaseWise Report,Investigation Report,Refund Report,Payment Report,Due Report,Expendature Report,Invest for IP Patient,Payment Mode Report,Reprint Discharge Summary,Empty Beds,Ref Doctor Report,Operation Report,FinancialGlance,DocVisitReport,ServiceReport,investdeptwiseReport,PackageReport,Referal Investigation,Investigation Count,FianlDiagreport,Investigation Charges,Investigation Collection,groupwise investigations,Changes,Daily Investigation Report,Userwisecollection1,Monthly Summary,prodatewise,Daily Investigation Count,Total Business Report,Case Sheet,Nursing Note,Admission Note,Treatment sheet,Vitalsigns,Progess Note,Case Sheets,Paymentmode Change,DayCollection Entry,Ac Exp,CollectionEntryReport,Ac Exp Report,Balance Sheet,search-uhid', 'yes', 'Registration,OP Consultation,OP Investigations,OP Procedures,OP Payments');

-- ---- [hospapp_mainmenu]  (5 rows) ----
INSERT INTO `hospapp_mainmenu` (`id`, `name`, `icon`, `display_order`) VALUES (1, 'Admin', 'bi-person-gear', 1);
INSERT INTO `hospapp_mainmenu` (`id`, `name`, `icon`, `display_order`) VALUES (2, 'Front Office', 'bi-hospital', 2);
INSERT INTO `hospapp_mainmenu` (`id`, `name`, `icon`, `display_order`) VALUES (4, 'OP', 'bi-person-check-fill', 4);
INSERT INTO `hospapp_mainmenu` (`id`, `name`, `icon`, `display_order`) VALUES (5, 'Lab', 'bi-flask', 5);
INSERT INTO `hospapp_mainmenu` (`id`, `name`, `icon`, `display_order`) VALUES (6, 'Reports', 'bi-file-earmark-text', 6);

-- ---- [hospapp_submenu]  (51 rows) ----
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (111, 'Employee Registration', '/Admin/empRegistration/', 1, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (112, 'Permission', '/Admin/addpermission/', 2, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (113, 'Change Password', '/Admin/ChangePassword/', 3, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (115, 'Department Master', '/Admin/Department/', 5, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (121, 'PRO Master', '/Admin/pro/', 11, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (122, 'State Master', '/Admin/statename/', 12, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (123, 'District Master', '/Admin/District/', 13, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (125, 'Doctor Master', '/Admin/Doctor/', 15, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (126, 'Ref Doc Master', '/Admin/refdoctordetails/', 16, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (127, 'Speciality Master', '/Admin/speciality/', 17, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (128, 'Service Type Master', '/ip/ServiceType/', 18, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (129, 'Case Type Master', '/Admin/casetype/', 19, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (133, 'Investigation Master', '/Admin/Investigation/', 23, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (134, 'Investigation Details', '/Admin/investdetailmaster/', 24, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (136, 'Roles Master', '/hospApp/admin/RolesPage/', 26, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (140, 'Invest Department', '/InvDepartment/', 30, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (141, 'Expenditure Master', '/frontoffice/expendituremaster/', 31, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (144, 'Inv Group Master', '/InvestGroupMaster/', 34, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (146, 'Payee Master', '/hospapp/admin/cardtypemaster/', 36, 1, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (148, 'Registration', '/op/oppatient/', 1, 2, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (149, 'OP Consultation', '/frontOffice/DocConsultation/', 2, 2, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (151, 'OP Modify', '/op/OPAdmissionModify/', 4, 2, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (152, 'prescription', '/select-patient/', 5, 2, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (176, 'OP Cancellation', '/op/Cancellation/', 1, 4, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (177, 'OP Procedures', '/frontOffice/opprocedure/', 2, 4, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (178, 'OP Investigations', '/Lab/OpInvestigation/', 3, 4, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (181, 'OP Payments', '/Op/Payment/', 6, 4, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (183, 'printpages', '/frontOffice/printpages', 7, 2, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (184, 'Collection Report', '/Reports/userwisecollection/', 1, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (187, 'Lab Entry', '/Lab/LabEntry/', 1, 5, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (188, 'Lab Modify', '/Lab/modifylab/', 2, 5, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (189, 'Lab Reports', '/Lab/prev_reports/', 3, 5, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (190, 'Concession Report', '/Reports/ConcessionReport/', 2, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (191, 'Patient Information', '/Reports/Patinfo/', 3, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (192, 'PRO Report', '/Reports/proreport', 5, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (193, 'investdeptwiseReport', '/Reports/investdeptwiseReport/', 6, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (194, 'Investigation Report', '/Reports/investigationReport/', 7, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (195, 'Expendature Report', '/frontOffice/ExpenditureReport/', 8, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (197, 'Cancellation Report', '/Reports/cancellationReport/', 10, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (198, 'Due Report', '/Reports/DueReport/', 11, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (200, 'Payment Mode Report', '/reports/daycollection/', 12, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (201, 'Ref Doctor Report', '/Reports/refdoctorreport', 13, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (202, 'Expenditure', '/frontoffice/Expenditure', 8, 2, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (203, 'DayWise Doctor Report', '/Reports/docwiseipoppatinfo/', 14, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (204, 'CaseWise Report', '/Reports/casewisereport/', 15, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (205, 'ServiceReport', '/Reports/serviceReport/', 16, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (206, 'investdeptwiseReport', '/Reports/investdeptwiseReport/', 17, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (207, 'Daily Investigation Count', '/Reports/dailyinvreport/', 18, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (208, 'Daily Investigation Report', '/Reports/dialyinvestigations', 19, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (209, 'Daily Procedures', '/Reports/DailyProcedures/', 20, 6, 1);
INSERT INTO `hospapp_submenu` (`id`, `name`, `url`, `display_order`, `main_menu_id`, `is_header`) VALUES (210, 'Observation Entry', '/check-basic/', 6, 2, 1);

-- ---- [tblroles_pages]  (51 rows) ----
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1383, 1, 111);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1384, 1, 112);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1385, 1, 113);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1386, 1, 115);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1387, 1, 121);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1388, 1, 122);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1389, 1, 123);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1390, 1, 125);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1391, 1, 126);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1392, 1, 127);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1343, 1, 128);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1344, 1, 129);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1345, 1, 133);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1346, 1, 134);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1342, 1, 136);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1347, 1, 140);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1348, 1, 141);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1349, 1, 144);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1350, 1, 146);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1351, 1, 148);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1352, 1, 149);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1353, 1, 151);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1354, 1, 152);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1355, 1, 176);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1356, 1, 177);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1357, 1, 178);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1358, 1, 181);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1359, 1, 183);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1360, 1, 184);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1361, 1, 187);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1362, 1, 188);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1363, 1, 189);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1364, 1, 190);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1365, 1, 191);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1366, 1, 192);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1367, 1, 193);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1368, 1, 194);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1369, 1, 195);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1370, 1, 197);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1371, 1, 198);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1372, 1, 200);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1373, 1, 201);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1374, 1, 202);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1375, 1, 203);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1376, 1, 204);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1377, 1, 205);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1378, 1, 206);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1379, 1, 207);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1380, 1, 208);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1381, 1, 209);
INSERT INTO `tblroles_pages` (`id`, `tblroles_id`, `submenu_id`) VALUES (1382, 1, 210);

-- ---- [tbluserpermission]  (1 rows) ----
INSERT INTO `tbluserpermission` (`id`, `username`, `password`, `permission`, `isactive`, `empid`, `empname`, `empdesig`, `department`, `emp_id`, `mainrole_id`, `app_permission`) VALUES (1, 'admin', '123', 'Registration,OP Consultation,OP Investigations,OP Procedures,OP Payments', 1, 'MH01', 'Admin', 'AdminRole', '', 1, 1, 0);

-- ---- [case_type_master]  (1 rows) ----
INSERT INTO `case_type_master` (`sno`, `casetype`, `active`, `createdby`, `createdtime`, `updatedby`, `updatedtime`) VALUES (1, 'cardio', 'Y', 'admin', '2026-08-13 20:13:22.959009', NULL, NULL);

-- ---- [hospapp_promaster]  (1 rows) ----
INSERT INTO `hospapp_promaster` (`proid`, `pro_name`, `specialized`, `address`, `phone`, `active`, `userid`, `createdby`, `updatedby`, `createddate`, `updateddate`) VALUES (1, 'self', NULL, NULL, 8546461613, 'Y', NULL, 'admin', NULL, '2026-08-13 20:11:40.395712', NULL);

-- ---- [refdoc_master]  (1 rows) ----
INSERT INTO `refdoc_master` (`docid`, `docname`, `phoneno`, `active`, `createdby`, `createdtime`, `updatedby`, `updatedtime`, `specialized_id`) VALUES (1, 'test', '8745454545', 'Y', 'admin', '2026-08-13 20:12:11.615460', NULL, NULL, 1);

-- ---- [speciality_master]  (1 rows) ----
INSERT INTO `speciality_master` (`sno`, `speciality`, `userid`, `insertedtime`, `updatedby`, `updatedtime`, `active`) VALUES (1, 'test', 'admin', '2026-08-13 20:11:26.965805', NULL, NULL, 'Y');

-- ---- [doctor_master]  (1 rows) ----
INSERT INTO `doctor_master` (`docid`, `docname`, `address`, `phoneno`, `consultfee`, `ipconsultfee`, `emrfee`, `active`, `createdby`, `createdtime`, `updatedby`, `updatedtime`, `speciality`, `revisittime`, `qualification`, `regno`) VALUES (1, 'Dr test', NULL, '7878787878', 400, 400, 400, 'Y', NULL, '2026-08-13 20:14:12.627407', NULL, NULL, 1, 5, 'MBBS GOLD MEDAL', '0000');

COMMIT TRANSACTION;
