from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from hospApp.models import Expenditure

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def ExpenditureMasterView(request):

    # Default operation
    operation = request.GET.get('operation', 'add')

    expenditures = []
    search_term = ''

    # =========================
    # ADD
    # =========================
    if request.method == 'POST' and 'add_btn' in request.POST:
        name = request.POST.get('expenditure_name', '').strip()

        if not name:
            messages.error(request, "Expenditure name is required")

        elif Expenditure.objects.filter(
            expenditure_name__iexact=name,
            active='Y'
        ).exists():
            messages.error(request, "Expenditure already exists")

        else:
            Expenditure.objects.create(
                expenditure_name=name,
                active='Y'   # ensure active
            )
            messages.success(request, "Expenditure added successfully")
            return redirect('ExpenditureMasterView')

    # =========================
    # SEARCH (MODIFY / DELETE)
    # =========================
    if request.method == 'POST' and 'search_btn' in request.POST:
        search_term = request.POST.get('search_term', '').strip()

        expenditures = Expenditure.objects.filter(
            expenditure_name__icontains=search_term,
            active='Y'
        )

    # =========================
    # UPDATE (MODIFY)
    # =========================
    if request.method == 'POST' and 'update_btn' in request.POST:
        sno = request.POST.get('update_btn')
        new_name = request.POST.get(f'expenditure_name_{sno}', '').strip()

        try:
            obj = Expenditure.objects.get(sno=sno, active='Y')

            if not new_name:
                messages.error(request, "Expenditure name cannot be empty")

            elif Expenditure.objects.filter(
                expenditure_name__iexact=new_name,
                active='Y'
            ).exclude(sno=sno).exists():
                messages.error(request, "Expenditure already exists")

            else:
                obj.expenditure_name = new_name
                obj.save()
                messages.success(request, "Expenditure updated successfully")

        except Expenditure.DoesNotExist:
            messages.error(request, "Expenditure not found")

        return redirect(reverse('ExpenditureMasterView') + '?operation=modify')

    # =========================
    # DELETE (SOFT DELETE)
    # =========================
    if request.method == 'POST' and 'delete_btn' in request.POST:
        sno = request.POST.get('delete_btn')

        try:
            obj = Expenditure.objects.get(sno=sno, active='Y')
            obj.active = 'N'   # 👈 soft delete
            obj.save()
            messages.success(request, "Expenditure deleted successfully (inactive)")

        except Expenditure.DoesNotExist:
            messages.error(request, "Expenditure not found")

        return redirect(reverse('ExpenditureMasterView') + '?operation=delete')

    # =========================
    # LOAD DATA (DEFAULT)
    # =========================
    if not expenditures:
        expenditures = Expenditure.objects.filter(active='Y')

    return render(request, 'hospApp/Admin/ExpenditureMaster.html', {
        'operation': operation,
        'expenditures': expenditures,
        'search_term': search_term
    })
from django.db import transaction
from hospApp.models import Expenditure, BillMaster

from django.db.models import Max
from hospApp.models import Expenditure, ExpenditureEntry

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Max
from hospApp.models import ExpenditureEntry
from django.http import JsonResponse    
from django.urls import reverse

@transaction.atomic
def ExpenditureView(request):    
    if request.method == "POST":
        try:
            expenditure_id = request.POST.get('expenditure')
            amount = request.POST.get('amount_paid')
            towards = request.POST.get('towards')
            username=request.user   

            last_bill = ExpenditureEntry.objects.select_for_update().aggregate(Max('bill_no'))['bill_no__max']
            bill_no = last_bill + 1 if last_bill else 1

            entry = ExpenditureEntry.objects.create(
                expenditure_id=expenditure_id,
                bill_no=bill_no,
                amount=amount,
                towards=towards,
                username=username

            )

            # 🔥 REDIRECT TO PRINT PAGE
            return JsonResponse({
                "success": True,
                "redirect_url": reverse("expenditure_print", args=[entry.bill_no])
            })

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('ExpenditureView')
    # ======================
    # GET (Load form)
    # ======================
    from hospApp.models import Expenditure
    exp = Expenditure.objects.filter(active='Y').order_by('expenditure_name')

    # Show next bill number (for UI only)
    last_bill = ExpenditureEntry.objects.aggregate(Max('bill_no'))['bill_no__max']
    bill_no = last_bill + 1 if last_bill else 1

    return render(request, 'hospApp/frontOffice/Expenditure.html', {
        'exp': exp,
        'bill_no': bill_no
    })





from django.shortcuts import render, get_object_or_404
from hospApp.models import ExpenditureEntry
from num2words import num2words
from hospApp.models import ExpenditureEntry ,HospitalMaster

from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def expenditure_print(request, billno):
    hospital = HospitalMaster.objects.filter(active='a').first()
    entry = get_object_or_404(
        ExpenditureEntry.objects.select_related('expenditure'),
        bill_no=billno
    )
    is_cancelled = not ExpenditureEntry.objects.filter(
        bill_no=billno,
        active='Y'
    ).exists()
    inwords = num2words(entry.amount, to='cardinal').replace('-', ' ').title()
    context = {
        "entry": entry,
        "inwords": inwords , # optional
        "hospital":hospital ,
        "is_cancelled": is_cancelled
    }

    return render(request, "hospApp/frontoffice/expenditure_print.html", context)





from hospApp.models import Expenditure  , Tbluserpermission
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Sum
from hospApp.models import Expenditure, Tbluserpermission


