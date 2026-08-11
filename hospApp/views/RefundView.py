from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Min
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json

from hospApp.models import (
    OpPatientRegistration,
    BankMaster,
    OpPayment,
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    TblRefund,
    InvestigationMaster,
    ServiceTypeMaster,
    DoctorMaster
)
from django.contrib.auth.decorators import login_required
# =====================================================
# REFUND MAIN PAGE
# =====================================================

@login_required(login_url='login')
def RefundView(request):
    patient = None
    uhid = request.GET.get("uhid")

    if uhid:
        patient = OpPatientRegistration.objects.filter(uhid=uhid).first()

    context = {
        "patient": patient,
        "payee_list": BankMaster.objects.all(),
    }
    return render(request, "hospApp/frontoffice/Refund.html", context)


# =====================================================
# FETCH REFUNDABLE BILLS
# =====================================================
@login_required(login_url='login')
def get_refund_bills_by_towards(request):
    uhid    = request.GET.get("uhid")
    towards = request.GET.get("towards")
    billno  = request.GET.get("billno")

    bills = []

    # ================= CONSULTATION =================
    if towards == "Consultation":
        qs = DoctorConsultation.objects.filter(uhid=uhid, isactive="Y")
        if billno:
            qs = qs.filter(billno=billno)

        for c in qs:
            total     = c.consulfee  or 0
            base_paid = c.paidamt    or 0
            base_conc = c.concession or 0

            op = OpPayment.objects.filter(
                uhid=uhid, billno=c.billno, active="Y"
            ).aggregate(paid=Sum("patamt"), conc=Sum("concession"))

            op_paid = op["paid"] or 0
            op_conc = op["conc"] or 0

            refunded = TblRefund.objects.filter(
                uhid=uhid, billno=c.billno, towords="Consultation"
            ).aggregate(r=Sum("refund"))["r"] or 0

            original_paid = base_paid + op_paid          # ✅ raw paid, never changes
            paid          = original_paid - refunded      # net paid after refunds
            conc          = base_conc + op_conc
            balance       = total - (original_paid + conc)

            if original_paid <= 0 and conc <= 0:
                continue

            bills.append({
                "billno":        c.billno,
                "created":       c.createddate,
                "total":         total,
                "paid":          paid,           # net paid (used for calc)
                "original_paid": original_paid,  # ✅ original paid (for prev_paid display)
                "concession":    conc,
                "refunded":      refunded,
                "refundable":    max(paid, 0),
                "balance":       balance,
            })

    # ================= PROCEDURES =================
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
            base_paid = p["base_paid"] or 0
            base_conc = p["base_conc"] or 0

            op = OpPayment.objects.filter(
                uhid=uhid, billno=p["billno"], active="Y"
            ).aggregate(paid=Sum("patamt"), conc=Sum("concession"))

            op_paid = op["paid"] or 0
            op_conc = op["conc"] or 0

            refunded = TblRefund.objects.filter(
                uhid=uhid, billno=p["billno"], towords="Procedures"
            ).aggregate(r=Sum("refund"))["r"] or 0

            original_paid = base_paid + op_paid          # ✅ raw paid
            paid          = original_paid - refunded      # net paid
            conc          = base_conc + op_conc
            balance       = (p["total"] or 0) - (original_paid + conc)

            if original_paid <= 0 and conc <= 0:
                continue

            bills.append({
                "billno":        p["billno"],
                "created":       p["created"],
                "total":         p["total"],
                "paid":          paid,
                "original_paid": original_paid,  # ✅
                "concession":    conc,
                "refunded":      refunded,
                "refundable":    max(paid, 0),
                "balance":       balance,
            })

    # ================= INVESTIGATION =================
    elif towards == "Investigation":
        qs = (
            tblInvestigationDetails.objects
            .filter(uhid=uhid)
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
            base_paid = i["base_paid"] or 0
            base_conc = i["base_conc"] or 0

            op = OpPayment.objects.filter(
                uhid=uhid, billno=i["billno"], active="Y"
            ).aggregate(paid=Sum("patamt"), conc=Sum("concession"))

            op_paid = op["paid"] or 0
            op_conc = op["conc"] or 0

            refunded = TblRefund.objects.filter(
                uhid=uhid, billno=i["billno"], towords="Investigation"
            ).aggregate(r=Sum("refund"))["r"] or 0

            original_paid = base_paid + op_paid          # ✅ raw paid, never subtract refund
            paid          = original_paid - refunded      # net paid for calculations
            conc          = base_conc + op_conc
            balance = (i["total"] or 0) - (original_paid + conc) + refunded
            active_total = tblInvestigationDetails.objects.filter(
                billno=i["billno"], active="Y"
            ).aggregate(s=Sum("cost"))["s"] or 0

            if original_paid <= 0 and conc <= 0:
                continue

            bills.append({
                "billno":        i["billno"],
                "created":       i["created"],
                "total":         i["total"],
                "paid":          paid,           # net paid (used in JS calc)
                "original_paid": original_paid,  # ✅ always original (shown in prev_paid)
                "concession":    conc,
                "refunded":      refunded,
                "refundable":    max(paid, 0),
                "balance":       balance,
                "active_total":  active_total
            })

    return JsonResponse({"success": True, "bills": bills})


# =====================================================
# FETCH BILL ITEMS
# =====================================================

@login_required(login_url='login')
def get_bill_items(request):
    billno  = request.GET.get("billno")
    towards = request.GET.get("towards")

    items = []

    # ================= INVESTIGATION =================
    if towards == "Investigation":
        qs = tblInvestigationDetails.objects.filter(
            billno=billno
        ).values("invname", "cost", "active")

        inv_ids = [int(q["invname"]) for q in qs if str(q["invname"]).isdigit()]

        inv_map = {
            i.ino: i.invname
            for i in InvestigationMaster.objects.filter(ino__in=inv_ids)
        }

        for q in qs:
            inv_id = int(q["invname"])
            items.append({
                "id":     q["invname"],
                "name":   inv_map.get(inv_id, "Unknown Investigation"),
                "amount": q["cost"],
                "active": q["active"],
            })

    # ================= PROCEDURES =================
    elif towards == "Procedures":
        qs = TblServices.objects.filter(
            billno=billno, isactive="Y"
        ).values("id", "services", "amount")

        service_ids = [int(q["services"]) for q in qs]

        service_map = {
            s.serviceid: s.servicename
            for s in ServiceTypeMaster.objects.filter(serviceid__in=service_ids)
        }

        for q in qs:
            items.append({
                "id":     q["id"],
                "name":   service_map.get(int(q["services"]), "Unknown Service"),
                "amount": q["amount"],
            })

    # ================= CONSULTATION =================
    elif towards == "Consultation":
        qs = DoctorConsultation.objects.filter(
            billno=billno, isactive="Y"
        )

        for f in qs:
            doctor = DoctorMaster.objects.filter(
                docid=f.doctor_id, active="Y"
            ).first()

            items.append({
                "id":     f.id,
                "name":   doctor.docname if doctor else "Unknown Doctor",
                "amount": f.consulfee,
            })

    return JsonResponse({"success": True, "items": items})


# =====================================================
# SAVE REFUND
# =====================================================
@csrf_exempt
@login_required(login_url='login')
def save_refund(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    try:
        uhid           = request.POST.get("uhid")
        billno         = request.POST.get("billno")
        refund_amt     = float(request.POST.get("pay_amount",      0))
        prev_paid      = float(request.POST.get("prev_paid",       0))
        balance        = float(request.POST.get("refund_balance",  0))  # ✅ paid - refund
        usercode       = request.POST.get("usercode")
        towards        = request.POST.get("Towards")

        selected_items = json.loads(request.POST.get("selected_items", "[]"))

        # Get bill time from investigation table
        investigation = tblInvestigationDetails.objects.filter(
            billno=billno
        ).first()

        bill_time = investigation.generateddate if investigation else None

        TblRefund.objects.create(
            uhid        = uhid,
            billno      = billno,
            refund      = refund_amt,
            amtpaid     = investigation.paidamt if investigation else 0,
            totalamt    = investigation.cost    if investigation else 0,
            balance     = balance,       # ✅ stores paid - refund_amt
            usercode    = request.user.username,
            createdtime = timezone.now(),
            billtime    = bill_time,
            towords     = towards,
            type        = "REFUND",
            createdby   = usercode,
        )

        for item in selected_items:
            if item["type"] == "Investigation":
                tblInvestigationDetails.objects.filter(
                    billno=billno,
                    invname=str(item["id"])
                ).update(active="N",refund="Y")

            elif item["type"] == "Procedures":
                TblServices.objects.filter(
                    id=item["id"]
                ).update(isactive="N")

        return JsonResponse({
            "success": True,
            "message": "Refund processed successfully"
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        })