from django.shortcuts import render, redirect
from django.contrib import messages
from hospApp.models import MainDepartmentMaster
from django.utils import timezone
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def DepartmentMaster(request):

    operation = None
    departments = None
    search_term = ''
    searched = False

    # =========================
    # POST HANDLING
    # =========================
    if request.method == 'POST':

        operation = request.POST.get('operation')
        update_id = request.POST.get('update_id')
        search_term = (request.POST.get('search_term') or '').strip()

        # -------------------------
        # DEFAULT ADD (NO RADIO)
        # -------------------------
        if not operation and not update_id:

            dept_name = (request.POST.get('department') or '').strip()

            if not dept_name:
                messages.error(request, "Please enter a Department Name.")
                return redirect(request.path + "?operation=add")

            if MainDepartmentMaster.objects.filter(
                department__iexact=dept_name, active='Y'
            ).exists():
                messages.error(
                    request,
                    f"A department with the name '{dept_name}' already exists."
                )
                return redirect(request.path + "?operation=add")

            MainDepartmentMaster.objects.create(
                department=dept_name,
                active='Y',
                createdby='admin',
                createddate=timezone.now(),
                updatedby='admin',
                updatedtime=timezone.now()
            )

            messages.success(
                request,
                f"Department '{dept_name}' added successfully."
            )
            return redirect(request.path + "?operation=add")

        # -------------------------
        # ADD MODE
        # -------------------------
        if operation == 'add':

            dept_name = (request.POST.get('department') or '').strip()

            if not dept_name:
                messages.error(request, "Please enter a Department Name.")
                return redirect(request.path + "?operation=add")

            if MainDepartmentMaster.objects.filter(
                department__iexact=dept_name, active='Y'
            ).exists():
                messages.error(
                    request,
                    f"A department with the name '{dept_name}' already exists."
                )
                return redirect(request.path + "?operation=add")

            MainDepartmentMaster.objects.create(
                department=dept_name,
                active='Y',
                createdby='admin',
                createddate=timezone.now(),
                updatedby='admin',
                updatedtime=timezone.now()
            )

            messages.success(
                request,
                f"Department '{dept_name}' added successfully."
            )
            return redirect(request.path + "?operation=add")

        # -------------------------
        # MODIFY MODE
        # -------------------------
        if operation == 'modify' and update_id:

            dept_name = (request.POST.get(f'department_{update_id}') or '').strip()

            if not dept_name:
                messages.error(request, "Please enter a Department Name to update.")
                return redirect(request.path + "?operation=modify")

            try:
                dept = MainDepartmentMaster.objects.get(pk=update_id)

                duplicate = MainDepartmentMaster.objects.filter(
                    department__iexact=dept_name,
                    active='Y'
                ).exclude(pk=update_id).exists()

                if duplicate:
                    messages.error(
                        request,
                        f"Department '{dept_name}' already exists."
                    )
                    return redirect(request.path + "?operation=modify")

                dept.department = dept_name
                dept.updatedby = 'admin'
                dept.updatedtime = timezone.now()
                dept.save()

                messages.success(
                    request,
                    f"Department '{dept.department}' updated successfully."
                )

            except MainDepartmentMaster.DoesNotExist:
                messages.error(request, "Department not found.")

            return redirect(request.path + "?operation=modify")

        # -------------------------
        # DELETE MODE
        # -------------------------
        if operation == 'delete' and update_id:

            try:
                dept = MainDepartmentMaster.objects.get(pk=update_id)
                dept.active = 'N'
                dept.updatedby = 'admin'
                dept.updatedtime = timezone.now()
                dept.save()

                messages.success(
                    request,
                    f"Department '{dept.department}' deleted successfully."
                )

            except MainDepartmentMaster.DoesNotExist:
                messages.error(request, "Department not found.")

            return redirect(request.path + "?operation=delete")

    # =========================
    # GET HANDLING
    # =========================
    operation = request.GET.get('operation', 'add')
    search_term = (request.GET.get('search') or '').strip()

    if operation == 'modify':
        if search_term:
            departments = MainDepartmentMaster.objects.filter(
                department__icontains=search_term,
                active='Y'
            ).order_by('dno')
            searched = True
        else:
            departments = MainDepartmentMaster.objects.filter(
                active='Y'
            ).order_by('dno')

    elif operation == 'delete':
        if search_term:
            departments = MainDepartmentMaster.objects.filter(
                department__icontains=search_term,
                active='Y'
            ).order_by('dno')
            searched = True
        else:
            departments = MainDepartmentMaster.objects.filter(
                active='Y'
            ).order_by('dno')

    else:  # add
        departments = MainDepartmentMaster.objects.filter(
            active='Y'
        ).order_by('dno')

    return render(request, 'hospApp/Admin/DepartmentMaster.html', {
        'departments': departments,
        'operation': operation,
        'search_term': search_term,
        'searched': searched,
    })
