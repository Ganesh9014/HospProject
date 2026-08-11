from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json

from hospApp.forms.UserPermissionForm import UserPermissionForm
from hospApp.models import Employee, Tbluserpermission
from hospApp.models.menus import MainMenu, SubMenu
from hospApp.models.tblroles import tblRoles


@login_required(login_url='login')
def add_permission(request):

    employees = list(
        Employee.objects.values('id', 'emp_id', 'emp_name', 'designation')
    )
    # menus = MainMenu.objects.prefetch_related('sublinks').order_by('display_order')
    permission_menus = MainMenu.objects.prefetch_related('sublinks').order_by('display_order')
    employee_roles = {
        emp.id: emp.designation
        for emp in Employee.objects.all()
    }

    # Includes ALL roles (base + custom) since custom is now mainrole='yes'
    role_pages = {
        role.roleid: list(role.pages.values_list('id', flat=True))
        for role in tblRoles.objects.all()
    }

    role_header_pages = {
        role.roleid: list(role.header_pages.values_list('id', flat=True))
        for role in tblRoles.objects.all()
    }

    existing_users = {}
    for perm in Tbluserpermission.objects.select_related('emp', 'mainrole').all():
        if not perm.emp_id:
            continue
        is_custom = '_CUSTOM_' in (perm.mainrole.rolename or '') if perm.mainrole else False

        existing_users[str(perm.emp_id)] = {
            'username':          perm.username,
            'perm_id':           perm.id,
            'isactive':          perm.isactive,
            'app_permission':    getattr(perm, 'app_permission', False),
            'role_id':           perm.mainrole_id,      # actual saved role (base or custom)
            'is_custom':         is_custom,
            'saved_permissions': [],
        }

    if request.method == 'POST':
        emp_id       = request.POST.get('emp')
        is_existing  = str(emp_id) in existing_users

        form = UserPermissionForm(request.POST)
        form.is_existing = is_existing

        if form.is_valid():
            if is_existing:
                perm_id  = existing_users[str(emp_id)]['perm_id']
                user_perm = Tbluserpermission.objects.get(id=perm_id)
                user_perm.emp            = form.cleaned_data['emp']
                user_perm.username       = form.cleaned_data['username']
                user_perm.isactive       = form.cleaned_data['isactive']
                user_perm.app_permission = form.cleaned_data.get('app_permission', False)
            else:
                user_perm = form.save(commit=False)

            if user_perm.emp:
                user_perm.empid    = user_perm.emp.emp_id
                user_perm.empname  = user_perm.emp.emp_name
                user_perm.empdesig = user_perm.emp.designation

            user_perm.permission = ""

            role           = form.cleaned_data.get('mainrole')
            sublink_ids    = request.POST.getlist('sublinks')
            selected_sublinks = SubMenu.objects.filter(id__in=sublink_ids)
            header_sublink_ids = request.POST.getlist('header_sublinks')
            selected_header_sublinks = SubMenu.objects.filter(id__in=header_sublink_ids)
            add_more_pages = request.POST.get('id_add_more_pages')

            pages_differ = False
            if role:
                base_role_page_ids = set(role.pages.values_list('id', flat=True))
                selected_page_ids  = set(map(int, sublink_ids)) if sublink_ids else set()

                base_role_header_ids = set(role.header_pages.values_list('id', flat=True))
                selected_header_ids  = set(map(int, header_sublink_ids)) if header_sublink_ids else set()

                # Pages or headers differ from base role → need a custom role
                pages_differ = add_more_pages and (
                    (selected_page_ids != base_role_page_ids) or
                    (selected_header_ids != base_role_header_ids)
                )

            if pages_differ:
                # Count existing custom roles for this user to get next version number
                username = form.cleaned_data.get('username') or user_perm.username
                emp_id_str = user_perm.empid or ''
                
                existing_custom_count = tblRoles.objects.filter(
                    rolename__startswith=f"{username}_CUSTOM_{emp_id_str}"
                ).count()
                
                version = existing_custom_count + 1
                
                custom_role = tblRoles.objects.create(
                    rolename=f"{username}_CUSTOM_{emp_id_str}_v{version}",
                    mainrole='yes',
                )
                custom_role.pages.set(selected_sublinks)
                custom_role.header_pages.set(selected_header_sublinks)
                custom_role.save()
                user_perm.mainrole = custom_role
            else:
                # ── Pages match base role → assign base role directly ────────────
                # No deletion of old custom roles — just reassign
                user_perm.mainrole = role

            user_perm.save()
            messages.success(request, "User permissions saved successfully.")
            return redirect('addpermission')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
                return redirect('addpermission')  # ← redirect instead of falling through to render
            
    else:
        form = UserPermissionForm()

    return render(request, 'hospApp/Admin/addpermission.html', {
        'form':              form,
        # 'menus':             menus,
        'permission_menus': permission_menus,
        'employees':         json.dumps(employees),
        'role_pages':        json.dumps(role_pages),
        'role_header_pages': json.dumps(role_header_pages),
        'employee_roles':    json.dumps(employee_roles),
        'existing_users':    json.dumps(existing_users),
    })