from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Sum
from hospApp.models import Expenditure, Tbluserpermission, ExpenditureEntry



from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def ExpenditureReportView(request):

    # ✅ Users dropdown
    users = Tbluserpermission.objects.filter(isactive=True).order_by('username')

    # ✅ Expenditure dropdown (master table)
    all_expenditures = Expenditure.objects.all().order_by('expenditure_name')

    # ✅ Get filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    username = request.GET.get('username')
    expenditure_id = request.GET.get('expenditure')
    report_type = request.GET.get('report_type')

    # ✅ MAIN DATA (IMPORTANT CHANGE HERE)
    filtered_expenditures = ExpenditureEntry.objects.all()

    # ✅ DATE FILTER
    if from_date and to_date:
        try:
            start_date = datetime.strptime(from_date, "%Y-%m-%d")
            end_date = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)

            filtered_expenditures = filtered_expenditures.filter(
                created_at__gte=start_date,
                created_at__lt=end_date
            )
        except Exception as e:
            print("Date Error:", e)

    # ✅ USER FILTER
    if username and username != "ALL":
        filtered_expenditures = filtered_expenditures.filter(username=username)

    # ✅ EXPENDITURE FILTER (FK FIX)
    if expenditure_id and expenditure_id != "ALL":
        filtered_expenditures = filtered_expenditures.filter(
            expenditure__sno=expenditure_id
        )

    # ✅ REPORT TYPE
    if report_type == "SUMMARY":
        report_data = filtered_expenditures.values('username').annotate(
            total_amount=Sum('amount')
        ).order_by('username')
    else:
        report_data = filtered_expenditures.order_by('-created_at')

    # ✅ TOTAL
    total_amount = filtered_expenditures.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # ✅ RESPONSE
    return render(request, 'hospApp/reports/ExpenditureReport.html', {
        "users": users,
        "expenditures": all_expenditures,   # dropdown
        "report_data": report_data,         # actual report
        "total_amount": total_amount,

        # keep selections
        "from_date": from_date,
        "to_date": to_date,
        "selected_user": username,
        "selected_expenditure": expenditure_id,
        "report_type": report_type,
    })
from django.shortcuts import render
from django.db.models import Sum
from hospApp.models import ExpenditureEntry

from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime, timedelta
from hospApp.models import ExpenditureEntry, Tbluserpermission

from django.utils import timezone
from django.utils import timezone

from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone

from hospApp.models import (
    ExpenditureEntry,
    Tbluserpermission,
    HospitalMaster,
    Expenditure
)


from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone

from hospApp.models import (
    ExpenditureEntry,
    Tbluserpermission,
    HospitalMaster,
    Expenditure
)




from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def userwise_collection_report(request):

    # =========================
    # 🔹 BASIC DATA
    # =========================
    users = Tbluserpermission.objects.filter(isactive=True).order_by('username')
    hospital = HospitalMaster.objects.filter(active='a').first()

    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    username = request.GET.get('username')
    expenditure_id = request.GET.get('expenditure')
    report_type = request.GET.get('report_type')

    logged_user = request.session.get("username")

    # =========================
    # 🔹 BASE QUERY
    # =========================
    expenditures = ExpenditureEntry.objects.select_related('expenditure').all()

    # =========================
    # ✅ DATE FILTER (FIXED + TIMEZONE SAFE)
    # =========================
    from_date = None
    to_date = None

    if from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d")
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d")

            # ✅ convert to timezone aware
            from_date = timezone.make_aware(from_date)
            to_date = timezone.make_aware(to_date)

            end_date = to_date + timedelta(days=1)

            expenditures = expenditures.filter(
                created_at__gte=from_date,
                created_at__lt=end_date,active="Y"  
            )

        except Exception as e:
            print("Date Error:", e)

    # =========================
    # ✅ USER FILTER
    # =========================
    if username and username != "ALL":
        expenditures = expenditures.filter(username=username)

    # =========================
    # ✅ EXPENDITURE FILTER + NAME
    # =========================
    selected_expenditure_name = "ALL"

    if expenditure_id and expenditure_id != "ALL":
        try:
            expenditure_id = int(expenditure_id)  # ✅ ensure integer

            expenditures = expenditures.filter(
                expenditure__sno=expenditure_id
            )

            exp_obj = Expenditure.objects.filter(sno=expenditure_id).first()
            if exp_obj:
                selected_expenditure_name = exp_obj.expenditure_name

        except ValueError:
            selected_expenditure_name = "ALL"

    # =========================
    # ✅ REPORT TYPE
    # =========================
    if report_type == "SUMMARY":
        expenditures = expenditures.values('username').annotate(
            total_amount=Sum('amount')
        ).order_by('username')
    else:
        expenditures = expenditures.order_by('created_at')

    # =========================
    # ✅ TOTAL
    # =========================
    total_amount = expenditures.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # =========================
    # ✅ RESPONSE
    # =========================
    return render(request, 'hospApp/reports/ExpenditureReportResult.html', {
        'users': users,
        'expenditures': expenditures,
        'from_date': from_date,
        'to_date': to_date,
        'selected_user': username,
        'selected_expenditure': expenditure_id,
        'selected_expenditure_name': selected_expenditure_name,
        'report_type': report_type,
        'total_amount': total_amount,
        'hospital': hospital,
        'logged_user': logged_user,
        'print_time': timezone.now(),
    })