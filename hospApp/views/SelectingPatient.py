from django.utils import timezone
from datetime import datetime, time
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField
from hospApp.utils import filter_by_date_range
from hospApp.models import DoctorConsultation


@login_required(login_url='login')
def SearchConsultationUHIDView1(request):

    today = timezone.localtime().date()

    from_date_str = request.GET.get("from_date", str(today))
    to_date_str   = request.GET.get("to_date",   str(today))

    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    except ValueError:
        from_date = today

    try:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    except ValueError:
        to_date = today

    name        = request.GET.get("name",        "").strip()
    phone       = request.GET.get("phone",       "").strip()
    uhid        = request.GET.get("uhid",        "").strip()
    search_type = request.GET.get("search_type", "")

    # ✅ Priority annotation (same for all queries)
    priority_annotation = Case(
        When(is_prescription_done=False, then=0),
        When(is_prescription_done=True,  then=1),
        output_field=IntegerField()
    )

    # ✅ Name or Phone → search whole table, no date filter
    if search_type == "name" and name:
        qs = DoctorConsultation.objects.filter(
            isactive='Y',
            patname__icontains=name
        ).annotate(priority=priority_annotation).order_by("priority", "tokenno")

    elif search_type == "phone" and phone:
        qs = DoctorConsultation.objects.filter(
            isactive='Y',
            phone__icontains=phone
        ).annotate(priority=priority_annotation).order_by("priority", "tokenno")

    elif search_type == "uhid" and uhid:
        qs = DoctorConsultation.objects.filter(
            isactive='Y',
            uhid__icontains=uhid
        ).annotate(priority=priority_annotation).order_by("priority", "tokenno")

    else:
        # ✅ Date range using IST-aware filter_by_date_range
        qs = filter_by_date_range(
            DoctorConsultation.objects.filter(isactive='Y'),
            'createddate', from_date, to_date
        ).annotate(priority=priority_annotation).order_by("priority", "tokenno")

    qs = qs[:300]

    return render(request, "hospApp/Admin/SearchConsultationUHID1.html", {
        "patients":    qs,
        "from_date":   from_date_str,
        "to_date":     to_date_str,
        "name":        name,
        "phone":       phone,
        "uhid":        uhid,
        "search_type": search_type,
    })


@login_required(login_url='login')
def CompletedConsultationsView(request):
    """
    Shows only completed (prescription done) consultations.
    Same filters as SearchConsultationUHIDView1 but restricted to is_prescription_done=True.
    """
    today = timezone.localtime().date()

    from_date_str = request.GET.get("from_date", str(today))
    to_date_str   = request.GET.get("to_date",   str(today))

    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    except ValueError:
        from_date = today

    try:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
    except ValueError:
        to_date = today

    name        = request.GET.get("name",        "").strip()
    phone       = request.GET.get("phone",       "").strip()
    uhid        = request.GET.get("uhid",        "").strip()
    search_type = request.GET.get("search_type", "")

    # Base queryset — only completed consultations
    base_qs = DoctorConsultation.objects.filter(isactive='Y', is_prescription_done=True)

    if search_type == "name" and name:
        qs = base_qs.filter(patname__icontains=name).order_by("tokenno")

    elif search_type == "phone" and phone:
        qs = base_qs.filter(phone__icontains=phone).order_by("tokenno")

    elif search_type == "uhid" and uhid:
        qs = base_qs.filter(uhid__icontains=uhid).order_by("tokenno")

    else:
        qs = filter_by_date_range(
            base_qs, 'createddate', from_date, to_date
        ).order_by("tokenno")

    qs = qs[:300]

    return render(request, "hospApp/Admin/CompletedConsultations.html", {
        "patients":    qs,
        "from_date":   from_date_str,
        "to_date":     to_date_str,
        "name":        name,
        "phone":       phone,
        "uhid":        uhid,
        "search_type": search_type,
    })