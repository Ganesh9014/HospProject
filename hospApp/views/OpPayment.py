from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Min

from num2words import num2words

from hospApp.models import (
    OpPatientRegistration,
    BillMaster,
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    BankMaster,
    OpPayment,
    Tbluserpermission,
    HospitalMaster
)

# --------------------------------------------------
# CONSTANTS & HELPERS
# --------------------------------------------------

ALLOWED_BILL_TYPES = ["CONSULTATION", "INVESTIGATION", "PROCEDURE"]

BILL_TYPE_MAP = {
    "CONSULTATION": "Consultation",
    "INVESTIGATION": "Investigation",
    "PROCEDURE": "Procedures",
}

from django.contrib.auth.decorators import login_required


def to_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


# --------------------------------------------------
# OP PAYMENT PAGE
# --------------------------------------------------

@login_required(login_url='login')
@never_cache
def op_payment_page(request):
    payee_list = BankMaster.objects.filter(active='Y').order_by('name')
    uhid = request.GET.get("uhid")
    patient = OpPatientRegistration.objects.filter(uhid=uhid).first()

    return render(
        request,
        "hospApp/frontoffice/OpPayment.html",
        {
            "patient": patient,
            "payee_list": payee_list
        }
    )


# --------------------------------------------------
# GET PATIENT BY UHID
# --------------------------------------------------

@login_required(login_url='login')
def get_patient_by_uhid(request):
    uhid = request.GET.get("uhid")
    patient = OpPatientRegistration.objects.filter(uhid=uhid).first()

    if not patient:
        return JsonResponse({"success": False})

    return JsonResponse({
        "success": True,
        "patient": {
            "uhid": patient.uhid,
            "name": patient.patname,
            "age": patient.age,
            "agetype": patient.agetype,
            "gender": patient.gender,
            "phone": patient.phone,
            "patid": patient.patid,
            "address": patient.address
        }
    })


# --------------------------------------------------
# GET BILL TYPE BY BILL NO
# --------------------------------------------------

@login_required(login_url='login')
def get_bill_type_by_billno(request):
    billno = request.GET.get("billno")
    bill = BillMaster.objects.filter(billno=billno, active="Y").first()

    if not bill:
        return JsonResponse({"success": False})

    return JsonResponse({
        "success": True,
        "bill_type": bill.bill_type,
        "uhid": bill.uhid
    })


# --------------------------------------------------
# GET BILLS BY TOWARDS (LEDGER BASED)
# --------------------------------------------------

