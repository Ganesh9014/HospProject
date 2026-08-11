from hospApp.models import Tbluserpermission
from hospApp.models.menus import MainMenu


def menus_processor(request):
    """
    Inject role-based sidebar menus into all templates
    """

    # Not logged in → no menus
    if not request.user.is_authenticated:
        return {'menus': []}

    # Get user's role
    perm = (
        Tbluserpermission.objects
        .filter(username=request.user.username, isactive=True)
        .select_related('mainrole')
        .first()
    )

    role = perm.mainrole if perm else None
    menus = []

    if role:
        for menu in MainMenu.objects.prefetch_related('sublinks').order_by('display_order'):
            allowed = menu.sublinks.filter(roles=role).order_by('display_order')

            # Always attach filtered sublinks
            menu.sublinks_filtered = allowed

            if allowed.exists():
                menus.append(menu)

    return {'menus': menus}
from hospApp.models import Tbluserpermission


from hospApp.models import Tbluserpermission
from hospApp.models.menus import SubMenu


def header_links_processor(request):
    if not request.user.is_authenticated:
        return {'header_links': []}

    perm = (
        Tbluserpermission.objects
        .filter(username=request.user.username, isactive=True)
        .select_related('mainrole')
        .prefetch_related('mainrole__header_pages')
        .first()
    )

    if not perm or not perm.mainrole:
        return {'header_links': []}

    role = perm.mainrole
    header_links = role.header_pages.all().order_by('display_order')

    return {'header_links': header_links}


from django.utils import timezone
from datetime import timedelta
from hospApp.models import Prescription, Prescription3, OpPatientRegistration, SittingsPage, DoctorConsultation


def revisit_alerts_processor(request):
    if not request.user.is_authenticated:
        return {'revisit_alerts': [], 'sitting_alerts': []}

    today = timezone.now().date()
    notify_from = today
    notify_to = today + timedelta(days=2)

    written_alerts = list(
        Prescription.objects
        .filter(next_visit_date__range=(notify_from, notify_to))
        .values('uhid', 'consult__uhid', 'patient_name', 'next_visit_date')
        .order_by('next_visit_date')
    )

    audio_alerts = list(
        Prescription3.objects
        .filter(next_visit_date__range=(notify_from, notify_to))
        .values('consult__uhid', 'patient_name', 'next_visit_date')
        .order_by('next_visit_date')
    )

    # Collect all UHIDs
    all_uhids = set()
    for item in written_alerts:
        u = item.get('uhid') or item.get('consult__uhid')
        if u:
            item['resolved_uhid'] = u
            all_uhids.add(u)

    for item in audio_alerts:
        u = item.get('consult__uhid')
        if u:
            item['resolved_uhid'] = u
            all_uhids.add(u)

    # Map UHID -> latest patient name from OpPatientRegistration
    patient_map = {}
    if all_uhids:
        patient_map = dict(
            OpPatientRegistration.objects
            .filter(uhid__in=all_uhids)
            .values_list('uhid', 'patname')
        )

    seen = set()
    revisit_alerts = []
    for item in sorted(written_alerts + audio_alerts, key=lambda x: x['next_visit_date']):
        uhid = item.get('resolved_uhid')
        pat_name = patient_map.get(uhid) or item.get('patient_name') or ""

        key = (pat_name.upper(), item['next_visit_date'])
        if key not in seen:
            seen.add(key)
            days_left = (item['next_visit_date'] - today).days
            revisit_alerts.append({
                'patient_name': pat_name,
                'next_visit_date': item['next_visit_date'],
                'days_left': days_left,
                'badge': 'today' if days_left == 0 else ('tomorrow' if days_left == 1 else 'in2days')
            })

    # ================= SITTING ALERTS =================
    raw_sitting_objs = list(
        SittingsPage.objects
        .filter(next_sitting_date__range=(notify_from, notify_to))
        .order_by('next_sitting_date')
    )

    sitting_uhids = set(s.uhid for s in raw_sitting_objs if s.uhid)
    sitting_pat_map = {}
    if sitting_uhids:
        for p in OpPatientRegistration.objects.filter(uhid__in=sitting_uhids):
            sitting_pat_map[p.uhid] = f"{p.title or ''} {p.patname or ''}".strip()

    sitting_alerts = []
    seen_sittings = set()
    for s in raw_sitting_objs:
        pat_name = sitting_pat_map.get(s.uhid, "")
        if not pat_name:
            consult = DoctorConsultation.objects.filter(uhid=s.uhid).order_by('-id').first()
            if consult:
                pat_name = consult.patname or ""

        days_left = (s.next_sitting_date - today).days
        key = (s.uhid, s.billno, s.sitting, s.next_sitting_date)
        if key not in seen_sittings:
            seen_sittings.add(key)
            sitting_alerts.append({
                'patient_name': pat_name or "Patient",
                'uhid': s.uhid,
                'billno': s.billno,
                'sitting': s.sitting or "Sitting",
                'next_sitting_date': s.next_sitting_date,
                'days_left': days_left,
                'badge': 'today' if days_left == 0 else ('tomorrow' if days_left == 1 else 'in2days')
            })

    return {
        'revisit_alerts': revisit_alerts,
        'sitting_alerts': sitting_alerts
    }


