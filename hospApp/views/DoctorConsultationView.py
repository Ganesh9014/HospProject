from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Max
from django.contrib.auth.decorators import login_required
from django.db import transaction
import logging
from django.urls import reverse
from django.utils.timezone import localdate

from barcode import Code128
from barcode.writer import ImageWriter

from io import BytesIO
import base64
from datetime import datetime, time
from django.utils import timezone
from django.db.models import Max

from hospApp.models import (
    OpPatientRegistration,
    CaseTypeMaster,
    ProMaster,
    DoctorMaster,
    RefDoctorMaster,
    BankMaster,
    
    Tbluserpermission,BillMaster,HospitalMaster
)

from hospApp.models.DoctorConsultation import DoctorConsultation

logger = logging.getLogger(__name__)



def safe_int(val, default=0):
    try:
        # handle strings like "10.0"
        return int(float(val))
    except (TypeError, ValueError):
        return default

# -------------------------------------------------------------------------
# DOCTOR CONSULTATION MAIN PAGE
# -------------------------------------------------------------------------
@login_required(login_url='login')

def DoctorConsultationView(request):

    case_types = CaseTypeMaster.objects.filter(active='Y').order_by('casetype')
    pro_list = ProMaster.objects.filter(active='Y').order_by('pro_name')
    doctor_list = DoctorMaster.objects.filter(active='Y').order_by('docname')
    payee_list = BankMaster.objects.filter(active='Y').order_by('name')

    # ----------------------------
    # RESTORE SAVED FORM DATA (if usercode was wrong)
    # ----------------------------
    saved_data = request.session.pop('consult_form_data', None)
    show_invalid = request.session.pop('consult_invalid_usercode', False)

    context = {
        'case_types': case_types,
        'pro_list': pro_list,
        'doctor_list': doctor_list,
        'payee_list': payee_list,
        'show_invalid_usercode': show_invalid,
    }

    # If saved POST exists → repopulate
    if saved_data:
        context.update(saved_data)

    # =====================================================
    #                        POST
    # =====================================================
    if request.method == 'POST':

        uhid             = request.POST.get('uhid', '').strip()
        doctor_id        = request.POST.get('doctor')
        case_type_id     = request.POST.get('casetype')
        pro_id           = request.POST.get('proid', '').strip()

        fee              = safe_int(request.POST.get('fee',        '0').strip(), 0)
        concession       = safe_int(request.POST.get('concession', '0').strip(), 0)
        dueamt           = safe_int(request.POST.get('due',        '0').strip(), 0)

        # ── SPLIT PAYMENT ────────────────────────────────────────────────────
        cash_amt         = safe_int(request.POST.get('cash_amt',        '0').strip(), 0)
        online_amt       = safe_int(request.POST.get('online_amt',      '0').strip(), 0)
        online_mode      = request.POST.get('online_mode',    '').strip()   # UPI / Card / Cheque / NEFT
        online_details   = request.POST.get('online_details', '').strip()   # UPI no / card name / etc.

        paidamt          = cash_amt + online_amt                             # total paid
        # ─────────────────────────────────────────────────────────────────────

        paymenttype      = request.POST.get('paymenttype', 'Cash').strip()  # kept for backward compat
        visit_type       = request.POST.get('visittype', 'Normal').strip()
        concreason       = request.POST.get('concreason', '').strip()
        usercode         = request.POST.get('usercode', '').strip()
        consultation_type = request.POST.get("consultation_type", "Normal").strip()

        # ── DETERMINE paymenttype label ──────────────────────────────────────
        if cash_amt > 0 and online_amt > 0:
            paymenttype = f"Split (Cash + {online_mode})" if online_mode else "Split"
        elif online_amt > 0 and online_mode:
            paymenttype = online_mode
        else:
            paymenttype = "Cash"
        # ─────────────────────────────────────────────────────────────────────

        # ---------------- PASSWORD VALIDATION --------------------------------
        logged_user = request.session.get("username")
        user = Tbluserpermission.objects.filter(username=logged_user, isactive=True).first()

        if not user or usercode != user.password:
            return JsonResponse({
                "success": False,
                "error_type": "invalid_usercode",
                "message": "Invalid username or password"
            })

        # ---------------------------------------------------------------------
        # VALIDATIONS
        # ---------------------------------------------------------------------
        if not uhid:
            context['error'] = "UHID is required."
            return render(request, 'hospApp/Admin/DoctorConsultation.html', context)

        if not doctor_id:
            context['error'] = "Doctor is required."
            return render(request, 'hospApp/Admin/DoctorConsultation.html', context)

        if not case_type_id:
            context['error'] = "Case type is required."
            return render(request, 'hospApp/Admin/DoctorConsultation.html', context)

        # ── SPLIT PAYMENT VALIDATION ──────────────────────────────────────────
        # cash + online must not exceed (fee - concession)
        max_payable = fee - concession
        if max_payable < 0:
            max_payable = 0

        if paidamt > max_payable:
            return JsonResponse({
                "success": False,
                "error_type": "payment_error",
                "message": f"Total paid amount (₹{paidamt}) cannot exceed Fee − Discount (₹{max_payable})."
            })

        if online_amt > 0 and not online_mode:
            return JsonResponse({
                "success": False,
                "error_type": "payment_error",
                "message": "Please select an online payment mode (UPI / Card / Cheque / NEFT)."
            })
        # ─────────────────────────────────────────────────────────────────────

        # CASE TYPE
        try:
            case_type_obj = CaseTypeMaster.objects.get(sno=case_type_id, active='Y')
        except:
            context['error'] = "Invalid case type."
            return render(request, 'hospApp/Admin/DoctorConsultation.html', context)

        # PRO
        pro_obj = None
        if pro_id:
            pro_obj = ProMaster.objects.filter(proid=pro_id, active='Y').first()

        # DOCTOR
        try:
            doctor = DoctorMaster.objects.get(docid=doctor_id, active='Y')
        except:
            context['error'] = "Invalid doctor."
            return render(request, 'hospApp/Admin/DoctorConsultation.html', context)

        # PATIENT
        try:
            patient = OpPatientRegistration.objects.get(uhid=uhid)
        except OpPatientRegistration.DoesNotExist:
            context['error'] = "Patient not found."
            return render(request, 'hospApp/Admin/DoctorConsultation.html', context)

        # ---------------- FEE CALCULATION ------------------------------------
        consult_fee = int(fee or 0)
        last_consult = None

        if visit_type.lower() == "revisit":
            last_consult = DoctorConsultation.objects.filter(
                uhid=uhid, doctor=doctor, isactive='Y',
                casetypemaster=case_type_obj
            ).order_by('-createddate').first()

            revisittime = doctor.revisittime or 0
            if last_consult and revisittime > 0:
                days_since = (timezone.now() - last_consult.createddate).days
                if days_since <= revisittime:
                    consult_fee = 0

        calculated_due = consult_fee - paidamt - concession
        if calculated_due < 0:
            calculated_due = 0

        # TOKEN & OP NUMBER
        now   = timezone.now()
        today = now.date()
        start_dt = timezone.make_aware(datetime.combine(today, time.min))
        end_dt   = timezone.make_aware(datetime.combine(today, time.max))

        last_token = DoctorConsultation.objects.filter(
            regdt__range=(start_dt, end_dt), isactive='Y'
        ).aggregate(Max('tokenno'))['tokenno__max']
        token_no = (last_token or 0) + 1

        daily_count = DoctorConsultation.objects.filter(
            regdt__range=(start_dt, end_dt), isactive='Y'
        ).count() + 1
        op_no = f"P{today.year}{daily_count:04d}"

        # ---------------- SAVE -----------------------------------------------
        try:
            with transaction.atomic():
                bill = BillMaster.objects.create(
                    bill_type='CONSULTATION',
                    uhid=patient.uhid,
                    created_by=request.user.username
                )

                consult = DoctorConsultation.objects.create(
                    patid=patient.patid,
                    uhid=patient.uhid,
                    patname=patient.patname,
                    age=patient.age,
                    agetype=patient.agetype,
                    gender=patient.gender,
                    gardian=patient.fname,
                    address=patient.address,
                    phone=patient.phone,
                    opno=op_no,
                    tokenno=token_no,

                    casetypemaster=case_type_obj,
                    visittype=visit_type,
                    refdoctor=patient.refdoctor,
                    promaster=pro_obj,

                    # ── payment ──────────────────────────────────
                    paymenttype=paymenttype,      # e.g. "Split (Cash + UPI)"
                    paymode=paymenttype,
                    cardname=online_details,      # reuse existing field for detail

                    cash_amt=cash_amt,            # 🆕 cash portion
                    online_amt=online_amt,        # 🆕 online portion
                    online_mode=online_mode,      # 🆕 UPI / Card / etc.
                    online_details=online_details, # 🆕 UPI no. / card name / etc.
                    # ─────────────────────────────────────────────

                    doctor=doctor,
                    consulfee=consult_fee,
                    regdt=now,
                    paidamt=paidamt,              # total = cash + online
                    concession=concession,
                    due=calculated_due,

                    userid=request.user.username,
                    createddate=now,
                    concreason=concreason,
                    isactive='Y',
                    billno=bill.billno,
                    consulttype=consultation_type,

                    is_revisit=visit_type.lower() == "revisit",
                    previous_consult=last_consult if (visit_type.lower() == "revisit" and last_consult) else None,
                )

        except Exception as ex:
            logger.exception("Error saving consultation: %s", ex)
            context['error'] = "Could not save consultation. Try again."
            return render(request, 'hospApp/Admin/DoctorConsultation.html', context)

        return JsonResponse({
            "success": True,
            "redirect_url": reverse('consultation-print-select', args=[consult.pk])
        })


    # =====================================================
    #                        GET
    # =====================================================
    return render(request, 'hospApp/Admin/DoctorConsultation.html', context)
