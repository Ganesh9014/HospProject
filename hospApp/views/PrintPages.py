


from django.shortcuts import render
from django.contrib.auth.decorators import login_required   

from hospApp.models import ExpenditureEntry
@login_required(login_url='login')
def PrintPages(request):
    billno = request.GET.get("billno")
    bill_type = (request.GET.get("type") or "").strip().upper()

    context = {
        "type": bill_type   # ✅ always set first
    }

    if billno and bill_type == "EXPENDITURE":
        entry = ExpenditureEntry.objects.select_related('expenditure').filter(bill_no=billno,).first()

        if entry:
            context.update({
                "bill_no": entry.bill_no,
                "bill_date": entry.created_at,
                "expenditure_name": entry.expenditure.expenditure_name,
                "amount": entry.amount,
                "towards": entry.towards,
            })

    return render(request, 'hospApp/frontoffice/PrintPages.html', context)
from django.http import JsonResponse
from hospApp.models import BillMaster, OpPatientRegistration
from django.http import JsonResponse
from django.db.models import Sum, Min
from hospApp.models import (
    BillMaster,
    OpPatientRegistration,
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment
)

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Min, Max
from hospApp.models import (
    BillMaster,
    OpPatientRegistration,
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment
)


@login_required(login_url='login')
def get_bill_details_by_billno(request):
    billno = request.GET.get("billno")

    # ---------------- BILL ----------------
    bill = BillMaster.objects.filter(billno=billno,).first()
    if not bill:
        return JsonResponse({"success": False, "message": "Invalid Bill No"})

    # ---------------- PATIENT ----------------
    patient = OpPatientRegistration.objects.filter(uhid=bill.uhid).first()
    if not patient:
        return JsonResponse({"success": False, "message": "Patient not found"})

    bill_type = bill.bill_type.strip().upper()

    total = 0
    base_paid = 0
    base_conc = 0

    # =========================================================
    # ================== SOURCE TOTAL =========================
    # =========================================================

    # ---------------- CONSULTATION ----------------
    if bill_type == "CONSULTATION":
        src = DoctorConsultation.objects.filter(billno=billno).first()
        if src:
            total = src.consulfee or 0
            base_paid = src.paidamt or 0
            base_conc = src.concession or 0

    # ---------------- PROCEDURE ----------------
    elif bill_type == "PROCEDURE":
        src = TblServices.objects.filter(billno=billno,).aggregate(
            total=Sum("amount"),
            base_paid=Min("paidamt"),
            base_conc=Min("concessionamt")
        )
        total = src["total"] or 0
        base_paid = src["base_paid"] or 0
        base_conc = src["base_conc"] or 0

    # ---------------- INVESTIGATION ----------------
    elif bill_type == "INVESTIGATION":
        src = tblInvestigationDetails.objects.filter(billno=billno,).aggregate(
            total=Sum("cost"),
            base_paid=Min("paidamt"),
            base_conc=Min("concessionamt")
        )
        total = src["total"] or 0
        base_paid = src["base_paid"] or 0
        base_conc = src["base_conc"] or 0

    # =========================================================
    # ================== OPPAYMENT (SPECIAL) ==================
    # =========================================================
    elif bill_type in ["OPPAYMENT", "OPPAYMENTS"]:
        op = OpPayment.objects.filter(
            uhid=bill.uhid,
            invbillno=bill.billno,    
        ).aggregate(
            totalamt=Max("totalamt"),
            paid=Sum("patamt"),
            concession=Max("concession"),
            due=Max("due")   
        )

        total = op["totalamt"] or 0
        paid = op["paid"] or 0
        concession = op["concession"] or 0
        due = op["due"] or 0
        if due < 0:
            due = 0

        # 🔥 EARLY RETURN (VERY IMPORTANT)
        return JsonResponse({
            "success": True,
            "data": {
                "bill_date": bill.bill_date,
                "uhid": patient.uhid,
                "patient_type": bill.bill_type,
                "patient_name": f"{patient.title} {patient.patname}",
                "bill_no": bill.billno,
                "age": patient.age,
                "phone": patient.phone,
                "gender": patient.gender,
                "total_amount": total,
                "paid_amount": paid,
                "concession": concession,
                "due_amount": due
            }
        })

    # =========================================================
    # =============== OP LEDGER (NON-OPPAYMENT) ================
    # =========================================================
    op = OpPayment.objects.filter(
        uhid=bill.uhid,
        billno=billno,
        active='Y'
    ).aggregate(
        paid=Sum("patamt"),
        conc=Sum("concession")
    )

    paid = base_paid + (op["paid"] or 0)
    concession = base_conc + (op["conc"] or 0)

    due = total - (paid + concession)
    if due < 0:
        due = 0

    # ---------------- FINAL RESPONSE ----------------
    return JsonResponse({
        "success": True,
        "data": {
            "bill_date": bill.bill_date,
            "uhid": patient.uhid,
            "patient_type": bill.bill_type,
            "patient_name": f"{patient.title} {patient.patname}",
            "bill_no": bill.billno,
            "age": patient.age,
            "phone": patient.phone,
            "gender": patient.gender,
            "total_amount": total,
            "paid_amount": paid,
            "concession": concession,
            "due_amount": due
        }
    })

