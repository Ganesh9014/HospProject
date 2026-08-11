from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from hospApp.forms import OpPatientRegistrationForm
from hospApp.models import (
    OpPatientRegistration,
    RefDoctorMaster,
    HospitalMaster,
    Tbluserpermission
)
from hospApp.models.Address import State, District, City
from hospApp.models.ProMaster import ProMaster


@login_required(login_url='login')
def OpPatientRegistrationView(request):
    india_time = timezone.localtime(timezone.now())
    india_time = timezone.localtime(timezone.now())
    formatted_time = india_time
    if request.method == 'POST':
        form = OpPatientRegistrationForm(request.POST)
        if form.is_valid():

            # ⭐ GET USER CODE (this is actually password input)
            entered_pass = form.cleaned_data.get("userid", "").strip()

            # ⭐ VALIDATE LOGIN PASSWORD
            logged_user = request.session.get("username")
            user = Tbluserpermission.objects.filter(username=logged_user, isactive=True).first()
            
            # If password incorrect → preserve user's form data in session,
            # set a one-time flag to show alert on next GET and redirect (PRG).
            if not user or entered_pass != user.password:
                # store POST values so the form can be repopulated once on the redirected GET
                request.session['opreg_form_data'] = request.POST.dict()
                request.session['opreg_show_invalid_usercode'] = True
                # Do NOT add a messages.error here for this case (we use the one-time session flag).
                return redirect('OpPatientRegistration')

            # ⭐ PASSWORD IS CORRECT → Continue saving
            obj = form.save(commit=False)

            # -------------------------------
            #  STATE / DISTRICT / CITY (store names)
            # -------------------------------
            state_id = request.POST.get('state')
            district_id = request.POST.get('district')
            city_id = request.POST.get('city')

            if state_id:
                s = State.objects.filter(id=state_id).first()
                if s:
                    obj.state = s.statename

            if district_id:
                d = District.objects.filter(id=district_id).first()
                if d:
                    obj.district = d.districtname

            if city_id:
                c = City.objects.filter(id=city_id).first()
                if c:
                    obj.city = c.cityname

            # -------------------------------
            #  SAVE PRO AS ID
            # -------------------------------
            pro_id = request.POST.get('pro_id', '').strip()
            pro_name = request.POST.get('pro_name', '').strip()

            if pro_id:
                pro_obj = ProMaster.objects.filter(proid=pro_id, active='Y').first()
                obj.pro = pro_obj
            else:
                if pro_name.upper() == "SELF":
                    pro_obj = ProMaster.objects.filter(
                        pro_name__iexact="SELF", active='Y'
                    ).first()
                    obj.pro = pro_obj
                else:
                    obj.pro = None

            # -------------------------------
            #  SAVE REF DOCTOR AS ID
            # -------------------------------
            refname = request.POST.get('refdoctor', '').strip()

            if refname:
                if refname.upper() == "SELF":
                    ref = RefDoctorMaster.objects.filter(
                        docname__iexact="SELF",
                        active='Y'
                    ).first()
                    obj.refdoctor = ref
                else:
                    ref = RefDoctorMaster.objects.filter(
                        docname__iexact=refname,
                        active='Y'
                    ).first()

                    if not ref:
                        ref = RefDoctorMaster.objects.create(
                            docname=refname,
                            active='Y',
                            createdtime=timezone.now(),
                        )

                    obj.refdoctor = ref
            else:
                obj.refdoctor = None

            # -------------------------------
            #  UHID GENERATION
            # -------------------------------
            if not obj.uhid:
                hospital = HospitalMaster.objects.filter(active='a').first()
                hospital_initial = hospital.initial if hospital else "HSP"
                year = timezone.now().year
                prefix = f"{hospital_initial}{year}"

                last_record = (
                    OpPatientRegistration.objects
                    .filter(uhid__startswith=prefix)
                    .order_by('-uhid')
                    .first()
                )

                if last_record:
                    try:
                        last_num = int(last_record.uhid.replace(prefix, ''))
                    except ValueError:
                        last_num = 0
                    next_num = last_num + 1
                else:
                    next_num = 1

                obj.uhid = f"{prefix}{next_num:04d}"

            # -------------------------------
            #  SAVE RECORD
            # -------------------------------
            obj.save()

            messages.success(request, "Registration saved successfully!")
            return redirect('OpPatientRegistration')

        else:
            print("FORM ERRORS:", form.errors)
            # We intentionally render with the invalid form so user sees field-level errors and
            # their inputs remain. This is the one case that will still be a POST-render and may
            # prompt form re-submission on browser refresh. If you want to avoid that too, we can
            # implement PRG for invalid-form and restore errors from session. Let me know.

    else:
        # -------------------------------
        #  PRE-GENERATE UHID FOR GET REQUEST
        # -------------------------------
        hospital = HospitalMaster.objects.filter(active='a').first()
        hospital_initial = hospital.initial if hospital else "HSP"
        year = india_time.year
        prefix = f"{hospital_initial}{year}"

        last = (
            OpPatientRegistration.objects
            .filter(uhid__startswith=prefix)
            .order_by('-uhid')
            .first()
        )

        if last:
            try:
                num = int(last.uhid.replace(prefix, ""))
            except ValueError:
                num = 0
            next_num = num + 1
        else:
            next_num = 1

        next_uhid = f"{prefix}{next_num:04d}"

        # If we have saved POST data from a previous invalid-password POST,
        # repopulate the form once and show one-time alert.
        saved_data = request.session.pop('opreg_form_data', None)
        show_invalid = request.session.pop('opreg_show_invalid_usercode', False)

        if saved_data:
            # Use saved_data as initial so all user's inputs are shown after the alert.
            # Note: saved_data is a plain dict from QueryDict.dict() — adequate for typical fields.
            form = OpPatientRegistrationForm(initial=saved_data)
        else:
            form = OpPatientRegistrationForm(initial={
                'uhid': next_uhid,
                'entrydate': formatted_time,
                'pro': None,
                'refdoctor': None,
            })

    states = State.objects.all().order_by('statename')

    context = {
        'form': form,
        'states': states,
        'entry_display': formatted_time,
        # include the one-time flag for the template to show an alert
        'show_invalid_usercode_alert': locals().get('show_invalid', False),
    }

    response = render(request, 'hospApp/Admin/OpPatientRegistration.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# -------------------------- AJAX HELPERS --------------------------

@login_required(login_url='login')
@csrf_exempt
def load_districts(request):
    state_id = request.GET.get('state_id')
    districts = District.objects.filter(state_id=state_id).order_by('districtname')
    return JsonResponse(list(districts.values('id', 'districtname')), safe=False)


@login_required(login_url='login')
@csrf_exempt
def load_cities(request):
    district_id = request.GET.get('district_id')
    cities = City.objects.filter(district_id=district_id)

    if not cities.exists():
        district = District.objects.filter(id=district_id).first()
        if district:
            return JsonResponse([{
                'id': 0,
                'cityname': district.districtname
            }], safe=False)

    return JsonResponse(list(cities.values('id', 'cityname')), safe=False)



@login_required(login_url='login')
@csrf_exempt
def suggest_pros(request):
    query = request.GET.get('term', '').strip()

    if query:
        results = list(
            ProMaster.objects.filter(
                pro_name__icontains=query,
                active='Y'
            ).values('proid', 'pro_name')[:10]
        )
    else:
        results = []

    return JsonResponse(results, safe=False)


@login_required(login_url='login')
@csrf_exempt
def suggest_refdoctors(request):
    query = request.GET.get('term', '').strip()
    results = []

    if query:
        docs = RefDoctorMaster.objects.filter(
            docname__icontains=query,
            active='Y'
        ).values_list('docname', flat=True)[:10]
        results = list(docs)

    return JsonResponse(results, safe=False)


@login_required(login_url='login')
@csrf_exempt
def add_refdoctor_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'msg': 'Only POST allowed'}, status=405)

    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()

    if not name:
        return JsonResponse({'status': 'error', 'msg': 'Doctor name required'}, status=400)

    if not phone.isdigit() or len(phone) != 10:
        return JsonResponse({'status': 'error', 'msg': 'Invalid phone number'}, status=400)

    # exact match (same name & same phone)
    existing = RefDoctorMaster.objects.filter(
        docname__iexact=name,
        phoneno=phone,
        active='Y'
    ).first()

    if existing:
        return JsonResponse({
            'status': 'success',
            'created': False,
            'docname': existing.docname
        })

    # name exists with different phone
    mismatch = RefDoctorMaster.objects.filter(
        docname__iexact=name
    ).exclude(phoneno=phone).first()

    if mismatch:
        return JsonResponse({
            'status': 'error',
            'msg': f"Doctor already exists with another number ({mismatch.phoneno})"
        }, status=400)

    # create new doctor
    newdoc = RefDoctorMaster.objects.create(
        docname=name,
        phoneno=phone,
        active='Y',
        createdtime=timezone.now(),
    )

    return JsonResponse({
        'status': 'success',
        'created': True,
        'docid': newdoc.docid, 
        'docname': newdoc.docname,
        'msg': 'Doctor added successfully'
    })
