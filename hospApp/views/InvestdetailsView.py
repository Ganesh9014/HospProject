from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from hospApp.models import NewInvMaster, DepartmentPhotoMaster
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def InvestdetailsView(request):
    departments = DepartmentPhotoMaster.objects.filter(active='Y').order_by('dno')

    if request.method == "POST":
        inv_id         = request.POST.get("inv_id")
        operation      = request.POST.get("operation")
        impression     = request.POST.get("impression")
        overall_method = request.POST.get("overall_method")
        department     = request.POST.get("department")

        if not inv_id:
            messages.error(request, "Please select Investigation")
            return redirect(request.path)

        # ── Resolve department name (no hardcoded IDs) ───────────
        dept_obj     = DepartmentPhotoMaster.objects.filter(dno=department).first()
        dept_name    = dept_obj.department.lower() if dept_obj else ""
        is_radiology = "radiology" in dept_name

        # ── RADIOLOGY ────────────────────────────────────────────
        if is_radiology:
            radiology_report = request.POST.get("radiology_report", "")

            if operation == "modify":
                NewInvMaster.objects.filter(invname=inv_id).delete()

            NewInvMaster.objects.create(
                invname    = inv_id,
                defaults   = radiology_report,
                impression = impression,
                header     = "",
                test       = "",
                submethod  = None,
                units      = "",
                normal     = "",
                method     = None,
            )

        # ── NORMAL departments ───────────────────────────────────
        else:
            headers    = request.POST.getlist("header[]")
            tests      = request.POST.getlist("test[]")
            submethods = request.POST.getlist("method[]")
            defaults   = request.POST.getlist("default[]")
            units      = request.POST.getlist("units[]")
            normals    = request.POST.getlist("normal_values[]")

            result_types      = request.POST.getlist("result_type[]")
            range_modes       = request.POST.getlist("range_mode[]")
            abnormal_values_l = request.POST.getlist("abnormal_values[]")

            # Common mode fields (male_low/high used as the single range)
            male_lows         = request.POST.getlist("male_low[]")
            male_highs        = request.POST.getlist("male_high[]")
            female_lows       = request.POST.getlist("female_low[]")
            female_highs      = request.POST.getlist("female_high[]")
            child_lows        = request.POST.getlist("child_low[]")
            child_highs       = request.POST.getlist("child_high[]")
            child_age_cutoffs = request.POST.getlist("child_age_cutoff[]")

            # Split mode fields (separate names to avoid collision)
            male_lows_split        = request.POST.getlist("male_low_split[]")
            male_highs_split       = request.POST.getlist("male_high_split[]")
            female_lows_split      = request.POST.getlist("female_low_split[]")
            female_highs_split     = request.POST.getlist("female_high_split[]")
            child_lows_split       = request.POST.getlist("child_low_split[]")
            child_highs_split      = request.POST.getlist("child_high_split[]")
            child_age_cutoffs_split = request.POST.getlist("child_age_cutoff_split[]")

            def to_float(val):
                try:
                    return float(val) if val not in (None, "") else None
                except (ValueError, TypeError):
                    return None

            if operation == "modify":
                NewInvMaster.objects.filter(invname=inv_id).delete()

            for i in range(len(tests)):
                if not tests[i].strip():
                    continue

                mode = range_modes[i] if i < len(range_modes) else "common"

                if mode == "split":
                    # Use dedicated split fields
                    ml = to_float(male_lows_split[i])        if i < len(male_lows_split)        else None
                    mh = to_float(male_highs_split[i])       if i < len(male_highs_split)       else None
                    fl = to_float(female_lows_split[i])      if i < len(female_lows_split)      else None
                    fh = to_float(female_highs_split[i])     if i < len(female_highs_split)     else None
                    cl = to_float(child_lows_split[i])       if i < len(child_lows_split)       else None
                    ch = to_float(child_highs_split[i])      if i < len(child_highs_split)      else None
                    ca = to_float(child_age_cutoffs_split[i]) if i < len(child_age_cutoffs_split) else None
                else:
                    # Common mode — copy male_low/high into all three groups
                    ml = to_float(male_lows[i])  if i < len(male_lows)  else None
                    mh = to_float(male_highs[i]) if i < len(male_highs) else None
                    # Copy the same range to female and child too
                    fl, fh = ml, mh
                    cl, ch = ml, mh
                    ca = 999  # effectively disable child age cutoff (all ages share range)

                NewInvMaster.objects.create(
                    invname          = inv_id,
                    header           = headers[i],
                    test             = tests[i],
                    submethod        = submethods[i] if submethods[i] else None,
                    defaults         = defaults[i],
                    units            = units[i],
                    normal           = normals[i],
                    impression       = impression,
                    method           = overall_method if overall_method else None,
                    result_type      = result_types[i] if i < len(result_types) else "numeric",
                    male_low         = ml,
                    male_high        = mh,
                    female_low       = fl,
                    female_high      = fh,
                    child_low        = cl,
                    child_high       = ch,
                    child_age_cutoff = ca,
                    abnormal_values  = abnormal_values_l[i] if i < len(abnormal_values_l) else None,
                )

        messages.success(
            request,
            "Investigation details updated successfully"
            if operation == "modify"
            else "Investigation details saved successfully"
        )

        return redirect(request.path)

    return render(
        request,
        "hospApp/Admin/Investdetails.html",
        {"departments": departments}
    )


# ── rest of views ────────────────────────────────────────────────────

from django.http import JsonResponse
from hospApp.models import NewInvMaster


@login_required(login_url='login')
@login_required(login_url='login')
def fetch_investigation_details(request):
    inv_id = request.GET.get("inv_id")

    try:
        inv_id = int(inv_id)
    except (ValueError, TypeError):
        return JsonResponse({"rows": []})

    rows = (
        NewInvMaster.objects
        .filter(invname=inv_id)
        .order_by("sno")
        .values("sno", "header", "test", "submethod",
                "method", "defaults", "units", "normal", "impression",
                "result_type", "male_low", "male_high",
                "female_low", "female_high",
                "child_low", "child_high", "child_age_cutoff",
                "abnormal_values")
    )
    return JsonResponse({"rows": list(rows)})

from django.views.decorators.http import require_POST


@login_required(login_url='login')
@require_POST
def delete_investigation_row(request):
    sno = request.POST.get("sno")
    if not sno:
        return JsonResponse({"status": "error", "message": "Invalid row"}, status=400)
    NewInvMaster.objects.filter(sno=sno).delete()
    return JsonResponse({"status": "success"})


from hospApp.models import InvestigationMaster, DepartmentPhotoMaster


@login_required(login_url='login')
def get_investigation_department(request):
    inv_id = request.GET.get("inv_id")
    try:
        inv  = InvestigationMaster.objects.get(ino=inv_id, active='Y')
        dept = DepartmentPhotoMaster.objects.get(department=inv.department)

        is_radiology = "radiology" in dept.department.lower()

        return JsonResponse({
            "department_id": dept.dno,
            "is_radiology":  is_radiology,
        })
    except (InvestigationMaster.DoesNotExist, DepartmentPhotoMaster.DoesNotExist) as e:
        print("DEBUG get_investigation_department EXCEPTION:", e)
        return JsonResponse({"department_id": None, "is_radiology": False})