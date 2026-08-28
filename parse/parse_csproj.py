import xml.etree.ElementTree as ET

from parse.dependency import Dependency


def parse_csproj(content: str) -> list[Dependency]:
    csproj_packages = []
    root = ET.fromstring(content)
    if '{' in root.tag:
        ns = root.tag.split('}')[0].strip('{')
    else:
        ns = ''
    csproj_tag = f'{{{ns}}}PackageReference' if ns else 'PackageReference'
    version_tag = f'{{{ns}}}Version' if ns else 'Version'
    package_elements = root.findall('.//' + csproj_tag)
    for element in package_elements:
        package_name = element.attrib.get('Include')
        version = element.attrib.get('Version')
        if version is None:
            version_element = element.find(version_tag)
            version = (
                version_element.text.strip()
                if version_element is not None and version_element.text
                else None
            )
        if package_name:
            csproj_packages.append(
                {
                    'name': package_name.lower(),
                    'version': version,
                }
            )
    return csproj_packages