from hospApp.models import TblOpCancellation
# -------------------------------------------------------------------------
# PRINT SELECTION
# -------------------------------------------------------------------------
@login_required(login_url='login')
def consultation_print_select(request, pk):
    consult = get_object_or_404(DoctorConsultation, pk=pk,)
    doctor = consult.doctor
    is_cancelled = TblOpCancellation.objects.filter(billno=consult.billno).exists()

    if request.method == 'POST':
        ptype = request.POST.get('print_type', 'receipt')
        if ptype == 'receipt':
            return redirect('consultation-receipt', pk=consult.pk)
        elif ptype == 'prescription':
            return redirect('consultation-prescription', pk=consult.pk)

    return render(request, 'hospApp/Admin/consultation_print_select.html', {
        'consult': consult,
        'doctorname': doctor,
        'is_cancelled': is_cancelled    
    })

from datetime import timedelta

# -------------------------------------------------------------------------
# PRESCRIPTION PRINT
# -------------------------------------------------------------------------
@login_required(login_url='login')
def consultation_prescription(request, pk):
    hospital = HospitalMaster.objects.filter(active='a').first()
    consult = get_object_or_404(DoctorConsultation, pk=pk,)
    is_cancelled = TblOpCancellation.objects.filter(billno=consult.billno).exists()

    doctor = consult.doctor
    speciality = doctor.speciality

    # ✅ Fetch patient details using UHID from consult
    patient = get_object_or_404(OpPatientRegistration, uhid=consult.uhid)

    # -------- Generate UHID Barcode ----------
    uhid_value = str(consult.uhid)
    buffer_uhid = BytesIO()
    uhid_barcode = Code128(uhid_value, writer=ImageWriter())
    uhid_barcode.write(buffer_uhid, {
        "write_text": False,
        "module_height": 5,
        "font_size": 0,
        'module_width': 0.3,
        'dpi': 300
    })
    uhid_barcode_base64 = base64.b64encode(buffer_uhid.getvalue()).decode("utf-8")

    # -------- Generate BILL NO Barcode ----------
    bill_value = str(consult.billno)
    buffer_bill = BytesIO()
    bill_barcode = Code128(bill_value, writer=ImageWriter())
    bill_barcode.write(buffer_bill, {
        "write_text": False,
        "module_height": 5,
        "font_size": 0,
        'module_width': 0.3,
        'dpi': 300
    })
    bill_barcode_base64 = base64.b64encode(buffer_bill.getvalue()).decode("utf-8")
    valid_upto = consult.regdt + timedelta(days=7)
    return render(request, 'hospApp/Admin/consultation_prescription.html', {
        'consult': consult,
        'hospital': hospital,
        'user_print': request.user.username,
        'doctorname': doctor,
        'speciality': speciality,
        'barcode_uhid': uhid_barcode_base64,
        'barcode_billno': bill_barcode_base64,
        'patient': patient,   # ✅ patient object passed to template
        'valid_upto': valid_upto, 
        'is_cancelled': is_cancelled
    })


