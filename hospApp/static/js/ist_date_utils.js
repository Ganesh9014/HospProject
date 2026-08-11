// static/js/ist_date_utils.js
// ✅ Handles IST date defaults + midnight refresh for ALL pages

(function () {

    function getISTDateStr() {
        const istOffset = 5.5 * 60 * 60 * 1000;
        const istNow    = new Date(Date.now() + istOffset);
        return istNow.toISOString().split('T')[0];
    }

    function setDefaultDates() {
        const today = getISTDateStr();

        // ✅ Auto-set any from_date / to_date input that is empty
        document.querySelectorAll('input[name="from_date"]').forEach(el => {
            if (!el.value) el.value = today;
        });
        document.querySelectorAll('input[name="to_date"]').forEach(el => {
            if (!el.value) el.value = today;
        });
    }

    function scheduleISTMidnightRefresh() {
        const istOffset   = 5.5 * 60 * 60 * 1000;
        const istNow      = new Date(Date.now() + istOffset);
        const istMidnight = new Date(istNow);

        // Next midnight IST = 18:30 UTC
        istMidnight.setUTCHours(18, 30, 0, 0);
        if (istMidnight <= new Date()) {
            istMidnight.setUTCDate(istMidnight.getUTCDate() + 1);
        }

        const ms = istMidnight - Date.now();
        setTimeout(() => window.location.reload(), ms);
    }

    document.addEventListener("DOMContentLoaded", function () {
        setDefaultDates();
        scheduleISTMidnightRefresh();
    });

})();