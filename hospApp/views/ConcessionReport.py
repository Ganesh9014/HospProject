

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from hospApp.models import Tbluserpermission
@login_required(login_url='login')
def ConcessionReport(request):
    users = Tbluserpermission.objects.filter(isactive=True).order_by('username')
    return render(request, 'hospApp/reports/ConcessionReport.html', {"users": users})

from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Min
from django.contrib.auth.decorators import login_required
from hospApp.models import tblInvestigationDetails, OpPayment, DoctorConsultation, TblServices, OpPatientRegistration,HospitalMaster
from datetime import datetime
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Min
from django.contrib.auth.decorators import login_required
from hospApp.models import (
    tblInvestigationDetails, OpPayment, DoctorConsultation,
    TblServices, OpPatientRegistration, HospitalMaster
)



def parse_date(value):
    if "T" in value:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    else:
        return datetime.strptime(value, "%Y-%m-%d")


@login_required(login_url='login')
def concession_report(request):

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    username = request.GET.get("username")
    services = request.GET.getlist("services[]")

    if not from_date or not to_date:
        return render(request, "hospApp/reports/concessionreport.html")

    fd = parse_date(from_date)
    td = parse_date(to_date)

    start = timezone.make_aware(fd)
    end = timezone.make_aware(td + timedelta(days=1))

    investigation = []
    consultation = []
    procedure = []
    payments = []

    total_inv = 0
    total_cons = 0
    total_proc = 0
    total_pay = 0

    # ================= COMMON PATIENT MAP =================
    all_uhids = set()

    # ================= INVESTIGATION =================
    if not services or "OP Investigations" in services:

        invs = (
            tblInvestigationDetails.objects
            .filter(generateddate__gte=start, generateddate__lt=end, active='Y')
            .values('billno', 'uhid', 'concreason', 'createdby')
            .annotate(
                total=Sum('cost'),
                base_paid=Min('paidamt'),
                base_conc=Min('concessionamt'),
                created=Min('generateddate')
            )
        )

        if username and username != "ALL":
            invs = invs.filter(createdby=username)

        invs = list(invs)
        all_uhids.update(i['uhid'] for i in invs)

        for i in invs:
            final_conc = i['base_conc'] or 0
            paid = i['base_paid'] or 0

            if final_conc > 0:
                investigation.append(i)

    # ================= CONSULTATION =================
    if not services or "OP Consultation" in services:

        cons = DoctorConsultation.objects.filter(
            regdt__gte=start, regdt__lt=end, isactive='Y'
        )

        if username and username != "ALL":
            cons = cons.filter(userid=username)

        cons = list(cons)
        all_uhids.update(c.uhid for c in cons)

        for c in cons:
            if (c.concession or 0) > 0:
                consultation.append(c)

    # ================= PROCEDURE =================
    if not services or "OP Procedures" in services:

        procs = (
            TblServices.objects
            .filter(createddate__gte=start, createddate__lt=end, isactive='Y')
            .values('billno', 'uhid', 'concreason', 'createdby')
            .annotate(
                total=Sum('amount'),
                base_paid=Min('paidamt'),
                base_conc=Min('concessionamt'),
                created=Min('createddate')
            )
        )

        if username and username != "ALL":
            procs = procs.filter(createdby=username)

        procs = list(procs)
        all_uhids.update(p['uhid'] for p in procs)

        for p in procs:
            if (p['base_conc'] or 0) > 0:
                procedure.append(p)

    # ================= PAYMENTS =================
    if not services or "OP Payments" in services:

        pays = (
            OpPayment.objects
            .filter(billdate__gte=start, billdate__lt=end, active='Y')
            .values('billno', 'uhid', 'userid','concreason','updatedby','invbillno')
            .annotate(
                total=Sum('totalamt'),
                paid=Sum('patamt'),
                conc=Sum('concession'),
                created=Min('billdate')
            )
        )

        if username and username != "ALL":
            pays = pays.filter(updatedby=username)
        
        pays = list(pays)
        all_uhids.update(p['uhid'] for p in pays)

        for p in pays:
            if (p['conc'] or 0) > 0:
                payments.append(p)

    # ================= FETCH PATIENT MAP =================
    patients = OpPatientRegistration.objects.filter(uhid__in=all_uhids)
    patient_map = {p.uhid: p for p in patients}

    # ================= FINAL BUILD =================

    # INVESTIGATION
    final_investigation = []
    for i in investigation:
        final_conc = i['base_conc'] or 0
        paid = i['base_paid'] or 0
        total_inv += final_conc

        p = patient_map.get(i['uhid'])

        final_investigation.append({
            'patname': p.patname if p else "",
            'uhid': i['uhid'],
            'billno': i['billno'],
            'total': i['total'],
            'paid': paid,
            'user': i['createdby'],
            'concession': final_conc,
            'reason': i['concreason'],
            'date': i['created'],


        })

    # CONSULTATION
    final_consultation = []
    for c in consultation:
        final_conc = c.concession or 0
        paid = c.paidamt or 0
        total_cons += final_conc

        p = patient_map.get(c.uhid)

        final_consultation.append({
            'patname': p.patname if p else "",
            'uhid': c.uhid,
            'billno': c.billno,
            'paid': paid,
            'concession': final_conc,
            'reason': getattr(c, 'concreason', ''),
            'total': c.consulfee,
            'user': c.userid,
            'date': c.createddate
        })

    # PROCEDURE
    final_procedure = []
    for p in procedure:
        final_conc = p['base_conc'] or 0
        paid = p['base_paid'] or 0
        total_proc += final_conc

        pat = patient_map.get(p['uhid'])

        final_procedure.append({
            'patname': pat.patname if pat else "",
            'uhid': p['uhid'],
            'billno': p['billno'],
            'paid': paid,
            'concession': final_conc,
            'reason': p['concreason'],
            'total': p['total'],
            'user': p['createdby'],
            'date': p['created']
        })

    # PAYMENTS
    final_payments = []
    for p in payments:
        
        final_conc = p['conc'] or 0
        total_pay += final_conc

        pat = patient_map.get(p['uhid'])

        final_payments.append({
            'patname': pat.patname if pat else "",
            'uhid': p['uhid'],
            'billno': p['billno'],
            'total': p['total'] or 0,
            'paid': p['paid'] or 0,
            'concession': final_conc,
            'reason': p['concreason'],
            'user': p['userid'],
            'date': p['created'],
            'username': p['updatedby'],
            'invbillno': p['invbillno']
            
        })

    # ================= TOTAL =================
    grand_total = total_inv + total_cons + total_proc + total_pay

    hospital = HospitalMaster.objects.filter(active='a').first()
    
    return render(request, "hospApp/reports/concession_result.html", {
        "investigation": final_investigation,
        "consultation": final_consultation,
        "procedure": final_procedure,
        "payments": final_payments,
        "total_inv": total_inv,
        "total_cons": total_cons,
        "total_proc": total_proc,
        "total_pay": total_pay,
        "grand_total": grand_total,
        "from_date": fd,
        "to_date": td,
        "print_time": timezone.now(),
        "hospital": hospital,
        "user":request.GET.get("username")
    })