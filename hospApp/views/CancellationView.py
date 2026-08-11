from django.shortcuts import render, redirect
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal

from hospApp.models import (
    TblOpCancellation,
    tblInvestigationDetails,
    DoctorConsultation,
    TblServices,
    BillMaster,
    OpPayment,
    Tbluserpermission,
    ExpenditureEntry
)
from hospApp.models import InvestigationReport
from django.contrib.auth.decorators import login_required   
@login_required(login_url='login')
def CancellationView(request):

    # ================= POST REQUEST =================
    if request.method == "POST":

        billno       = request.POST.get("bill_no")
        patient_type = request.POST.get("patient_type")
        reason       = request.POST.get("cancellation_reason")
        userid       = request.POST.get("username")
        usercode     = request.POST.get("usercode")

        # ================= BILL MASTER =================
        try:
            billmaster = BillMaster.objects.get(billno=billno, active="Y")
        except BillMaster.DoesNotExist:
            messages.error(request, "Invalid bill number")
            return redirect("CancellationView")

        # ================= EXPENDITURE =================
        # ================= EXPENDITURE =================
        # ================= EXPENDITURE =================
        if patient_type == "Expenditure":
            qs = ExpenditureEntry.objects.filter(bill_no=billno, active="Y")

            if not qs.exists():
                messages.warning(request, "This expenditure is already cancelled")
                return redirect("CancellationView")

            with transaction.atomic():
                qs.update(
                    active       = "N",
                    reason       = reason,
                    selecteduser = userid,
                    user         = request.user.username if request.user.is_authenticated else None
                )

            messages.success(request, "Expenditure cancelled successfully")
            return redirect("CancellationView")
        # ================= CHECK REPORT EXISTS (Investigation only) =================
        if patient_type == "Investigation":
            report_exists = InvestigationReport.objects.filter(
                billno=billno,
                is_active=True
            ).exists()

            if report_exists:
                messages.error(request, "❌ Report already generated. Cannot cancel this bill.")
                return redirect("CancellationView")

        # ================= FETCH ACTIVE RECORDS =================
        if patient_type == "Investigation":
            qs = tblInvestigationDetails.objects.filter(billno=billno, active="Y")

        elif patient_type == "Consultation":
            qs = DoctorConsultation.objects.filter(billno=billno, isactive="Y")

        elif patient_type == "Procedure":
            qs = TblServices.objects.filter(billno=billno, isactive="Y")

        elif patient_type == "OpPayment":
            qs = OpPayment.objects.filter(invbillno=billno, active="Y")

        else:
            messages.error(request, "Invalid patient type")
            return redirect("CancellationView")

        if not qs.exists():
            messages.warning(request, "This bill is already cancelled")
            return redirect("CancellationView")

        # ================= AMOUNT CALCULATION =================
        total_amt        = Decimal('0.00')
        total_paid       = Decimal('0.00')
        total_due        = Decimal('0.00')
        total_concession = Decimal('0.00')

        if patient_type == "Investigation":
            total_amt        = qs.aggregate(amt=Sum('cost'))['amt'] or 0
            row              = qs.first()
            total_paid       = row.paidamt or 0
            total_due        = row.due or 0
            total_concession = row.concessionamt or 0

        elif patient_type == "Procedure":
            total_amt        = qs.aggregate(amt=Sum('amount'))['amt'] or 0
            row              = qs.first()
            total_paid       = row.paidamt or 0
            total_due        = row.due or 0
            total_concession = row.concessionamt or 0

        elif patient_type == "Consultation":
            row              = qs.first()
            total_amt        = row.consulfee or 0
            total_paid       = row.paidamt or 0
            total_due        = row.due or 0
            total_concession = row.concession or 0

        elif patient_type == "OpPayment":
            row              = qs.first()
            total_amt        = row.totalamt or 0
            total_paid       = row.paidamt or 0
            total_due        = row.due or 0
            total_concession = row.concession or 0

        # ================= SAVE CANCELLATION =================
        with transaction.atomic():

            TblOpCancellation.objects.create(
                uhid         = request.POST.get("uhid"),
                billno       = billno,
                patname      = request.POST.get("patient_name"),
                age          = request.POST.get("age"),
                gender       = request.POST.get("gender"),
                phoneno      = request.POST.get("phone_no"),
                billdate     = request.POST.get("bill_date"),
                totalamt     = total_amt,
                amtpaid      = total_paid,
                bal          = total_due,
                concessionamt= total_concession,
                refundamt    = total_paid,
                Reason       = reason,
                userid       = userid,
                type         = patient_type,
                createddate  = timezone.now(),
                createdby    = request.user.username if request.user.is_authenticated else None
            )

            # ================= CANCEL MAIN RECORD =================
            if patient_type == "Investigation":
                qs.update(active="N")

            elif patient_type == "Consultation":
                qs.update(isactive="N")

            elif patient_type == "Procedure":
                qs.update(isactive="N")

            elif patient_type == "OpPayment":
                qs.update(active="N")

            # ================= CANCEL RELATED OP PAYMENTS =================
            if patient_type != "OpPayment":

                op_payments = OpPayment.objects.filter(
                    billno=billno,
                    active="Y"
                )

                op_bill_nos = list(
                    op_payments.values_list('invbillno', flat=True)
                )

                # Save cancellation entry for every payment bill
                for op in op_payments:

                    TblOpCancellation.objects.create(
                        uhid=op.uhid,
                        billno=op.invbillno,      # Payment bill number
                        patname=op.patname,
                        age=op.age,
                        gender=op.gender,
                        phoneno=op.phone,
                        billdate=op.billdate,

                        totalamt=op.totalamt or 0,
                        amtpaid=op.patamt or 0,
                        bal=op.due or 0,
                        concessionamt=op.concession or 0,

                        refundamt=op.patamt or 0,

                        Reason=reason,
                        userid=userid,
                        type="OpPayment",

                        createddate=timezone.now(),
                        createdby=request.user.username
                    )

                # Inactivate payment records
                op_payments.update(active="N")

                # Inactivate corresponding bill masters
                BillMaster.objects.filter(
                    billno__in=op_bill_nos,
                    active="Y"
                ).update(active="N")

            # ================= CANCEL BILLMASTER =================
            billmaster.active = "N"
            billmaster.save()

        messages.success(request, "Cancellation completed successfully")
        return redirect("CancellationView")

    # ================= GET REQUEST =================
    bill_type = (request.GET.get("type") or "").strip().upper()
    billno    = request.GET.get("billno")
    context   = {"type": bill_type}

    # ================= EXPENDITURE AUTO-FILL =================
    if bill_type == "EXPENDITURE" and billno:
        entry = ExpenditureEntry.objects.select_related('expenditure').filter(
            bill_no=billno, 
        ).first()

        if entry:
            context.update({
                "bill_no":          entry.bill_no,
                "bill_date":        entry.created_at,
                "expenditure_name": entry.expenditure.expenditure_name,
                "amount":           entry.amount,
                "towards":          entry.towards,
            })

    users = Tbluserpermission.objects.filter(isactive=True).order_by('username')
    context["users"] = users

    return render(
        request,
        "hospApp/frontoffice/CancellationPage.html",
        context
    )


# ================= VALIDATE USER =================
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
@require_POST
def validate_user_code(request):
    usercode = request.POST.get("usercode", "").strip()

    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "User not logged in"
        })

    user = Tbluserpermission.objects.filter(
        username=request.user.username,
        isactive=True
    ).first()

    if not user or user.password != usercode:
        return JsonResponse({
            "success": False,
            "message": "Invalid User Code"
        })

    return JsonResponse({"success": True})