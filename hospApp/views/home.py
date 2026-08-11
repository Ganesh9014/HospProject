from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Max
from datetime import datetime, timedelta

from hospApp.models import (
    Tbluserpermission,
    MainMenu,
    DoctorConsultation,
    Login,
    tblInvestigationDetails,
    TblServices,
    Prescription,
    Prescription3,
)



from django.db.models import Sum, Min
from django.utils import timezone
from datetime import datetime, timedelta
from hospApp.models import (
    DoctorConsultation,
    Login,
    tblInvestigationDetails,
    TblServices,
    OpPayment
)


@login_required(login_url='login')
def home(request):

    today = timezone.now().date()
    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = start + timedelta(days=1)

    # ✅ EXISTING COUNTS
    op_count = DoctorConsultation.objects.filter(
        regdt__gte=start,
        regdt__lt=end,
        opno__isnull=False
    ).count()

    login_count = Login.objects.filter(
        logintime__gte=start,
        logintime__lt=end
    ).count()

    # ================= TOTAL DUES =================
    total_due = 0

    # -------- INVESTIGATION --------
    invs = (
        tblInvestigationDetails.objects
        .filter(generateddate__gte=start, generateddate__lt=end, active='Y')
        .values('billno', 'uhid')
        .annotate(
            total=Sum('cost'),
            base_paid=Min('paidamt'),
            base_conc=Min('concessionamt')
        )
    )

    for i in invs:
        op = OpPayment.objects.filter(
            uhid=i['uhid'], billno=i['billno'], active='Y'
        ).aggregate(paid=Sum('patamt'), conc=Sum('concession'))

        paid = (i['base_paid'] or 0) + (op['paid'] or 0)
        conc = (i['base_conc'] or 0) + (op['conc'] or 0)
        due = (i['total'] or 0) - (paid + conc)

        if due > 0:
            total_due += due

    # -------- CONSULTATION --------
    cons = DoctorConsultation.objects.filter(
        regdt__gte=start, regdt__lt=end, isactive='Y'
    )

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
            total_due += due

    # -------- PROCEDURE --------
    procs = (
        TblServices.objects
        .filter(createddate__gte=start, createddate__lt=end, isactive='Y')
        .values('billno', 'uhid')
        .annotate(
            total=Sum('amount'),
            base_paid=Min('paidamt'),
            base_conc=Min('concessionamt')
        )
    )

    for p in procs:
        op = OpPayment.objects.filter(
            uhid=p['uhid'], billno=p['billno'], active='Y'
        ).aggregate(paid=Sum('patamt'), conc=Sum('concession'))

        paid = (p['base_paid'] or 0) + (op['paid'] or 0)
        conc = (p['base_conc'] or 0) + (op['conc'] or 0)
        due = (p['total'] or 0) - (paid + conc)

        if due > 0:
            total_due += due
    total_concession = get_today_concession_total()

    # ================= FINAL =================
    return render(request, 'hospApp/home.html', {
        'op_count': op_count,
        'login_count': login_count,
        'total_due': total_due,
        'total_concession': total_concession,
    })

@login_required(login_url='login')
def addDoc(request):
    return render(request, 'hospApp/empRegistration.html')





from datetime import datetime, timedelta
from django.utils import timezone
from hospApp.models import DoctorConsultation   , HospitalMaster