from django.urls import reverse
from django.http import JsonResponse
from hospApp.models import DoctorConsultation, TblServices, tblInvestigationDetails,Tbluserpermission


@login_required(login_url='login')
def save_print_page(request):
    if request.method != "POST":
        return JsonResponse({"success": False})

    billno = request.POST.get("bill_no")
    patient_type = request.POST.get("patient_type", "").strip().upper()
    entered_pass = request.POST.get("usercode", "").strip()
    logged_user = request.session.get("username")

    user = Tbluserpermission.objects.filter(
        username=logged_user,
        isactive=True
    ).first()

    # ❌ INVALID USER CODE
    if not user or entered_pass != user.password:
        return JsonResponse({
            "success": False,
            "message": "❗ Invalid User Code"
        })

    # ---------------- CONSULTATION ----------------
    if patient_type == "CONSULTATION":
        consult = DoctorConsultation.objects.filter(billno=billno).first()
        if not consult:
            return JsonResponse({
                "success": False,
                "message": "Consultation not found"
            })

        redirect_url = reverse(
            "consultation-print-select",
            args=[consult.pk]
        )

    # ---------------- INVESTIGATION ----------------
    elif patient_type == "INVESTIGATION":
        redirect_url = reverse(
            "op_investigation_bill",
            args=[billno]
        )

    # ---------------- PROCEDURE ----------------
    elif patient_type in ["PROCEDURE", "PROCEDURES"]:
        redirect_url = reverse(
            "op_procedure_bill",
            args=[billno]
        )
    elif patient_type in ["OPPAYMENT", "OPPAYMENTS"]:
        redirect_url = reverse(
            "op_payment_receipt",
            args=[billno]
    )    
    elif patient_type == "EXPENDITURE":
        redirect_url = reverse(
            "expenditure_print",  # create this view/template
            args=[billno]
        )    

    else:
        return JsonResponse({
            "success": False,
            "message": "Invalid bill type"
        })

    return JsonResponse({
        "success": True,
        "redirect_url": redirect_url
    })



from django.shortcuts import render
from django.db.models import Sum, Min
from hospApp.models import (
    BillMaster,
    OpPatientRegistration,
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment
)
from django.utils import timezone
from datetime import date

from django.shortcuts import render
from django.db.models import Sum, Min
from datetime import date
from hospApp.models import (
    BillMaster,
    OpPatientRegistration,
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment
)

from django.shortcuts import render
from django.db.models import Sum, Min
from datetime import date
from hospApp.models import (
    BillMaster,
    OpPatientRegistration,
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment
)
from hospApp.models import ExpenditureEntry
from django.http import JsonResponse    
from django.contrib.auth.decorators import login_required   
from django.db.models import Max
from hospApp.utils import filter_by_date_range
from django.utils import timezone
from datetime import datetime, date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Min, Max
from django.http import JsonResponse
from hospApp.models import (
    BillMaster, OpPatientRegistration, DoctorConsultation,
    TblServices, tblInvestigationDetails, OpPayment, ExpenditureEntry
)

