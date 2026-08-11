from django.shortcuts import render
from hospApp.models import TblServices, OpPatientRegistration, HospitalMaster, ServiceTypeMaster
from django.utils import timezone
from datetime import datetime, timedelta
from itertools import groupby
from django.contrib.auth.decorators import login_required   
@login_required(login_url='login')
def DailyProcedures(request):
    return render(request, 'hospApp/reports/DailyProcedures.html')

@login_required(login_url='login')
def DailyProceduresResult(request):
    from_date = request.GET.get('from_date')
    to_date   = request.GET.get('to_date')

    if from_date and to_date:
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end   = datetime.strptime(to_date,   "%Y-%m-%d") + timedelta(days=1)

    records = (
        TblServices.objects
        .filter(
            generateddate__gte=start,
            generateddate__lt=end,
            isactive='Y',
            ipno__isnull=True
        )
        .exclude(services__isnull=True)
        .exclude(services='')
        .order_by('billno', 'id')
    )

    # ── Patient map ──
    uhid_list = list({r.uhid for r in records if r.uhid})
    pat_map   = {
        p.uhid: p
        for p in OpPatientRegistration.objects.filter(uhid__in=uhid_list)
    }

    # ── Service name map  { str(serviceid): servicename } ──
    svc_ids = list({r.services for r in records if r.services})
    svc_map = {
        str(s.serviceid): s.servicename or '—'
        for s in ServiceTypeMaster.objects.filter(serviceid__in=svc_ids)
    }

    # ── Group by bill number ──
    bills = []
    for billno, items in groupby(records, key=lambda x: x.billno):
        item_list = list(items)
        first     = item_list[0]

        pat     = pat_map.get(first.uhid)
        patname = f"{pat.patname}".strip() if pat else '—'
        age     = f"{pat.age} {pat.agetype}" if pat and pat.age else '—'
        gender  = pat.gender if pat else '—'
        phone   = pat.phone  if pat else '—'

        proc_rows  = []
        total_cost = 0

        for idx, svc in enumerate(item_list, start=1):
            qty      = svc.qty or 1
            cost     = svc.amount or 0
            svc_name = svc_map.get(str(svc.services), '—')   # name lookup

            proc_rows.append({
                'sno':       idx,
                'procedure': svc_name,
                'type':      svc.services_typename or '—',
                'qty':       qty,
                'cost':      cost,
                'total':     cost * qty,
                'doctor':    svc.doctor or '—',
                'id':        svc.services
            })
            total_cost += cost * qty

        bills.append({
            'billno':     billno,
            'uhid':       first.uhid,
            'patname':    patname,
            'age':        age,
            'gender':     gender,
            'phone':      phone,
            'billedby':   first.createdby    or '—',
            'billedtime': first.generateddate,
            'paidamt':    first.paidamt       or 0,
            'concession': first.concessionamt or 0,
            'due':        first.due        or 0,
            'paymode':    first.paymentmode   or '—',
            'proc_rows':  proc_rows,
            'total_cost': total_cost,
        })

    hospital = HospitalMaster.objects.filter(active='a').first()

    context = {
        'logged_user':      request.session.get("username"),
        'bills':            bills,
        'from_date':        datetime.strptime(from_date, '%Y-%m-%d').date(),
        'to_date':          datetime.strptime(to_date,   '%Y-%m-%d').date(),
        'grand_total':      sum(b['total_cost'] for b in bills),
        'grand_total_paid': sum(b['paidamt']    for b in bills),
        'grand_total_due':  sum(b['due']        for b in bills),
        'grand_total_concession': sum(b['concession'] for b in bills),
        'total_bills':      len(bills),
        'hospital':         hospital,
        'print_time':       timezone.now(),
    }
    return render(request, 'hospApp/reports/DailyProceduresResult.html', context)