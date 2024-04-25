import json

sbom = json.loads(open('clipper-api.bom').read())
licenses = set()

for component in sbom['components']:
    if 'licenses' not in component.keys():
        # print(f'NO LICENSES FOUND FOR {component["name"]}')
        continue
    for licence in component['licenses']:
        if 'license' in licence.keys():
            if 'id' in licence['license'].keys():
                licenses.add(licence['license']['id'])
            elif 'text' in licence['license'].keys():
                continue
                # licenses.add(licence['license']['text']['content'])
        elif 'expression' in licence.keys():
            licenses.add(licence['expression'])
        else:
            raise Exception('No license found')
print(licenses)