@login_required(login_url='login')
def op_report(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    hospital = HospitalMaster.objects.filter(active='a').first()

    if from_date and to_date:
        from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
    else:
        from_date = timezone.now().date()
        to_date = from_date

    start = timezone.make_aware(datetime.combine(from_date, datetime.min.time()))
    end = timezone.make_aware(datetime.combine(to_date, datetime.max.time()))

    patreg = OpPatientRegistration.objects.filter(
        entrytime__gte=start,
        entrytime__lte=end,
    ).order_by('entrytime')

    # ✅ Build a map of uhid -> latest casetype from DoctorConsultation
    uhids = list(patreg.values_list('uhid', flat=True))

    casetype_map = {
        c.uhid: c.casetypemaster.casetype
        for c in DoctorConsultation.objects.filter(
            uhid__in=uhids,
            casetypemaster__isnull=False,
            isactive='Y'
        ).select_related('casetypemaster').order_by('uhid', '-regdt')  # latest first
        if c.casetypemaster
    }
    # Note: dict comprehension keeps the last written value per uhid,
    # but since we ordered by -regdt, we need distinct. Use the approach below:

    # ✅ Better approach - get latest consultation per uhid
    from django.db.models import Max

    latest_consultations = (
        DoctorConsultation.objects
        .filter(uhid__in=uhids, casetypemaster__isnull=False, isactive='Y')
        .select_related('casetypemaster')
        .order_by('uhid', '-regdt')  # latest first per uhid
    )

    casetype_map = {}
    for c in latest_consultations:
        if c.uhid not in casetype_map:  # keep only latest per uhid
            casetype_map[c.uhid] = c.casetypemaster.casetype if c.casetypemaster else ""

    # ================= BUILD DATA =================
    data = []
    for c in patreg:
        data.append({
            "uhid":     c.uhid,
            "regdt":    c.entrytime,
            "patname":  c.patname if c else "",
            "age":      c.age if c else "",
            "gender":   c.gender if c else "",
            "mobile":   c.phone if c else "",
            "pro":      c.pro.pro_name if c and c.pro else "",
            "refdoc":   c.refdoctor.docname if c and c.refdoctor else "",
            'address':  c.address if c else '',
            'fname':    c.fname if c else '',
            "casetype": casetype_map.get(c.uhid, "-"),  # ✅ fetched from DoctorConsultation
        })

    return render(request, 'hospApp/admin/op_report.html', {
        'data': data,
        'from_date': from_date,
        'to_date': to_date,
        'hospital': hospital,
        'username': request.session.get("username"),
        "print_time": timezone.now(),
    })
@login_required(login_url='login')
def login_reports(request):
    today = timezone.now().date()

    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = start + timedelta(days=1)

    data = Login.objects.filter(
        logintime__gte=start,
        logintime__lt=end
    ).order_by('logintime')

    return render(request, 'hospApp/admin/login_reports.html', {
        'data': data,
        'today': today
    })


@login_required(login_url='login')
def Investigation_details(request):
    today = timezone.now().date()

    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = start + timedelta(days=1)

    data = tblInvestigationDetails.objects.filter(
        generateddate__gte=start,
        generateddate__lt=end,
        active='Y'
    ).values(
        'billno',
        'uhid',
        'patname',
        'phone'
    ).annotate(
        total_cost=Sum('cost'),
        due=Max('due'),
        paidamt=Max('paidamt'),
        concessionamt=Max('concessionamt'),
        latest_date=Max('generateddate')
    ).order_by('-latest_date')

    return render(request, 'hospApp/admin/Investigation_details_home.html', {
        'data': data,
        'today': today
    })

@login_required(login_url='login')
def procedure_details(request):
    today = timezone.now().date()

    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = start + timedelta(days=1)

    data = TblServices.objects.filter(
        createddate__gte=start,
        createddate__lt=end,
        isactive='Y'
    ).values(
        'billno',
        'uhid'
    ).annotate(
        total_cost=Sum('amount'),
        due=Max('due'),
        paidamt=Max('paidamt'),
        concessionamt=Max('concessionamt'),
        latest_date=Max('createddate')
    ).order_by('-latest_date')

    return render(request, 'hospApp/admin/procedure_details_home.html', {
        'data': data,
        'today': today
    })



from django.db.models import Sum, Min
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from hospApp.models import tblInvestigationDetails, OpPayment


from django.utils import timezone
from datetime import datetime, timedelta

@login_required(login_url='login')
def investigation_dues_report(request):

    today = timezone.now().date()

    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = start + timedelta(days=1)

    data = []

    invs = (
        tblInvestigationDetails.objects
        .filter(
            generateddate__gte=start,
            generateddate__lt=end,
            active='Y'
        )
        .values('billno', 'uhid', 'patname', 'phone')
        .annotate(
            total=Sum('cost'),
            base_paid=Min('paidamt'),
            base_conc=Min('concessionamt'),
            created=Min('generateddate')
        )
    )

    for i in invs:
        op = OpPayment.objects.filter(
            uhid=i['uhid'],
            billno=i['billno'],
            active='Y'
        ).aggregate(
            paid=Sum('patamt'),
            conc=Sum('concession')
        )

        final_paid = (i['base_paid'] or 0) + (op['paid'] or 0)
        final_conc = (i['base_conc'] or 0) + (op['conc'] or 0)

        final_due = (i['total'] or 0) - (final_paid + final_conc)

        if final_due > 0:
            data.append({
                'uhid': i['uhid'],
                'patname': i['patname'],
                'phone': i['phone'],
                'billno': i['billno'],
                'total': i['total'],
                'paid': final_paid,
                'due': final_due,
                'date': i['created']
            })

    return render(request, 'hospApp/reports/investigation_dues.html', {
        'data': data,
        'today': today
    })


from django.db.models import Sum, Min
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta

from hospApp.models import (
    tblInvestigationDetails,
    DoctorConsultation,
    TblServices,
    OpPayment
)

from hospApp.models import OpPatientRegistration
@login_required(login_url='login')
def all_dues_today(request):

    today = timezone.now().date()
    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = start + timedelta(days=1)

    investigation = []
    consultation = []
    procedure = []

    total_due_inv = 0
    total_due_cons = 0
    total_due_proc = 0

    # ---------------- INVESTIGATION ----------------
    invs = (
        tblInvestigationDetails.objects
        .filter(generateddate__gte=start, generateddate__lt=end, active='Y')
        .values('billno', 'uhid', 'patname', 'concreason','createdby')
        .annotate(
            total=Sum('cost'),
            base_paid=Min('paidamt'),
            base_conc=Min('concessionamt'),
            created=Min('generateddate')
        )
    )

    for i in invs:
        op = OpPayment.objects.filter(
            uhid=i['uhid'], billno=i['billno'], active='Y'
        ).aggregate(paid=Sum('patamt'), conc=Sum('concession'))

        paid = (i['base_paid'] or 0) + (op['paid'] or 0)
        conc = (i['base_conc'] or 0) + (op['conc'] or 0)
        due = (i['total'] or 0) - (paid + conc)

        if due > 0:
            total_due_inv += due
            investigation.append({
                'patname': i['patname'],
                'uhid': i['uhid'],
                'billno': i['billno'],
                'total': i['total'],
                'paid': paid,
                'due': due,
                'reason': i['concreason'],
                'user': i['createdby'],
                'date': i['created']
            })

    # ---------------- CONSULTATION ----------------
    cons = DoctorConsultation.objects.filter(
        regdt__gte=start, regdt__lt=end, isactive='Y'
    )

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
            consultation.append({
                'patname': c.patname,
                'uhid': c.uhid,
                'billno': c.billno,
                'total': total,
                'paid': paid,
                'due': due,
                'user': c.userid,    
                'reason': getattr(c, 'concreason', ''),
                'date': c.createddate
            })

    # ---------------- PROCEDURE ----------------
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
    uhids = [p['uhid'] for p in procs]
    patients = OpPatientRegistration.objects.filter(uhid__in=uhids)

    patient_map = {
        p.uhid: f"{p.patname}"
        for p in patients
    }
    for p in procs:
        op = OpPayment.objects.filter(
            uhid=p['uhid'], billno=p['billno'], active='Y'
        ).aggregate(paid=Sum('patamt'), conc=Sum('concession'))

        paid = (p['base_paid'] or 0) + (op['paid'] or 0)
        conc = (p['base_conc'] or 0) + (op['conc'] or 0)
        due = (p['total'] or 0) - (paid + conc)

        if due > 0:
            total_due_proc += due

            procedure.append({
                'patname': patient_map.get(p['uhid'], ''),  # 🔥 HERE
                'uhid': p['uhid'],
                'billno': p['billno'],
                'total': p['total'],    
                'paid': paid,
                'due': due,
                'reason': p['concreason'],
                'user': p['createdby'], 
                'date': p['created']
            })

    return render(request, 'hospApp/reports/investigation_dues.html', {
        'investigation': investigation,
        'consultation': consultation,
        'procedure': procedure,
        'total_due_inv': total_due_inv,
        'total_due_cons': total_due_cons,
        'total_due_proc': total_due_proc,
        'today': today
    })




from django.db.models import Sum, Min
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta

from hospApp.models import (
    tblInvestigationDetails,
    DoctorConsultation,
    TblServices,
    OpPayment,
    OpPatientRegistration
)


from django.db.models import Sum, Min
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta

from hospApp.models import (
    tblInvestigationDetails,
    DoctorConsultation,
    TblServices,
    OpPayment,
    OpPatientRegistration
)


@login_required(login_url='login')
def all_concessions_today(request):

    today = timezone.now().date()
    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = start + timedelta(days=1)

    investigation = []
    consultation = []
    procedure = []

    total_inv = 0
    total_cons = 0
    total_proc = 0

    # ================= INVESTIGATION =================
    invs = (
        tblInvestigationDetails.objects
        .filter(generateddate__gte=start, generateddate__lt=end, active='Y')
        .values('billno', 'uhid', 'patname', 'concreason','createdby')
        .annotate(
            total=Sum('cost'),
            base_paid=Min('paidamt'),
            base_conc=Min('concessionamt'),
            created=Min('generateddate')
        )
    )

    for i in invs:
        op = OpPayment.objects.filter(
            uhid=i['uhid'], billno=i['billno'], active='Y'
        ).aggregate(
            paid=Sum('patamt'),
            conc=Sum('concession')
        )

        paid = (i['base_paid'] or 0) + (op['paid'] or 0)
        final_conc = (i['base_conc'] or 0) + (op['conc'] or 0)

        if final_conc > 0:
            total_inv += final_conc

            investigation.append({
                'patname': i['patname'],
                'uhid': i['uhid'],
                'billno': i['billno'],
                'total': i['total'],
                'paid': paid,
                'user': i['createdby'],
                'concession': final_conc,
                'reason': i['concreason'],
                'date': i['created']
            })

    # ================= CONSULTATION =================
    cons = DoctorConsultation.objects.filter(
        regdt__gte=start, regdt__lt=end, isactive='Y'
    )

    for c in cons:
        total = c.consulfee or 0
        op = OpPayment.objects.filter(
            uhid=c.uhid, billno=c.billno, active='Y'
        ).aggregate(
            paid=Sum('patamt'),
            conc=Sum('concession')
        )

        paid = (c.paidamt or 0) + (op['paid'] or 0)
        final_conc = (c.concession or 0) + (op['conc'] or 0)

        if final_conc > 0:
            total_cons += final_conc

            consultation.append({
                'patname': c.patname,
                'uhid': c.uhid,
                'billno': c.billno,
                'paid': paid,
                'concession': final_conc,
                'reason': getattr(c, 'concreason', ''),
                'total': total,
                'user': c.userid,
                'date': c.createddate
            })

    # ================= PROCEDURE =================
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

    # 🔥 patient mapping (UHID → name)
    uhids = [p['uhid'] for p in procs]
    patients = OpPatientRegistration.objects.filter(uhid__in=uhids)

    patient_map = {
        p.uhid: f"{p.patname}"
        for p in patients
    }

    for p in procs:
        op = OpPayment.objects.filter(
            uhid=p['uhid'], billno=p['billno'], active='Y'
        ).aggregate(
            paid=Sum('patamt'),
            conc=Sum('concession')
        )

        paid = (p['base_paid'] or 0) + (op['paid'] or 0)
        final_conc = (p['base_conc'] or 0) + (op['conc'] or 0)

        if final_conc > 0:
            total_proc += final_conc

            procedure.append({
                'patname': patient_map.get(p['uhid'], ''),
                'uhid': p['uhid'],
                'billno': p['billno'],
                'paid': paid,
                'concession': final_conc,
                'reason': p['concreason'],
                'total': p['total'],
                'user': p['createdby'], 
                'date': p['created']
            })

    # ================= FINAL =================
    return render(request, 'hospApp/reports/concession_report.html', {
        'investigation': investigation,
        'consultation': consultation,
        'procedure': procedure,
        'total_inv': total_inv,
        'total_cons': total_cons,
        'total_proc': total_proc,
        'today': today
    })


from django.contrib.auth.decorators import login_required


def get_today_concession_total():
    today = timezone.now().date()
    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = start + timedelta(days=1)

    total = 0

    # Investigation
    invs = tblInvestigationDetails.objects.filter(
        generateddate__gte=start, generateddate__lt=end, active='Y'
    ).values('billno', 'uhid').annotate(
        base_conc=Min('concessionamt')
    )

    for i in invs:
        op = OpPayment.objects.filter(
            uhid=i['uhid'], billno=i['billno'], active='Y'
        ).aggregate(conc=Sum('concession'))

        total += (i['base_conc'] or 0) + (op['conc'] or 0)

    # Consultation
    cons = DoctorConsultation.objects.filter(
        regdt__gte=start, regdt__lt=end, isactive='Y'
    )

    for c in cons:
        op = OpPayment.objects.filter(
            uhid=c.uhid, billno=c.billno, active='Y'
        ).aggregate(conc=Sum('concession'))

        total += (c.concession or 0) + (op['conc'] or 0)

    # Procedure
    procs = TblServices.objects.filter(
        createddate__gte=start, createddate__lt=end, isactive='Y'
    ).values('billno', 'uhid').annotate(
        base_conc=Min('concessionamt')
    )

    for p in procs:
        op = OpPayment.objects.filter(
            uhid=p['uhid'], billno=p['billno'], active='Y'
        ).aggregate(conc=Sum('concession'))

        total += (p['base_conc'] or 0) + (op['conc'] or 0)

    return total