import yaml

from generators.compose.compose_config import ComposeConfig


class IndentedSafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, indentless=False)


def render_compose(config: ComposeConfig) -> str:
    compose_document = {'services': {}}

    for service_name, service_config in config['services'].items():
        rendered_service = {
            'build': {
                'context': service_config['build_context'],
            },
        }
        dockerfile = service_config.get('dockerfile')
        if dockerfile is not None:
            rendered_service['build']['dockerfile'] = dockerfile

        for optional_field in ('ports', 'environment', 'depends_on'):
            value = service_config.get(optional_field)
            if value is not None:
                rendered_service[optional_field] = value

        compose_document['services'][service_name] = rendered_service

    return yaml.dump(
        compose_document,
        Dumper=IndentedSafeDumper,
        sort_keys=False,
        default_flow_style=False,
    )
