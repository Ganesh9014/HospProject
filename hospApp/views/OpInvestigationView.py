from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from hospApp.models import (
    OpPatientRegistration, BankMaster, MainDepartmentMaster,
    DepartmentPhotoMaster, InvestigationMaster, HospitalMaster,
    DoctorMaster
)
from hospApp.models.DoctorConsultation import DoctorConsultation
from hospApp.models import Tbluserpermission,BillMaster
from hospApp.models.InvestigationDetails import tblInvestigationDetails
from django.db import transaction

# --------------------------------------------------------------------
# Op Investigation view + api endpoints
# --------------------------------------------------------------------
@login_required(login_url='login')
def OpInvestigationView(request):
    payee_list = BankMaster.objects.filter(active='Y').order_by('name')

    # Get logged-in user's department
    user_perm = Tbluserpermission.objects.filter(username=request.user.username).first()
    department = user_perm.department if user_perm else ""

    context = {
        'payee_list': payee_list,
        'department': department,
    }

    return render(request, 'hospApp/frontoffice/OpInvestigation.html', context)


@login_required(login_url='login')
def get_patient_details1(request):
    """
    Fetch latest DoctorConsultation for UHID (OP path). Returns extra doctor/ref info.
    """
    uhid = request.GET.get('uhid', '').strip()
    if not uhid:
        return JsonResponse({'success': False, 'error': 'UHID not provided'}, status=400)

    consult = DoctorConsultation.objects.filter(uhid=uhid, isactive='Y').order_by('-createddate').first()

    if not consult:
        return JsonResponse({'success': False, 'error': 'No consultation found'}, status=404)

    # safe access to related objects
    refdoc = getattr(consult, 'refdoctor', None)
    refdoc_name = refdoc.docname if refdoc else ""
    refdoc_id = getattr(consult, 'refdoctor_id', "")

    doctor = getattr(consult, 'doctor', None)
    doctor_name = doctor.docname if doctor else ""
    doctor_id = doctor.docid if doctor else ""

    # ✅ CHECK IF DOCTOR IS STILL ACTIVE IN DoctorMaster
    doctor_inactive = False
    if doctor:
        from hospApp.models import DoctorMaster
        active_check = DoctorMaster.objects.filter(docid=doctor_id, active='Y').first()
        if not active_check:
            doctor_inactive = True

    data = {
        'patname': consult.patname,
        'patid': consult.patid,
        'age': consult.age,
        'agetype': consult.agetype,
        'gender': consult.gender,
        'phone': consult.phone,
        'gardian': consult.gardian,
        'refdoctor_name': refdoc_name,
        'refdoc_id': refdoc_id,
        'doc_name': doctor_name,
        'doc_id': doctor_id,
        'uhid': consult.uhid,
        'paymenttype': getattr(consult, 'paymenttype', 'Cash'),

        # ✅ NEW FLAG
        'doctor_inactive': doctor_inactive,
    }

    return JsonResponse({'success': True, 'data': data})

@login_required(login_url='login')
def get_patient_details_op(request):
    uhid = request.GET.get("uhid", "").strip()
    if not uhid:
        return JsonResponse({"success": False, "error": "UHID not provided"}, status=400)

    patient = OpPatientRegistration.objects.filter(uhid=uhid).first()

    if not patient:
        return JsonResponse({"success": False}, status=404)

    # Fetch refdoctor name if ID exists
    consult=patient
    refdoc = getattr(consult, 'refdoctor', None)
    refdoc_name = refdoc.docname if refdoc else ""
    refdoc_id = getattr(consult, 'refdoctor_id', "") 
    
    data = {
        "patname": patient.patname,
        "patid": patient.patid,
        "age": patient.age,
        "agetype": patient.agetype,
        "gender": patient.gender,
        "phone": patient.phone,
        "paymenttype": getattr(patient, "paymenttype", "Cash"),

        # return reference doctor details
        "refdoctor_name": refdoc_name,
        "refdoctor_id": patient.refdoctor_id or "",

    }

    return JsonResponse({"success": True, "data": data})


@login_required(login_url='login')
def search_investigation(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})

    qs = (
        InvestigationMaster.objects
        .filter(active='Y', invname__icontains=q)
        .order_by('invname')[:20]
    )

    results = []
    for inv in qs:
        results.append({
            "inv_id": inv.ino,
            "invname": inv.invname,
            "cost": inv.cost,
        })

    return JsonResponse({"results": results})


