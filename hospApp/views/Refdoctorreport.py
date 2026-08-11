
from django.shortcuts import render
from hospApp.models import RefDoctorMaster  



from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def Refdoctorreport(request):
    REF=RefDoctorMaster.objects.all().order_by('docname')
    return render(request,'hospApp/reports/Refdoctorreport.html',{'REF':REF})

from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Max, OuterRef, Subquery

from hospApp.models import (
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment,
    OpPatientRegistration,
    RefDoctorMaster,
    HospitalMaster,
    TblOpCancellation,
    TblRefund
)


# Duplicate imports cleaned up

from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def RefDoctorReportResult(request):

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    ref_id = request.GET.get("REF")

    hospital = HospitalMaster.objects.filter(active='a').first()

    if not from_date or not to_date:
        return render(request, "hospApp/reports/Refdoctorreport.html")

    fd = datetime.strptime(from_date, "%Y-%m-%d")
    td = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)

    # ================= REF FILTER =================
    uhid_list = None
    selected_ref_name = "ALL"

    if ref_id and ref_id != "ALL":
        uhid_list = list(
            OpPatientRegistration.objects.filter(
                refdoctor_id=ref_id
            ).values_list('uhid', flat=True)
        )
        ref_obj = RefDoctorMaster.objects.filter(docid=ref_id).first()
        if ref_obj:
            selected_ref_name = ref_obj.docname

        # ⬇️ If no patients found for this ref doctor, return empty
        if not uhid_list:
            return render(request, "hospApp/reports/Refdoctorresult.html", {
                "consultation_data": [], "procedure_data": [],
                "investigation_data": [], "payment_data": [],
                "consultation_total": 0, "procedure_total": 0,
                "investigation_total": 0, "op_total": 0,
                "grand_total": 0, "hospital": hospital,
                "selected_pro_name": selected_ref_name,
                "from_date": from_date, "to_date": to_date,
                "logged_user": request.session.get("username"),
                "print_time": timezone.now(),
            })

    # ================= PATIENT MAP (built once, used everywhere) =================
    # Build patient map up front from uhid_list if filtered, else lazily after
    if uhid_list is not None:
        patients = OpPatientRegistration.objects.filter(
            uhid__in=uhid_list
        ).select_related('pro', 'refdoctor')
        patient_map = {p.uhid: p for p in patients}
    else:
        patient_map = {}  # will be populated after collecting uhids from bills

    # ================= CONSULTATION =================
    consultation_qs = DoctorConsultation.objects.filter(
        createddate__gte=fd,
        createddate__lt=td,
        
    )
    if uhid_list is not None:
        consultation_qs = consultation_qs.filter(uhid__in=uhid_list)

    consultation_bills = consultation_qs.values(
        'billno', 'uhid', 'regdt', 'opno'   # ✅ grab opno directly here
    ).annotate(paidamt=Sum('paidamt'))

    # ================= PROCEDURE =================
    procedure_qs = TblServices.objects.filter(
        createddate__gte=fd,
        createddate__lt=td,
        
    )
    if uhid_list is not None:
        procedure_qs = procedure_qs.filter(uhid__in=uhid_list)

    procedure_bills = procedure_qs.values(
        'billno', 'uhid'
    ).annotate(
        generateddate=Max('generateddate'),
        paidamt=Max('paidamt')
    )

    # ================= INVESTIGATION =================
    investigation_qs = tblInvestigationDetails.objects.filter(
        generateddate__gte=fd,
        generateddate__lt=td,
        
    )
    if uhid_list is not None:
        investigation_qs = investigation_qs.filter(uhid__in=uhid_list)

    investigation_bills = investigation_qs.values(
        'billno', 'uhid'
    ).annotate(
        generateddate=Max('generateddate'),
        paidamt=Max('paidamt')
    )

    # ================= PAYMENTS =================
    payment_qs = OpPayment.objects.filter(
        billdate__gte=fd,
        billdate__lt=td,
        
    )
    if uhid_list is not None:
        payment_qs = payment_qs.filter(uhid__in=uhid_list)

    op_payment_bills = payment_qs.values(
        'invbillno', 'uhid', 'billdate'
    ).annotate(paidamt=Sum('patamt'))

    # ================= CANCELLATIONS =================
    cancellation_qs = TblOpCancellation.objects.filter(
        createddate__gte=fd,
        createddate__lt=td
    )
    if uhid_list is not None:
        cancellation_qs = cancellation_qs.filter(uhid__in=uhid_list)

    cancellation_bills = cancellation_qs.values(
        'billno', 'uhid', 'createddate'
    ).annotate(amtpaid=Sum('amtpaid'))

    # ================= REFUNDS =================
    refund_qs = TblRefund.objects.filter(
        createdtime__gte=fd,
        createdtime__lt=td
    )
    if uhid_list is not None:
        refund_qs = refund_qs.filter(uhid__in=uhid_list)

    refund_bills = refund_qs.values(
        'billno', 'uhid', 'createdtime'
    ).annotate(refund=Sum('refund'))

    # ================= BUILD PATIENT MAP FOR "ALL" CASE =================
    if uhid_list is None:
        uhids = set()
        uhids.update([row['uhid'] for row in consultation_bills])
        uhids.update([row['uhid'] for row in procedure_bills])
        uhids.update([row['uhid'] for row in investigation_bills])
        uhids.update([row['uhid'] for row in op_payment_bills])
        uhids.update([row['uhid'] for row in cancellation_bills])
        uhids.update([row['uhid'] for row in refund_bills])

        patients = OpPatientRegistration.objects.filter(
            uhid__in=uhids
        ).select_related('pro', 'refdoctor')
        patient_map = {p.uhid: p for p in patients}

    # ================= HELPER =================
    def patient_info(uhid):
        p = patient_map.get(uhid)
        return {
            "patname": p.patname if p else "",
            "pro": p.pro.pro_name if p and p.pro else "",
            "refdoc": p.refdoctor.docname if p and p.refdoctor else "",
        }

    # ================= COMBINED DATA =================
    combined_data = []
    consultation_total = procedure_total = investigation_total = op_total = cancellation_total = refund_total = 0

    for row in consultation_bills:
        info = patient_info(row["uhid"])
        amt = row["paidamt"] or 0
        consultation_total += amt
        combined_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": row.get("opno", ""),   # ✅ from the queryset directly
            "amount": amt,
            "date": row["regdt"],
            "billno": row["billno"],
            "source": "CONSULTATION"
        })

    for row in procedure_bills:
        info = patient_info(row["uhid"])
        amt = row["paidamt"] or 0
        procedure_total += amt
        combined_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": "",
            "amount": amt,
            "date": row["generateddate"],
            "billno": row["billno"],
            "source": "PROCEDURE"
        })

    for row in investigation_bills:
        info = patient_info(row["uhid"])
        amt = row["paidamt"] or 0
        investigation_total += amt
        combined_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": "",
            "amount": amt,
            "date": row["generateddate"],
            "billno": row["billno"],
            "source": "INVESTIGATION"
        })

    for row in op_payment_bills:
        info = patient_info(row["uhid"])
        amt = row["paidamt"] or 0
        op_total += amt
        combined_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": "",
            "amount": amt,
            "date": row["billdate"],
            "billno": row["invbillno"],
            "source": "PAYMENT"
        })

    for row in cancellation_bills:
        info = patient_info(row["uhid"])
        amt = row["amtpaid"] or 0
        cancellation_total += amt
        combined_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": "",
            "amount": amt,
            "date": row["createddate"],
            "billno": row["billno"],
            "source": "CANCELLATION"
        })

    for row in refund_bills:
        info = patient_info(row["uhid"])
        amt = row["refund"] or 0
        refund_total += amt
        combined_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": "",
            "amount": amt,
            "date": row["createdtime"],
            "billno": row["billno"],
            "source": "REFUND"
        })

    consultation_data = [x for x in combined_data if x["source"] == "CONSULTATION"]
    procedure_data    = [x for x in combined_data if x["source"] == "PROCEDURE"]
    investigation_data= [x for x in combined_data if x["source"] == "INVESTIGATION"]
    payment_data      = [x for x in combined_data if x["source"] == "PAYMENT"]
    cancellation_data = [x for x in combined_data if x["source"] == "CANCELLATION"]
    refund_data       = [x for x in combined_data if x["source"] == "REFUND"]

    grand_total = consultation_total + procedure_total + investigation_total + op_total - cancellation_total - refund_total

    return render(request, "hospApp/reports/Refdoctorresult.html", {
        "consultation_data": consultation_data,
        "procedure_data": procedure_data,
        "investigation_data": investigation_data,
        "payment_data": payment_data,
        "cancellation_data": cancellation_data,
        "refund_data": refund_data,
        "consultation_total": consultation_total,
        "procedure_total": procedure_total,
        "investigation_total": investigation_total,
        "op_total": op_total,
        "cancellation_total": cancellation_total,
        "refund_total": refund_total,
        "grand_total": grand_total,
        "hospital": hospital,
        "selected_pro_name": selected_ref_name,
        "from_date": datetime.strptime(from_date, "%Y-%m-%d"),
        "to_date": datetime.strptime(to_date, "%Y-%m-%d"),
        "logged_user": request.session.get("username"),
        "print_time": timezone.now(),
    })