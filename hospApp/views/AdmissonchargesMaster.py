from django.shortcuts import render, redirect
from django.contrib import messages
from hospApp.models import Report
from django.utils import timezone

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def AdmissionCharges(request):

    operation = None
    reports = None
    search_term = ''
    searched = False

    # =========================
    # POST HANDLING
    # =========================
    if request.method == 'POST':

        operation = request.POST.get('operation')
        update_id = request.POST.get('update_id')
        search_term = (request.POST.get('search_term') or '').strip()
        rptname = (request.POST.get('rptname') or '').strip()
        cost = request.POST.get('cost')

        # -------------------------
        # DEFAULT ADD (NO RADIO)
        # -------------------------
        if not operation and not update_id:

            if not rptname:
                messages.error(request, "Please enter a Report Name.")
                return redirect(request.path + "?operation=add")

            if Report.objects.filter(rptname__iexact=rptname, active='Y').exists():
                messages.error(
                    request,
                    f"A report with the name '{rptname}' already exists."
                )
                return redirect(request.path + "?operation=add")

            Report.objects.create(
                rptname=rptname,
                cost=0,
                active='Y',
                userid='admin',
                createddate=timezone.now(),
                updatedby='admin',
                updateddate=timezone.now()
            )

            messages.success(
                request,
                f"Report '{rptname}' added successfully with cost = 0."
            )
            return redirect(request.path + "?operation=add")

        # -------------------------
        # ADD OPERATION
        # -------------------------
        if operation == 'add':

            if not rptname:
                messages.error(request, "Report Name is required.")
                return redirect(request.path + "?operation=add")

            if Report.objects.filter(rptname__iexact=rptname, active='Y').exists():
                messages.error(
                    request,
                    f"A report with the name '{rptname}' already exists."
                )
                return redirect(request.path + "?operation=add")

            if not cost:
                messages.error(request, "Cost is required.")
                return redirect(request.path + "?operation=add")

            try:
                cost_val = float(cost)
                if cost_val < 0:
                    messages.error(request, "Cost cannot be negative.")
                    return redirect(request.path + "?operation=add")
            except ValueError:
                messages.error(request, "Cost must be a valid number.")
                return redirect(request.path + "?operation=add")

            Report.objects.create(
                rptname=rptname,
                cost=cost_val,
                active='Y',
                userid='admin',
                createddate=timezone.now(),
                updatedby='admin',
                updateddate=timezone.now()
            )

            messages.success(request, f"Report '{rptname}' added successfully.")
            return redirect(request.path + "?operation=add")

        # -------------------------
        # MODIFY OPERATION
        # -------------------------
        if operation == 'modify' and update_id:

            new_cost = request.POST.get(f'cost_{update_id}')

            if not new_cost:
                messages.error(request, "Please enter a cost to update.")
                return redirect(request.path + "?operation=modify")

            try:
                new_cost_val = float(new_cost)
                rpt = Report.objects.get(pk=update_id)
                rpt.cost = new_cost_val
                rpt.updatedby = 'admin'
                rpt.updateddate = timezone.now()
                rpt.save()
                messages.success(
                    request,
                    f"Report '{rpt.rptname}' updated successfully."
                )
            except ValueError:
                messages.error(request, "Updated cost must be a number.")
            except Report.DoesNotExist:
                messages.error(request, "Report not found.")

            return redirect(request.path + "?operation=modify")

        # -------------------------
        # DELETE OPERATION
        # -------------------------
        if operation == 'delete' and update_id:

            try:
                rpt = Report.objects.get(pk=update_id)
                rpt.active = 'N'
                rpt.updatedby = 'admin'
                rpt.updateddate = timezone.now()
                rpt.save()
                messages.success(
                    request,
                    f"Report '{rpt.rptname}' deleted successfully."
                )
            except Report.DoesNotExist:
                messages.error(request, "Report not found.")

            return redirect(request.path + "?operation=delete")

    # =========================
    # GET HANDLING
    # =========================
    operation = request.GET.get('operation', 'add')
    search_term = (request.GET.get('search') or '').strip()

    if operation == 'modify':
        if search_term:
            reports = Report.objects.filter(
                rptname__icontains=search_term, active='Y'
            ).order_by('reportid')
            searched = True
        else:
            reports = Report.objects.filter(active='Y').order_by('reportid')

    elif operation == 'delete':
        if search_term:
            reports = Report.objects.filter(
                rptname__icontains=search_term, active='Y'
            ).order_by('reportid')
            searched = True
        else:
            reports = Report.objects.filter(active='Y').order_by('reportid')

    else:  # add
        reports = Report.objects.filter(active='Y').order_by('reportid')

    return render(request, 'hospApp/Admin/AdmissionChargesMaster.html', {
        'reports': reports,
        'operation': operation,
        'search_term': search_term,
        'searched': searched,
    })
