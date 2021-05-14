import json
import os
import requests

headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
datas = json.dumps({"sentence": "this is a test"})

r = requests.post("http://0.0.0.0:9988/NLP/dependency_analysis", data=datas, headers=headers)
print(r.text)

