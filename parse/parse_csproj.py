import xml.etree.ElementTree as ET

def parse_csproj(content: str) -> list[str]:
    csproj_packages = []
    root = ET.fromstring(content)
    if '{' in root.tag:
        ns = root.tag.split('}')[0].strip('{')
    else:
        ns = ''
    csproj_tag = f'{{{ns}}}PackageReference' if ns else 'PackageReference'
    package_elements = root.findall('.//' + csproj_tag)
    for element in package_elements:
        package_name = element.attrib.get('Include')
        if package_name:
            csproj_packages.append(package_name.lower())
    return csproj_packages