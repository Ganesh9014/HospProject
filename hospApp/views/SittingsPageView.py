from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from hospApp.models import OpPatientRegistration, DoctorConsultation, TblServices, SittingsPage, HospitalMaster, ServiceTypeMaster, OpPayment, TblOpCancellation
from datetime import datetime
from django.db.models import Sum
from num2words import num2words




@login_required(login_url='login')
def SittingsPageView(request):
    return render(request, 'hospApp/Admin/SittingsPage.html')


@login_required(login_url='login')
def get_sittings_patient_data(request):
    uhid = request.GET.get('uhid', '').strip()
    if not uhid:
        return JsonResponse({'success': False, 'message': 'UHID is required'})

    # Search in OpPatientRegistration
    patient = OpPatientRegistration.objects.filter(uhid=uhid).first()
    consult = None
    pat_name = ""
    age = ""
    gender = ""
    phone = ""
    ref_doc = ""

    if patient:
        pat_name = f"{patient.title or ''} {patient.patname or ''}".strip()
        age = f"{patient.age or ''} {patient.agetype or ''}".strip()
        gender = patient.gender or ""
        phone = patient.phone or ""
        if hasattr(patient, 'refdoctor') and patient.refdoctor:
            ref_doc = patient.refdoctor.docname or ""
    else:
        # Fallback to DoctorConsultation
        consult = DoctorConsultation.objects.filter(uhid=uhid).order_by('-id').first()
        if consult:
            pat_name = consult.patname or ""
            age = f"{consult.age or ''} {consult.agetype or ''}".strip()
            gender = consult.gender or ""
            phone = getattr(consult, 'phone', '') or ""
            ref_doc = getattr(consult, 'refdoctor', '') or ""

    if not patient and not consult:
        return JsonResponse({'success': False, 'message': 'Patient not found for the given UHID'})

    # Fetch procedure bills from TblServices
    services = TblServices.objects.filter(uhid=uhid, isactive='Y').order_by('-createddate')
    raw_bills = list(services.values_list('billno', flat=True).distinct())
    bills = [b for b in raw_bills if b is not None]

    # Select latest bill number if available
    selected_bill = bills[0] if bills else None
    sittings_list = []
    total_qty = 0

    if selected_bill:
        sittings_list, total_qty = fetch_sittings_for_bill(uhid, selected_bill)

    return JsonResponse({
        'success': True,
        'patient': {
            'uhid': uhid,
            'patname': pat_name,
            'age': age,
            'gender': gender,
            'phone': phone,
            'refdoctor': ref_doc,
        },
        'bills': bills,
        'selected_bill': selected_bill,
        'total_qty': total_qty,
        'sittings': sittings_list
    })


@login_required(login_url='login')
def get_sittings_procedures_by_bill(request):
    uhid = request.GET.get('uhid', '').strip()
    billno = request.GET.get('billno', '').strip()

    if not uhid or not billno:
        return JsonResponse({'success': False, 'message': 'UHID and Bill No are required'})

    sittings_list, total_qty = fetch_sittings_for_bill(uhid, billno)

    return JsonResponse({
        'success': True,
        'total_qty': total_qty,
        'sittings': sittings_list
    })


