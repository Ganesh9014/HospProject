from django.shortcuts import render
from datetime import datetime, timedelta
from django.db.models import Sum, Max, OuterRef, Subquery
from django.utils import timezone

from hospApp.models import (
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    TblOpCancellation,
    OpPayment,
    OpPatientRegistration,
    Tbluserpermission,
    ExpenditureEntry,
    HospitalMaster,
    TblRefund
)
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def UserWiseCollection(request):
    users = Tbluserpermission.objects.filter(isactive=True).order_by('username')
    return render(request, 'hospApp/reports/UserwiseCollection.html', {"users": users})

@login_required(login_url='login')
def userwise_collection_report1(request):

    # ================= BASIC INPUTS =================
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    username = request.GET.get("username")
    report_type = request.GET.get("report_type")
    services = request.GET.getlist("services[]")

    if not from_date or not to_date:
        return render(request, "hospApp/reports/userwisecollection_report.html")

    show_all = not services

    fd = datetime.strptime(from_date, "%Y-%m-%dT%H:%M")
    td = datetime.strptime(to_date, "%Y-%m-%dT%H:%M") + timedelta(minutes=1)

    # ================= COMMON SUBQUERY =================
    patient_name_sq = OpPatientRegistration.objects.filter(
        uhid=OuterRef('uhid')
    ).values('patname')[:1]

    # ==================================================
    # OP CONSULTATION
    # ==================================================
    consultation_total = 0
    consultation_bills = []

    if show_all or "OP Consultation" in services:
        qs = DoctorConsultation.objects.filter(
            createddate__gte=fd,
            createddate__lt=td,
            
        )

        if username and username != "ALL":
            qs = qs.filter(userid=username)

        consultation_bills = (
            qs.values(
                'billno', 'uhid', 'paymenttype',
                'regdt', 'userid', 'cardname','cash_amt','online_amt','online_mode'
            )
            .annotate(
                patname=Subquery(patient_name_sq),   # ✅ FIXED
                paidamt=Sum('paidamt')
            )
            .order_by('billno')
        )

        consultation_total = sum(c['paidamt'] or 0 for c in consultation_bills)

    # ==================================================
    # OP PROCEDURES
    # ==================================================
    procedure_total = 0
    procedure_bills = []

    if show_all or "OP Procedures" in services:
        qs = TblServices.objects.filter(
            createddate__gte=fd,
            createddate__lt=td,
            
        )

        if username and username != "ALL":
            qs = qs.filter(createdby=username)

        procedure_bills = (
            qs.values('billno', 'uhid')
            .annotate(
                patname=Subquery(patient_name_sq),
                generateddate=Max('generateddate'),
                createdby=Max('createdby'),
                paymentmode=Max('paymentmode'),
                cardname=Max('cardname'),
                paidamt=Max('paidamt'),
            )
            .order_by('billno')
        )

        procedure_total = sum(p['paidamt'] or 0 for p in procedure_bills)

    # ==================================================
    # OP INVESTIGATIONS
    # ==================================================
    investigation_total = 0
    investigation_bills = []

    if show_all or "OP Investigations" in services:
        qs = tblInvestigationDetails.objects.filter(
            generateddate__gte=fd,
            generateddate__lt=td,
        
        )

        if username and username != "ALL":
            qs = qs.filter(createdby=username)

        investigation_bills = (
            qs.values('billno', 'uhid')   # ✅ FIXED
            .annotate(
                patname=Subquery(patient_name_sq),   # ✅ FIXED
                generateddate=Max('generateddate'),
                createdby=Max('createdby'),
                paymentmode=Max('paymentmode'),
                cardname=Max('cardname'),
                paidamt=Max('paidamt'),
            )
            .order_by('billno')
        )

        investigation_total = sum(i['paidamt'] or 0 for i in investigation_bills)

    # ==================================================
    # OP PAYMENTS
    # ==================================================
    op_total = 0
    op_payment_bills = []

    if show_all or "OP Payments" in services:
        qs = OpPayment.objects.filter(
            billdate__gte=fd,
            billdate__lt=td,
            
        )

        if username and username != "ALL":
            qs = qs.filter(updatedby=username)

        op_payment_bills = (
            qs.values(
                'invbillno', 'uhid', 'billdate',
                'updatedby', 'paymentmode', 'cardname'
            )
            .annotate(
                patname=Subquery(patient_name_sq),
                paidamt=Sum('patamt')
            )
            .order_by('invbillno')
        )

        op_total = sum(o['paidamt'] or 0 for o in op_payment_bills)

    # ==================================================
    # OP CANCELLATIONS
    # ==================================================
    cancellation_total = 0
    cancellation_bills = []

    if show_all or "OP Cancellations" in services:
        qs = TblOpCancellation.objects.filter(
            createddate__gte=fd,
            createddate__lt=td
        )

        if username and username != "ALL":
            qs = qs.filter(createdby=username)

        cancellation_bills = (
            qs.values(
                'billno', 'uhid',
                'createddate', 'createdby'
            )
            .annotate(
                patname=Subquery(patient_name_sq),   # ✅ FIXED
                amtpaid=Sum('amtpaid')
            )
        )

        cancellation_total = sum(c['amtpaid'] or 0 for c in cancellation_bills)

    # ==================================================
    # EXPENDITURE
    # ==================================================
    expenditure_total = 0
    expenditure_bills = []

    if show_all or "EXPENDITURE" in services:
        qs = ExpenditureEntry.objects.filter(
            created_at__gte=fd,
            created_at__lt=td,
            active="Y"  
        )

        if username and username != "ALL":
            qs = qs.filter(username=username)

        expenditure_bills = qs.values(
            'bill_no', 'amount', 'towards', 'created_at'
        ).order_by('bill_no')

        expenditure_total = sum(e['amount'] or 0 for e in expenditure_bills)

    # ==================================================
    # OP REFUNDS
    # ==================================================
    refund_total = 0
    refund_bills = []

    if show_all or "Refunds" in services:
        qs = TblRefund.objects.filter(
            createdtime__gte=fd,
            createdtime__lt=td
        )

        if username and username != "ALL":
            qs = qs.filter(createdby=username)

        refund_bills = (
            qs.values(
                'billno', 'uhid','usercode',
                'createdtime', 'createdby'
            )
            .annotate(
                patname=Subquery(patient_name_sq),
                refund=Sum('refund')
            )
            .order_by('billno')
        )

        refund_total = sum(r['refund'] or 0 for r in refund_bills)

    # ==================================================
    # PAYMENT MODE TOTALS
    # ==================================================
    # ==================================================