# -------------------------------------------------------------------------
# RECEIPT PRINT
# -------------------------------------------------------------------------

from django.db.models import Sum
from hospApp.models import OpPayment
from num2words import num2words

@login_required(login_url='login')
def consultation_receipt(request, pk):
    consult = get_object_or_404(DoctorConsultation, pk=pk,)
    is_cancelled = TblOpCancellation.objects.filter(billno=consult.billno).exists()


    hospital = HospitalMaster.objects.filter(active='a').first()
    doctor = consult.doctor
    speciality = doctor.speciality

    # ---------------- SOURCE (BASE) ----------------
    total = consult.consulfee or 0
    base_paid = consult.paidamt or 0
    base_conc = consult.concession or 0

    # ---------------- OP PAYMENT (LEDGER) ----------------
    op = OpPayment.objects.filter(
        uhid=consult.uhid,
        billno=consult.billno,
        active="Y"
    ).aggregate(
        paid=Sum("patamt"),
        conc=Sum("concession")
    )

    paid = base_paid + (op["paid"] or 0)
    concession = base_conc + (op["conc"] or 0)

    due = total - (paid + concession)
    if due < 0:
        due = 0

    inwords = num2words(paid, to='cardinal').replace('-', ' ').title()

    # -------- Generate UHID Barcode ----------
    uhid_value = str(consult.uhid)
    buffer_uhid = BytesIO()
    uhid_barcode = Code128(uhid_value, writer=ImageWriter())
    uhid_barcode.write(buffer_uhid, {
        "write_text": False,
        "module_height": 5,
        "module_width": 0.2,
        "dpi": 600
    })
    uhid_barcode_base64 = base64.b64encode(buffer_uhid.getvalue()).decode("utf-8")

    # -------- Generate BILL NO Barcode ----------
    bill_value = str(consult.billno)
    buffer_bill = BytesIO()
    bill_barcode = Code128(bill_value, writer=ImageWriter())
    bill_barcode.write(buffer_bill, {
        "write_text": False,
        "module_height": 5,
        "module_width": 0.2,
        "dpi": 600
    })
    bill_barcode_base64 = base64.b64encode(buffer_bill.getvalue()).decode("utf-8")

    return render(request, 'hospApp/Admin/consultation_receipt.html', {
        'consult': consult,
        'doctorname': doctor,
        'speciality': speciality,
        'hospital': hospital,

        # 🔥 LEDGER VALUES
        'total': total,
        'paid': paid,
        'concession': concession,
        'due': due,
        'inwords': inwords,

        'barcode_uhid': uhid_barcode_base64,
        'barcode_billno': bill_barcode_base64,
        'is_cancelled': is_cancelled, 
    })