@login_required(login_url='login')
def bill_lookup_by_type(request):

    bill_type = request.GET.get("type", "").strip().upper()
    today     = timezone.localtime().date()  # ✅ IST today

    from_date = request.GET.get("from_date") or today.isoformat()
    to_date   = request.GET.get("to_date")   or today.isoformat()
    if not request.GET:
        from django.shortcuts import redirect
        return redirect(f"{request.path}?from_date={today}&to_date={today}")


    def parse_date(val):
        try:
            return date.fromisoformat(val)
        except:
            return None

    from_dt = parse_date(from_date)
    to_dt   = parse_date(to_date)

    # ---------------- VALIDATION ----------------
    error = None
    if not from_dt or not to_dt:
        error = "Invalid date format."
    elif from_dt > today or to_dt > today:
        error = "Future dates are not allowed."
    elif from_dt.year < 2000 or to_dt.year < 2000:
        error = "Invalid year entered."

    if error:
        return render(request, "hospApp/frontoffice/BillLookup.html", {
            "results": [], "bill_type": bill_type,
            "from_date": from_date, "to_date": to_date, "error": error
        })

    # ================= EXPENDITURE =================
    if bill_type == "EXPENDITURE":
        # ✅ Use filter_by_date_range
        entries = filter_by_date_range(
            ExpenditureEntry.objects.all(),
            'created_at', from_dt, to_dt
        )
        results = [{
            "billno":   e.bill_no,
            "patient":  e.expenditure.expenditure_name,
            "total":    e.amount,
            "towards":  e.towards,
            "date":     e.created_at.strftime("%d-%m-%Y %H:%M:%S")
        } for e in entries]

        return render(request, "hospApp/frontoffice/BillLookup.html", {
            "results": results, "bill_type": bill_type,
            "from_date": from_date, "to_date": to_date
        })

    # ================= OPPAYMENT alias =================
    if bill_type == "OPPAYMENT":
        bill_type = "OPPAYMENTS"

    uhid    = request.GET.get("uhid", "").strip()
    patient = request.GET.get("patient", "").strip()
    results = []

    # ---------------- BASE QUERY ----------------
    bills = BillMaster.objects.filter(bill_type__iexact=bill_type)

    # ---------------- FILTER LOGIC ----------------
    if uhid:
        # ✅ Search whole table by UHID
        bills = bills.filter(uhid=uhid)

    elif patient:
        # ✅ Search whole table by patient name
        uhid_list = OpPatientRegistration.objects.filter(
            patname__icontains=patient
        ).values_list("uhid", flat=True)
        bills = bills.filter(uhid__in=uhid_list)

    else:
        # ✅ Date range using IST-aware filter
        bills = filter_by_date_range(bills, 'bill_date', from_dt, to_dt)

    # ---------------- PROCESS EACH BILL ----------------
    for bill in bills:
        billno     = bill.billno
        bill_uhid  = bill.uhid
        patient_obj = OpPatientRegistration.objects.filter(uhid=bill_uhid).first()
        total = paid = concession = due = 0

        if bill_type == "CONSULTATION":
            src = DoctorConsultation.objects.filter(billno=billno,).first()
            op  = OpPayment.objects.filter(uhid=bill_uhid, billno=billno,).aggregate(
                paid=Sum("patamt"), conc=Sum("concession")
            )
            total      = src.consulfee   or 0 if src else 0
            paid       = (src.paidamt    or 0 if src else 0) + (op["paid"] or 0)
            concession = (src.concession or 0 if src else 0) + (op["conc"] or 0)
            due        = total - (paid + concession)

        elif bill_type == "PROCEDURE":
            src = TblServices.objects.filter(billno=billno,).aggregate(
                total=Sum("amount"), base_paid=Min("paidamt"), base_conc=Min("concessionamt")
            )
            op  = OpPayment.objects.filter(uhid=bill_uhid, billno=billno, ).aggregate(
                paid=Sum("patamt"), conc=Sum("concession")
            )
            total      = src["total"]      or 0
            paid       = (src["base_paid"] or 0) + (op["paid"] or 0)
            concession = (src["base_conc"] or 0) + (op["conc"] or 0)
            due        = total - (paid + concession)

        elif bill_type == "INVESTIGATION":
            src = tblInvestigationDetails.objects.filter(billno=billno,).aggregate(
                total=Sum("cost"), base_paid=Min("paidamt"), base_conc=Min("concessionamt")
            )
            op  = OpPayment.objects.filter(uhid=bill_uhid, billno=billno,).aggregate(
                paid=Sum("patamt"), conc=Sum("concession")
            )
            total      = src["total"]      or 0
            paid       = (src["base_paid"] or 0) + (op["paid"] or 0)
            concession = (src["base_conc"] or 0) + (op["conc"] or 0)
            due        = total - (paid + concession)

        elif bill_type == "OPPAYMENTS":
            op  = OpPayment.objects.filter(invbillno=billno,).aggregate(
                totalamt=Max("totalamt"), paid=Sum("patamt"),
                concession=Max("concession"), due=Max("due")
            )
            total      = op["totalamt"]   or 0
            paid       = op["paid"]       or 0
            concession = op["concession"] or 0
            due        = op["due"]        or 0

        if due < 0:
            due = 0

        results.append({
            "billno":      billno,
            "uhid":        bill_uhid,
            "patient":     patient_obj.patname if patient_obj else "",
            "total":       total,
            "paid":        paid,
            "concession":  concession,
            "due":         due
        })

    return render(request, "hospApp/frontoffice/BillLookup.html", {
        "results":   results,
        "bill_type": bill_type,
        "from_date": from_date,
        "to_date":   to_date
    })