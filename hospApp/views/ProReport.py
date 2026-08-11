


from django.shortcuts import render 
from hospApp.models import ProMaster    
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def ProReportForm(request):
    PRO = ProMaster.objects.all().order_by('pro_name')
    return render(request, 'hospApp/reports/ProReport.html', {"PRO": PRO})
from django.shortcuts import render
from hospApp.models import DoctorConsultation
from datetime import datetime

from django.shortcuts import render
from hospApp.models import DoctorConsultation

from django.shortcuts import render
from hospApp.models import DoctorConsultation,HospitalMaster
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum

from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum

from hospApp.models import DoctorConsultation, HospitalMaster, ProMaster

@login_required(login_url='login')
def ProReportResult1(request):

    # =========================
    # 🔹 GET PARAMETERS
    # =========================
    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")
    pro_id = request.GET.get("PRO")

    hospital = HospitalMaster.objects.filter(active='a').first()

    # =========================
    # 🔹 BASE QUERY
    # =========================
    data = DoctorConsultation.objects.select_related(
        'promaster', 'refdoctor'
    ).all()

    # =========================
    # ✅ DATE FILTER (FIXED)
    # =========================
    from_date = None
    to_date = None

    if from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

            # ✅ timezone aware
            from_date = timezone.make_aware(from_date)
            to_date = timezone.make_aware(to_date)

            end_date = to_date + timedelta(days=1)

            data = data.filter(
                createddate__gte=from_date,
                createddate__lt=end_date
            )

        except Exception as e:
            print("Date Error:", e)

    # =========================
    # ✅ PRO FILTER + NAME
    # =========================
    selected_pro_name = "ALL"

    if pro_id and pro_id != "ALL":
        try:
            pro_id = int(pro_id)   # ✅ important

            data = data.filter(promaster_id=pro_id)

            pro_obj = ProMaster.objects.filter(proid=pro_id).first()
            if pro_obj:
                selected_pro_name = pro_obj.pro_name

        except ValueError:
            selected_pro_name = "ALL"

    # =========================
    # ✅ ORDER
    # =========================
    data = data.order_by('-createddate')

    # =========================
    # ✅ TOTAL
    # =========================
    total_amount = data.aggregate(
        total=Sum('paidamt')
    )['total'] or 0

    # =========================
    # ✅ RESPONSE
    # =========================
    return render(request, "hospApp/reports/ProReportResult.html", {
        "report": data,
        "total": total_amount,
        "hospital": hospital,
        "from_date": from_date,
        "to_date": to_date,
        "pro_id": pro_id,
        "selected_pro_name": selected_pro_name,
        "print_time": timezone.now(),
    })


from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Max, OuterRef, Subquery

from hospApp.models import (
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment,
    TblOpCancellation,
    ExpenditureEntry,
    OpPatientRegistration,
    ProMaster
)


from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Max, OuterRef, Subquery