# PAYMENT MODE TOTALS
# ==================================================

    # ==================================================
# PAYMENT MODE TOTALS
# ==================================================

    def sum_by_mode(bills, mode, key):
        return sum(
            b['paidamt'] or 0
            for b in bills
            if (b.get(key) or '').upper() == mode
        )

    def sum_split_by_mode(bills, mode):
        """For sections that have cash_amt / online_amt / online_mode fields."""
        if mode == "CASH":
            return sum(b.get('cash_amt') or 0 for b in bills)
        else:
            return sum(
                b.get('online_amt') or 0
                for b in bills
                if (b.get('online_mode') or '').upper() == mode
            )

    # ── Fetch split fields for procedures ───────────────────────────────
    procedure_bills_split = (
        TblServices.objects.filter(
            createddate__gte=fd,
            createddate__lt=td,
        ).filter(createdby=username) if (username and username != "ALL") else
        TblServices.objects.filter(createddate__gte=fd, createddate__lt=td)
    ).values('billno').annotate(
        cash_amt=Max('cash_amt'),
        online_amt=Max('online_amt'),
        online_mode=Max('online_mode'),
    ) if (show_all or "OP Procedures" in services) else []

    # ── Fetch split fields for investigations ───────────────────────────
    investigation_bills_split = (
        tblInvestigationDetails.objects.filter(
            generateddate__gte=fd,
            generateddate__lt=td,
        ).filter(createdby=username) if (username and username != "ALL") else
        tblInvestigationDetails.objects.filter(generateddate__gte=fd, generateddate__lt=td)
    ).values('billno').annotate(
        cash_amt=Max('cash_amt'),
        online_amt=Max('online_amt'),
        online_mode=Max('online_mode'),
    ) if (show_all or "OP Investigations" in services) else []

    # ── Fetch split fields for op payments ──────────────────────────────
    op_payment_bills_split = (
        OpPayment.objects.filter(
            billdate__gte=fd,
            billdate__lt=td,
            active="Y"
        ).filter(updatedby=username) if (username and username != "ALL") else
        OpPayment.objects.filter(billdate__gte=fd, billdate__lt=td, active="Y")
    ).values('invbillno').annotate(
        cash_amt=Max('cash_amt'),
        online_amt=Max('online_amt'),
        online_mode=Max('online_mode'),
    ) if (show_all or "OP Payments" in services) else []

    # ── Totals ───────────────────────────────────────────────────────────
    cash_total = (
        sum_split_by_mode(consultation_bills, "CASH")
        + sum_split_by_mode(procedure_bills_split,     "CASH")
        + sum_split_by_mode(investigation_bills_split, "CASH")
        + sum_split_by_mode(op_payment_bills_split,    "CASH")
    )

    card_total = (
        sum_split_by_mode(consultation_bills,          "CARD")
        + sum_split_by_mode(procedure_bills_split,     "CARD")
        + sum_split_by_mode(investigation_bills_split, "CARD")
        + sum_split_by_mode(op_payment_bills_split,    "CARD")
    )

    upi_total = (
        sum_split_by_mode(consultation_bills,          "UPI")
        + sum_split_by_mode(procedure_bills_split,     "UPI")
        + sum_split_by_mode(investigation_bills_split, "UPI")
        + sum_split_by_mode(op_payment_bills_split,    "UPI")
    )

    cheque_total = (
        sum_split_by_mode(consultation_bills,          "CHEQUE")
        + sum_split_by_mode(procedure_bills_split,     "CHEQUE")
        + sum_split_by_mode(investigation_bills_split, "CHEQUE")
        + sum_split_by_mode(op_payment_bills_split,    "CHEQUE")
    )

    neft_total = (
        sum_split_by_mode(consultation_bills,          "NEFT")
        + sum_split_by_mode(procedure_bills_split,     "NEFT")
        + sum_split_by_mode(investigation_bills_split, "NEFT")
        + sum_split_by_mode(op_payment_bills_split,    "NEFT")
    )
    

    # ==================================================
    # GRAND TOTAL
    # ==================================================
    grand_total = (
        consultation_total
        + procedure_total
        + investigation_total
        + op_total
        - cancellation_total
        - expenditure_total
        - refund_total
    )
    
    fd_display = datetime.strptime(from_date, "%Y-%m-%dT%H:%M")
    td_display = datetime.strptime(to_date, "%Y-%m-%dT%H:%M")
    hospital=HospitalMaster.objects.filter(active='a').first()  
    context = {
        "from_date": fd_display,
        "to_date": td_display,
        "username": username,
        "consultation_bills": consultation_bills,
        "procedure_bills": procedure_bills,
        "investigation_bills": investigation_bills,
        "op_payment_bills": op_payment_bills,
        "cancellation_bills": cancellation_bills,
        "refund_bills": refund_bills,
        "consultation_total": consultation_total,
        "procedure_total": procedure_total,
        "investigation_total": investigation_total,
        "op_total": op_total,
        "cancellation_total": cancellation_total,
        "refund_total": refund_total,
        "cash_total": cash_total,
        "card_total": card_total,
        "upi_total": upi_total,
        "cheque_total": cheque_total,
        "neft_total": neft_total,
        "grand_total": grand_total,
        'username': request.user.username,
        "print_time": timezone.now(),
        "expenditure_bills": expenditure_bills,
        "expenditure_total": expenditure_total,
        "hospital":hospital 
    }

    if report_type == "SUMMARY":
        return render(request, "hospApp/reports/userwisecollection_summary.html", context)

    return render(request, "hospApp/reports/userwisecollection_report.html", context)