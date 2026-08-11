
from django.shortcuts import render 

from hospApp.models import PaymentModeUpdateLog
from django.contrib.auth.decorators import login_required   
from hospApp.models import (
    BillMaster,
    OpPatientRegistration,
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment,
    BankMaster
)

def paymentmodeupdate(request):
    banks = BankMaster.objects.filter(
        active='Y'
    ).order_by('name')

    return render(request,'hospApp/frontOffice/paymentmodeupdate.html',{'banks':banks})
    


from django.http import JsonResponse
from django.db.models import Sum, Min, Max

@login_required(login_url='login')
def get_paymentmode_details(request):

    billno = request.GET.get("billno")

    bill = BillMaster.objects.filter(
        billno=billno
    ).first()

    if not bill:
        return JsonResponse({
            "success": False,
            "message": "Invalid Bill No"
        })

    patient = OpPatientRegistration.objects.filter(
        uhid=bill.uhid
    ).first()

    bill_type = (bill.bill_type or "").upper().strip()

    cash_amt = 0
    online_amt = 0
    online_mode = ""
    online_details = ""

    total = paid = concession = due = 0
    if bill_type == "CONSULTATION":

        src = DoctorConsultation.objects.filter(
            billno=billno
        ).first()

        if src:
            total = src.consulfee or 0
            paid = src.paidamt or 0
            concession = src.concession or 0
            due = src.due or 0

            cash_amt = src.cash_amt or 0
            online_amt = src.online_amt or 0
            online_mode = src.online_mode or ""
            online_details = src.online_details or ""

    elif bill_type == "PROCEDURE":

        first_row = TblServices.objects.filter(
            billno=billno
        ).first()

        src = TblServices.objects.filter(
            billno=billno
        ).aggregate(
            total=Sum("amount"),
            paid=Min("paidamt"),
            concession=Min("concessionamt")
        )

        total = src["total"] or 0
        paid = src["paid"] or 0
        concession = src["concession"] or 0
        due = total - (paid + concession)

        if first_row:
            cash_amt = first_row.cash_amt or 0
            online_amt = first_row.online_amt or 0
            online_mode = first_row.online_mode or ""
            online_details = first_row.online_details or ""


    elif bill_type == "INVESTIGATION":

        first_row = tblInvestigationDetails.objects.filter(
            billno=billno
        ).first()

        src = tblInvestigationDetails.objects.filter(
            billno=billno
        ).aggregate(
            total=Sum("cost"),
            paid=Min("paidamt"),
            concession=Min("concessionamt")
        )

        total = src["total"] or 0
        paid = src["paid"] or 0
        concession = src["concession"] or 0
        due = total - (paid + concession)

        if first_row:
            cash_amt = first_row.cash_amt or 0
            online_amt = first_row.online_amt or 0
            online_mode = first_row.online_mode or ""
            online_details = first_row.online_details or ""
    elif bill_type in ["OPPAYMENT", "OPPAYMENTS"]:

        op = OpPayment.objects.filter(
            invbillno=billno
        ).first()

        if op:
            total = op.totalamt or 0
            paid = op.patamt or 0
            concession = op.concession or 0
            due = op.due or 0

            cash_amt = op.cash_amt or 0
            online_amt = op.online_amt or 0
            online_mode = op.online_mode or ""
            online_details = op.online_details or ""
    return JsonResponse({
        "success": True,
        "data": {
            "bill_date": bill.bill_date,
            "uhid": patient.uhid if patient else "",
            "patient_name": patient.patname if patient else "",
            "age": patient.age if patient else "",
            "phone": patient.phone if patient else "",
            "gender": patient.gender if patient else "",
            "bill_no": bill.billno,
            "patient_type": bill.bill_type,

            "total_amount": total,
            "paid_amount": paid,
            "concession": concession,
            "due_amount": due,

            "cash_amt": cash_amt,
            "online_amt": online_amt,
            "online_mode": online_mode,
            "online_details": online_details
        }
    })            


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from hospApp.models import (
    Tbluserpermission,
    DoctorConsultation,
    TblServices,
    tblInvestigationDetails,
    OpPayment
)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def save_payment_mode_update(request):


        if request.method != "POST":
            return JsonResponse({
                "success": False,
                "message": "Invalid Request"
            })

        billno = request.POST.get("bill_no")

        patient_type = (
            request.POST.get("patient_type", "")
            .strip()
            .upper()
        )

        patient_name = ""
        uhid = ""

        bill = BillMaster.objects.filter(
            billno=billno
        ).first()

        if bill:
            uhid = bill.uhid or ""

            patient = OpPatientRegistration.objects.filter(
                uhid=uhid
            ).first()

            if patient:
                patient_name = patient.patname

        online_mode = request.POST.get(
            "online_mode",
            ""
        ).strip()

        online_details = request.POST.get(
            "online_details",
            ""
        ).strip()

        entered_pass = request.POST.get(
            "usercode",
            ""
        ).strip()

        logged_user = request.session.get("username")

        user = Tbluserpermission.objects.filter(
            username=logged_user,
            isactive=True
        ).first()

        if not user or entered_pass != user.password:
            return JsonResponse({
                "success": False,
                "message": "Invalid User Code"
            })

        obj = None

        # ---------------- CONSULTATION ----------------
        if patient_type == "CONSULTATION":

            obj = DoctorConsultation.objects.filter(
                billno=billno
            ).first()

            if not obj:
                return JsonResponse({
                    "success": False,
                    "message": "Consultation Not Found"
                })

            old_mode = obj.online_mode
            old_ref = obj.online_details

            if (
                old_mode == online_mode and
                old_ref == online_details
            ):
                return JsonResponse({
                    "success": False,
                    "message": "No Changes Detected"
                })

            DoctorConsultation.objects.filter(
                billno=billno
            ).update(
                online_mode=online_mode,
                online_details=online_details
            )

        # ---------------- PROCEDURE ----------------
        elif patient_type in ["PROCEDURE", "PROCEDURES"]:

            obj = TblServices.objects.filter(
                billno=billno
            ).first()

            if not obj:
                return JsonResponse({
                    "success": False,
                    "message": "Procedure Not Found"
                })

            old_mode = obj.online_mode
            old_ref = obj.online_details

            if (
                old_mode == online_mode and
                old_ref == online_details
            ):
                return JsonResponse({
                    "success": False,
                    "message": "No Changes Detected"
                })

            # Update ALL rows
            TblServices.objects.filter(
                billno=billno
            ).update(
                online_mode=online_mode,
                online_details=online_details
            )

        # ---------------- INVESTIGATION ----------------
        elif patient_type == "INVESTIGATION":

            obj = tblInvestigationDetails.objects.filter(
                billno=billno
            ).first()

            if not obj:
                return JsonResponse({
                    "success": False,
                    "message": "Investigation Not Found"
                })

            old_mode = obj.online_mode
            old_ref = obj.online_details

            if (
                old_mode == online_mode and
                old_ref == online_details
            ):
                return JsonResponse({
                    "success": False,
                    "message": "No Changes Detected"
                })

            # Update ALL rows
            tblInvestigationDetails.objects.filter(
                billno=billno
            ).update(
                online_mode=online_mode,
                online_details=online_details
            )

        # ---------------- OP PAYMENT ----------------
        elif patient_type in ["OPPAYMENT", "OPPAYMENTS"]:

            obj = OpPayment.objects.filter(
                invbillno=billno
            ).first()

            if not obj:
                return JsonResponse({
                    "success": False,
                    "message": "Payment Not Found"
                })

            old_mode = obj.online_mode
            old_ref = obj.online_details

            if (
                old_mode == online_mode and
                old_ref == online_details
            ):
                return JsonResponse({
                    "success": False,
                    "message": "No Changes Detected"
                })

            OpPayment.objects.filter(
                invbillno=billno
            ).update(
                online_mode=online_mode,
                online_details=online_details
            )

        else:
            return JsonResponse({
                "success": False,
                "message": "Invalid Bill Type"
            })

        # ---------------- AUDIT LOG ----------------

        PaymentModeUpdateLog.objects.create(
            uhid=obj.uhid,
            patient_name=patient_name,
            bill_type=patient_type,

            old_online_mode=old_mode,
            new_online_mode=online_mode,

            old_reference=old_ref,
            new_reference=online_details,

            updated_by=logged_user,
            bill_no=billno,  
            

        )

        return JsonResponse({
            "success": True,
            "message": "Payment Mode Updated Successfully"
        })

