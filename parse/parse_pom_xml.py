import xml.etree.ElementTree as ET

from parse.dependency import Dependency


def parse_pom_xml(content: str) -> list[Dependency]:
    dependencies = []
    root = ET.fromstring(content)
    if '{' in root.tag:
        ns = root.tag.split('}')[0].strip('{')
    else:
        ns = ''
    dep_tag = f'{{{ns}}}dependency' if ns else 'dependency'
    dependency_elements = root.findall('.//' + dep_tag)
    artifact_tag = f'{{{ns}}}artifactId' if ns else 'artifactId'
    version_tag = f'{{{ns}}}version' if ns else 'version'
    for element in dependency_elements:
        artifact_element = element.find(artifact_tag)
        version_element = element.find(version_tag)
        version = (
            version_element.text.strip()
            if version_element is not None and version_element.text
            else None
        )
        if artifact_element is not None and artifact_element.text:
            dependencies.append(
                {
                    'name': artifact_element.text.strip().lower(),
                    'version': version,
                }
            )

    return dependencies