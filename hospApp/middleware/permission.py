from django.shortcuts import redirect
from django.contrib.auth import logout


class RolePermissionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from hospApp.models import Tbluserpermission
        from hospApp.models.menus import SubMenu

        path = request.path.rstrip('/')
        path_lower = path.lower()

        # =====================================================
        # 1️⃣ PUBLIC URLS
        # =====================================================
        PUBLIC_PREFIXES = ('/login', '/logout', '/admin', '/static', '/media', '/api/mobile')

        if path == '':
            return self.get_response(request)

        if any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return self.get_response(request)

        # =====================================================
        # 2️⃣ AUTH CHECK
        # =====================================================
        if not request.user.is_authenticated:
            logout(request)
            return redirect('/')

        # =====================================================
        # 3️⃣ HOME ALWAYS ALLOWED
        # =====================================================
        if path_lower.startswith('/home'):
            return self.get_response(request)

        # =====================================================
        # 4️⃣ ROLE LOOKUP
        # =====================================================
        perm = (
            Tbluserpermission.objects
            .filter(username=request.user.username, isactive=True)
            .select_related('mainrole')
            .prefetch_related('mainrole__pages', 'mainrole__header_pages')
            .first()
        )

        if not perm or not perm.mainrole:
            logout(request)
            return redirect('/')

        # URLs this user is allowed to access (both sidebar pages and header pages)
        allowed_urls = {
            url.rstrip('/').lower()
            for url in (
                list(perm.mainrole.pages.values_list('url', flat=True)) +
                list(perm.mainrole.header_pages.values_list('url', flat=True))
            )
            if url
        }

        # =====================================================
        # 5️⃣ DIRECT MATCH — user has this page assigned
        # =====================================================
        for allowed in allowed_urls:
            if path_lower == allowed or path_lower.startswith(allowed + '/'):
                return self.get_response(request)

        # =====================================================
        # 6️⃣ CHECK IF THIS IS A REGISTERED PAGE IN DATABASE
        #    If YES → it's a real page → user doesn't have it → BLOCK
        #    If NO  → it's an ajax/helper/result url → ALLOW
        #    (helper urls are only reachable FROM a page the user already has)
        # =====================================================
        all_registered_urls = {
            url.rstrip('/').lower()
            for url in SubMenu.objects.values_list('url', flat=True)
            if url
        }

        if path_lower in all_registered_urls:
            # It's a real registered page but user doesn't have permission
            print(f"BLOCKED REGISTERED PAGE: '{path_lower}' | ALLOWED: {allowed_urls}")
            return redirect('/home/')

        
        return self.get_response(request)