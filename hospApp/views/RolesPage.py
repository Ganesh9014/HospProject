import json
from django.shortcuts import render, redirect
from django.contrib import messages

from hospApp.models.menus import MainMenu, SubMenu
from hospApp.models.tblroles import tblRoles

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def RolesPage(request):
    # -------------------------------
    # DATA FOR UI (ADMIN ONLY)
    # -------------------------------
    admin_menus = MainMenu.objects.prefetch_related('sublinks').order_by('display_order')
    roles = tblRoles.objects.all()

    role_data = {}
    for role in roles:
        role_data[str(role.roleid)] = {
            'pages': list(role.pages.values_list('id', flat=True)),
            'header_pages': list(role.header_pages.values_list('id', flat=True))
        }

    if request.method == 'POST':
        operation = request.POST.get('operation_radio')
        rolename = request.POST.get('rolename')
        role_id = request.POST.get('role_id')
        page_ids = request.POST.getlist('pages')
        header_page_ids = request.POST.getlist('header_pages')

        if operation == 'add':
            if not rolename:
                messages.error(request, "Role name is required")
                return redirect(request.path)

            role = tblRoles.objects.create(
                rolename=rolename,
                mainrole='yes',
            )

            role.pages.set(SubMenu.objects.filter(id__in=page_ids))
            role.header_pages.set(SubMenu.objects.filter(id__in=header_page_ids))
            messages.success(request, "Role added successfully")

        elif operation == 'update':
            if not role_id:
                messages.error(request, "Please select a role to update")
                return redirect(request.path)

            role = tblRoles.objects.get(roleid=role_id)
            role.pages.set(SubMenu.objects.filter(id__in=page_ids))
            role.header_pages.set(SubMenu.objects.filter(id__in=header_page_ids))
            role.save()

            messages.success(request, "Role updated successfully")

        return redirect(request.path)

    return render(request, 'hospApp/Admin/RolesPage.html', {
        'admin_menus': admin_menus,   # ✅ SAFE NAME
        'roles': roles,
        'role_data': json.dumps(role_data),
    })
