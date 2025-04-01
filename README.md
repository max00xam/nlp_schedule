# nlp_schedule

una libreria per il parsing di frasi in italiano che contengono un "promemoria"
ad esempio "fra 15 minuti ricordami ..." oppure "ogni venerdì all 15 ricordami ...°

esempio di utilizzo:

```
>>> from nlp_schedule import parse
>>> result, _dict = parse("domani alle 15 e 30 ricordami di fare la spesa")
>>> result
(datetime.datetime(2025, 4, 2, 15, 30), 'fare la spesa')
>>> _dict
{'time': '20250401185745', 't_y': '*', 't_m': '*', 't_w': '*', 't_d': '*', 't_hh': '*', 't_mm': '*', 't_ss': '*',
'hh': '15', 'mm': '30', 'year': '2025', 'month': '4', 'day': '2', 'dow': '*', 'repeat': 'off', 'remain': 'fare la spesa'}
```
