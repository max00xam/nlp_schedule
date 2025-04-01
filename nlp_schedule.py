import re
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def numbers(text):
    n = {
        "all'una": "alle 1",

        "un'ora": "1 ora",

        "un quarto d'ora": "15 minuti",
        "mezz'ora": "30 minuti",
        "tre quarti d'ora": "45 minuti",

        "un quarto": "15 minuti",
        "e mezza": "e 30 minuti",
        "tre quarti": "45 minuti",

        "un": 1, "uno": 1, "due": 2, "tre": 3, "quattro": 4, "cinque": 5, "sei": 6, "sette": 7, "otto": 8, "nove": 9, "dieci": 10,
        "undici": 11, "dodici": 12, "tredici": 13, "quattordici": 14, "quindici": 15, "sedici": 16, "diciassette": 17, "diciotto": 18, "diciannove": 19,
        "venti": 20, "ventuno": 21, "ventidue": 22, "ventitre": 23, "ventiquattro": 24, "venticinque": 25, "ventisei": 26, "ventisette": 27, "ventotto": 28, "ventinove": 29, "trenta": 30,
        "trentuno": 31, "trentadue": 32, "trentatre": 33, "trentaquattro": 34, "trentacinque": 35, "trentasei": 36, "trentasette": 37, "trentotto": 38, "trentanove": 39, "quaranta": 40,
        "quarantuno": 41, "quarantadue": 42, "quarantatre": 43, "quarantaquattro": 44, "quarantacinque": 45, "quarantasei": 46, "quarantasette": 47, "quarantotto": 48, "quarantanove": 49, "cinquanta": 50,
        "cinquantuno": 51, "cinquantadue": 52, "cinquantatre": 53, "cinquantaquattro": 54, "cinquantacinque": 55, "cinquantasei": 56, "cinquantasette": 57, "cinquantotto": 58, "cinquantanove": 59, "sessanta": 60
    }

    for i in n.keys():
        text = text.replace(f" {i} ", f" {n[i]} ")

        if text.endswith(f" {i}"):
            text = text[:text.rfind(f" {i}")] + f" {n[i]}"

        if text.startswith(f"{i} "):
            text = f"{n[i]} " + text[len(f"{i} "):]

    return text

def is_valid_sentence(text, activation_mandatory = False):
    regexes = [
        r"^(?P<activation>jarvis)\s+",
        r"^(?P<activation>hey coso)\s+",
        r"^(?P<activation>python)\s+",
        r"(?:imposta|impostare|aggiungi|aggiungere)\s+(?:promemoria|nota|appuntamento|alert|sveglia)(?:\s+per\s+)?(?P<subject>.+)?",
        r"(?:mi\s+ricordi|ricordi|mi\s+puoi\s+ricordare|ricordare|ricordami|puoi\s+ricordarmi|ricordarmi|ricordarmelo|ricordamelo|devo\s+fare)(?:\s+(?:di|che|anche))?(?P<subject>.+)?",
        r"(?:fra|tra)\s+",
    ]

    subject = ""
    text = text.lower()
    valid = False
    activation = None
    for r in regexes:
        res = re.search(r, text)
        if res:
            if "subject" in res.groupdict(): subject = res.group("subject").strip()
            activation = "activation" in res.groupdict()
            text = text.replace(res.group(), "")
            valid = True
    if activation_mandatory and not activation: valid = False
    return valid, text.strip(), subject

