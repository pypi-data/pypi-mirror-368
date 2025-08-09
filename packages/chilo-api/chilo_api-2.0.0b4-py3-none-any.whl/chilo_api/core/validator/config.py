from typing import Any, Dict, Optional


class ConfigValidator:
    '''
    A class to validate configuration settings for the API.
    This class checks if the configuration settings are of the correct type, required fields are present,
    and if any custom validation rules are met.
    Attributes
    ---------- 
    VALIDATION_RULES: List[Tuple[str, type, bool, Optional[str]]]
        A list of tuples where each tuple contains the field name, expected type, whether it is required, and an optional custom error message.
    ENUM_RULES: Dict[str, Tuple[str, ...]]
        A dictionary where each key is a field name and the value is a tuple of valid values for that field.
    Methods
    ----------
    validate(**kwargs: Any) -> None:
        Validates the provided configuration settings against the defined rules.
    '''
    VALIDATION_RULES = [
        ('base_path', str, False, None),
        ('handlers', str, True, 'handlers is required; must be glob pattern string {route: file_path}'),
        ('openapi', str, False, 'schema should either be file path string'),
        ('openapi_validate_request', bool, False, None),
        ('openapi_validate_response', bool, False, None),
        ('verbose', bool, False, None),
    ]
    ENUM_RULES = {
        'cache_mode': ('all', 'static-only', 'dynamic-only')
    }

    @staticmethod
    def validate(**kwargs: Any) -> None:
        # Standard type validations
        for field, expected_type, required, custom_msg in ConfigValidator.VALIDATION_RULES:
            ConfigValidator._validate_field(kwargs, field, expected_type, required, custom_msg)

        # Custom validations
        ConfigValidator._validate_cache_size(kwargs)
        ConfigValidator._validate_openapi_dependencies(kwargs)
        ConfigValidator._validate_enums(kwargs)

    @staticmethod
    def _validate_field(kwargs: Dict[str, Any], field: str, expected_type: type,required: bool, custom_msg: Optional[str] = None) -> None:
        value = kwargs.get(field)
        if value is None:
            if required:
                raise RuntimeError(custom_msg or f'{field} is required')
            return

        if not isinstance(value, expected_type):
            msg = custom_msg or f'{field} must be a {expected_type.__name__}'
            raise RuntimeError(msg)

    @staticmethod
    def _validate_cache_size(kwargs: Dict[str, Any]) -> None:
        cache_size = kwargs.get('cache_size')
        if cache_size is not None and not isinstance(cache_size, int):
            raise RuntimeError('cache_size should be an int (0 for unlimited size) or None (to disable route caching)')

    @staticmethod
    def _validate_openapi_dependencies(kwargs: Dict[str, Any]) -> None:
        if kwargs.get('openapi_validate_request') and kwargs.get('openapi') is None:
            raise RuntimeError('schema is required to use openapi_validate_request')

    @staticmethod
    def _validate_enums(kwargs: Dict[str, Any]) -> None:
        for field, valid_values in ConfigValidator.ENUM_RULES.items():
            value = kwargs.get(field)
            if value and value not in valid_values:
                raise RuntimeError(f'{field} should be one of: {", ".join(valid_values)}')
