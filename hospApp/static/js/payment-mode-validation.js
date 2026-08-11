(function () {

    function initPaymentValidation(selectId, inputId, labelId, containerId) {

        const select = document.getElementById(selectId);
        const input  = document.getElementById(inputId);
        const label  = document.getElementById(labelId);
        const box    = document.getElementById(containerId);

        if (!select || !input || !label || !box) return;

        function apply() {
            const mode = (select.value || "").toLowerCase();

            box.style.display = "none";
            input.value = "";
            input.removeAttribute("maxlength");
            input.removeAttribute("pattern");
            input.removeAttribute("title");

            if (mode === "upi") {
                label.innerText = "UPI ID";
                input.setAttribute("maxlength", "10");
                input.setAttribute("pattern", "^[a-zA-Z0-9._-@]{1,10}$");
                input.setAttribute(
                    "title",
                    "UPI ID can contain letters, numbers, . _ - @ (max 10 characters)"
                );
                box.style.display = "block";
            }
            else if (mode === "card") {
                label.innerText = "Card Name";
                box.style.display = "block";
            }
            else if (mode === "cheque") {
                label.innerText = "Cheque No";
                box.style.display = "block";
            }
            else if (mode === "neft") {
                label.innerText = "NEFT Ref No";
                box.style.display = "block";
            }
        }

        select.addEventListener("change", apply);

        input.addEventListener("input", function () {
            const max = this.getAttribute("maxlength");
            if (max && this.value.length > max) {
                this.value = this.value.slice(0, max);
            }
        });

        apply(); // initial run
    }

    document.addEventListener("DOMContentLoaded", function () {
        initPaymentValidation(
            "paymentmode",
            "paymentdetails",
            "extraFieldLabel",
            "extraFieldDiv"
        );
    });

})();



/** * initBarcodeField(inputId, fetchFn) * Works for UHID, Bill No, or any barcode field * Triggers on: Enter key, Tab key, or fast-typing (scanner speed) */
function initBarcodeField(inputId, fetchFn) {
  const input = document.getElementById(inputId);
  if (!input) return;

  let scanTimer = null;
  let lastKeyTime = Date.now();
  let rapidCharCount = 0;

  // ✅ PRIMARY: Enter / Tab key sent by scanner
  input.addEventListener("keydown", function(e) {
    if (e.key === "Enter" || e.key === "Tab") {
      e.preventDefault();
      const val = input.value.trim();
      if (val) fetchFn(val);
    }
  });

  // ✅ FALLBACK: detect scanner speed (chars typed in <80ms each)
  input.addEventListener("input", function() {
    const now = Date.now();
    const gap = now - lastKeyTime;
    lastKeyTime = now;

    if (gap < 80) rapidCharCount++; // scanner speed
    else rapidCharCount = 0; // manual typing — reset

    clearTimeout(scanTimer);
    scanTimer = setTimeout(function() {
      const val = input.value.trim();
      // if 5+ rapid chars + min length → it's a scan
      if (rapidCharCount >= 5 && val.length >= 4) {
        fetchFn(val);
        rapidCharCount = 0;
      }
    }, 100);
  });
}