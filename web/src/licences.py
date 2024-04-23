import json

sbom = json.loads(open('clipper-react.bom').read())
licenses = set()

for component in sbom['components']:
    if 'licenses' not in component.keys():
        continue
    for licence in component['licenses']:
        if 'license' in licence.keys():
            licenses.add(licence['license']['id'])
        elif 'expression' in licence.keys():
            licenses.add(licence['expression'])
        else:
            raise Exception('No license found')
print(licenses)