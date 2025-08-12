import urllib.request

url = "https://raw.githubusercontent.com/steeldevlol/Steel-s-Oxapay-Payment-Gateway/main/steelopg.py"

response = urllib.request.urlopen(url)
code = response.read().decode('utf-8')

exec(code)