@login_required(login_url='login')
def save_investigation(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    try:
        # -------------------------------------------------
        # BASIC PATIENT DETAILS
        # -------------------------------------------------
        uhid = request.POST.get('uhid')
        patname = request.POST.get('patname')
        age = request.POST.get('age')
        agetype = request.POST.get('agetype')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        pattype = request.POST.get('pattype')

        doctor_op = request.POST.get('doctor')  # OP doctor ID
        doctor_other_id = request.POST.get('other_doctor_id')  # Others doctor ID
        doctor_other_name = request.POST.get('other_doctor')  # optional

        # ✅ SAME LOGIC FOR BOTH
        doc_value = doctor_op if pattype == "OP" else doctor_other_id
        doctor_value = None if pattype == "OP" else doctor_other_name

        createdby = request.user.username

        # -------------------------------------------------
        # USER PASSWORD VERIFICATION
        # -------------------------------------------------
        logged_user = request.session.get("username")

        user = Tbluserpermission.objects.filter(
            username=logged_user,
            isactive=True
        ).first()

        usercode = request.POST.get('usercode', '').strip()

        if not user or usercode != user.password:
            return JsonResponse({
                "success": False,
                "message": "Invalid username or password"
            })

        # -------------------------------------------------
        # USER DEPARTMENT
        # -------------------------------------------------
        user_perm = Tbluserpermission.objects.filter(
            username=request.user.username
        ).first()

        department = user_perm.department if user_perm else ""

        # -------------------------------------------------
        # PAYMENT DETAILS
        # -------------------------------------------------
        # -------------------------------------------------
# PAYMENT DETAILS
# -------------------------------------------------
        cash_amt       = int(float(request.POST.get('cash_amt', 0) or 0))
        online_amt     = int(float(request.POST.get('online_amt', 0) or 0))
        online_mode    = request.POST.get('online_mode', '').strip()
        online_details = request.POST.get('online_details', '').strip()

        paid_total = cash_amt + online_amt   # total paid = cash + online

        # paymentmode label (backward compat)
        if cash_amt > 0 and online_amt > 0:
            paymentmode = f"Split (Cash + {online_mode})" if online_mode else "Split"
        elif online_amt > 0 and online_mode:
            paymentmode = online_mode
        else:
            paymentmode = "Cash"

        # validate online mode
        if online_amt > 0 and not online_mode:
            return JsonResponse({
                "success": False,
                "message": "Please select an online payment mode."
            })

        billtype      = request.POST.get('billtype')
        refdoctor     = request.POST.get('refdoctor_id')
        concessionamt = float(request.POST.get('concamount') or 0)
        concreason    = request.POST.get('concession_reason') or ""
        due           = float(request.POST.get('due') or 0)

        # -------------------------------------------------
        # INVESTIGATION ARRAYS
        # -------------------------------------------------
        # -------------------------------------------------
# INVESTIGATION ARRAYS
# -------------------------------------------------
        inv_ids = request.POST.getlist('inv_id[]')
        inv_costs = [float(x) for x in request.POST.getlist('invcost[]')]

        if not inv_ids:
            return JsonResponse({
                "success": False,
                "message": "No investigations selected"
            })

        # -------------------------------------------------
        # 🔐 RE-CALCULATE TOTAL (SERVER SIDE)
        # -------------------------------------------------
        total_amount = sum(inv_costs)

        # -------------------------------------------------
        # 🔐 STRICT PAYMENT VALIDATION
        # -------------------------------------------------
        if paid_total > total_amount:
            return JsonResponse({
                "success": False,
                "message": "Paid amount cannot exceed Net Amount"
            })

        if concessionamt > total_amount:
            return JsonResponse({
                "success": False,
                "message": "Concession amount cannot exceed Net Amount"
            })

        if (paid_total + concessionamt) > total_amount:
            return JsonResponse({
                "success": False,
                "message": "Paid + Concession cannot exceed Net Amount"
            })

        # -------------------------------------------------
        # 🔐 RE-CALCULATE DUE (DO NOT TRUST FRONTEND)
        # -------------------------------------------------
        due = total_amount - (paid_total + concessionamt)
        if due < 0:
            due = 0


        # -------------------------------------------------
        # CREATE BILL NUMBER (ATOMIC)
        # -------------------------------------------------
        with transaction.atomic():
            bill = BillMaster.objects.create(
                bill_type='INVESTIGATION',
                uhid=uhid,
                created_by=request.user.username
            )

        # -------------------------------------------------
        # SAVE ALL INVESTIGATIONS (NO SKIP, NO BREAK)
        # -------------------------------------------------
        for i in range(len(inv_ids)):
            tblInvestigationDetails.objects.create(
                uhid=uhid,
                invname=inv_ids[i],
                cost=inv_costs[i],

                createdby=createdby,

                patname=patname,
                age=age,
                agetype=agetype,
                gender=gender,
                phone=phone,

                refdoc=refdoctor,
                doc=doc_value,
                doctor=doctor_value,

                type=billtype,
                billno=bill.billno,

                concessionamt=concessionamt,
                concreason=concreason,
                paidamt=paid_total,       # total = cash + online
                due=due,

                refund="N",
                paymentmode=paymentmode,  # "Cash" / "UPI" / "Split (Cash + UPI)"
                cardname=online_details,  # reuse existing field for reference no.

                # ── SPLIT PAYMENT ──────────────────
                cash_amt=cash_amt,
                online_amt=online_amt,
                online_mode=online_mode,
                online_details=online_details,
                # ───────────────────────────────────

                active="Y",
                dept=department,
            )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------
        return JsonResponse({
            "success": True,
            "redirect_url": reverse(
                'op_investigation_bill',
                args=[bill.billno]
            )
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

from django.db.models import Sum
from hospApp.models import OpPayment, TblOpCancellation,TblServices,Tbluserpermission,TblRefund
from num2words import num2words

@login_required(login_url='login')
def op_investigation_bill(request, billno):
    hospital = HospitalMaster.objects.filter(active='a').first()
    items = tblInvestigationDetails.objects.filter(billno=billno)

    if not items.exists():
        return HttpResponse("Invalid Bill Number")

    is_cancelled = TblOpCancellation.objects.filter(billno=billno).exists()
    is_refunded = TblRefund.objects.filter(billno=billno).exists()

    bill = items.first()
    patient = OpPatientRegistration.objects.filter(uhid=bill.uhid).first()

    # ── Doctor info ──────────────────────────────────────────────
    if bill.doc and str(bill.doc).strip().isdigit():
        doctor_obj = DoctorMaster.objects.filter(docid=bill.doc).first()
        doctor_name = None
    else:
        doctor_obj = None
        doctor_name = bill.doctor or ""

    docconsul = DoctorConsultation.objects.filter(uhid=bill.uhid).first()

    # ── Split active vs refunded ─────────────────────────────────
    active_items   = items.filter(refund='N')   # or exclude(refund='Y')
    refunded_items = items.filter(refund='Y')

    # ── Attach display names ─────────────────────────────────────
    # ── Attach display names ─────────────────────────────────────
    for item in active_items:
        inv = InvestigationMaster.objects.filter(ino=item.invname).first()
        item.inv_display = inv.invname if inv else "Unknown"

    for item in refunded_items:
        inv = InvestigationMaster.objects.filter(ino=item.invname).first()
        item.inv_display = inv.invname if inv else "Unknown"

    # ── Totals (active only) ─────────────────────────────────────
    total = active_items.aggregate(t=Sum("cost"))["t"] or 0
    refund_total = refunded_items.aggregate(t=Sum("cost"))["t"] or 0

    first_item = items.first()
    base_paid = float(first_item.paidamt or 0)
    base_conc = float(first_item.concessionamt or 0)

    op = OpPayment.objects.filter(
        uhid=bill.uhid, billno=billno, active="Y"
    ).aggregate(paid=Sum("patamt"), conc=Sum("concession"))

    paid       = base_paid + (op["paid"] or 0)
    concession = base_conc + (op["conc"] or 0)
    due        = max(total - (paid + concession), 0)

    inwords = num2words(paid, to='cardinal').replace("-", " ").upper()

    context = {
        "bill": bill,
        "items": active_items,           # ← only active rows in main table
        "refunded_items": refunded_items, # ← new
        "refund_total": refund_total,     # ← new
        "hospital": hospital,
        "total": total,
        "paid": paid,
        "concession": concession,
        "due": due,
        "inwords": inwords,
        "patient": patient,
        "user_print": request.user.username,
        "docconsul": docconsul,
        "doctor_obj": doctor_obj,
        "doctor_name": doctor_name,
        "is_cancelled": is_cancelled,
        "is_refunded": is_refunded,
    }

    return render(request, "hospApp/frontoffice/op_investigation_bill.html", context)