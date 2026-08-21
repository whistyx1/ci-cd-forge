import xml.etree.ElementTree as ET

def parse_pom_xml(content: str) -> list[str]:
    dependencies = []
    root = ET.fromstring(content)
    if '{' in root.tag:
        ns = root.tag.split('}')[0].strip('{')
    else:
        ns = ''
    dep_tag = f'{{{ns}}}dependency' if ns else 'dependency'
    dependency_elements = root.findall('.//' + dep_tag)
    artifact_tag = f'{{{ns}}}artifactId' if ns else 'artifactId'
    for element in dependency_elements:
        artifact_element = element.find(artifact_tag)
        if artifact_element is not None and artifact_element.text:
            dependencies.append(artifact_element.text.lower())

    return dependencies