# -------------------------------------------------------------------------
# AJAX: GET PATIENT DETAILS
# -------------------------------------------------------------------------
@login_required(login_url='login')
def get_patient_details(request):
    uhid = request.GET.get('uhid')

    if not uhid:
        return JsonResponse({'success': False, 'error': 'UHID not provided'}, status=400)

    try:
        patient = OpPatientRegistration.objects.get(uhid=uhid)
    except OpPatientRegistration.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No patient found with this UHID'}, status=404)
    except Exception as ex:
        logger.exception("Error fetching patient details: %s", ex)
        return JsonResponse({'success': False, 'error': 'Unexpected error'}, status=500)

    last_consult = DoctorConsultation.objects.filter(
        uhid=uhid,
        createddate__isnull=False,isactive='Y'
    ).order_by('-createddate').first()
 
    visit_type = "Normal"
    if last_consult:
        revisittime = last_consult.doctor.revisittime or 0
        days = (timezone.now() - last_consult.createddate).days

        if revisittime > 0 and days <= revisittime:
            visit_type = "Revisit"
        else:
            visit_type = "Review"

    refdoctor_obj = patient.refdoctor
    refdoctor_name = refdoctor_obj.docname if refdoctor_obj else ""
    pro = None
    pro_name = ""
    pro_id = ""

    try:
        pro = ProMaster.objects.get(proid=patient.pro_id, active='Y')
        pro_name = pro.pro_name
        pro_id = pro.proid
    except:
        pass

    data = {
        'patname': patient.patname,
        'age': patient.age,
        'agetype': patient.agetype,
        'gender': patient.gender,
        'fname': patient.fname,
        'phone': patient.phone,
        'refdoctor': refdoctor_name,
        'visit_type': visit_type,
        'patid': patient.patid,
        'pro_name': pro_name,
        'pro_id': pro_id,
        'opno': last_consult.opno if last_consult else ""
    }

    return JsonResponse({'success': True, 'data': data})


