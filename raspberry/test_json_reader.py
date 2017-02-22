import json

with open('experiment_settings.json','r') as f:
    settings = f.read().replace('\n', ' ').replace('\r', '')
    settings = json.loads(settings)
print settings

raw_input('done')
