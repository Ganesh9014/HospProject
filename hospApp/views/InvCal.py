from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncDate
from hospApp.models import tblInvestigationDetails, InvestigationMaster
import calendar
from datetime import date, timedelta


def InvCal(request):
    return render(request, 'hospApp/reports/InvCalReport.html')


from django.shortcuts import render
from django.db.models import Count, Func, F
from django.db.models.fields import DateField
from hospApp.models import tblInvestigationDetails, InvestigationMaster
import calendar
from datetime import date, timedelta, datetime
import pytz



from django.shortcuts import render
from django.db.models import Count, Func
from django.db.models.fields import DateField
from hospApp.models import tblInvestigationDetails, InvestigationMaster,HospitalMaster
from datetime import date, timedelta, datetime
import calendar
import pytz
from django.utils import timezone   

def InvCal(request):
    return render(request, 'hospApp/reports/InvCalReport.html')


def InvCalResult(request):
    from_date_str = request.GET.get('from_date')  # YYYY-MM-DD
    to_date_str   = request.GET.get('to_date')    # YYYY-MM-DD

    # ── Parse exact selected dates ────────────────────────────────────
    start_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    end_date   = datetime.strptime(to_date_str,   '%Y-%m-%d').date()

    # ── Expand calendar range to full months ──────────────────────────
    # Calendar starts from day-1 of the start_date's month
    cal_start = date(start_date.year, start_date.month, 1)
    # Calendar ends on last day of the end_date's month
    last_day_of_end_month = calendar.monthrange(end_date.year, end_date.month)[1]
    cal_end = date(end_date.year, end_date.month, last_day_of_end_month)

    # ── IST-aware datetimes for DB filter (only selected range) ───────
    ist      = pytz.timezone('Asia/Kolkata')
    start_dt = ist.localize(datetime(start_date.year, start_date.month, start_date.day,  0,  0,  0))
    end_dt   = ist.localize(datetime(end_date.year,   end_date.month,   end_date.day,   23, 59, 59))

    # ── Full calendar date list (all days of spanned months) ──────────
    all_dates = []
    cur = cal_start
    while cur <= cal_end:
        all_dates.append(cur)
        cur += timedelta(days=1)

    # ── Investigation master map ───────────────────────────────────────
    inv_master = {
        str(obj.ino): obj.invname
        for obj in InvestigationMaster.objects.all()
    }

    # ── UTC→IST conversion inside SQL Server ─────────────────────────
    class ConvertTzDate(Func):
        function = 'CAST'
        template = "CAST(%(expressions)s AT TIME ZONE 'UTC' AT TIME ZONE 'India Standard Time' AS DATE)"
        output_field = DateField()

    # ── Query ONLY selected date range data ───────────────────────────
    qs = (
        tblInvestigationDetails.objects
        .filter(
            generateddate__gte=start_dt,
            generateddate__lte=end_dt,
            active='Y'
        )
        .exclude(invname__isnull=True)
        .exclude(invname='')
        .annotate(test_date=ConvertTzDate('generateddate'))
        .values('invname', 'test_date')
        .annotate(cnt=Count('ID_PK'))
        .order_by('invname', 'test_date')
    )

    # ── Build raw dict: { inv_label: { date: count } } ────────────────
    # Only dates within selected range get actual counts
    raw = {}
    for row in qs:
        inv_id    = str(row['invname'] or '').strip()
        inv_label = inv_master.get(inv_id, f"Unknown(ID:{inv_id})")
        d         = row['test_date']
        if start_date <= d <= end_date:          # safety check
            raw.setdefault(inv_label, {})[d] = row['cnt']

    # ── Only investigations that have data in selected range ──────────
    inv_names  = sorted(raw.keys())
    rows       = []
    col_totals = [0] * len(all_dates)            # covers full calendar

    for inv in inv_names:
        day_map   = raw[inv]
        counts    = []
        row_total = 0
        for i, d in enumerate(all_dates):
            if start_date <= d <= end_date:
                c = day_map.get(d, 0)            # 0 if no records that day
            else:
                c = None                         # None = outside selected range → shows "—"
            counts.append(c)
            if c:                                # add to totals only for real data
                col_totals[i] += c
                row_total += c
        rows.append({'name': inv, 'counts': counts, 'total': row_total})

    grand_total = sum(c for c in col_totals if c)
    zipped_totals = list(zip(all_dates, col_totals))
    hospital = HospitalMaster.objects.filter(active='a').first()
    total_days = (end_date - start_date).days + 1
    logged_user = request.session.get("username")    
    context = {
        'all_dates':    all_dates,
        'cal_start':    cal_start,
        'cal_end':      cal_end,
        'start_date':   start_date,       # actual selected start
        'end_date':     end_date,         # actual selected end
        'rows':         rows,
        'col_totals':   col_totals,
        'grand_total':  grand_total,
        'zipped_totals':zipped_totals,
        'hospital':     hospital,
        'total_days':   total_days,
        'logged_user':  logged_user,
        'print_time':   timezone.now(),
    }
    return render(request, 'hospApp/reports/InvCalResult.html', context)