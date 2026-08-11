from django.shortcuts import render
from hospApp.models import Tbluserpermission
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def DueReports(request):
    users = Tbluserpermission.objects.filter(isactive=True).order_by('username')
    return render(request, 'hospApp/reports/DueReports.html',{"users": users})


from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Min
from django.shortcuts import render
from hospApp.models import tblInvestigationDetails, DoctorConsultation, TblServices, OpPayment, OpPatientRegistration, HospitalMaster

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Min
from django.shortcuts import render
from hospApp.models import (
    tblInvestigationDetails, DoctorConsultation,
    TblServices, OpPayment, OpPatientRegistration, HospitalMaster
)


@login_required(login_url='login')
def all_dues_filtered(request):

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    username = request.GET.get('username')

    if not from_date or not to_date:
        today = timezone.now().date()
        from_date = to_date = today

    start = timezone.make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
    end = timezone.make_aware(datetime.strptime(to_date, "%Y-%m-%d")) + timedelta(days=1)

    investigation = []
    consultation = []
    procedure = []

    total_due_inv = 0
    total_due_cons = 0
    total_due_proc = 0

    # ================= COLLECT ALL UHIDS =================
    all_uhids = set()

    # ================= INVESTIGATION =================
    invs = (
        tblInvestigationDetails.objects
        .filter(generateddate__gte=start, generateddate__lt=end, active='Y')
    )

    if username:
        invs = invs.filter(createdby=username)

    invs = list(
        invs.values('billno','uhid','concreason','createdby')
        .annotate(
            total=Sum('cost'),
            base_paid=Min('paidamt'),
            base_conc=Min('concessionamt'),
            created=Min('generateddate')
        )
    )

    all_uhids.update(i['uhid'] for i in invs)

    # ================= CONSULTATION =================
    cons = DoctorConsultation.objects.filter(
        regdt__gte=start, regdt__lt=end, isactive='Y'
    )

    if username:
        cons = cons.filter(userid=username)

    cons = list(cons)
    all_uhids.update(c.uhid for c in cons)

    # ================= PROCEDURE =================
    procs = TblServices.objects.filter(
        createddate__gte=start, createddate__lt=end, isactive='Y'
    )

    if username:
        procs = procs.filter(createdby=username)

    procs = list(
        procs.values('billno','uhid','concreason','createdby')
        .annotate(
            total=Sum('amount'),
            base_paid=Min('paidamt'),
            base_conc=Min('concessionamt'),
            created=Min('createddate')
        )
    )

    all_uhids.update(p['uhid'] for p in procs)

    # ================= PATIENT MAP =================
    patients = OpPatientRegistration.objects.filter(uhid__in=all_uhids)
    patient_map = {p.uhid: p for p in patients}

    # ================= PROCESS INVESTIGATION =================
    for i in invs:
        op = OpPayment.objects.filter(
            uhid=i['uhid'], billno=i['billno'], active='Y'
        ).aggregate(paid=Sum('patamt'), conc=Sum('concession'))

        paid = (i['base_paid'] or 0) + (op['paid'] or 0)
        conc = (i['base_conc'] or 0) + (op['conc'] or 0)
        due = (i['total'] or 0) - (paid + conc)

        if due > 0:
            total_due_inv += due
            pat = patient_map.get(i['uhid'])

            investigation.append({
                **i,
                'patname': pat.patname if pat else "",
                'paid': paid,
                'due': due,
                "generateddate": i['created'],
            })

    # ================= PROCESS CONSULTATION =================
    for c in cons:
        total = c.consulfee or 0
        base_paid = c.paidamt or 0
        base_conc = c.concession or 0

        op = OpPayment.objects.filter(
            uhid=c.uhid, billno=c.billno, active='Y'
        ).aggregate(paid=Sum('patamt'), conc=Sum('concession'))

        paid = base_paid + (op['paid'] or 0)
        conc = base_conc + (op['conc'] or 0)
        due = total - (paid + conc)

        if due > 0:
            total_due_cons += due
            pat = patient_map.get(c.uhid)

            consultation.append({
                'patname': pat.patname if pat else "",
                'uhid': c.uhid,
                'billno': c.billno,
                'total': total,
                'paid': paid,
                'due': due,
                'user': c.userid,
                'reason': getattr(c, 'concreason', ''),
                'date': c.createddate,
                'concreason': getattr(c, 'concreason', '')
            })

    # ================= PROCESS PROCEDURE =================
    for p in procs:
        op = OpPayment.objects.filter(
            uhid=p['uhid'], billno=p['billno'], active='Y'
        ).aggregate(paid=Sum('patamt'), conc=Sum('concession'))

        paid = (p['base_paid'] or 0) + (op['paid'] or 0)
        conc = (p['base_conc'] or 0) + (op['conc'] or 0)
        due = (p['total'] or 0) - (paid + conc)

        if due > 0:
            total_due_proc += due
            pat = patient_map.get(p['uhid'])

            procedure.append({
                'patname': pat.patname if pat else "",
                **p,
                'paid': paid,
                'due': due,
                "createddate": p['created'],
                'concreason': p['concreason'],
                'user': p['createdby']
            })

    hospital = HospitalMaster.objects.filter(active='a').first()

    grand_total = total_due_inv + total_due_cons + total_due_proc
   

    return render(request, 'hospApp/reports/DueReportResult.html', {
        'investigation': investigation,
        'consultation': consultation,
        'procedure': procedure,
        'total_due_inv': total_due_inv,
        'total_due_cons': total_due_cons,
        'total_due_proc': total_due_proc,
        "from_date": datetime.strptime(from_date, "%Y-%m-%d"),
        "to_date": datetime.strptime(to_date, "%Y-%m-%d"),
        'username': username,
        'grand_total': grand_total,
        'hospital': hospital,
        'logged_user': request.session.get("username"),
        'print_time': timezone.now(),
    })