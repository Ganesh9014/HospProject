from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from hospApp.models import CaseTypeMaster
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def CaseTypeMasterView(request):

    # ============================
    # POST HANDLING (NO RENDER)
    # ============================
    if request.method == 'POST':

        operation = request.POST.get('operation', 'add')

        # ---------- ADD ----------
        if operation == 'add':
            casetype = (request.POST.get('casetype') or '').strip()

            if not casetype:
                messages.error(request, "Please enter Case Type.")
            elif CaseTypeMaster.objects.filter(
                casetype__iexact=casetype, active='Y'
            ).exists():
                messages.error(request, f"Case Type '{casetype}' already exists.")
            else:
                CaseTypeMaster.objects.create(
                    casetype=casetype,
                    active='Y',
                    createdby=request.user.username,
                    createdtime=timezone.now()
                )
                messages.success(
                    request,
                    f"Case Type '{casetype}' added successfully."
                )

            return redirect(request.path + "?operation=add")

        # ---------- MODIFY ----------
        if operation == 'modify' and 'update_btn' in request.POST:
            update_id = request.POST.get('update_btn')
            new_name = (request.POST.get(f'casetype_{update_id}') or '').strip()

            if not new_name:
                messages.error(request, "Please enter Case Type.")
            elif CaseTypeMaster.objects.filter(
                casetype__iexact=new_name,
                active='Y'
            ).exclude(pk=update_id).exists():
                messages.error(request, f"Case Type '{new_name}' already exists.")
            else:
                try:
                    case = CaseTypeMaster.objects.get(pk=update_id, active='Y')
                    case.casetype = new_name
                    case.updatedby = request.user.username
                    case.updatedtime = timezone.now()
                    case.save()
                    messages.success(
                        request,
                        f"Case Type '{new_name}' updated successfully."
                    )
                except CaseTypeMaster.DoesNotExist:
                    messages.error(request, "Case Type not found.")

            return redirect(request.path + "?operation=modify")

        # ---------- DELETE ----------
        if operation == 'delete' and 'delete_btn' in request.POST:
            delete_id = request.POST.get('delete_btn')
            try:
                case = CaseTypeMaster.objects.get(pk=delete_id, active='Y')
                case.active = 'N'
                case.updatedby = request.user.username
                case.updatedtime = timezone.now()
                case.save()
                messages.success(
                    request,
                    f"Case Type '{case.casetype}' deleted successfully."
                )
            except CaseTypeMaster.DoesNotExist:
                messages.error(request, "Case Type not found.")

            return redirect(request.path + "?operation=delete")

        # ---------- SEARCH (POST fallback) ----------
        search_case = (request.POST.get('casetype') or '').strip()
        qs = f"?operation={operation}"
        if search_case:
            qs += f"&casetype={search_case}"

        return redirect(request.path + qs)

    # ============================
    # GET HANDLING (ONLY RENDER)
    # ============================
    operation = request.GET.get('operation', 'add')
    search_case = (request.GET.get('casetype') or '').strip()

    casetypes = CaseTypeMaster.objects.filter(active='Y').order_by('casetype')

    if search_case:
        casetypes = casetypes.filter(casetype__icontains=search_case)

    return render(request, 'hospApp/Admin/CaseTypeMaster.html', {
        'operation': operation,
        'casetypes': casetypes,
    })
