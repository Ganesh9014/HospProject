
from django.shortcuts import render
from hospApp.models import BankMaster
from django.utils.timezone import make_aware    
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def daycollection(request):
    list=BankMaster.objects.filter(active='Y').order_by('sno') 
    return render(request, 'hospApp/reports/DayCollection.html',{'list':list})


from hospApp.models import BankMaster

from django.shortcuts import render
from hospApp.models import BankMaster
from datetime import datetime
from django.utils.timezone import make_aware
from django.db.models import Sum, Max, OuterRef, Subquery
from django.utils import timezone
from hospApp.models import (
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    TblOpCancellation,
    OpPayment,
    OpPatientRegistration,
    HospitalMaster
)
def apply_payment_filter(qs, payment_mode):
    if not payment_mode or payment_mode == "ALL":
        return qs

    if payment_mode.upper() == "CASH":
        return qs.filter(cash_amt__gt=0)

    return qs.filter(
        online_mode__iexact=payment_mode,
        online_amt__gt=0
    )
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def paymentmode_collection_report(request):
    list = BankMaster.objects.filter(active='Y').order_by('name')
    hospital = HospitalMaster.objects.filter(active='a').first()

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    payment_mode = request.GET.get("payment_mode")

    if not from_date or not to_date:
        return render(request, "hospApp/reports/paymentmode_report.html", {
            "list": list
        })

    fd = make_aware(datetime.strptime(from_date, "%Y-%m-%dT%H:%M"))
    td = make_aware(datetime.strptime(to_date, "%Y-%m-%dT%H:%M"))

    # ✅ COMMON SUBQUERY
    patient_name_sq = OpPatientRegistration.objects.filter(
        uhid=OuterRef('uhid')
    ).values('patname')[:1]

    # ================= OP CONSULTATION =================
    # ================= OP CONSULTATION =================
    qs = DoctorConsultation.objects.filter(
        createddate__gte=fd,
        createddate__lte=td,
        isactive="Y"
    )

    from django.db.models import Q, Case, When, IntegerField

    if payment_mode and payment_mode != "ALL":
        mode_upper = payment_mode.upper()
        if mode_upper == "CASH":
            qs = qs.filter(cash_amt__gt=0)
        else:
            qs = qs.filter(online_mode__iexact=payment_mode, online_amt__gt=0)

    consultation_bills = (
        qs.values('billno', 'uhid', 'paymenttype', 'regdt', 'userid',
                'cardname', 'cash_amt', 'online_amt', 'online_mode')
        .annotate(
            patname=Subquery(patient_name_sq),
            paidamt=Sum('paidamt')
        )
        .order_by('billno')
    )

    # For filtered mode, show only the relevant portion of paid amount
    if payment_mode and payment_mode != "ALL":
        mode_upper = payment_mode.upper()
        if mode_upper == "CASH":
            consultation_total = sum(c['cash_amt'] or 0 for c in consultation_bills)
        else:
            consultation_total = sum(c['online_amt'] or 0 for c in consultation_bills)
    else:
        consultation_total = sum(c['paidamt'] or 0 for c in consultation_bills)

    # ================= OP PROCEDURES =================
    # ================= OP PROCEDURES =================
    qs = TblServices.objects.filter(
        createddate__gte=fd,
        createddate__lte=td,
        isactive="Y"
    )

    qs = apply_payment_filter(qs, payment_mode)

    procedure_bills = (
        qs.values(
            'billno',
            'uhid',
            'cash_amt',
            'online_amt',
            'online_mode'
        )
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

    if payment_mode and payment_mode != "ALL":
        if payment_mode.upper() == "CASH":
            procedure_total = sum(
                p['cash_amt'] or 0
                for p in procedure_bills
            )
        else:
            procedure_total = sum(
                p['online_amt'] or 0
                for p in procedure_bills
            )
    else:
        procedure_total = sum(
            p['paidamt'] or 0
            for p in procedure_bills
        )


    # ================= OP INVESTIGATIONS =================
    qs = tblInvestigationDetails.objects.filter(
        generateddate__gte=fd,
        generateddate__lte=td,
        active="Y"
    )

    qs = apply_payment_filter(qs, payment_mode)

    investigation_bills = (
        qs.values(
            'billno',
            'uhid',
            'cash_amt',
            'online_amt',
            'online_mode'
        )
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

    if payment_mode and payment_mode != "ALL":
        if payment_mode.upper() == "CASH":
            investigation_total = sum(
                i['cash_amt'] or 0
                for i in investigation_bills
            )
        else:
            investigation_total = sum(
                i['online_amt'] or 0
                for i in investigation_bills
            )
    else:
        investigation_total = sum(
            i['paidamt'] or 0
            for i in investigation_bills
        )


    # ================= OP PAYMENTS =================
    qs = OpPayment.objects.filter(
        billdate__gte=fd,
        billdate__lte=td,
        active="Y"
    )

    qs = apply_payment_filter(qs, payment_mode)

    op_payment_bills = (
        qs.values(
            'invbillno',
            'uhid',
            'billdate',
            'updatedby',
            'paymentmode',
            'cardname',
            'cash_amt',
            'online_amt',
            'online_mode'
        )
        .annotate(
            patname=Subquery(patient_name_sq),
            paidamt=Sum('patamt')
        )
        .order_by('invbillno')
    )

    if payment_mode and payment_mode != "ALL":
        if payment_mode.upper() == "CASH":
            op_total = sum(
                o['cash_amt'] or 0
                for o in op_payment_bills
            )
        else:
            op_total = sum(
                o['online_amt'] or 0
                for o in op_payment_bills
            )
    else:
        op_total = sum(
            o['paidamt'] or 0
            for o in op_payment_bills
        )

    # ================= OP CANCELLATION =================
    qs = TblOpCancellation.objects.filter(
        createddate__gte=fd,
        createddate__lte=td
    )

    cancellation_bills = (
        qs.values('billno', 'uhid', 'createddate', 'userid')
        .annotate(
            patname=Subquery(patient_name_sq),   # ✅ FIXED
            amtpaid=Sum('amtpaid')
        )
    )

    cancellation_total = sum(c['amtpaid'] or 0 for c in cancellation_bills)

    # ================= GRAND TOTAL =================
    grand_total = (
        consultation_total
        + procedure_total
        + investigation_total
        + op_total
    )

    context = {
        "list": list,
        "from_date": fd,
        "to_date": td,

        "consultation_bills": consultation_bills,
        "procedure_bills": procedure_bills,
        "investigation_bills": investigation_bills,
        "op_payment_bills": op_payment_bills,
        "cancellation_bills": cancellation_bills,

        "consultation_total": consultation_total,
        "procedure_total": procedure_total,
        "investigation_total": investigation_total,
        "op_total": op_total,
        "cancellation_total": cancellation_total,

        "grand_total": grand_total,
        "hospital": hospital,
        'username': request.user.username,
        'print_time': timezone.now(),
        'payment_mode': payment_mode
    }

    return render(request, "hospApp/reports/paymentmode_collection_report.html", context)