@login_required(login_url='login')
def get_bills_by_towards(request):
    uhid = request.GET.get("uhid")
    towards = request.GET.get("towards")
    billno = request.GET.get("billno")

    bills = []

    # ---------------- CONSULTATION ----------------
    if towards == "Consultation":
        qs = DoctorConsultation.objects.filter(uhid=uhid, isactive="Y")
        if billno:
            qs = qs.filter(billno=billno)

        for c in qs:
            total = c.consulfee or 0
            base_paid = c.paidamt or 0
            base_conc = c.concession or 0

            op = OpPayment.objects.filter(
                uhid=uhid,
                billno=c.billno,active="Y"
            ).aggregate(
                paid=Sum("patamt"),
                conc=Sum("concession")
            )

            paid = base_paid + (op["paid"] or 0)
            conc = base_conc + (op["conc"] or 0)
            balance = total - (paid + conc)

            if balance > 0:
                bills.append({
                    "billno": c.billno,
                    "created": c.createddate,
                    "total": total,
                    "paid": paid,
                    "concession": conc,
                    "balance": balance
                })

    # ---------------- PROCEDURES ----------------
    elif towards == "Procedures":
        qs = (
            TblServices.objects
            .filter(uhid=uhid, isactive="Y")
            .values("billno")
            .annotate(
                created=Min("generateddate"),
                total=Sum("amount"),
                base_paid=Min("paidamt"),
                base_conc=Min("concessionamt")
            )
        )
        if billno:
            qs = qs.filter(billno=billno)

        for p in qs:
            op = OpPayment.objects.filter(
                uhid=uhid,
                billno=p["billno"],active="Y"
            ).aggregate(
                paid=Sum("patamt"),
                conc=Sum("concession")
            )

            paid = (p["base_paid"] or 0) + (op["paid"] or 0)
            conc = (p["base_conc"] or 0) + (op["conc"] or 0)
            balance = (p["total"] or 0) - (paid + conc)

            if balance > 0:
                bills.append({
                    "billno": p["billno"],
                    "created": p["created"],
                    "total": p["total"],
                    "paid": paid,
                    "concession": conc,
                    "balance": balance
                })

    # ---------------- INVESTIGATION ----------------
    elif towards == "Investigation":
        qs = (
            tblInvestigationDetails.objects
            .filter(uhid=uhid, active="Y")
            .values("billno")
            .annotate(
                created=Min("generateddate"),
                total=Sum("cost"),
                base_paid=Min("paidamt"),
                base_conc=Min("concessionamt")
            )
        )
        if billno:
            qs = qs.filter(billno=billno)

        for i in qs:
            op = OpPayment.objects.filter(
                uhid=uhid,
                billno=i["billno"],active="Y"
            ).aggregate(
                paid=Sum("patamt"),
                conc=Sum("concession")
            )

            paid = (i["base_paid"] or 0) + (op["paid"] or 0)
            conc = (i["base_conc"] or 0) + (op["conc"] or 0)
            balance = (i["total"] or 0) - (paid + conc)

            if balance > 0:
                bills.append({
                    "billno": i["billno"],
                    "created": i["created"],
                    "total": i["total"],
                    "paid": paid,
                    "concession": conc,
                    "balance": balance
                })

    return JsonResponse({
        "success": True,
        "bills": bills
    })


# --------------------------------------------------
# SAVE OP PAYMENT (LEDGER BASED)
# --------------------------------------------------


