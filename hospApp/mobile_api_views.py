"""
Mobile API views for the Hospital React Native app.
All responses are JSON. Auth uses a simple token (base64-encoded username:timestamp).
No third-party package required.
"""

import json
import base64
import time
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Sum, Min, Max, OuterRef, Subquery

from hospApp.models import (
    Tbluserpermission,
    DoctorConsultation,
    Login,
    tblInvestigationDetails,
    TblServices,
    OpPayment,
    TblOpCancellation,
    OpPatientRegistration,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _cors(response):
    """Add CORS headers so the Expo app on a phone can reach this server."""
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-Mobile-Token"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def _make_token(username: str) -> str:
    payload = f"{username}:{int(time.time())}"
    return base64.b64encode(payload.encode()).decode()


def _decode_token(token: str):
    """Return username from token, or None if invalid."""
    try:
        payload = base64.b64decode(token.encode()).decode()
        username, _ = payload.split(":", 1)
        return username
    except Exception:
        return None


def _get_authenticated_user(request):
    """Extract token from X-Mobile-Token header and return Tbluserpermission or None."""
    token = request.headers.get("X-Mobile-Token", "")
    if not token:
        return None
    username = _decode_token(token)
    if not username:
        return None
    try:
        return Tbluserpermission.objects.get(username=username, isactive=True, app_permission=True)
    except Tbluserpermission.DoesNotExist:
        return None


def _json_error(message, status=400):
    return _cors(JsonResponse({"success": False, "error": message}, status=status))


def _json_ok(data):
    return _cors(JsonResponse({"success": True, **data}))


# ─────────────────────────────────────────────────────────────────────────────
# 1. LOGIN  POST /api/mobile/auth/login/
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def mobile_login(request):
    if request.method == "OPTIONS":
        return _cors(JsonResponse({}))

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return _json_error("Invalid JSON body")

    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        return _json_error("Username and password are required")

    try:
        user = Tbluserpermission.objects.get(
            username=username, password=password, isactive=True, app_permission=True
        )
    except Tbluserpermission.DoesNotExist:
        return _json_error("Invalid username or password", status=401)

    # Record login time
    Login.objects.create(
        user=user,
        name=user.empname or username,
        logintime=timezone.now(),
    )

    token = _make_token(username)

    return _json_ok({
        "token": token,
        "username": user.username,
        "empname": user.empname or username,
        "role": user.mainrole.rolename if user.mainrole else "USER",
        "department": user.department or "",
    })


# ─────────────────────────────────────────────────────────────────────────────
# 2. LOGOUT  POST /api/mobile/auth/logout/
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def mobile_logout(request):
    if request.method == "OPTIONS":
        return _cors(JsonResponse({}))

    user = _get_authenticated_user(request)
    if user:
        latest = Login.objects.filter(user=user).order_by("-logintime").first()
        if latest and not latest.logouttime:
            latest.logouttime = timezone.now()
            latest.save()

    return _json_ok({"message": "Logged out"})


# ─────────────────────────────────────────────────────────────────────────────
# 3. DASHBOARD  GET /api/mobile/dashboard/
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def mobile_dashboard(request):
    if request.method == "OPTIONS":
        return _cors(JsonResponse({}))

    user = _get_authenticated_user(request)
    if not user:
        return _json_error("Unauthorized", status=401)

    today = timezone.now().date()
    start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end = start + timedelta(days=1)

    # Today's OP count
    op_count = DoctorConsultation.objects.filter(
        regdt__gte=start, regdt__lt=end, opno__isnull=False
    ).count()

    # Today's login count
    login_count = Login.objects.filter(
        logintime__gte=start, logintime__lt=end
    ).count()

    # ── Due amount (Investigation + Consultation + Procedure) ──
    total_due = 0

    invs = (
        tblInvestigationDetails.objects
        .filter(generateddate__gte=start, generateddate__lt=end, active="Y")
        .values("billno", "uhid")
        .annotate(total=Sum("cost"), base_paid=Min("paidamt"), base_conc=Min("concessionamt"))
    )
    for i in invs:
        op = OpPayment.objects.filter(
            uhid=i["uhid"], billno=i["billno"], active="Y"
        ).aggregate(paid=Sum("patamt"), conc=Sum("concession"))
        due = (i["total"] or 0) - ((i["base_paid"] or 0) + (i["base_conc"] or 0) + (op["paid"] or 0) + (op["conc"] or 0))
        if due > 0:
            total_due += due

    cons = DoctorConsultation.objects.filter(regdt__gte=start, regdt__lt=end, isactive="Y")
    for c in cons:
        op = OpPayment.objects.filter(
            uhid=c.uhid, billno=c.billno, active="Y"
        ).aggregate(paid=Sum("patamt"), conc=Sum("concession"))
        due = (c.consulfee or 0) - ((c.paidamt or 0) + (c.concession or 0) + (op["paid"] or 0) + (op["conc"] or 0))
        if due > 0:
            total_due += due

    procs = (
        TblServices.objects
        .filter(createddate__gte=start, createddate__lt=end, isactive="Y")
        .values("billno", "uhid")
        .annotate(total=Sum("amount"), base_paid=Min("paidamt"), base_conc=Min("concessionamt"))
    )
    for p in procs:
        op = OpPayment.objects.filter(
            uhid=p["uhid"], billno=p["billno"], active="Y"
        ).aggregate(paid=Sum("patamt"), conc=Sum("concession"))
        due = (p["total"] or 0) - ((p["base_paid"] or 0) + (p["base_conc"] or 0) + (op["paid"] or 0) + (op["conc"] or 0))
        if due > 0:
            total_due += due

    # ── Today's total collection ──
    # Consultation: Sum paidamt per bill (each consultation = 1 row per bill normally)
    cons_total = DoctorConsultation.objects.filter(
        regdt__gte=start, regdt__lt=end, isactive="Y"
    ).aggregate(total=Sum("paidamt"))["total"] or 0

    # Investigations: Max paidamt per billno group (paidamt is stored on every item row)
    inv_bills = (
        tblInvestigationDetails.objects
        .filter(generateddate__gte=start, generateddate__lt=end, active="Y")
        .values("billno")
        .annotate(bill_paid=Max("paidamt"))
    )
    inv_total = sum(b["bill_paid"] or 0 for b in inv_bills)

    # Procedures: Max paidamt per billno group (same reason as investigations)
    proc_bills = (
        TblServices.objects
        .filter(createddate__gte=start, createddate__lt=end, isactive="Y")
        .values("billno")
        .annotate(bill_paid=Max("paidamt"))
    )
    proc_total = sum(b["bill_paid"] or 0 for b in proc_bills)

    # OP additional payments
    op_payment_total = OpPayment.objects.filter(
        billdate__gte=start, billdate__lt=end, active="Y"
    ).aggregate(total=Sum("patamt"))["total"] or 0

    grand_total = float(cons_total) + float(inv_total) + float(proc_total) + float(op_payment_total)

    return _json_ok({
        "date": today.strftime("%d %b %Y"),
        "op_count": op_count,
        "login_count": login_count,
        "total_due": round(float(total_due), 2),
        "total_collection": round(grand_total, 2),
        "breakdown": {
            "consultation": round(float(cons_total), 2),
            "investigation": round(float(inv_total), 2),
            "procedure": round(float(proc_total), 2),
            "op_payment": round(float(op_payment_total), 2),
        },
    })


# ─────────────────────────────────────────────────────────────────────────────
# 4. COLLECTION REPORT  GET /api/mobile/reports/collection/
#    ?from_date=2026-08-01&to_date=2026-08-10
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def mobile_reports_collection(request):
    if request.method == "OPTIONS":
        return _cors(JsonResponse({}))

    user = _get_authenticated_user(request)
    if not user:
        return _json_error("Unauthorized", status=401)

    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")

    try:
        if from_date_str and to_date_str:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        else:
            from_date = to_date = timezone.now().date()
    except ValueError:
        return _json_error("Invalid date format. Use YYYY-MM-DD")

    fd = timezone.make_aware(datetime.combine(from_date, datetime.min.time()))
    td = timezone.make_aware(datetime.combine(to_date, datetime.max.time()))

    # ── Consultation: 1 paidamt per row, just Sum ──
    cons_total = DoctorConsultation.objects.filter(
        createddate__gte=fd, createddate__lte=td, isactive="Y"
    ).aggregate(total=Sum("paidamt"))["total"] or 0

    # ── Procedures: paidamt repeated on every item row → Max per billno ──
    proc_bills = (
        TblServices.objects
        .filter(createddate__gte=fd, createddate__lte=td, isactive="Y")
        .values("billno")
        .annotate(bill_paid=Max("paidamt"))
    )
    proc_total = sum(b["bill_paid"] or 0 for b in proc_bills)

    # ── Investigations: same pattern as procedures ──
    inv_bills = (
        tblInvestigationDetails.objects
        .filter(generateddate__gte=fd, generateddate__lte=td, active="Y")
        .values("billno")
        .annotate(bill_paid=Max("paidamt"))
    )
    inv_total = sum(b["bill_paid"] or 0 for b in inv_bills)

    # ── OP additional payments ──
    op_total = OpPayment.objects.filter(
        billdate__gte=fd, billdate__lte=td, active="Y"
    ).aggregate(total=Sum("patamt"))["total"] or 0

    # ── Cancellations (shown separately, NOT added to grand total) ──
    cancel_total = TblOpCancellation.objects.filter(
        createddate__gte=fd, createddate__lte=td
    ).aggregate(total=Sum("amtpaid"))["total"] or 0

    grand = float(cons_total) + float(proc_total) + float(inv_total) + float(op_total)

    return _json_ok({
        "from_date": from_date.strftime("%d %b %Y"),
        "to_date": to_date.strftime("%d %b %Y"),
        "summary": [
            {"label": "Consultation",    "amount": round(float(cons_total),   2)},
            {"label": "Procedures",      "amount": round(float(proc_total),   2)},
            {"label": "Investigations",  "amount": round(float(inv_total),    2)},
            {"label": "OP Payments",     "amount": round(float(op_total),     2)},
            {"label": "Cancellations",   "amount": round(float(cancel_total), 2)},
        ],
        "grand_total": round(grand, 2),
    })

