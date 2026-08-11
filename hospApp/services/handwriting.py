# hospApp/services/handwriting.py
import hmac
import hashlib
import json
import requests
from django.conf import settings

MYSCRIPT_APP_KEY  = settings.MYSCRIPT_APPLICATION_KEY
MYSCRIPT_HMAC_KEY = settings.MYSCRIPT_HMAC_KEY
MYSCRIPT_URL      = "https://cloud.myscript.com/api/v4.0/iink/batch"


def _compute_hmac(app_key, hmac_key, request_data_str):
    combined_key = (app_key + hmac_key).encode("utf-8")
    message = request_data_str.encode("utf-8")
    return hmac.new(combined_key, message, hashlib.sha512).hexdigest()


def _signaturepad_to_strokegroups(stroke_data):
    """
    Convert SignaturePad's toData() output into MyScript's expected strokeGroups.
    Each pen stroke (pen-down to pen-up) is converted to a separate strokeGroup
    with timestamps normalized to relative milliseconds.
    """
    if not stroke_data:
        return []

    # Find earliest timestamp to make all timestamps relative to first stroke
    all_times = [
        p["time"]
        for group in stroke_data
        for p in group.get("points", [])
        if "time" in p
    ]
    t_offset = min(all_times) if all_times else 0

    stroke_groups = []
    for group in stroke_data:
        points = group.get("points", [])
        if not points:
            continue

        stroke = {
            "x": [round(p["x"], 1) for p in points],
            "y": [round(p["y"], 1) for p in points],
            "t": [int(p.get("time", i * 50) - t_offset) for i, p in enumerate(points)],
        }
        # Each pen stroke gets its own strokeGroup to assist layout analysis
        stroke_groups.append({"strokes": [stroke]})

    return stroke_groups


def recognize_handwriting(stroke_data_json: str, image_data_url: str = "", lang: str = "en_US") -> dict | None:
    """
    Recognize handwritten text using MyScript Batch API.
    Returns a dict: {"full_text": str, "lines": [{"text", "x", "y", "width", "height"}, ...]}
    or None on failure.
    """
    if not stroke_data_json:
        print("❌ No stroke data provided for MyScript recognition")
        return None

    try:
        stroke_data = json.loads(stroke_data_json)
    except (TypeError, json.JSONDecodeError) as e:
        print("❌ Failed to parse stroke_data JSON:", e)
        return None

    stroke_groups = _signaturepad_to_strokegroups(stroke_data)
    if not stroke_groups:
        print("❌ Built stroke_groups is empty")
        return None

    payload = {
        "configuration": {
            "lang": lang,
            "text": {
                "guides": {"enable": False},
                "smartGuide": {"enable": False}
            }
        },
        "contentType": "Text",
        "conversionState": "DIGITAL_EDIT",
        "strokeGroups": stroke_groups,
    }

    payload_str = json.dumps(payload, separators=(",", ":"))
    signature   = _compute_hmac(MYSCRIPT_APP_KEY, MYSCRIPT_HMAC_KEY, payload_str)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.myscript.jiix",
        "applicationKey": MYSCRIPT_APP_KEY,
        "hmac": signature,
    }

    try:
        response = requests.post(MYSCRIPT_URL, data=payload_str, headers=headers, timeout=15)
        print("📡 MyScript status:", response.status_code)
        response.raise_for_status()
        result = response.json()

        # 1. Best approach: parse JIIX lines[] — includes label + bounding-box per line
        lines_data = result.get("lines", [])
        if lines_data:
            structured_lines = []
            full_text_parts  = []
            for line in lines_data:
                # Get line label (direct or from words)
                line_label = line.get("label", "").strip()
                if not line_label:
                    words = line.get("words", [])
                    line_label = " ".join(
                        w.get("label", "") for w in words if w.get("label")
                    ).strip()

                # Get bounding box — MyScript JIIX uses "bounding-box" (hyphen)
                bbox = line.get("bounding-box", {})

                if line_label:
                    structured_lines.append({
                        "text":   line_label,
                        "x":      round(float(bbox.get("x",      0)),   1),
                        "y":      round(float(bbox.get("y",      0)),   1),
                        "width":  round(float(bbox.get("width",  200)), 1),
                        "height": round(float(bbox.get("height", 30)),  1),
                    })
                    full_text_parts.append(line_label)

            if structured_lines:
                full_text = "\n".join(full_text_parts)
                print("✅ MyScript recognized (lines with positions):", repr(full_text))
                return {"full_text": full_text, "lines": structured_lines}

        # 2. Fall back: top-level label (no position data)
        label = result.get("label") or result.get("text", "")
        if label and label.strip():
            text = label.strip()
            print("✅ MyScript recognized (label, no positions):", repr(text))
            return {"full_text": text, "lines": []}

        # 3. Last resort: top-level words list
        words_list = result.get("words", [])
        if words_list:
            text = " ".join(w.get("label", "") for w in words_list if w.get("label")).strip()
            if text:
                print("✅ MyScript recognized (words):", repr(text))
                return {"full_text": text, "lines": []}

        print("⚠️ MyScript returned empty labels. Full result:", result)
        return None

    except Exception as e:
        print("❌ MyScript recognition failed:", e)
        return None