@login_required(login_url='login')
def save_op_payment(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    uhid = request.POST.get("uhid")
    billno = request.POST.get("billno")
    towards = request.POST.get("Towards")

    pay_amt = to_int(request.POST.get("pay_amount"))
    new_conc = to_int(request.POST.get("concession"))
    prev_paid_form = to_int(request.POST.get("prev_paid"))
    balance_form = to_int(request.POST.get("balance"))
    usercode = request.POST.get("usercode")
    # ── SPLIT PAYMENT ────────────────────────────────────
    cash_amt       = to_int(request.POST.get('cash_amt', 0))
    online_amt     = to_int(request.POST.get('online_amt', 0))
    online_mode    = request.POST.get('online_mode', '').strip()
    online_details = request.POST.get('online_details', '').strip()

    pay_amt = cash_amt + online_amt

    if cash_amt > 0 and online_amt > 0:
        paymentmode = f"Split (Cash + {online_mode})" if online_mode else "Split"
    elif online_amt > 0 and online_mode:
        paymentmode = online_mode
    else:
        paymentmode = "Cash"

    if online_amt > 0 and not online_mode:
        return JsonResponse({"success": False, "message": "Please select an online payment mode."})
# ─────────────────────────────────────────────────────

    # ---------------- BILL VALIDATION ----------------
    bill = BillMaster.objects.filter(billno=billno, active="Y").first()
    if not bill:
        return JsonResponse({"success": False, "message": "Invalid Bill Number"})

    if bill.bill_type not in ALLOWED_BILL_TYPES:
        return JsonResponse({"success": False, "message": "Bill not allowed for OP Payment"})

    if BILL_TYPE_MAP.get(bill.bill_type) != towards:
        return JsonResponse({"success": False, "message": "Bill type mismatch"})

    # ---------------- USER VALIDATION ----------------
    user = Tbluserpermission.objects.filter(
        username=request.user.username,
        isactive=True
    ).first()

    if not user or user.password != usercode:
        return JsonResponse({"success": False, "message": "Invalid User Code"})

    # ---------------- SOURCE DATA ----------------
    total = base_paid = base_conc = 0

    if towards == "Consultation":
        src = DoctorConsultation.objects.filter(uhid=uhid, billno=billno, isactive="Y").first()
        if not src:
            return JsonResponse({"success": False, "message": "Invalid consultation bill"})

        total = src.consulfee or 0
        base_paid = src.paidamt or 0
        base_conc = src.concession or 0

    elif towards == "Procedures":
        src = TblServices.objects.filter(uhid=uhid, billno=billno, isactive="Y").aggregate(
            total=Sum("amount"),
            base_paid=Min("paidamt"),
            base_conc=Min("concessionamt")  
        )
        total = src["total"] or 0
        base_paid = src["base_paid"] or 0
        base_conc = src["base_conc"] or 0

    elif towards == "Investigation":
        src = tblInvestigationDetails.objects.filter(uhid=uhid, billno=billno, active="Y").aggregate(
            total=Sum("cost"),
            base_paid=Min("paidamt"),
            base_conc=Min("concessionamt")  
        )
        total = src["total"] or 0
        base_paid = src["base_paid"] or 0
        base_conc = src["base_conc"] or 0

    # ---------------- LEDGER CALCULATION ----------------
    op = OpPayment.objects.filter(
        uhid=uhid,
        billno=billno,active="Y"    
    ).aggregate(
        paid=Sum("patamt"),
        conc=Sum("concession")
    )

    prev_paid = base_paid + (op["paid"] or 0)
    prev_conc = base_conc + (op["conc"] or 0)

    new_paid_total = prev_paid + pay_amt
    new_conc_total = prev_conc + new_conc

    due = total - (new_paid_total + new_conc_total)
    if due < 0:
        due = 0

    # ---------------- SAVE ----------------
    with transaction.atomic():
        payment_bill = BillMaster.objects.create(
            bill_type="OPPAYMENTS",
            uhid=uhid,
            created_by=request.user.username,active="Y"
        )

        OpPayment.objects.create(
            uhid=uhid,
            patname=request.POST.get("patname"),
            age=request.POST.get("age"),
            agetype=request.POST.get("agetype"),
            gender=request.POST.get("gender"),
            phone=request.POST.get("phone"),

            billdate=timezone.now(),
            billno=billno,
            totalamt=total,

            paidamt=prev_paid_form,
            patamt=pay_amt,
            concession=new_conc,
            preconcession=prev_conc,

            due=due,
            balance=balance_form,
            invbillno=payment_bill.billno,

            paymentmode=paymentmode,
            concreason=request.POST.get("concession_reason"),
            cardname=online_details,

            towords=towards,
            userid=usercode,
            updatedby=request.user.username,
            updateddate=timezone.now(),
            active="Y",
            cash_amt=cash_amt,
            online_amt=online_amt,
            online_mode=online_mode,
            online_details=online_details,
        )

    return JsonResponse({
        "success": True,
        "redirect_url": reverse("op_payment_receipt", args=[payment_bill.billno])
    })


# --------------------------------------------------
# OP PAYMENT RECEIPT
# --------------------------------------------------
from hospApp.models import TblOpCancellation

from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def op_payment_receipt(request, invbillno):
    payment = get_object_or_404(OpPayment, invbillno=invbillno,)
    hospital = HospitalMaster.objects.filter(active='a').first()
    
    # ← Fetch latest patient data from registration
    patient = OpPatientRegistration.objects.filter(uhid=payment.uhid).first()
    is_cancelled = TblOpCancellation.objects.filter(billno=invbillno).exists()


    amount_words = num2words(payment.patamt).replace("-", " ").title()

    return render(
        request,
        "hospApp/frontoffice/op_payment_receipt.html",
        {
            "hospital": hospital,
            "consult": payment,
            "patient": patient,        # ← pass patient separately
            "inwords": amount_words,
            "request": request,
            "is_cancelled": is_cancelled
        }
    )