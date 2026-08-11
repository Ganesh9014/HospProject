-- ============================================================
-- SQL Server INSERT script — Hospital Database
-- Generated automatically from live database
-- Run AFTER: python manage.py migrate
-- Open in SSMS and execute (F5)
-- ============================================================

SET NOCOUNT ON;
BEGIN TRANSACTION;

-- ---- [state_master]  (2 rows) ----
SET IDENTITY_INSERT [state_master] ON;
INSERT INTO [state_master] ([sno], [statename]) VALUES (1, 'Telangana');
INSERT INTO [state_master] ([sno], [statename]) VALUES (2, 'Ap');
SET IDENTITY_INSERT [state_master] OFF;

-- ---- [hospApp_state]  (2 rows) ----
SET IDENTITY_INSERT [hospApp_state] ON;
INSERT INTO [hospApp_state] ([id], [statename]) VALUES (2, 'Andhra Pradesh');
INSERT INTO [hospApp_state] ([id], [statename]) VALUES (1, 'Telangana');
SET IDENTITY_INSERT [hospApp_state] OFF;

-- ---- [hospApp_district]  (44 rows) ----
SET IDENTITY_INSERT [hospApp_district] ON;
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (1, 'Adilabad', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (2, 'Bhadradri Kothagudem', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (3, 'Hanumakonda', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (4, 'Hyderabad', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (5, 'Jagtial', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (6, 'Jangaon', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (7, 'Jayashankar Bhupalpally', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (8, 'Jogulamba Gadwal', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (9, 'Kamareddy', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (10, 'Karimnagar', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (11, 'Khammam', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (12, 'Mahabubabad', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (13, 'Mahabubnagar', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (14, 'Mancherial', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (15, 'Medak', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (16, 'Medchal–Malkajgiri', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (17, 'Mulugu', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (18, 'Nagarkurnool', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (19, 'Nalgonda', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (20, 'Nirmal', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (21, 'Nizamabad', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (22, 'Peddapalli', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (23, 'Rajanna Sircilla', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (24, 'Rangareddy', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (25, 'Sangareddy', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (26, 'Siddipet', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (27, 'Suryapet', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (28, 'Vikarabad', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (29, 'Wanaparthy', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (30, 'Warangal', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (31, 'Yadadri Bhuvanagiri', 1);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (32, 'Anantapur', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (33, 'Chittoor', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (34, 'East Godavari', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (35, 'Guntur', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (36, 'Krishna', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (37, 'Kurnool', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (38, 'Nellore', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (39, 'Prakasam', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (40, 'Srikakulam', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (41, 'Visakhapatnam', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (42, 'Vizianagaram', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (43, 'West Godavari', 2);
INSERT INTO [hospApp_district] ([id], [districtname], [state_id]) VALUES (44, 'YSR Kadapa', 2);
SET IDENTITY_INSERT [hospApp_district] OFF;

-- ---- [hospApp_districtmaster]  (2 rows) ----
SET IDENTITY_INSERT [hospApp_districtmaster] ON;
INSERT INTO [hospApp_districtmaster] ([sno], [district_name], [active], [createdby], [createdtime], [updatedby], [updatetime], [state_name_id]) VALUES (1, 'kurnool', 'Y', 'admin', '2025-11-01 06:02:34.655944+00:00', 'admin', '2026-06-02 11:17:44.747668+00:00', 2);
INSERT INTO [hospApp_districtmaster] ([sno], [district_name], [active], [createdby], [createdtime], [updatedby], [updatetime], [state_name_id]) VALUES (2, 'Khammam', 'Y', 'admin', '2026-01-18 09:01:33.810440+00:00', 'admin', '2026-05-12 07:22:45.474389+00:00', 1);
SET IDENTITY_INSERT [hospApp_districtmaster] OFF;

-- ---- [hospApp_city]  (28 rows) ----
SET IDENTITY_INSERT [hospApp_city] ON;
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (1, 'Hyderabad', 4);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (2, 'Secunderabad', 4);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (3, 'Kukatpally', 16);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (4, 'Shamshabad', 24);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (5, 'Sangareddy', 25);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (6, 'Karimnagar', 10);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (7, 'Khammam', 11);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (8, 'Siddipet', 26);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (9, 'Nizamabad', 21);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (10, 'Kothagudem', 2);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (11, 'Bhongir', 31);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (12, 'Warangal', 3);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (13, 'Kazipet', 3);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (14, 'Hanamkonda', 3);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (29, 'Guntur', 35);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (30, 'Vijayawada', 36);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (31, 'Machilipatnam', 36);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (32, 'Kurnool', 37);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (33, 'Nellore', 38);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (34, 'Ongole', 39);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (35, 'Srikakulam', 40);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (36, 'Visakhapatnam', 41);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (37, 'Vizianagaram', 42);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (38, 'Eluru', 43);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (39, 'Kadapa', 44);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (40, 'Tenali', 35);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (41, 'Mangalagiri', 35);
INSERT INTO [hospApp_city] ([id], [cityname], [district_id]) VALUES (42, 'Gudivada', 36);
SET IDENTITY_INSERT [hospApp_city] OFF;

-- ---- [employee]  (1 rows) ----
SET IDENTITY_INSERT [employee] ON;
INSERT INTO [employee] ([id], [emp_id], [emp_name], [designation], [age], [doj], [address], [phone], [createdby], [createddate], [updatedby], [updatedtime], [active], [empid], [empname], [empdesig]) VALUES (1, 'MH01', 'Admin', 'AdminRole', 28, '2026-05-26', 'HYderabad', 8787888787, 'admin', NULL, NULL, NULL, NULL, NULL, NULL, NULL);
SET IDENTITY_INSERT [employee] OFF;

-- ---- [tblroles]  (1 rows) ----
SET IDENTITY_INSERT [tblroles] ON;
INSERT INTO [tblroles] ([RoleId], [RoleName], [RolePages], [mainrole], [roletables]) VALUES (1, 'AdminRole', 'Admin,Employee Registration,Permission,Change Password,Admission Charges,Department Master,Floors Master,Room Type Master,Rooms Master,Beds Master,Auto Services,PRO Master,State Master,District Master,City Master,Doctor Master,Ref Doc Master,Speciality Master,Service Type Master,Case Type Master,OT Master,Operation Master,Machine Equipment Master,Investigation Master,Investigation Details,InvestigationDetailsMaster,Resource Master,Roles Master,OtherCharges Master,Machine Eqp Master,Package Master,Invest Department,Expenditure Master,PRO Report,lab packages,Inv Group Master,Discharge Master,Payee Master,New Buttons Master,Front Office,Registration,Consultation,IP Registration,OP Modify,Patient Infomation,Print Pages,Advances,Expendature,Ambulance charge,IP,IP Consultation,IP Investigations,IP Procedures,IP Services,IP Operations,IP Bed Transfer,IP Machine Equipment,IP Miscellnaous,Other Charges,Discharge Form,IP Cancellation,IP Modify,IP Refund,Payments,Final Bill,Revoke ip,IP Concession,ipblock,New Discharge Summary,IP Invest Indent,IP Pharmacy Indent,OP,OP Cancellation,OP Procedures,OP Investigations,OP Concession,OP Refund,OP Payments,Lab,Lab Entry,Lab Modify,Lab Reports,Reports,Collection Report,Concession Report,Patient Information,Cancellation Report,PRO Report,Discharge Type Report,DayWise Doctor Report,CaseWise Report,Investigation Report,Refund Report,Payment Report,Due Report,Expendature Report,Invest for IP Patient,Payment Mode Report,Reprint Discharge Summary,Empty Beds,Ref Doctor Report,Operation Report,FinancialGlance,DocVisitReport,ServiceReport,investdeptwiseReport,PackageReport,Referal Investigation,Investigation Count,FianlDiagreport,Investigation Charges,Investigation Collection,groupwise investigations,Changes,Daily Investigation Report,Userwisecollection1,Monthly Summary,prodatewise,Daily Investigation Count,Total Business Report,Case Sheet,Nursing Note,Admission Note,Treatment sheet,Vitalsigns,Progess Note,Case Sheets,Paymentmode Change,DayCollection Entry,Ac Exp,CollectionEntryReport,Ac Exp Report,Balance Sheet,search-uhid', 'yes', 'Registration,OP Consultation,OP Investigations,OP Procedures,OP Payments');
SET IDENTITY_INSERT [tblroles] OFF;

-- ---- [hospApp_mainmenu]  (5 rows) ----
SET IDENTITY_INSERT [hospApp_mainmenu] ON;
INSERT INTO [hospApp_mainmenu] ([id], [name], [icon], [display_order]) VALUES (1, 'Admin', 'bi-person-gear', 1);
INSERT INTO [hospApp_mainmenu] ([id], [name], [icon], [display_order]) VALUES (2, 'Front Office', 'bi-hospital', 2);
INSERT INTO [hospApp_mainmenu] ([id], [name], [icon], [display_order]) VALUES (4, 'OP', 'bi-person-check-fill', 4);
INSERT INTO [hospApp_mainmenu] ([id], [name], [icon], [display_order]) VALUES (5, 'Lab', 'bi-flask', 5);
INSERT INTO [hospApp_mainmenu] ([id], [name], [icon], [display_order]) VALUES (6, 'Reports', 'bi-file-earmark-text', 6);
SET IDENTITY_INSERT [hospApp_mainmenu] OFF;

-- ---- [hospApp_submenu]  (52 rows) ----
SET IDENTITY_INSERT [hospApp_submenu] ON;
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (111, 'Employee Registration', '/Admin/empRegistration/', 1, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (112, 'Permission', '/Admin/addpermission/', 2, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (113, 'Change Password', '/Admin/ChangePassword/', 3, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (115, 'Department Master', '/Admin/Department/', 5, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (121, 'PRO Master', '/Admin/pro/', 11, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (122, 'State Master', '/Admin/statename/', 12, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (123, 'District Master', '/Admin/District/', 13, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (125, 'Doctor Master', '/Admin/Doctor/', 15, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (126, 'Ref Doc Master', '/Admin/refdoctordetails/', 16, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (127, 'Speciality Master', '/Admin/speciality/', 17, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (128, 'Service Type Master', '/ip/ServiceType/', 18, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (129, 'Case Type Master', '/Admin/casetype/', 19, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (133, 'Investigation Master', '/Admin/Investigation/', 23, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (134, 'Investigation Details', '/Admin/investdetailmaster/', 24, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (136, 'Roles Master', '/hospApp/admin/RolesPage/', 26, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (140, 'Invest Department', '/InvDepartment/', 30, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (141, 'Expenditure Master', '/frontoffice/expendituremaster/', 31, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (144, 'Inv Group Master', '/InvestGroupMaster/', 34, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (146, 'Payee Master', '/hospapp/admin/cardtypemaster/', 36, 1, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (148, 'Registration', '/op/oppatient/', 1, 2, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (149, 'OP Consultation', '/frontOffice/DocConsultation/', 2, 2, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (151, 'OP Modify', '/op/OPAdmissionModify/', 4, 2, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (152, 'prescription', '/select-patient/', 5, 2, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (176, 'OP Cancellation', '/op/Cancellation/', 1, 4, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (177, 'OP Procedures', '/frontOffice/opprocedure/', 2, 4, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (178, 'OP Investigations', '/Lab/OpInvestigation/', 3, 4, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (181, 'OP Payments', '/Op/Payment/', 6, 4, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (183, 'printpages', '/frontOffice/printpages', 7, 2, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (184, 'Collection Report', '/Reports/userwisecollection/', 1, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (187, 'Lab Entry', '/Lab/LabEntry/', 1, 5, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (188, 'Lab Modify', '/Lab/modifylab/', 2, 5, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (189, 'Lab Reports', '/Lab/prev_reports/', 3, 5, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (190, 'Concession Report', '/Reports/ConcessionReport/', 2, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (191, 'Patient Information', '/Reports/Patinfo/', 3, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (192, 'PRO Report', '/Reports/proreport', 5, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (193, 'investdeptwiseReport', '/Reports/investdeptwiseReport/', 6, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (194, 'Investigation Report', '/Reports/investigationReport/', 7, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (195, 'Expendature Report', '/frontOffice/ExpenditureReport/', 8, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (197, 'Cancellation Report', '/Reports/cancellationReport/', 10, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (198, 'Due Report', '/Reports/DueReport/', 11, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (200, 'Payment Mode Report', '/reports/daycollection/', 12, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (201, 'Ref Doctor Report', '/Reports/refdoctorreport', 13, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (202, 'Expenditure', '/frontoffice/Expenditure', 8, 2, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (203, 'DayWise Doctor Report', '/Reports/docwiseipoppatinfo/', 14, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (204, 'CaseWise Report', '/Reports/casewisereport/', 15, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (205, 'ServiceReport', '/Reports/serviceReport/', 16, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (206, 'investdeptwiseReport', '/Reports/investdeptwiseReport/', 17, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (207, 'Daily Investigation Count', '/Reports/dailyinvreport/', 18, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (208, 'Daily Investigation Report', '/Reports/dialyinvestigations', 19, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (209, 'Daily Procedures', '/Reports/DailyProcedures/', 20, 6, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (210, 'Observation Entry', '/check-basic/', 6, 2, 1);
INSERT INTO [hospApp_submenu] ([id], [name], [url], [display_order], [main_menu_id], [is_header]) VALUES (211, 'Refunds', '/Refunds/', 7, 4, 1);
SET IDENTITY_INSERT [hospApp_submenu] OFF;

-- ---- [hospApp_childsubmenu]  (52 rows) ----
SET IDENTITY_INSERT [hospApp_childsubmenu] ON;
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (1, 'Employee Registration', '/Admin/empRegistration/', 1, 111);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (2, 'Registration', '/op/oppatient/', 1, 148);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (3, 'OP Cancellation', '/op/Cancellation/', 1, 176);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (4, 'Collection Report', '/Reports/userwisecollection/', 1, 184);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (5, 'Lab Entry', '/Lab/LabEntry/', 1, 187);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (6, 'Lab Modify', '/Lab/modifylab/', 2, 188);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (7, 'OP Procedures', '/frontOffice/opprocedure/', 2, 177);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (8, 'OP Consultation', '/frontOffice/DocConsultation/', 2, 149);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (9, 'Concession Report', '/Reports/ConcessionReport/', 2, 190);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (10, 'Permission', '/Admin/addpermission/', 2, 112);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (11, 'Change Password', '/Admin/ChangePassword/', 3, 113);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (12, 'Patient Information', '/Reports/Patinfo/', 3, 191);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (13, 'OP Investigations', '/Lab/OpInvestigation/', 3, 178);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (14, 'Lab Reports', '/Lab/prev_reports/', 3, 189);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (15, 'OP Modify', '/op/OPAdmissionModify/', 4, 151);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (16, 'prescription', '/select-patient/', 5, 152);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (17, 'PRO Report', '/Reports/proreport', 5, 192);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (18, 'Department Master', '/Admin/Department/', 5, 115);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (19, 'investdeptwiseReport', '/Reports/investdeptwiseReport/', 6, 193);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (20, 'OP Payments', '/Op/Payment/', 6, 181);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (21, 'Observation Entry', '/check-basic/', 6, 210);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (22, 'Refunds', '/Refunds/', 7, 211);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (23, 'printpages', '/frontOffice/printpages', 7, 183);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (24, 'Investigation Report', '/Reports/investigationReport/', 7, 194);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (25, 'Expendature Report', '/frontOffice/ExpenditureReport/', 8, 195);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (26, 'Expenditure', '/frontoffice/Expenditure', 8, 202);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (27, 'Cancellation Report', '/Reports/cancellationReport/', 10, 197);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (28, 'Due Report', '/Reports/DueReport/', 11, 198);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (29, 'PRO Master', '/Admin/pro/', 11, 121);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (30, 'State Master', '/Admin/statename/', 12, 122);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (31, 'Payment Mode Report', '/reports/daycollection/', 12, 200);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (32, 'Ref Doctor Report', '/Reports/refdoctorreport', 13, 201);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (33, 'District Master', '/Admin/District/', 13, 123);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (34, 'DayWise Doctor Report', '/Reports/docwiseipoppatinfo/', 14, 203);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (35, 'CaseWise Report', '/Reports/casewisereport/', 15, 204);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (36, 'Doctor Master', '/Admin/Doctor/', 15, 125);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (37, 'Ref Doc Master', '/Admin/refdoctordetails/', 16, 126);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (38, 'ServiceReport', '/Reports/serviceReport/', 16, 205);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (39, 'investdeptwiseReport', '/Reports/investdeptwiseReport/', 17, 206);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (40, 'Speciality Master', '/Admin/speciality/', 17, 127);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (41, 'Service Type Master', '/ip/ServiceType/', 18, 128);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (42, 'Daily Investigation Count', '/Reports/dailyinvreport/', 18, 207);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (43, 'Daily Investigation Report', '/Reports/dialyinvestigations', 19, 208);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (44, 'Case Type Master', '/Admin/casetype/', 19, 129);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (45, 'Daily Procedures', '/Reports/DailyProcedures/', 20, 209);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (46, 'Investigation Master', '/Admin/Investigation/', 23, 133);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (47, 'Investigation Details', '/Admin/investdetailmaster/', 24, 134);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (48, 'Roles Master', '/hospApp/admin/RolesPage/', 26, 136);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (49, 'Invest Department', '/InvDepartment/', 30, 140);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (50, 'Expenditure Master', '/frontoffice/expendituremaster/', 31, 141);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (51, 'Inv Group Master', '/InvestGroupMaster/', 34, 144);
INSERT INTO [hospApp_childsubmenu] ([id], [name], [url], [display_order], [sub_menu_id]) VALUES (52, 'Payee Master', '/hospapp/admin/cardtypemaster/', 36, 146);
SET IDENTITY_INSERT [hospApp_childsubmenu] OFF;

-- ---- [tblroles_pages]  (51 rows) ----
SET IDENTITY_INSERT [tblroles_pages] ON;
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1383, 1, 111);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1384, 1, 112);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1385, 1, 113);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1386, 1, 115);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1387, 1, 121);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1388, 1, 122);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1389, 1, 123);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1390, 1, 125);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1391, 1, 126);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1392, 1, 127);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1343, 1, 128);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1344, 1, 129);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1345, 1, 133);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1346, 1, 134);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1342, 1, 136);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1347, 1, 140);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1348, 1, 141);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1349, 1, 144);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1350, 1, 146);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1351, 1, 148);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1352, 1, 149);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1353, 1, 151);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1354, 1, 152);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1355, 1, 176);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1356, 1, 177);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1357, 1, 178);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1358, 1, 181);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1359, 1, 183);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1360, 1, 184);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1361, 1, 187);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1362, 1, 188);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1363, 1, 189);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1364, 1, 190);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1365, 1, 191);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1366, 1, 192);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1367, 1, 193);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1368, 1, 194);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1369, 1, 195);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1370, 1, 197);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1371, 1, 198);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1372, 1, 200);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1373, 1, 201);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1374, 1, 202);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1375, 1, 203);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1376, 1, 204);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1377, 1, 205);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1379, 1, 207);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1380, 1, 208);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1381, 1, 209);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1382, 1, 210);
INSERT INTO [tblroles_pages] ([id], [tblroles_id], [submenu_id]) VALUES (1393, 1, 211);
SET IDENTITY_INSERT [tblroles_pages] OFF;

-- ---- [tblUserPermission]  (1 rows) ----
SET IDENTITY_INSERT [tblUserPermission] ON;
INSERT INTO [tblUserPermission] ([id], [username], [password], [permission], [isactive], [empid], [empname], [empdesig], [department], [emp_id], [mainrole_id]) VALUES (1, 'admin', '123', 'Registration,OP Consultation,OP Investigations,OP Procedures,OP Payments', 1, 'MH01', 'Admin', 'AdminRole', '', 1, 1);
SET IDENTITY_INSERT [tblUserPermission] OFF;

-- ---- [BankMaster]  (11 rows) ----
SET IDENTITY_INSERT [BankMaster] ON;
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (1, 'Cash', '2025-11-14 05:02:33.511552+00:00', 'admin', 'N');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (2, 'CASH', '2025-11-14 05:03:23.497102+00:00', 'admin', 'Y');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (3, 'CARD', '2025-11-14 05:03:40.527138+00:00', 'admin', 'Y');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (4, 'UPI', '2025-11-14 05:03:45.370085+00:00', 'admin', 'Y');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (5, 'CHEQUE', '2025-11-14 05:04:17.387087+00:00', 'admin', 'N');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (6, 'NEFT', '2025-11-14 05:04:27.898424+00:00', 'admin', 'Y');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (7, 'bbaa', '2025-11-14 05:08:54.323907+00:00', 'admin', 'N');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (8, 'etc', '2026-01-18 09:58:45.755335+00:00', 'admin', 'N');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (9, 'test', '2026-01-18 10:12:40.497695+00:00', 'admin', 'N');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (10, 'test', '2026-01-18 10:15:50.292723+00:00', 'admin', 'N');
INSERT INTO [BankMaster] ([sno], [name], [createddate], [createdby], [active]) VALUES (11, 'NA1', '2026-05-04 06:18:45.235684+00:00', 'admin', 'N');
SET IDENTITY_INSERT [BankMaster] OFF;

-- ---- [hospital_Master]  (1 rows) ----
SET IDENTITY_INSERT [hospital_Master] ON;
INSERT INTO [hospital_Master] ([sno], [name], [address], [phone], [createdby], [creaddate], [updatedby], [updatedtime], [active], [initial], [header], [height], [email], [img]) VALUES (1, 'MANOGNA MULTI SPECIALITY HOSPITAL', 'Plot no:239,Near Ramoji Film City,Abdullapurmet (M),RangaReddy,Ts-501512', '9666911192', 'admin', NULL, NULL, NULL, 'a', 'MH', 'n', 200, '', 'n');
SET IDENTITY_INSERT [hospital_Master] OFF;

-- ---- [department_photo_master]  (9 rows) ----
SET IDENTITY_INSERT [department_photo_master] ON;
INSERT INTO [department_photo_master] ([dno], [department], [active], [createdby], [createddate], [updatedby], [updatedtime], [phote], [photos], [contenttype], [name], [regno], [signature]) VALUES (5, 'gjdjgf', 'Y', 'admin', '2026-06-04 17:04:29.654754+00:00', NULL, NULL, '', NULL, NULL, 'jkhyvkjv', 'klhvkjhv', '');
INSERT INTO [department_photo_master] ([dno], [department], [active], [createdby], [createddate], [updatedby], [updatedtime], [phote], [photos], [contenttype], [name], [regno], [signature]) VALUES (6, 'khlvyj', 'Y', 'admin', '2026-06-04 17:04:44.412791+00:00', NULL, NULL, '', NULL, NULL, 'wrg', 'klyf', '');
INSERT INTO [department_photo_master] ([dno], [department], [active], [createdby], [createddate], [updatedby], [updatedtime], [phote], [photos], [contenttype], [name], [regno], [signature]) VALUES (7, 'Pathology', 'Y', 'admin', '2026-06-04 17:04:48.809594+00:00', 'admin', '2026-06-11 13:19:25.242884+00:00', '', NULL, NULL, 'ganesh', 'argrg', '');
INSERT INTO [department_photo_master] ([dno], [department], [active], [createdby], [createddate], [updatedby], [updatedtime], [phote], [photos], [contenttype], [name], [regno], [signature]) VALUES (8, 'rgerqg', 'Y', 'admin', '2026-06-04 17:04:54.380943+00:00', NULL, NULL, '', NULL, NULL, 'rgg', 'ggrg', '');
INSERT INTO [department_photo_master] ([dno], [department], [active], [createdby], [createddate], [updatedby], [updatedtime], [phote], [photos], [contenttype], [name], [regno], [signature]) VALUES (9, 'rweg3g', 'Y', 'admin', '2026-06-04 17:05:00.095908+00:00', NULL, NULL, '', NULL, NULL, 'regg', 'ggs', '');
INSERT INTO [department_photo_master] ([dno], [department], [active], [createdby], [createddate], [updatedby], [updatedtime], [phote], [photos], [contenttype], [name], [regno], [signature]) VALUES (10, 'rgrg', 'Y', 'admin', '2026-06-04 17:05:05.034914+00:00', NULL, NULL, '', NULL, NULL, 'regrg', 'regrg', '');
INSERT INTO [department_photo_master] ([dno], [department], [active], [createdby], [createddate], [updatedby], [updatedtime], [phote], [photos], [contenttype], [name], [regno], [signature]) VALUES (11, 'gmnm', 'Y', 'admin', '2026-06-04 17:05:12.226137+00:00', NULL, NULL, '', NULL, NULL, 'rtjuj', 'fgmjm', '');
INSERT INTO [department_photo_master] ([dno], [department], [active], [createdby], [createddate], [updatedby], [updatedtime], [phote], [photos], [contenttype], [name], [regno], [signature]) VALUES (12, 'gfhmnfgn', 'Y', 'admin', '2026-06-04 17:05:17.568986+00:00', NULL, NULL, '', NULL, NULL, 'ngghmn', 'nghngh', '');
INSERT INTO [department_photo_master] ([dno], [department], [active], [createdby], [createddate], [updatedby], [updatedtime], [phote], [photos], [contenttype], [name], [regno], [signature]) VALUES (13, 'hgmnrj', 'Y', 'admin', '2026-06-04 17:05:21.929333+00:00', NULL, NULL, '', NULL, NULL, 'fgmnrtj', 'fgmnte', '');
SET IDENTITY_INSERT [department_photo_master] OFF;

-- ---- [case_type_master]  (1 rows) ----
SET IDENTITY_INSERT [case_type_master] ON;
INSERT INTO [case_type_master] ([sno], [casetype], [active], [createdby], [createdtime], [updatedby], [updatedtime]) VALUES (2, 'CARDIO', 'Y', 'admin', '2026-06-08 06:34:15.532423+00:00', NULL, NULL);
SET IDENTITY_INSERT [case_type_master] OFF;

-- ---- [hospApp_promaster]  (1 rows) ----
SET IDENTITY_INSERT [hospApp_promaster] ON;
INSERT INTO [hospApp_promaster] ([proid], [pro_name], [specialized], [address], [phone], [active], [userid], [createdby], [updatedby], [createddate], [updateddate]) VALUES (2, 'SELF', NULL, NULL, 7844475444, 'Y', NULL, 'admin', NULL, '2026-06-08 06:14:32.591221+00:00', NULL);
SET IDENTITY_INSERT [hospApp_promaster] OFF;

-- ---- [inv_group_master]  (1 rows) ----
SET IDENTITY_INSERT [inv_group_master] ON;
INSERT INTO [inv_group_master] ([sno], [gname], [userid], [insertedtime], [updatedby], [updatedtime], [active]) VALUES (2, 'test', 'admin', '2026-06-11 13:19:54.389660+00:00', NULL, NULL, 'Y');
SET IDENTITY_INSERT [inv_group_master] OFF;

-- ---- [investigation_master]  (2 rows) ----
SET IDENTITY_INSERT [investigation_master] ON;
INSERT INTO [investigation_master] ([ino], [invname], [department_id], [groups], [cost], [ip], [active], [createdby], [createddate], [updatedby], [updateddate]) VALUES (6, 'Complete blood picture(CBP)', 7, 'test', 500, 500, 'Y', 'admin', '2026-06-11 13:21:18.347370+00:00', NULL, NULL);
INSERT INTO [investigation_master] ([ino], [invname], [department_id], [groups], [cost], [ip], [active], [createdby], [createddate], [updatedby], [updateddate]) VALUES (7, 'urine test', 7, 'test', 600, 600, 'Y', 'admin', '2026-06-12 07:17:23.679786+00:00', NULL, NULL);
SET IDENTITY_INSERT [investigation_master] OFF;

-- ---- [refdoc_master]  (1 rows) ----
SET IDENTITY_INSERT [refdoc_master] ON;
INSERT INTO [refdoc_master] ([docid], [docname], [phoneno], [active], [createdby], [createdtime], [updatedby], [updatedtime], [specialized_id]) VALUES (2, 'SELF', '7454545454', 'Y', 'admin', '2026-06-08 06:32:45.861549+00:00', NULL, NULL, 2);
SET IDENTITY_INSERT [refdoc_master] OFF;

-- ---- [service_type_master]  (2 rows) ----
SET IDENTITY_INSERT [service_type_master] ON;
INSERT INTO [service_type_master] ([serviceid], [servicename], [servicetypename], [servicecode], [description], [charge], [labservices], [active], [createdby], [createdtime], [updatedby], [updatedtime]) VALUES (2, 'ambulance charge', NULL, NULL, NULL, 500, NULL, 'Y', NULL, '2026-06-12 07:38:59.998301+00:00', NULL, NULL);
INSERT INTO [service_type_master] ([serviceid], [servicename], [servicetypename], [servicecode], [description], [charge], [labservices], [active], [createdby], [createdtime], [updatedby], [updatedtime]) VALUES (3, 'cleaning', NULL, NULL, NULL, 600, NULL, 'Y', NULL, '2026-06-12 07:40:18.361327+00:00', NULL, NULL);
SET IDENTITY_INSERT [service_type_master] OFF;

-- ---- [speciality_master]  (1 rows) ----
SET IDENTITY_INSERT [speciality_master] ON;
INSERT INTO [speciality_master] ([sno], [speciality], [userid], [insertedtime], [updatedby], [updatedtime], [active]) VALUES (2, 'TEST', 'admin', '2026-06-08 06:32:22.965139+00:00', NULL, NULL, 'Y');
SET IDENTITY_INSERT [speciality_master] OFF;

-- ---- [doctor_master]  (2 rows) ----
SET IDENTITY_INSERT [doctor_master] ON;
INSERT INTO [doctor_master] ([docid], [docname], [address], [phoneno], [consultfee], [ipconsultfee], [emrfee], [active], [createdby], [createdtime], [updatedby], [updatedtime], [speciality], [revisittime], [qualification], [regno]) VALUES (3, 'Dr TEST', NULL, '7545454545', 500, 500, 500, 'Y', NULL, '2026-06-08 06:34:43.129343+00:00', NULL, NULL, 2, 5, 'TEST', '46333');
INSERT INTO [doctor_master] ([docid], [docname], [address], [phoneno], [consultfee], [ipconsultfee], [emrfee], [active], [createdby], [createdtime], [updatedby], [updatedtime], [speciality], [revisittime], [qualification], [regno]) VALUES (4, 'Dr ganesh', NULL, '7575757727', 500, 500, 550, 'Y', NULL, '2026-06-11 12:35:56.870820+00:00', NULL, NULL, 2, 5, 'MBBS,GOLD MEDALS', '65511212121212');
SET IDENTITY_INSERT [doctor_master] OFF;

-- ---- [tblInvestigationDetails]  (4 rows) ----
SET IDENTITY_INSERT [tblInvestigationDetails] ON;
INSERT INTO [tblInvestigationDetails] ([uhid], [invname], [cost], [generateddate], [createdby], [updatedby], [updatedtime], [billno], [ipno], [patname], [age], [agetype], [gender], [doc], [refdoc], [ID_PK], [type], [concessionamt], [concreason], [paidamt], [due], [refundate], [refund], [paymentmode], [cardname], [active], [cancelreson], [dept], [phone], [doctor], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES ('MH20260004', '6', 500, '2026-06-11 13:21:42.089912+00:00', 'admin', NULL, NULL, 31, NULL, 'test four', 25, 'Years', 'Male', '4', '2', 37, NULL, 200, 'hgcutch', 250, 50, NULL, 'N', 'CASH', '', 'Y', NULL, '', 8511313131, NULL, 0, 0, NULL, NULL);
INSERT INTO [tblInvestigationDetails] ([uhid], [invname], [cost], [generateddate], [createdby], [updatedby], [updatedtime], [billno], [ipno], [patname], [age], [agetype], [gender], [doc], [refdoc], [ID_PK], [type], [concessionamt], [concreason], [paidamt], [due], [refundate], [refund], [paymentmode], [cardname], [active], [cancelreson], [dept], [phone], [doctor], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES ('MH20260004', '6', 500, '2026-06-12 06:51:48.730943+00:00', 'admin', NULL, NULL, 32, NULL, 'test four', 25, 'Years', 'Male', '4', '2', 38, NULL, 50, 'rtuyrturtmn f iyu', 400, 50, NULL, 'N', 'Split (Cash + UPI)', 'ghjkgk gky', 'Y', NULL, '', 8511313131, NULL, 200, 200, 'sssss', 'NEFT');
INSERT INTO [tblInvestigationDetails] ([uhid], [invname], [cost], [generateddate], [createdby], [updatedby], [updatedtime], [billno], [ipno], [patname], [age], [agetype], [gender], [doc], [refdoc], [ID_PK], [type], [concessionamt], [concreason], [paidamt], [due], [refundate], [refund], [paymentmode], [cardname], [active], [cancelreson], [dept], [phone], [doctor], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES ('MH20260004', '6', 500, '2026-06-12 07:18:41.770560+00:00', 'admin', NULL, NULL, 33, NULL, 'test four', 25, 'Years', 'Male', '4', '2', 39, NULL, 50, 'jhdfyjdj', 1000, 50, NULL, 'N', 'Split (Cash + NEFT)', '123456', 'N', NULL, '', 8511313131, NULL, 500, 500, '000000', 'UPI');
INSERT INTO [tblInvestigationDetails] ([uhid], [invname], [cost], [generateddate], [createdby], [updatedby], [updatedtime], [billno], [ipno], [patname], [age], [agetype], [gender], [doc], [refdoc], [ID_PK], [type], [concessionamt], [concreason], [paidamt], [due], [refundate], [refund], [paymentmode], [cardname], [active], [cancelreson], [dept], [phone], [doctor], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES ('MH20260004', '7', 600, '2026-06-12 07:18:41.780823+00:00', 'admin', NULL, NULL, 33, NULL, 'test four', 25, 'Years', 'Male', '4', '2', 40, NULL, 50, 'jhdfyjdj', 1000, 50, NULL, 'N', 'Split (Cash + NEFT)', '123456', 'N', NULL, '', 8511313131, NULL, 500, 500, '000000', 'UPI');
SET IDENTITY_INSERT [tblInvestigationDetails] OFF;

-- ---- [tblservices]  (8 rows) ----
SET IDENTITY_INSERT [tblservices] ON;
INSERT INTO [tblservices] ([ID_PK], [uhid], [services], [services_typename], [amount], [generateddate], [generatedtime], [createdby], [createddate], [updatedby], [updateddate], [billno], [pattype], [type], [concessionamt], [concreason], [paidamt], [due], [qty], [ipno], [isactive], [cardname], [paymentmode], [doctor], [doc_id], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES (3, 'MH20260004', '2', 'ambulance charge', 500, '2026-06-12 07:59:57.847986+00:00', '2026-06-12 07:59:57.847986+00:00', 'admin', '2026-06-12 07:59:57.847986+00:00', NULL, NULL, 34, 'OP', 'OP', 50, 'tryu  tjri', 1050, 0, 1, NULL, 'Y', '123456', 'Split (Cash + UPI)', 'Dr ganesh', 4, 550, 500, '123456', 'UPI');
INSERT INTO [tblservices] ([ID_PK], [uhid], [services], [services_typename], [amount], [generateddate], [generatedtime], [createdby], [createddate], [updatedby], [updateddate], [billno], [pattype], [type], [concessionamt], [concreason], [paidamt], [due], [qty], [ipno], [isactive], [cardname], [paymentmode], [doctor], [doc_id], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES (4, 'MH20260004', '3', 'cleaning', 600, '2026-06-12 07:59:57.865870+00:00', '2026-06-12 07:59:57.865870+00:00', 'admin', '2026-06-12 07:59:57.865870+00:00', NULL, NULL, 34, 'OP', 'OP', 50, 'tryu  tjri', 1050, 0, 1, NULL, 'Y', '123456', 'Split (Cash + UPI)', 'Dr ganesh', 4, 550, 500, '123456', 'UPI');
INSERT INTO [tblservices] ([ID_PK], [uhid], [services], [services_typename], [amount], [generateddate], [generatedtime], [createdby], [createddate], [updatedby], [updateddate], [billno], [pattype], [type], [concessionamt], [concreason], [paidamt], [due], [qty], [ipno], [isactive], [cardname], [paymentmode], [doctor], [doc_id], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES (5, 'MH20260004', '3', 'cleaning', 700, '2026-06-12 08:02:55.153039+00:00', '2026-06-12 08:02:55.153039+00:00', 'admin', '2026-06-12 08:02:55.153039+00:00', NULL, NULL, 35, 'OP', 'OP', 100, '6fuyuy6fi6', 900, 200, 2, NULL, 'Y', 'yiufiyuf', 'Split (Cash + NEFT)', 'Dr ganesh', 4, 500, 400, 'yiufiyuf', 'NEFT');
INSERT INTO [tblservices] ([ID_PK], [uhid], [services], [services_typename], [amount], [generateddate], [generatedtime], [createdby], [createddate], [updatedby], [updateddate], [billno], [pattype], [type], [concessionamt], [concreason], [paidamt], [due], [qty], [ipno], [isactive], [cardname], [paymentmode], [doctor], [doc_id], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES (6, 'MH20260004', '2', 'ambulance charge', 500, '2026-06-12 08:02:55.175710+00:00', '2026-06-12 08:02:55.175710+00:00', 'admin', '2026-06-12 08:02:55.175710+00:00', NULL, NULL, 35, 'OP', 'OP', 100, '6fuyuy6fi6', 900, 200, 1, NULL, 'Y', 'yiufiyuf', 'Split (Cash + NEFT)', 'Dr ganesh', 4, 500, 400, 'yiufiyuf', 'NEFT');
INSERT INTO [tblservices] ([ID_PK], [uhid], [services], [services_typename], [amount], [generateddate], [generatedtime], [createdby], [createddate], [updatedby], [updateddate], [billno], [pattype], [type], [concessionamt], [concreason], [paidamt], [due], [qty], [ipno], [isactive], [cardname], [paymentmode], [doctor], [doc_id], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES (7, 'MH20260004', '3', 'cleaning', 1000, '2026-06-12 08:09:43.822280+00:00', '2026-06-12 08:09:43.822280+00:00', 'admin', '2026-06-12 08:09:43.822280+00:00', NULL, NULL, 36, 'OP', 'OP', 100, 'eyjty yjej', 1200, 200, 2, NULL, 'Y', '', 'Split (Cash + CARD)', 'Dr ganesh', 4, 1000, 200, '', 'CARD');
INSERT INTO [tblservices] ([ID_PK], [uhid], [services], [services_typename], [amount], [generateddate], [generatedtime], [createdby], [createddate], [updatedby], [updateddate], [billno], [pattype], [type], [concessionamt], [concreason], [paidamt], [due], [qty], [ipno], [isactive], [cardname], [paymentmode], [doctor], [doc_id], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES (8, 'MH20260004', '2', 'ambulance charge', 500, '2026-06-12 08:09:43.835858+00:00', '2026-06-12 08:09:43.835858+00:00', 'admin', '2026-06-12 08:09:43.835858+00:00', NULL, NULL, 36, 'OP', 'OP', 100, 'eyjty yjej', 1200, 200, 1, NULL, 'Y', '', 'Split (Cash + CARD)', 'Dr ganesh', 4, 1000, 200, '', 'CARD');
INSERT INTO [tblservices] ([ID_PK], [uhid], [services], [services_typename], [amount], [generateddate], [generatedtime], [createdby], [createddate], [updatedby], [updateddate], [billno], [pattype], [type], [concessionamt], [concreason], [paidamt], [due], [qty], [ipno], [isactive], [cardname], [paymentmode], [doctor], [doc_id], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES (9, 'MH20260004', '2', 'ambulance charge', 500, '2026-06-12 09:05:16.679497+00:00', '2026-06-12 09:05:16.679497+00:00', 'admin', '2026-06-12 09:05:16.679497+00:00', NULL, NULL, 37, 'OP', 'OP', 200, 'xfgdt djhj', 400, 500, 1, NULL, 'Y', '123456', 'Split (Cash + UPI)', 'Dr ganesh', 4, 200, 200, '123456', 'UPI');
INSERT INTO [tblservices] ([ID_PK], [uhid], [services], [services_typename], [amount], [generateddate], [generatedtime], [createdby], [createddate], [updatedby], [updateddate], [billno], [pattype], [type], [concessionamt], [concreason], [paidamt], [due], [qty], [ipno], [isactive], [cardname], [paymentmode], [doctor], [doc_id], [cash_amt], [online_amt], [online_details], [online_mode]) VALUES (10, 'MH20260004', '3', 'cleaning', 600, '2026-06-12 09:05:16.693669+00:00', '2026-06-12 09:05:16.693669+00:00', 'admin', '2026-06-12 09:05:16.693669+00:00', NULL, NULL, 37, 'OP', 'OP', 200, 'xfgdt djhj', 400, 500, 1, NULL, 'Y', '123456', 'Split (Cash + UPI)', 'Dr ganesh', 4, 200, 200, '123456', 'UPI');
SET IDENTITY_INSERT [tblservices] OFF;

COMMIT TRANSACTION;
