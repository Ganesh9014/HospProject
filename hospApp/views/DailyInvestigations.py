from django.shortcuts import render
from hospApp.models import tblInvestigationDetails
from hospApp.models import OpPatientRegistration ,HospitalMaster # adjust import path if different
from datetime import datetime, timedelta
from itertools import groupby
import pytz
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required   
@login_required(login_url='login')
def DailyInvestigations(request):
    return render(request, 'hospApp/reports/DailyInvestigations.html')

@login_required(login_url='login')
def DailyInvestigationsResult(request):
    from_date = request.GET.get('from_date')
    to_date   = request.GET.get('to_date')

    if from_date and to_date:
        start = datetime.strptime(from_date, "%Y-%m-%d")
        end = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)


    records = (
        tblInvestigationDetails.objects
        .filter(
            generateddate__gte=start,
            generateddate__lte=end,
            active='Y',
            ipno__isnull=True        # OP only
        )
        .exclude(invname__isnull=True)
        .exclude(invname='')
        .order_by('billno', 'ID_PK')
    )

    # ── Build UHID set from results, fetch all matching OP patients in ONE query ──
    uhid_list = list({r.uhid for r in records if r.uhid})
    pat_map   = {
        p.uhid: p
        for p in OpPatientRegistration.objects.filter(uhid__in=uhid_list)
    }
    inv_ids = list({r.invname for r in records if r.invname})
    from hospApp.models import InvestigationMaster

    inv_map = {
        str(inv.ino): inv.invname
        for inv in InvestigationMaster.objects.filter(ino__in=inv_ids)
    }
    # ── Group by bill number ──
    bills = []
    for billno, items in groupby(records, key=lambda x: x.billno):
        item_list = list(items)
        first     = item_list[0]

        # Get patient from OpPatientRegistration, fallback to tblInvestigationDetails
        pat       = pat_map.get(first.uhid)
        patname   = f"{pat.patname}".strip() if pat else (first.patname or '—')
        age       = f"{pat.age} {pat.agetype}"           if pat and pat.age else (f"{first.age} {first.agetype}" if first.age else '—')
        gender    = pat.gender   if pat else (first.gender  or '—')
        phone     = pat.phone    if pat else (str(first.phone) if first.phone else '—')

        # Investigation rows
        inv_rows   = []
        total_cost = 0
        for idx, inv in enumerate(item_list, start=1):
            inv_name = inv_map.get(str(inv.invname), '—')

            inv_rows.append({
                'sno': idx,
                'invname': inv_name,
                'qty': 1,
                'cost': inv.cost or 0,
                'id': inv.invname,
                'concesion':inv.concessionamt
            })
            total_cost += inv.cost or 0

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
            'paymode':    first.paymentmode   or '—',
            'concesion':  first.concessionamt ,
            'due':        first.due        or 0,
            'inv_rows':   inv_rows,
            'total_cost': total_cost,
        })
    hospital = HospitalMaster.objects.filter(active='a').first()
    context = {
        'logged_user': request.session.get("username"),
        'bills':       bills,
        'from_date':   datetime.strptime(from_date, '%Y-%m-%d').date(),
        'to_date':     datetime.strptime(to_date,   '%Y-%m-%d').date(),
        'grand_total': sum(b['total_cost'] for b in bills),
        'grand_total_paid': sum(b['paidamt'] for b in bills),
        'grand_total_concession': sum(b['concession'] for b in bills),
        'grand_total_due': sum(b['due'] for b in bills),    
        'total_bills': len(bills),
        'hospital': hospital,
        'print_time': timezone.now(),
    }
    return render(request, 'hospApp/reports/DailyInvestigationsResult.html', context)