# -------------------------------------------------------------------------
# AJAX: DOCTOR SEARCH
# -------------------------------------------------------------------------
@login_required(login_url='login')
def search_doctors(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        doctors = DoctorMaster.objects.filter(
            Q(docname__icontains=query),
            active='Y'
        ).order_by('docname')[:10]

        for d in doctors:

            display_name = d.docname

            if d.speciality:
                display_name += f" ({d.speciality.speciality})"

            results.append({
                'name': display_name,
                'doctor_name': d.docname,   # 🔥 actual doctor name
                'consultfee': d.consultfee or 0,
                'id': d.docid,
                'emrfee': d.emrfee or 0
            })

    return JsonResponse({'results': results})


# -------------------------------------------------------------------------
# AJAX: CHECK REVISIT FEE
# -------------------------------------------------------------------------
@login_required(login_url='login')
def check_revisit_fee(request):
    uhid = request.GET.get('uhid', '').strip()
    doctor_id = request.GET.get('doctor', '').strip()
    case_type_id = request.GET.get('casetype', '').strip()

    if not uhid or not doctor_id or not case_type_id:
        return JsonResponse({'zero_fee': False})

    try:
        case_type_obj = CaseTypeMaster.objects.get(sno=case_type_id)
    except CaseTypeMaster.DoesNotExist:
        return JsonResponse({'zero_fee': False})
    except Exception as ex:
        logger.exception("Error in check_revisit_fee lookup: %s", ex)
        return JsonResponse({'zero_fee': False})

    last_consult = DoctorConsultation.objects.filter(
        uhid=uhid,
        doctor_id=doctor_id,
        casetypemaster=case_type_obj,
        createddate__isnull=False,isactive='Y'  
    ).order_by('-createddate').first()

    if last_consult:
        doctor = last_consult.doctor
        revisittime = doctor.revisittime or 0

        if revisittime > 0:
            days_since = (timezone.now() - last_consult.createddate).days
            if days_since <= revisittime:
                return JsonResponse({'zero_fee': True})

    return JsonResponse({'zero_fee': False})