@login_required(login_url='login')
def save_sitting_entry(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

    uhid = request.POST.get('uhid', '').strip()
    billno = request.POST.get('billno', '').strip()
    sitting = request.POST.get('sitting', '').strip()
    sdate_str = request.POST.get('sdate', '').strip()
    remarks = request.POST.get('remarks', '').strip()
    next_sdate_str = request.POST.get('next_sitting_date', '').strip()

    if not uhid or not billno or not sitting:
        return JsonResponse({'success': False, 'message': 'UHID, Bill No, and Sitting identifier are required'})

    existing_obj = SittingsPage.objects.filter(uhid=uhid, billno=str(billno), sitting=sitting).first()

    sdate_val = None
    if sdate_str:
        try:
            sdate_val = datetime.strptime(sdate_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid date format'})
    elif existing_obj and existing_obj.sdate:
        sdate_val = existing_obj.sdate
    else:
        return JsonResponse({'success': False, 'message': f'Date is required for {sitting}'})

    next_sdate_val = None
    if next_sdate_str:
        try:
            next_sdate_val = datetime.strptime(next_sdate_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid next sitting date format'})

    defaults_dict = {
        'sdate': sdate_val,
        'remarks': remarks,
        'next_sitting_date': next_sdate_val,
        'created_by': request.user.username
    }

    # Save or update sitting entry in SittingsPage model
    sitting_obj, created = SittingsPage.objects.update_or_create(
        uhid=uhid,
        billno=str(billno),
        sitting=sitting,
        defaults=defaults_dict
    )

    action_text = "created" if created else "updated"
    return JsonResponse({
        'success': True,
        'message': f"{sitting} {action_text} successfully!"
    })


def fetch_sittings_for_bill(uhid, billno):
    """Helper function to calculate total quantity and fetch sittings list for a given bill."""
    proc_qs = TblServices.objects.filter(uhid=uhid, billno=billno, isactive='Y')
    total_qty = 0
    for p in proc_qs:
        total_qty += (p.qty or 1)

    if total_qty == 0:
        total_qty = 1  # Default at least 1 sitting if procedure exists

    # Fetch existing saved sittings from SittingsPage model
    saved_qs = SittingsPage.objects.filter(uhid=uhid, billno=str(billno))
    saved_map = {s.sitting: s for s in saved_qs}

    sittings_list = []
    for i in range(1, total_qty + 1):
        sitting_key = f"Sitting {i}"
        saved_obj = saved_map.get(sitting_key)

        sdate_str = ""
        remarks = ""
        next_sdate_str = ""
        is_saved = False

        if saved_obj:
            sdate_str = saved_obj.sdate.strftime("%Y-%m-%d") if saved_obj.sdate else ""
            remarks = saved_obj.remarks or ""
            if saved_obj.next_sitting_date:
                next_sdate_str = saved_obj.next_sitting_date.strftime("%Y-%m-%d")
            is_saved = True

        sittings_list.append({
            'sitting_no': i,
            'sitting': sitting_key,
            'sdate': sdate_str,
            'remarks': remarks,
            'next_sitting_date': next_sdate_str,
            'is_saved': is_saved
        })

    return sittings_list, total_qty


@login_required(login_url='login')
def sittings_receipt(request):
    uhid = request.GET.get('uhid', '').strip()
    billno = request.GET.get('billno', '').strip()

    if not uhid or not billno:
        return HttpResponse("Invalid request parameters: UHID and Bill No are required.", status=400)

    hospital = HospitalMaster.objects.filter(active='a').first() or HospitalMaster.objects.first()

    # Patient info
    patient_obj = OpPatientRegistration.objects.filter(uhid=uhid).first()
    pat_data = {}
    if patient_obj:
        pat_data = {
            'uhid': patient_obj.uhid,
            'patname': f"{patient_obj.title or ''} {patient_obj.patname or ''}".strip(),
            'age': f"{patient_obj.age or ''} {patient_obj.agetype or ''}".strip(),
            'gender': patient_obj.gender or "",
            'phone': patient_obj.phone or "",
        }
    else:
        consult = DoctorConsultation.objects.filter(uhid=uhid).order_by('-id').first()
        if consult:
            pat_data = {
                'uhid': consult.uhid,
                'patname': consult.patname or "",
                'age': f"{consult.age or ''} {consult.agetype or ''}".strip(),
                'gender': consult.gender or "",
                'phone': getattr(consult, 'phone', '') or "",
            }

    # Fetch procedure services for this bill to get service_name & doctor
    services = TblServices.objects.filter(uhid=uhid, billno=billno, isactive='Y')
    if not services.exists():
        services = TblServices.objects.filter(billno=billno)

    is_cancelled = TblOpCancellation.objects.filter(billno=billno).exists()
    bill = services.first()

    raw_service_ids = list(services.values_list('services', flat=True).distinct())

    resolved_names = []
    for s_val in raw_service_ids:
        if s_val:
            if str(s_val).isdigit():
                master_svc = ServiceTypeMaster.objects.filter(serviceid=int(s_val)).first()
                if master_svc and master_svc.servicename:
                    resolved_names.append(master_svc.servicename)
                else:
                    resolved_names.append(str(s_val))
            else:
                resolved_names.append(str(s_val))

    service_name = ", ".join(resolved_names) if resolved_names else "OP Procedure"

    doctor = ""
    if bill:
        if hasattr(bill, 'doc') and bill.doc and getattr(bill.doc, 'docname', None):
            doctor = bill.doc.docname
        elif bill.doctor:
            doctor = bill.doctor

    # ---------------- TOTAL & PAYMENT CALCULATIONS ----------------
    total = sum((x.amount or 0) for x in services)

    first_item = services.first()
    base_paid = float(first_item.paidamt or 0) if first_item else 0.0
    base_conc = float(first_item.concessionamt or 0) if first_item else 0.0

    # ---------------- OP PAYMENT LEDGER ----------------
    op = OpPayment.objects.filter(
        uhid=uhid,
        billno=billno,
        active="Y"
    ).aggregate(
        paid=Sum("patamt"),
        conc=Sum("concession")
    )

    paid = base_paid + float(op["paid"] or 0)
    concession = base_conc + float(op["conc"] or 0)

    due = total - (paid + concession)
    if due < 0:
        due = 0

    try:
        inwords = num2words(paid, to="cardinal").replace("-", " ").upper()
    except Exception:
        inwords = ""

    # Sittings recorded
    sittings = SittingsPage.objects.filter(uhid=uhid, billno=str(billno)).order_by('sno')

    context = {
        'hospital': hospital,
        'patient': pat_data,
        'billno': billno,
        'bill': bill,
        'service_name': service_name,
        'doctor': doctor,
        'sittings': sittings,
        'total': total,
        'paid': paid,
        'concession': concession,
        'due': due,
        'inwords': inwords,
        'is_cancelled': is_cancelled,
        'current_date': timezone.now(),
    }
    return render(request, 'hospApp/Admin/sittings_receipt.html', context)