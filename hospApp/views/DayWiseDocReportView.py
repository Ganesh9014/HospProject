from django.shortcuts import render
from datetime import datetime, timedelta
from django.db.models import Sum, Max
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from hospApp.models import (
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment,
    OpPatientRegistration,
    DoctorMaster,
    HospitalMaster,
    TblOpCancellation,
    TblRefund
)


@login_required(login_url='login')
def DayWiseDocReportView(request):
    doctor = DoctorMaster.objects.all().order_by('docname')
    return render(request, 'hospApp/reports/DaywiseDocReport.html', {'doctor': doctor})


@login_required(login_url='login')
def DayWiseDocReportResult(request):

    from_date = request.GET.get("from_date")
    to_date   = request.GET.get("to_date")
    doctor_id = request.GET.get("PRO")

    hospital = HospitalMaster.objects.filter(active='a').first()

    if not from_date or not to_date:
        return render(request, "hospApp/reports/DaywiseDocReport.html")

    fd = timezone.make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
    td = timezone.make_aware(datetime.strptime(to_date, "%Y-%m-%d")) + timedelta(days=1)

    selected_doctor_name = "ALL"
    if doctor_id and doctor_id != "ALL":
        doc_obj = DoctorMaster.objects.filter(docid=doctor_id).first()
        if doc_obj:
            selected_doctor_name = doc_obj.docname

    doctor_name_map = {
        str(d.docid): d.docname
        for d in DoctorMaster.objects.all()
    }

    # ─────────────────────────────────────────────────────────────
    # CONSULTATION
    # ─────────────────────────────────────────────────────────────
    consultation_qs = DoctorConsultation.objects.filter(
        createddate__gte=fd,
        createddate__lt=td,
    )
    if doctor_id and doctor_id != "ALL":
        consultation_qs = consultation_qs.filter(doctor_id=doctor_id)

    consultation_bills = list(
        consultation_qs.values('billno', 'uhid', 'regdt', 'opno', 'doctor_id')
                       .annotate(paidamt=Sum('paidamt'))
    )

    # ─────────────────────────────────────────────────────────────
    # PROCEDURE
    # ─────────────────────────────────────────────────────────────
    procedure_qs = TblServices.objects.filter(
        createddate__gte=fd,
        createddate__lt=td,
    )
    if doctor_id and doctor_id != "ALL":
        procedure_qs = procedure_qs.filter(doc_id=doctor_id)

    procedure_bills = list(
        procedure_qs.values('billno', 'uhid', 'doc_id')
                    .annotate(
                        generateddate=Max('generateddate'),
                        paidamt=Max('paidamt'),
                    )
    )

    # ─────────────────────────────────────────────────────────────
    # INVESTIGATION
    # ─────────────────────────────────────────────────────────────
    investigation_qs = tblInvestigationDetails.objects.filter(
        generateddate__gte=fd,
        generateddate__lt=td,
    )
    if doctor_id and doctor_id != "ALL":
        investigation_qs = investigation_qs.filter(doc=str(doctor_id))

    investigation_bills = list(
        investigation_qs.values('billno', 'uhid', 'doc')
                        .annotate(
                            generateddate=Max('generateddate'),
                            paidamt=Max('paidamt'),
                        )
    )

    # ─────────────────────────────────────────────────────────────
    # COMBINED UHID LIST FROM ALL THREE SOURCES
    # ─────────────────────────────────────────────────────────────
    all_filtered_uhids = list(
        {row['uhid'] for row in consultation_bills}
        | {row['uhid'] for row in procedure_bills}
        | {row['uhid'] for row in investigation_bills}
    )

    # ─────────────────────────────────────────────────────────────
    # OP PAYMENT → BUILD MAP ONLY
    # ─────────────────────────────────────────────────────────────
    payment_qs = OpPayment.objects.filter(
        billdate__gte=fd,
        billdate__lt=td,
    )
    if doctor_id and doctor_id != "ALL" and all_filtered_uhids:
        payment_qs = payment_qs.filter(uhid__in=all_filtered_uhids)

    op_payment_bills = list(
        payment_qs.values('billno')
                  .annotate(paidamt=Sum('patamt'))
    )

    payment_map = {}
    for row in op_payment_bills:
        billno = row["billno"]
        amt = row["paidamt"] or 0
        payment_map[billno] = payment_map.get(billno, 0) + amt

    # ─────────────────────────────────────────────────────────────
    # OP CANCELLATIONS & OP REFUNDS
    # ─────────────────────────────────────────────────────────────
    cancellation_qs = TblOpCancellation.objects.filter(
        createddate__gte=fd,
        createddate__lt=td
    )
    refund_qs = TblRefund.objects.filter(
        createdtime__gte=fd,
        createdtime__lt=td
    )

    if doctor_id and doctor_id != "ALL":
        doc_bills = set()
        doc_consultation_bills = DoctorConsultation.objects.filter(doctor_id=doctor_id).values_list('billno', flat=True)
        doc_services_bills = TblServices.objects.filter(doc_id=doctor_id).values_list('billno', flat=True)
        doc_investigation_bills = tblInvestigationDetails.objects.filter(doc=str(doctor_id)).values_list('billno', flat=True)
        
        doc_bills.update(doc_consultation_bills)
        doc_bills.update(doc_services_bills)
        doc_bills.update(doc_investigation_bills)

        cancellation_qs = cancellation_qs.filter(billno__in=doc_bills)
        refund_qs = refund_qs.filter(billno__in=doc_bills)

    cancellation_bills = list(
        cancellation_qs.values('billno', 'uhid', 'createddate')
                       .annotate(amtpaid=Sum('amtpaid'))
    )

    refund_bills = list(
        refund_qs.values('billno', 'uhid', 'createdtime')
                 .annotate(refund=Sum('refund'))
    )

    # ─────────────────────────────────────────────────────────────
    # PATIENT MAP
    # ─────────────────────────────────────────────────────────────
    all_uhids = (
        {row['uhid'] for row in consultation_bills}
        | {row['uhid'] for row in procedure_bills}
        | {row['uhid'] for row in investigation_bills}
        | {row['uhid'] for row in cancellation_bills}
        | {row['uhid'] for row in refund_bills}
    )

    patient_map = {
        p.uhid: p
        for p in OpPatientRegistration.objects.filter(uhid__in=all_uhids)
                                               .select_related('pro', 'refdoctor')
    }

    

    def patient_info(uhid):
        p = patient_map.get(uhid)
        return {
            "patname": p.patname if p else "",
            "pro":     p.pro.pro_name if p and p.pro else "",
            "refdoc":  p.refdoctor.docname if p and p.refdoctor else "",
        }

    # ─────────────────────────────────────────────────────────────
    # HELPER: GET DOCTOR NAME FROM ORIGINAL TABLE BY BILLNO
    # ─────────────────────────────────────────────────────────────


    def get_doctor_for_bill(billno):
        # Check consultation table
        consult = DoctorConsultation.objects.filter(billno=billno).values('doctor_id').first()
        if consult and consult['doctor_id']:
            return doctor_name_map.get(str(consult['doctor_id']), "")

        # Check investigation table
        invest = tblInvestigationDetails.objects.filter(billno=billno).values('doc').first()
        if invest and invest['doc']:
            return doctor_name_map.get(str(invest['doc']), "")

        # Check procedure table
        proc = TblServices.objects.filter(billno=billno).values('doc_id').first()
        if proc and proc['doc_id']:
            return doctor_name_map.get(str(proc['doc_id']), "")

        return ""

    # ─────────────────────────────────────────────────────────────
    # BUILD DATA
    # ─────────────────────────────────────────────────────────────
    consultation_data  = []
    procedure_data     = []
    investigation_data = []

    consultation_total = procedure_total = investigation_total = 0

    # CONSULTATION
    for row in consultation_bills:
        info = patient_info(row["uhid"])
        billno = row["billno"]

        bill_amt = row["paidamt"] or 0
        paid_amt = payment_map.get(billno, 0)
        total_amt = bill_amt + paid_amt

        doc_name = doctor_name_map.get(str(row["doctor_id"]), "")
        consultation_total += total_amt

        consultation_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": row.get("opno") or "",
            "doctor": doc_name,
            "bill_amount": bill_amt,
            "paid_amount": paid_amt,
            "amount": total_amt,
            "date": row["regdt"],
            "billno": billno,
            "source": "CONSULTATION",
        })

    # PROCEDURE
    for row in procedure_bills:
        info = patient_info(row["uhid"])
        billno = row["billno"]

        bill_amt = row["paidamt"] or 0
        paid_amt = payment_map.get(billno, 0)
        total_amt = bill_amt + paid_amt

        doc_name = doctor_name_map.get(str(row.get("doc_id") or ""), "")
        procedure_total += total_amt

        procedure_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": "",
            "doctor": doc_name,
            "bill_amount": bill_amt,
            "paid_amount": paid_amt,
            "amount": total_amt,
            "date": row["generateddate"],
            "billno": billno,
            "source": "PROCEDURE",
        })

    # INVESTIGATION
    for row in investigation_bills:
        info = patient_info(row["uhid"])
        billno = row["billno"]

        bill_amt = row["paidamt"] or 0
        paid_amt = payment_map.get(billno, 0)
        total_amt = bill_amt + paid_amt

        doc_name = doctor_name_map.get(str(row.get("doc") or ""), "")
        investigation_total += total_amt

        investigation_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": "",
            "doctor": doc_name,
            "bill_amount": bill_amt,
            "paid_amount": paid_amt,
            "amount": total_amt,
            "date": row["generateddate"],
            "billno": billno,
            "source": "INVESTIGATION",
        })

    cancellation_data = []
    refund_data = []
    cancellation_total = refund_total = 0

    # CANCELLATION
    for row in cancellation_bills:
        info = patient_info(row["uhid"])
        billno = row["billno"]
        amt = row["amtpaid"] or 0
        cancellation_total += amt

        c_doc = get_doctor_for_bill(billno)  # ← from original table

        cancellation_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": "",
            "doctor": c_doc,
            "amount": amt,
            "date": row["createddate"],
            "billno": billno,
            "source": "CANCELLATION",
        })

    # REFUND
    for row in refund_bills:
        info = patient_info(row["uhid"])
        billno = row["billno"]
        amt = row["refund"] or 0
        refund_total += amt

        r_doc = get_doctor_for_bill(billno)  # ← from original table

        refund_data.append({
            **info,
            "uhid": row["uhid"],
            "opno": "",
            "doctor": r_doc,
            "amount": amt,
            "date": row["createdtime"],
            "billno": billno,
            "source": "REFUND",
        })

    # FINAL TOTAL
    grand_total = consultation_total + procedure_total + investigation_total - cancellation_total - refund_total

    return render(request, "hospApp/reports/DaywiseDocReportResult.html", {
        "consultation_data": consultation_data,
        "procedure_data": procedure_data,
        "investigation_data": investigation_data,
        "cancellation_data": cancellation_data,
        "refund_data": refund_data,
        "consultation_total": consultation_total,
        "procedure_total": procedure_total,
        "investigation_total": investigation_total,
        "cancellation_total": cancellation_total,
        "refund_total": refund_total,
        "grand_total": grand_total,
        "hospital": hospital,
        "selected_doctor_name": selected_doctor_name,
        "from_date": datetime.strptime(from_date, "%Y-%m-%d"),
        "to_date": datetime.strptime(to_date, "%Y-%m-%d"),
        "print_time": timezone.now(),
        "logged_user": request.session.get("username"),
    })