def next_alert(alert):
    def make_str(alert, dt):
        str_alert = alert["year"] if alert['year'] != "*" else str(dt.year)
        str_alert += ("0" + alert["month"])[-2:] if alert['month'] != "*" else ("0" + str(dt.month))[-2:]
        str_alert += ("0" + alert["day"])[-2:] if alert['day'] != "*" else ("0" + str(dt.day))[-2:]
        str_alert += ("0" + alert["hh"])[-2:] if alert["hh"] != "*" else "12"
        str_alert += ("0" + alert["mm"])[-2:] if alert["mm"] != "*" else "00"
        str_alert += "00"
    
        return str_alert
    
    now = datetime.now()
    t_keys = [a for a in alert.keys() if a.startswith("t_") and alert[a] != "*"]
    if t_keys:
        dt = datetime.strptime(alert["time"], "%Y%m%d%H%M%S")
        for k in t_keys:
            if k == "t_hh":
                dt = dt + relativedelta(hours=int(alert["t_hh"]))

            if k == "t_mm":
                dt = dt + relativedelta(minutes=int(alert["t_mm"]))

            if k == "t_ss":
                dt = dt + relativedelta(seconds=int(alert["t_ss"]))

            if k == "t_w":
                dt = dt + relativedelta(weeks=int(alert["t_w"]))

            if k == "t_d":
                dt = dt + relativedelta(days=int(alert["t_d"]))

            if k == "t_m":
                dt = dt + relativedelta(months=int(alert["t_m"]))

            if k == "t_y":
                dt = dt + relativedelta(years=int(alert["t_y"]))

        str_alert = dt.strftime("%Y%m%d%H%M%S")

    else:
        if alert["day"] == "domani":
            dt = datetime.now() + timedelta(days=1)
            alert["day"] = str(dt.day)
            alert["month"] = str(dt.month)
            alert["year"] = str(dt.year)

        elif alert["day"] in ["dopo domani", "dopodomani"]:
            dt = datetime.now() + timedelta(days=2)
            alert["day"] = str(dt.day)
            alert["month"] = str(dt.month)
            alert["year"] = str(dt.year)

        if alert["hh"] != "*" and not int(alert["hh"]) in range(0, 24):
            return None, "invalid hh"
        
        elif alert["mm"] != "*" and not int(alert["mm"]) in range(0, 59):
            return None, "invalid mm"
        
        elif alert["year"] != "*" and int(alert["year"]) < now.year:
            return None, "invalid year"

        elif alert["month"] != "*" and not int(alert["month"]) in range(1, 13):
            return None, "invalid month"

        elif alert["day"] != "*" and not int(alert["day"]) in range(1, 32):
            return None, "invalid day"

        if alert["dow"] != "*":
            dt = datetime.now()
            if alert["hh"] != "*": dt = dt.replace(hour=int(alert["hh"]))
            if alert["mm"] != "*": dt = dt.replace(minute=int(alert["mm"]))

            while 1:
                if ["lun", "mar", "mer", "gio", "ven", "sab", "dom"][dt.weekday()] == alert["dow"][:3]:
                    if dt > datetime.now(): break

                dt = dt + timedelta(days=1)

            str_alert = make_str(alert, dt)
        else:
            str_alert = make_str(alert, now)
            
    try:    
        dt = datetime.strptime(str_alert, "%Y%m%d%H%M%S")
        
        if dt < now and alert["repeat"] != "off":
            while dt < now:
                if alert["repeat"] in "d*" and alert["day"] == "*":
                    dt = dt + timedelta(days = 1)
                    continue

                elif alert["repeat"] in "m*" and alert["month"] == "*":
                    _ = dt.strftime("%Y%m%d%H%M%S")
                    try:
                        dt = datetime.strptime(_[:4] + f"{(int(_[4:6]) + 1) % 12:02d}" + _[6:], "%Y%m%d%H%M%S")
                    except:
                        dt = dt + timedelta(days=30)
                    continue

                elif alert["repeat"] in "y*" and alert["year"] == "*":
                    _ = dt.strftime("%Y%m%d%H%M%S")
                    dt = datetime.strptime(str(int(_[:4]) + 1) + _[4:], "%Y%m%d%H%M%S")
                    continue
                    
                if alert["repeat"] == "*" and alert["dow"] != "*":
                    while 1:
                        if ["lun", "mar", "mer", "gio", "ven", "sab", "dom"][dt.weekday()] == alert["dow"][:3]:
                            if dt > datetime.now(): break

                        dt = dt + timedelta(days=1)
                    continue

            return dt, alert["remain"]
        
        elif datetime.strptime(str_alert, "%Y%m%d%H%M%S") > now:
            return datetime.strptime(str_alert, "%Y%m%d%H%M%S"), alert["remain"]

        else:
            return None, f"out of time str_alert {str_alert}"
            
    except:
        return None, f"invalid str_alert {str_alert}"
    
