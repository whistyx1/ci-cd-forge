def validate_multistage_config(
    config: object,
) -> None:
    if not isinstance(config, dict):
        raise ValueError('Config must be a dictionary.')

    accepted_strategies = ('single', 'multi')
    multi_stage_fields = (
        'runtime_image',
        'artifact_source',
        'artifact_destination',
    )
    required_fields = (
        *multi_stage_fields,
        'build_command',
    )

    strategy = config.get('strategy', 'single')
    if strategy not in accepted_strategies:
        raise ValueError("strategy must be 'single' or 'multi'.")

    if strategy == 'single':
        for field in multi_stage_fields:
            if config.get(field) is not None:
                raise ValueError(
                    f'{field} is only allowed for multi-stage strategy.'
                )
        return

    for field in required_fields:
        value = config.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f'{field} is required for multi-stage strategy.'
            )
