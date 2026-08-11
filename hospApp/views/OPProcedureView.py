

from django.shortcuts import render
from django.contrib.auth.decorators import login_required   
from hospApp.models import ServiceTypeMaster    
from django.http import JsonResponse    
from hospApp.models import BankMaster   


@login_required(login_url='login')  
def OPProcedureView(request):
    payee_list = BankMaster.objects.filter(active='Y').order_by('name')
    date=timezone.now()
    context = {
        'payee_list': payee_list,
        'date':date

        
    }
    

    return render(request, 'hospApp/frontoffice/OPProcedure.html', context)  
@login_required(login_url='login')
def search_service(request):
    q = request.GET.get("q", "").strip()

    if not q:
        return JsonResponse({"results": []})

    services = (
        ServiceTypeMaster.objects
        .filter(active='Y', servicename__icontains=q)
        .order_by("servicename")[:20]
    )

    data = []
    for s in services:
        data.append({
            "id": s.serviceid,
            "name": s.servicename,
            "charge": s.charge or 0
        })

    return JsonResponse({"results": data})
from django.db import transaction
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from hospApp.models import TblServices, BillMaster, Tbluserpermission
from hospApp.models import DoctorMaster
@login_required(login_url="login")
def save_procedure(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"})

    try:
        # ---------------- PATIENT ----------------
        uhid = request.POST.get("uhid")
        pattype = request.POST.get("pattype")
        createdby = request.user.username

        # ---------------- USER CODE ----------------
        usercode = request.POST.get("usercode", "").strip()
        user = Tbluserpermission.objects.filter(
            username=request.user.username,
            isactive=True
        ).first()

        if not user or user.password != usercode:
            return JsonResponse({
                "success": False,
                "message": "Invalid User Code"
            })
        
        # ── PAYMENT DETAILS ──────────────────────────────────────────────
        cash_amt       = int(float(request.POST.get('cash_amt', 0) or 0))
        online_amt     = int(float(request.POST.get('online_amt', 0) or 0))
        online_mode    = request.POST.get('online_mode', '').strip()
        online_details = request.POST.get('online_details', '').strip()

        paid_total = cash_amt + online_amt

        if cash_amt > 0 and online_amt > 0:
            paymentmode = f"Split (Cash + {online_mode})" if online_mode else "Split"
        elif online_amt > 0 and online_mode:
            paymentmode = online_mode
        else:
            paymentmode = "Cash"

        if online_amt > 0 and not online_mode:
            return JsonResponse({"success": False, "message": "Please select an online payment mode."})

        concession = float(request.POST.get("concamount") or 0)
        due        = float(request.POST.get("due") or 0)
        reason     = request.POST.get("concession_reason", "")
     
        # ---------------- SERVICES ----------------
        service_ids = request.POST.getlist("service_id[]")
        service_names = request.POST.getlist("servicename[]")
        qty_list = request.POST.getlist("qty[]")
        cost_list = request.POST.getlist("cost[]")

        doctor_op = request.POST.get("doctor")  # OP doctor ID
        doctor_other_id = request.POST.get("other_doctor_id")  # Others doctor ID

        # 🔹 Decide doctor ID
        if pattype == "OP":
            doctor_id = doctor_op
        else:
            if not doctor_other_id:
                return JsonResponse({
                    "success": False,
                    "message": "Please select doctor from suggestions"
                })
            doctor_id = doctor_other_id

        # 🔹 Fetch doctor from master (SOURCE OF TRUTH)
        doctor_obj = DoctorMaster.objects.filter(docid=doctor_id).first()

        if not doctor_obj:
            return JsonResponse({
                "success": False,
                "message": "Invalid doctor selected"
            })

        # 🔹 Always take name from DB (NOT from input)
        doctor_name = doctor_obj.docname
        

        if not service_ids:
            return JsonResponse({
                "success": False,
                "message": "No services selected"
            })

# ---------------- RE-CALCULATE TOTAL ----------------
        total_amount = sum(float(cost) for cost in cost_list)

# ---------------- STRICT VALIDATION ----------------
        if paid_total > total_amount:
            return JsonResponse({
                "success": False,
                "message": "Paid amount cannot exceed Net Amount"
            })

        if concession > total_amount:
            return JsonResponse({
                "success": False,
                "message": "Concession cannot exceed Net Amount"
            })

        if (paid_total + concession) > total_amount:
            return JsonResponse({
                "success": False,
                "message": "Paid + Concession cannot exceed Net Amount"
            })


        # ---------------- BILL NO ----------------
        with transaction.atomic():
            bill = BillMaster.objects.create(
                bill_type="PROCEDURE",
                uhid=uhid,
                created_by=request.user.username
            )

        # ---------------- SAVE SERVICES ----------------
        for i in range(len(service_ids)):
            TblServices.objects.create(
                uhid=uhid,
                services=service_ids[i],
                services_typename=service_names[i],
                qty=int(qty_list[i]),
                amount=float(cost_list[i]),

                billno=bill.billno,
                pattype=pattype,
                type="OP",

                paidamt=paid_total,
                due=due,
                concessionamt=concession,
                concreason=reason,

                paymentmode=paymentmode,
                cardname=online_details,      # reuse for reference no.

                # ── SPLIT PAYMENT ──────────────────
                cash_amt=cash_amt,
                online_amt=online_amt,
                online_mode=online_mode,
                online_details=online_details,
                # ───────────────────────────────────

                createdby=createdby,
                createddate=timezone.now(),
                generateddate=timezone.now(),
                generatedtime=timezone.now(),
                doc=doctor_obj,
                doctor=doctor_name,
                isactive="Y"
            )

        return JsonResponse({
            "success": True,
            "redirect_url": reverse(
                "op_procedure_bill",
                args=[bill.billno]
            )
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        })

from django.http import HttpResponse    
from hospApp.models import HospitalMaster, TblServices, DoctorMaster, DoctorConsultation , OpPatientRegistration           
from django.db.models import Sum
from hospApp.models import OpPayment, TblOpCancellation
from num2words import num2words

@login_required(login_url="login")
def op_procedure_bill(request, billno):
    hospital = HospitalMaster.objects.filter(active="a").first()
    items = TblServices.objects.filter(billno=billno,)
    is_cancelled = TblOpCancellation.objects.filter(billno=billno).exists()


    if not items.exists():
        return HttpResponse("Invalid Bill")

    bill = items.first()

    # ---------------- PATIENT ----------------
    patient = OpPatientRegistration.objects.filter(
        uhid=bill.uhid
    ).first()

    # ---------------- DOCTOR ----------------
    doctor = bill.doc if bill.doc else None

    # ---------------- TOTAL ----------------
    total = sum((x.amount or 0) for x in items)

    first_item = items.first()
    base_paid = float(first_item.paidamt or 0)
    base_conc = float(first_item.concessionamt or 0)

    # ---------------- OP PAYMENT LEDGER ----------------
    op = OpPayment.objects.filter(
        uhid=bill.uhid,
        billno=billno,active="Y"    
    ).aggregate(
        paid=Sum("patamt"),
        conc=Sum("concession")
    )

    paid = base_paid + (op["paid"] or 0)
    concession = base_conc + (op["conc"] or 0)

    due = total - (paid + concession)
    if due < 0:
        due = 0

    inwords = num2words(paid, to="cardinal").replace("-", " ").upper()

    context = {
        "hospital": hospital,
        "bill": bill,
        "items": items,

        "patient": patient,
        "doctor": doctor,

        # 🔥 LEDGER VALUES
        "total": total,
        "paid": paid,
        "concession": concession,
        "due": due,
        "inwords": inwords,

        "is_cancelled": is_cancelled
    }

    return render(
        request,
        "hospApp/frontoffice/op_procedure_bill.html",
        context
    )
