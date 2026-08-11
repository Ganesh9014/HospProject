from django.urls import path
from . import views

urlpatterns = [

    # ===================== AUTH =====================
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),

    # ===================== ADMIN MASTERS =====================
    path('Admin/empRegistration/', views.add_employee, name='empRegistration'),
    path('Admin/addpermission/', views.add_permission, name='addpermission'),
    path('Admin/ChangePassword/', views.ChangePassword, name='ChangePassword'),
    path('Admin/reportcharge_master/', views.AdmissionCharges, name='AdmissionCharges'),
    path('Admin/Department/', views.DepartmentMaster, name='DepartmentMaster'),
    path('ip/floors/', views.FloorMasterView, name='FloorMaster'),
    path('ip/Roomtype/', views.RoomTypeMasterView, name='RoomTypeMaster'),
    path('master/admin/Rooms/', views.RoomMasterView, name='RoomMasterView'),
    path('master/admin/beds/', views.BedMasterView, name='BedsMasterView'),
    path('Admin/statename/', views.StateMasterView, name='StateMasterView'),
    path('Admin/District/', views.DistrictMasterView, name='DistrictMasterView'),
    path('master/admin/Autoservices/', views.ServiceMasterView, name='ServiceMaster'),
    path('Admin/pro/', views.ProMasterView, name='ProMaster'),
    path('Admin/speciality/', views.SpecialityMasterView, name='SpecialityMasterView'),
    path('Admin/Doctor/', views.DoctorMasterView, name='DoctorMasterView'),
    path('Admin/refdoctordetails/', views.RefDoctorMasterView, name='RefDoctorMasterView'),
    path('ip/ServiceType/', views.ServiceTypeMasterView, name='ServiceTypeMasterView'),
    path('Admin/casetype/', views.CaseTypeMasterView, name='CaseTypeMasterView'),
    path('hospapp/admin/cardtypemaster/', views.BankMasterView, name='BankMaster'),

    # ===================== AJAX MASTERS =====================
    path('ajax/rooms-by-floor/', views.rooms_by_floor, name='ajax_rooms_by_floor'),
    path('add-refdoctor/', views.add_refdoctor_ajax, name='add_refdoctor_ajax'),
    path('load-districts/', views.load_districts, name='load_districts'),
    path('load-cities/', views.load_cities, name='load_cities'),
    path('ajax/suggest-refdoctors/', views.suggest_refdoctors, name='suggest_refdoctors'),
    path('ajax/suggest-pros/', views.suggest_pros, name='suggest_pros'),

    # ===================== OPD / IPD =====================
    path('op/oppatient/', views.OpPatientRegistrationView, name='OpPatientRegistration'),
    path('frontOffice/ipRegistration/', views.IpRegistrationView, name='IpRegistrationView'),

    # ===================== DOCTOR CONSULTATION =====================
    path('frontOffice/DocConsultation/', views.DoctorConsultationView, name='DocConsulationView'),
    path('doctor-consultation/print-select/<int:pk>/', views.consultation_print_select, name='consultation-print-select'),
    path('doctor-consultation/receipt/<int:pk>/', views.consultation_receipt, name='consultation-receipt'),
    path('doctor-consultation/prescription/<int:pk>/', views.consultation_prescription, name='consultation-prescription'),

    # ===================== PATIENT SEARCH =====================
    path('get-patient-details1/', views.get_patient_details1, name='get-patient-details1'),
    path('get-patient-details/', views.get_patient_details, name='get-patient-details'),
    path('search-uhid/', views.SearchUHIDView, name='SearchUHIDView'),
    path('search-consultation-uhid/', views.SearchConsultationUHIDView, name='SearchConsultationUHIDView'),
    path('search-doctors/', views.search_doctors, name='search-doctors'),
    path('search-doctors1/', views.search_doctors1, name='search-doctors1'),
    path('check-revisit-fee/', views.check_revisit_fee, name='check_revisit_fee'),

    # ===================== PROCEDURE & LAB =====================
    path('frontOffice/opprocedure/', views.OPProcedureView, name='OPProcedureView'),
    path('Lab/OpInvestigation/', views.OpInvestigationView, name='OpInvestigationView'),

    path('Admin/Investigation/', views.InvestigationMasterView, name='InvestigationMaserView'),
    path('InvDepartment/', views.InvDepartmentMasterView, name='InvDepartment'),
    path('InvestGroupMaster/', views.InvGroupMasterView, name='InvGroupMasterView'),
    path('search-investigation/', views.search_investigation, name='search-investigation'),
    path('save-investigation/', views.save_investigation, name='save_investigation'),
    path('op-investigation-bill/<int:billno>/', views.op_investigation_bill, name='op_investigation_bill'),

    # ===================== PRESCRIPTION MODULE (FINAL) =====================

    # ✅ Select patient for prescription
    path('select-patient/', views.SearchConsultationUHIDView1, name='SearchConsultationUHIDView1'),

    # ✅ Completed consultations — separate page
    path('completed-consultations/', views.CompletedConsultationsView, name='CompletedConsultationsView'),

    # ✅ Open Writing + Audio Prescription Page
    path('doctor/prescription/', views.create_prescription, name='create_prescription'),
    path('doctor/prescription/recognize-handwriting-ajax/', views.recognize_handwriting_ajax, name='recognize_handwriting_ajax'),

    # ✅ Print Writing Prescription
    path('prescription/print/<int:prescription_id>/', views.print_prescription, name='print_prescription'),

    # ✅ Save Audio Prescription (AJAX)
    path('prescriptions/audio/create/', views.create_audio_prescription_ajax, name='create_audio_prescription_ajax'),

    # ✅ Print Audio Prescription
    path('prescriptions/audio/print/<int:pres_id>/', views.print_audio_prescription, name='print_audio_prescription'),

    # ===================== TEST / GPT =====================
    path("check-gpt/", views.check_gpt_version, name='hello'),
    path("revisit/write/<int:consult_id>/", views.revisit_prescription, name="revisit_prescription"),

    path("revisit/audio/<int:consult_id>/", views.revisit_audio_prescription, name="revisit_audio_prescription"),

    path("revisit/<int:consult_id>/", views.smart_revisit_redirect, name="smart_revisit"),
    path('previous-prescription/<int:pk>/',views.previous_prescription_view,name='previous_prescription'),
    path('get-patient-details-op/', views.get_patient_details_op, name='get_patient_details_op'),
    path("search-service/", views.search_service, name="search_service"),

    path("save-procedure/", views.save_procedure, name="save_procedure"),
    path("procedure-bill/<int:billno>/", views.op_procedure_bill, name="op_procedure_bill"),
    path("check-basic/",views.check_basic,name="check_basic"),
    path("values_insert/",views.values_insert,name="values_insert"), 
    path("get_patient_details_for_insert/",views.get_patient_details_for_insert,name="get_patient_details_for_insert"),
    path("values-insert/", views.values_insert, name="values_insert"),
    path("Op/Payment/", views.op_payment_page, name="OpPayment"),
    path("ajax/get-bills/", views.get_bills_by_towards, name="get_bills_by_towards"),
    # path("ajax/get-consultation-payment/",views.get_consultation_payment,name="get_consultation_payment"),
    # path("ajax/get-procedure-payment/", views.get_procedure_payment),
    # path("ajax/get-investigation-payment/", views.get_investigation_payment),
   
    path("ajax/get-patient-by-uhid/", views.get_patient_by_uhid),
    path("ajax/get-bill-type/", views.get_bill_type_by_billno, name="get_bill_type"),
    
    # ---------------- SAVE OP PAYMENT ----------------
    path(
        "op-payment/save/",
        views.save_op_payment,
        name="save_op_payment"
    ),
    path(
    "op-payment/receipt/<str:invbillno>/",
    views.op_payment_receipt,
    name="op_payment_receipt"
    ),
    path(
    "frontOffice/printpages",
    views.PrintPages,
    name="printpages"
    ),
    path("ajax/get-bill-details/", views.get_bill_details_by_billno, name="get_bill_details"),
    path(
        "print-pages/save/",
        views.save_print_page,
        name="save_print_page"
    ),
    path("bill-lookup/", views.bill_lookup_by_type, name="bill_lookup"),
    path('op/Cancellation/',views.CancellationView,name='CancellationView'),
    path("ajax/validate-user/", views.validate_user_code, name="validate_user"),
    
    path("Reports/userwisecollection/", views.UserWiseCollection, name="UserWiseCollection"),
    path("userwise-collection/report/", views.userwise_collection_report1, name="userwise_collection_report1"),


    path("Refunds/",views.RefundView,name="RefundView"),
    path("ajax/get-refund-bills/", views.get_refund_bills_by_towards, name="get_refund_bills"),
    path("ajax/get-bill-items/", views.get_bill_items, name="get_bill_items"),
    # ADD THIS (do NOT remove existing urls)
    path("refund/save/", views.save_refund, name="save_refund"),
    path("hospApp/admin/RolesPage/", views.RolesPage, name="RolesPage"),
    path("Admin/investdetailmaster/", views.InvestdetailsView, name="InvestdetailsView"),
    path("hospApp/Admin/inv123/", views.InvestigationDetailsMaster, name="InvestigationDetailsMaster"),
    # urls.py
    path("get-investigation-details/", views.get_investigation_details, name="get-investigation-details"),
    path("fetch-investigation-details/", views.fetch_investigation_details,name="fetch_investigation_details"),
    path("delete-investigation-row/",views.delete_investigation_row,name="delete_investigation_row"),
    path("Lab/LabEntry/", views.LabEntry, name="LabEntry"),
    path('get-lab-entries/', views.get_lab_entries_by_date, name='get_lab_entries'),
    path('get-investigations/', views.get_investigations_by_bill, name='get_investigations'),
    path('get-patient-by-bill/', views.get_patient_by_bill, name='get_patient_by_bill'),
    path('get-report-entries/', views.get_report_entries, name='get_report_entries'),
    path(
    "Lab/ReportEntry/",
    views.ReportEntry,
    name="report_entry"
    ),
    path("report-entry/", views.ReportEntry, name="report_entry"),
    path("final-report/", views.FinalReportView, name="final_report"),
    path("save-report/", views.save_report_entries, name="save_report_entries"),
    path("check-report-exists/", views.check_report_exists, name="check_report_exists"),
    path(
    "get-investigation-department/",
    views.get_investigation_department,
    name="get_investigation_department"
    ),
    path("Lab/modifylab/", views.Modifylab, name="Modifylab"),
    path('get-investigations-date/', views.get_investigations_with_date, name='get_investigations_with_date'),
    path('get-existing-report/', views.get_existing_report, name='get_existing_report'),
    path('get-completed-investigations/', views.get_completed_investigations, name='get_completed_investigations'),
    path('Lab/prev_reports/',views.ReportsPage,name='ReportsPage'),
    path(
    'get-lab-entries/',
    views.get_lab_entries_by_date,
    name='get_lab_entries_by_date'
    ),
    path('op-report/', views.op_report, name='op_report'),

    path("login-reports/",views.login_reports,name="login_reports"),    
    path("inv_details_home/",views.Investigation_details,name="inv_details_home"),   
    path("pro_details_home/",views.procedure_details,name="pro_details_home"),
    path('all-dues/', views.all_dues_today, name='all_dues'),
    path('all_concessions_today/', views.all_concessions_today, name='all_concessions'),
    path("Reports/ConcessionReport/",views.ConcessionReport,name="ConcessionReport"),
    path('concession-report/', views.concession_report, name='concession_report'),
    path("op/OPAdmissionModify/",views.OpModify,name="OpModify"),
    path("op/RegistrationUhidFinder",views.RegistrationUhidFinder,name="RegistrationUhidFinder"),
    path('get-patient-details-simple/', views.get_patient_details_simple, name='get_patient_details_simple'),
    path('update-consultation/', views.update_consultation, name='update_consultation'),
    path("suggest_refdoctors1/", views.suggest_refdoctors1, name="suggest_refdoctors1"),
    path("frontoffice/expendituremaster/", views.ExpenditureMasterView, name="ExpenditureMasterView"),
    path("frontoffice/Expenditure/", views.ExpenditureView, name="ExpenditureView"),
    path('expenditure-print/<int:billno>/', views.expenditure_print, name='expenditure_print'),
    path("frontOffice/ExpenditureReport/", views.ExpenditureReportView, name="ExpenditureReportView"),
    path('expenditure-report/', views.userwise_collection_report, name='userwise_collection_report'),
    path('Reports/investigationReport/', views.InvestigationReportView, name='InvestigationReportView'),
    path('investigation-report/', views.investigation_report, name='investigation_report'),
    path("Reports/Patinfo/", views.patinfo, name="patinfo"),
    path('Reports/proreport', views.ProReportForm, name='pro_report_form'),
    path('pro-report/result/', views.ProReportResult, name='pro_report_result'),
    path("Reports/cancellationReport/", views.CancellationReport, name="CancellationReport"),
    path('cancellationReportResult/', views.CancellationReportResult, name='CancellationReportResult'),
    path("Reports/DueReport/", views.DueReports, name="DueReports"),
    path("reports/all-due-report/", views.all_dues_filtered, name="all_dues_filtered"),
    path("reports/daycollection/", views.daycollection, name="daycollection"),
    path('paymentmode-collection-report/', views.paymentmode_collection_report, name='paymentmode_collection_report'),
    path("Reports/refdoctorreport", views.Refdoctorreport, name="Refdoctorreport"),
    path('refdoctor-report-result/', views.RefDoctorReportResult, name='refdoctor_report_result'),
    path('Reports/docwiseipoppatinfo/',views.DayWiseDocReportView,name="DayWiseDocReportView"),
    path('daywisedoc-report-result/', views.DayWiseDocReportResult, name='DaywiseDocReportResult'),
    path('Reports/casewisereport/',views.CaseWiseReportView,name="CaseWiseReportView"),
    path('casewise-report-result/', views.CaseWiseReportResultView, name='CaseWiseReportResultView'), 
    path('Reports/serviceReport/',views.ServiceReportView,name="ServiceReportView"),
    path('service-report-result/', views.ServiceReportResultView, name='ServiceReportResultView'),  
    path('Reports/dailyinvreport/',views.InvCal,name="InvCal"),
    path('reports/invcalresult',views.InvCalResult,name="InvCalResult"),
    path('Reports/investdeptwiseReport/',views.InvestDeptWiseReport,name='InvestDeptWiseReport'),
    # urls.py
    path('search-department/', views.search_department, name='search_department'),
    path('Reports/investdeptwiseReportResult/',views.InvestDeptWiseReportResult,name='InvestDeptWiseReportResult'),
    path('Reports/dialyinvestigations/',views.DailyInvestigations,name='DailyInvestigations'),
    path('dialyinvestigationsresult/',views.DailyInvestigationsResult,name='DailyInvestigationsResult'),
    path('Reports/DailyProcedures/',       views.DailyProcedures,       name='DailyProcedures'),
    path('DailyProceduresResult/', views.DailyProceduresResult, name='DailyProceduresResult'),
    path('paymentmodeupdate/', views.paymentmodeupdate, name='paymentmodeupdate'),
    path(
        'ajax/get-paymentmode-details/',
        views.get_paymentmode_details,
        name='get_paymentmode_details'
    ),
    path(
    'save-payment-mode-update/',
    views.save_payment_mode_update,
    name='save_payment_mode_update'
    ),
    path('SittingsPage/', views.SittingsPageView, name='SittingsPageView'),
    path('get-sittings-patient-data/', views.get_sittings_patient_data, name='get_sittings_patient_data'),
    path('get-sittings-procedures-by-bill/', views.get_sittings_procedures_by_bill, name='get_sittings_procedures_by_bill'),
    path('save-sitting-entry/', views.save_sitting_entry, name='save_sitting_entry'),
    path('sittings-receipt/', views.sittings_receipt, name='sittings_receipt'),


    

 
   




    




    








]