from hospApp.models import (
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment,
    TblOpCancellation,
    OpPatientRegistration,
    ProMaster,
    HospitalMaster,
    TblRefund
)
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def ProReportResult(request):

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    pro_id = request.GET.get("PRO")

    hospital = HospitalMaster.objects.filter(active='a').first()

    if not from_date or not to_date:
        return render(request, "hospApp/reports/ProReport.html")

    fd = datetime.strptime(from_date, "%Y-%m-%d")
    td = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)

    # ================= PRO NAME =================
    selected_pro_name = "ALL"
    if pro_id and pro_id != "ALL":
        pro_obj = ProMaster.objects.filter(proid=pro_id).first()
        if pro_obj:
            selected_pro_name = pro_obj.pro_name

    # ================= CONSULTATION =================
    consultation_qs = DoctorConsultation.objects.filter(
        createddate__gte=fd,
        createddate__lt=td,

    )
    if pro_id and pro_id != "ALL":
        consultation_qs = consultation_qs.filter(promaster_id=pro_id)

    consultation_bills = consultation_qs.values(
        'billno', 'uhid', 'regdt', 'opno'  # ✅ opno fetched directly
    ).annotate(paidamt=Sum('paidamt'))

    # ✅ Get uhid_list ONLY from date-filtered consultations
    # This is the correct set of patients for this PRO in this date range
    uhid_list = list(set([row['uhid'] for row in consultation_bills]))

    # If specific PRO selected but no consultations found, return empty
    if pro_id and pro_id != "ALL" and not uhid_list:
        return render(request, "hospApp/reports/ProReportResult.html", {
            "consultation_data": [], "procedure_data": [],
            "investigation_data": [], "payment_data": [],
            "consultation_total": 0, "procedure_total": 0,
            "investigation_total": 0, "op_total": 0,
            "grand_total": 0, "hospital": hospital,
            "selected_pro_name": selected_pro_name,
            "from_date": datetime.strptime(from_date, "%Y-%m-%d"),
            "to_date": datetime.strptime(to_date, "%Y-%m-%d"),
            "logged_user": request.session.get("username"),
            "print_time": timezone.now(),
        })

    # ================= PROCEDURE =================
    procedure_qs = TblServices.objects.filter(
        createddate__gte=fd,
        createddate__lt=td,
    
    )
    # ✅ Only filter by uhid_list when a specific PRO is selected
    if pro_id and pro_id != "ALL" and uhid_list:
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
    if pro_id and pro_id != "ALL" and uhid_list:
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
    if pro_id and pro_id != "ALL" and uhid_list:
        payment_qs = payment_qs.filter(uhid__in=uhid_list)

    op_payment_bills = payment_qs.values(
        'invbillno', 'uhid', 'billdate'
    ).annotate(paidamt=Sum('patamt'))

    # ================= CANCELLATIONS =================
    cancellation_qs = TblOpCancellation.objects.filter(
        createddate__gte=fd,
        createddate__lt=td
    )
    if pro_id and pro_id != "ALL" and uhid_list:
        cancellation_qs = cancellation_qs.filter(uhid__in=uhid_list)

    cancellation_bills = cancellation_qs.values(
        'billno', 'uhid', 'createddate'
    ).annotate(amtpaid=Sum('amtpaid'))

    # ================= REFUNDS =================
    refund_qs = TblRefund.objects.filter(
        createdtime__gte=fd,
        createdtime__lt=td
    )
    if pro_id and pro_id != "ALL" and uhid_list:
        refund_qs = refund_qs.filter(uhid__in=uhid_list)

    refund_bills = refund_qs.values(
        'billno', 'uhid', 'createdtime'
    ).annotate(refund=Sum('refund'))

    # ================= PATIENT MAP =================
    all_uhids = set()
    all_uhids.update([row['uhid'] for row in consultation_bills])
    all_uhids.update([row['uhid'] for row in procedure_bills])
    all_uhids.update([row['uhid'] for row in investigation_bills])
    all_uhids.update([row['uhid'] for row in op_payment_bills])
    all_uhids.update([row['uhid'] for row in cancellation_bills])
    all_uhids.update([row['uhid'] for row in refund_bills])

    patients = OpPatientRegistration.objects.filter(
        uhid__in=all_uhids
    ).select_related('pro', 'refdoctor')

    patient_map = {p.uhid: p for p in patients}

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
            "opno": row.get("opno", ""),  # ✅ direct from queryset
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

    # ================= SPLIT BY SOURCE =================
    consultation_data  = [x for x in combined_data if x["source"] == "CONSULTATION"]
    procedure_data     = [x for x in combined_data if x["source"] == "PROCEDURE"]
    investigation_data = [x for x in combined_data if x["source"] == "INVESTIGATION"]
    payment_data       = [x for x in combined_data if x["source"] == "PAYMENT"]
    cancellation_data  = [x for x in combined_data if x["source"] == "CANCELLATION"]
    refund_data        = [x for x in combined_data if x["source"] == "REFUND"]

    grand_total = consultation_total + procedure_total + investigation_total + op_total - cancellation_total - refund_total

    return render(request, "hospApp/reports/ProReportResult.html", {
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
        "selected_pro_name": selected_pro_name,
        "from_date": datetime.strptime(from_date, "%Y-%m-%d"),
        "to_date": datetime.strptime(to_date, "%Y-%m-%d"),
        "logged_user": request.session.get("username"),
        "print_time": timezone.now(),
    })