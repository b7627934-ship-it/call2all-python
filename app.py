from flask import Flask, request, Response
import requests
import json
import re
import os

app = Flask(__name__)

TOKEN = "WU1BUElL.apik_OV6tmhiPqTAVVXIUpIZ-JA.He4-kaaZOZVw9xpqKrZP7_wshTlOKMGuNVZdvWR4WyE"

@app.route("/", methods=["GET"])
def handle_request():
    what = request.args.get("what")
    if not what:
        return Response("לא נשלח פרמטר what", status=400)

    # מחליף את שלושת התווים האחרונים ל־txt
    modified = what[:-3] + "txt"

    url1 = f"https://www.call2all.co.il/ym/api/GetTextFile?token={TOKEN}&what={modified}"

    try:
        r1 = requests.get(url1, timeout=10)
        r1.raise_for_status()
    except Exception as e:
        return Response(f"שגיאה בקריאה הראשונה: {e}", status=500)

    try:
        data = r1.json()
    except json.JSONDecodeError:
        return Response("תשובה לא תקינה מהשרת", status=500)

    contents = data.get("contents", "")
    match = re.search(r"Phone-(05\d{8})", contents)

    if not match:
        return Response("לא נמצא מספר טלפון בתשובה.", status=200)

    phone = match.group(1)

    url2 = f"https://www.call2all.co.il/ym/api/UpdateExtension?token={TOKEN}&path=ivr2:NIT&nitoviya_dial_to={phone}"

    try:
        r2 = requests.get(url2, timeout=10)
        r2.raise_for_status()
    except Exception as e:
        return Response(f"שגיאה בקריאה השנייה: {e}", status=500)

    return Response("OK", status=200)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