def make_dict(text, DEBUG = False):
    regexes = [
        "(?P<t_y>\d+)\s+ann[oi](?:\s+e\s+|\s+|$)",
        "(?P<t_m>\d+)\s+mes[ei](?:\s+e\s+|\s+|$)",
        "(?P<t_w>\d+)\s+settiman[ae](?:\s+e\s+|\s+|$)",
        "(?P<t_d>\d+)(?:\s*gg|\s+giorn[oi]|\s*g)(?:\s+e\s+|\s+|$)",

        "(?:il\s+|l')?(?P<day>\d{1,2})(?:\s+di\s+|\s+del\smese\sdi\s+|\s+del\smese\s+|\s+)(?P<month>gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)(?:\s+(?P<year>\d{4}))?(?:\s+|$)",
        "(?:il\s+|l')?(?P<day>\d{1,2})(?:\s+di\s+|\s+del\smese\sdi\s+|\s+del\smese\s+|\s+)(?P<month>gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)(?:\s+(?P<year>\d{4}))?(?:\s+|$)",
        "(?:il\s+|l')?(?P<day>\d{1,2})/(?P<month>\d{1,2})(?:/(?P<year>\d{4}))?(?:\s+|$)",
        "(?P<day>domani|dopo\s*domani)(?:\s+|$)",

        "(?P<dow>lun|mar|mer|gio|ven|sab|dom)(?:\s+|$)(?P<day>\d{1,2})?",
        "(?P<dow>luned[iì]|marted[iì]|mercoled[iì]|gioved[iì]|venerd[iì]|sabato|domenica)(?:\s+|$)(?P<day>\d{1,2})?",

        "(?:alle\s|all')(?P<hh>\d{1,2})(?:(?:(?:\s+e\s+|:)(?P<mm>\d{1,2}))(?:\s+minuti|\s+min|\s*mm|\s*m)?)?(\s+|$)",

        "(?P<t_hh>\d{1,2})(?:\s+or[ae]|\s*h{1,2})(?:\s+e\s+|\s+|$)",
        "(?P<t_mm>\d{1,2})(?:\s+minut[oi]|\s+min|\s*m{1,2})(?:\s+e\s+|\s+|$)",
        "(?P<t_ss>\d{1,2})(?:\s+second[oi]|\s+sec|\s*s{1,2})(?:\s+e\s+|\s+|$)",

        "(?:il\s+|l')(?P<day>\d{1,2})(?:\s+|$)",
    ]

    result = {"time": datetime.now().strftime("%Y%m%d%H%M%S"), "t_y": "*", "t_m": "*", "t_w": "*", "t_d": "*", "t_hh": "*", "t_mm": "*", "t_ss": "*", "hh": "*", "mm": "*", "year": "*", "month": "*", "day": "*", "dow": "*", "repeat": "", "remain": ""}
    _text = numbers(text)
    
    r = re.search(r"(?P<hh>\d+)\s+meno\s+(?P<mm>\d+)", _text)
    if r:
        _text = _text.replace(r.group(), f"{int(r.groupdict()['hh'])-1} e {60-int(r.groupdict()['mm'])}")

    if DEBUG: print(_text)
    for r in regexes:
        try:
            res = re.search(r, _text)
            if DEBUG and res == None: print(r)
        except:
            print("ERROR", r)
            return

        if res:
            if DEBUG:
                print(r)
                print("    >>>", res.groupdict())
            _text = _text.replace(res.group(), "")
            if DEBUG: print("    >>>", _text)

            for k in res.groupdict():
                if res.group(k): result[k] = res.group(k)

    for r in [
        r"(?:di\s+ogni|ogni(?:\s+(?P<day>\d+)\s+del)?|tutti\s+i|tutti\s+gli|tutti)(?:\s+(?P<repeat>ann[oi]|mes[ei]|giorn[oi]|or[ae]))?",
        r"(?:di\s+ogni|ogni(?:\s+(?P<dow>lun|mar|mer|gio|ven|sab|dom)\s+del)?|tutti\s+i|tutti\s+gli|tutti)(?:\s+(?P<repeat>ann[oi]|mes[ei]|giorn[oi]|or[ae]))?",
        r"(?:di\s+ogni|ogni(?:\s+(?P<dow>luned[iì]|marted[iì]|mercoled[iì]|gioved[iì]|venerd[iì]|sabato|domenica)\s+del)?|tutti\s+i|tutti\s+gli|tutti)(?:\s+(?P<repeat>ann[oi]|mes[ei]|giorn[oi]|or[ae]))?",
        r"(?:del\s+(?P<repeat>ann[oi]|mes[ei]))",
    ]:
        res = re.search(r, _text)
        if res:
            for k in res.groupdict():
                if res.group(k): result[k] = res.group(k)

            if DEBUG: print(r, _text)
            _text = _text.replace(res.group(), "")
            if DEBUG: print(_text)
            result["repeat"] = res.group("repeat") if res.group("repeat") else "tutti"

    months = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    s_months = [a[:3] for a in months]

    if result["month"] in months:
        result["month"] = str(months.index(result["month"]) + 1)

    if result["month"] in s_months:
        result["month"] = str(s_months.index(result["month"]) + 1)

    if result["repeat"] in ["giorno", "giorni"]:
        result["repeat"] = "d"

    elif result["repeat"] in ["mese", "mesi"]:
        result["repeat"] = "m"

    elif result["repeat"] in ["anno", "anni"]:
        result["repeat"] = "y"

    elif result["repeat"] in ["tutti"]:
        result["repeat"] = "*"

    else:
        result["repeat"] = "off"

    result["remain"] = _text.strip()

    return result

def parse(text, activation_mandatory = False, DEBUG = False):
    valid, v_text, subject = is_valid_sentence(text, activation_mandatory = activation_mandatory)

    if valid and not v_text.strip() and subject.strip():
        v_text = subject
        subject = ""

    if not valid:
        return None, "missing activation word"
    
    elif not v_text:
        return None, "invalid sentence"

    res = make_dict(v_text, DEBUG)
    if not [a for a in res.keys() if res[a] not in ["*", "off"] and a != "remain"]:
        return None, "invalid sentence"
    
    if subject: res["remain"] = subject
    return next_alert(res), res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join([a for a in sys.argv[1:] if a != "debug"])

        res = parse(text, DEBUG="debug" in sys.argv[1:])
        print({r:res[1][r] for r in res[1].keys() if res[1][r] != "*"})
        print(res[0])

    else:
        for text in [
                "fra 15 minuti ricordami di ...",
                "ogni 2 marzo ricordami che ...",
                "tutti i venerdi alle 15 e 40 ricordami che ...",
                "ogni 15 del mese ricordami che ...",
                "fra 2 ore e 40 minuti ricordami che ...",
                "fra 1h 15m ...",
                "fra mezz'ora ...",
                "fra un quarto d'ora devo fare ...",
                "domani alle 15 mi ricordi che ...",
                "il 7 alle 15 e 30 ricordami che ...",
                "il 25 di febbraio alle 22 ricordami che ...",
                "fra 5 giorni ricordami di ...",
                "fra 2 settimane ricordami ...",
                "fra 6 mesi ricordami ...",
                "fra 25 anni ricordami che ...",
                "martedi ricordami che ...",
                "ogni giovedi alle 21 mi puoi ricordare che ...",
                "martedi alle 15:30 mi puoi ricordare che ...",
                "tutti i giorni alle 15:30 mi puoi ricordare che ...",
                "ogni giorno alle 13 ricordami che ...",
                "il 15 di ogni mese ricordami che ...",
                "il 22 gennaio di ogni anno ricordami ...",
                "il 22 del mese gennaio di ogni anno ricordami ...",
                "antani come se fosse anziche no martedi",
                "jarvis ricordamelo anche alle 20 e mezza ...",
                "jarvis e anche alle 20 e un quarto ricordami ...",
                "Jarvis imposta sveglia alle 21 e 30 per ...",
                "imposta sveglia alle 21 per ...",
                "Jarvis puoi ricordarmi alle 3 meno un quarto ...",
                "il 28 febbraio alle 15 ...",
                "dopo domani alle 15 ...",
                "cioccolata con panna ...",
                "il 2 marzo 2025 alle 16 ...",
                "jarvis alle 19 ricordami di guardare il tg4"
            ]:

            print(text)
            res = parse(text)
            if res[0]:
                print({r:res[1][r] for r in res[1].keys() if res[1][r] != "*"})
                print(res[0])
                print("-"*60)
            else:
                print("ERORR:", res[1])
