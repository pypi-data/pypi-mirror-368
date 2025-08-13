import os
import re
from pathlib import Path
from typing import Any

import click
import yaml


@click.command()
@click.option(
    "--config", "-c", type=click.Path(exists=True), default="agentup.yml", help="Path to agent configuration file"
)
@click.option("--check-env", "-e", is_flag=True, help="Check environment variables")
@click.option("--check-handlers", "-h", is_flag=True, help="Check handler implementations")
@click.option("--strict", "-s", is_flag=True, help="Strict validation (fail on warnings)")
def validate(config: str, check_env: bool, check_handlers: bool, strict: bool):
    """Validate your agent configuration.

    Checks for:
    - Valid YAML syntax
    - Required fields
    - Plugin definitions
    - Service configurations
    - System prompt configuration
    - Plugin system prompts
    - Environment variables (with --check-env)
    - Handler implementations (with --check-handlers)
    """
    click.echo(click.style(f"Validating {config}...\n", fg="bright_blue", bold=True))

    errors = []
    warnings = []

    # Load and parse YAML
    config_data = load_yaml_config(config, errors)
    if not config_data:
        display_results(errors, warnings)
        return

    # Validate structure
    validate_required_fields(config_data, errors, warnings)
    validate_agent_section(config_data, errors, warnings)
    validate_plugins_section(config_data.get("plugins", []), errors, warnings)

    # Validate AI configuration against plugins requirements
    validate_ai_requirements(config_data, errors, warnings)

    # Optional validations
    if "services" in config_data:
        validate_services_section(config_data["services"], errors, warnings)

    if "security" in config_data:
        validate_security_section(config_data["security"], errors, warnings)

    if "middleware" in config_data:
        validate_middleware_section(config_data["middleware"], errors, warnings)

    # Validate AI system prompt configuration
    if "ai" in config_data:
        validate_system_prompt_section(config_data["ai"], errors, warnings)

    # Check environment variables
    if check_env:
        check_environment_variables(config_data, errors, warnings)

    # Check handler implementations
    if check_handlers:
        check_handler_implementations(config_data.get("plugins", []), errors, warnings)

    # Display results
    display_results(errors, warnings, strict)


def load_yaml_config(config_path: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        with open(config_path) as f:
            content = f.read()

        # Check for common YAML issues
        if "\t" in content:
            errors.append("YAML files should not contain tabs. Use spaces for indentation.")

        config = yaml.safe_load(content)

        if not isinstance(config, dict):
            errors.append("Configuration must be a YAML dictionary/object")
            return None

        click.echo(f"{click.style('✓', fg='green')} Valid YAML syntax")
        return config

    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML syntax: {str(e)}")
        return None
    except Exception as e:
        errors.append(f"Error reading configuration: {str(e)}")
        return None


def validate_required_fields(config: dict[str, Any], errors: list[str], warnings: list[str]):
    # Check for new flat format (name, description at top level) or old nested format (agent section)
    has_old_format = "agent" in config
    has_new_format = "name" in config and "description" in config

    if not has_old_format and not has_new_format:
        errors.append("Missing required fields: either 'agent' section or top-level 'name' and 'description'")

    # Plugins are always required
    if "plugins" not in config:
        errors.append("Missing required field: 'plugins'")
    elif not config["plugins"]:
        errors.append("Required field 'plugins' is empty")

    # Check for unknown top-level fields
    known_fields = {
        # Old nested format
        "agent",
        # New flat format - top-level agent info
        "name",
        "description",
        "version",
        # Common sections
        "plugins",
        "services",
        "security",
        "ai",
        "ai_provider",
        "mcp",
        "middleware",
        "monitoring",
        "observability",
        "development",
        "push_notifications",
        "state_management",
        "cache",
        "logging",
    }
    unknown_fields = set(config.keys()) - known_fields

    if unknown_fields:
        warnings.append(f"Unknown configuration fields: {', '.join(unknown_fields)}")


def validate_agent_section(config: dict[str, Any], errors: list[str], warnings: list[str]):
    # Check if using old nested format
    if "agent" in config:
        agent = config["agent"]
        if not agent:
            return
        required_agent_fields = ["name", "description"]
        for field in required_agent_fields:
            if field not in agent:
                errors.append(f"Missing required agent field: '{field}'")
            elif not agent[field] or not str(agent[field]).strip():
                errors.append(f"Agent field '{field}' is empty")
    else:
        # New flat format - check top-level fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: '{field}'")
            elif not config[field] or not str(config[field]).strip():
                errors.append(f"Field '{field}' is empty")

    # Validate version format if present (check both old and new formats)
    version = None
    if "agent" in config and "version" in config["agent"]:
        version = config["agent"]["version"]
    elif "version" in config:
        version = config["version"]

    if version and not re.match(r"^\d+\.\d+\.\d+", str(version)):
        warnings.append(f"Version '{version}' doesn't follow semantic versioning (x.y.z)")


def validate_plugins_section(plugins: list[dict[str, Any]], errors: list[str], warnings: list[str]):
    if not plugins:
        errors.append("No plugins defined. At least one plugin is required.")
        return

    if not isinstance(plugins, list):
        errors.append("Plugins must be a list")
        return

    plugin_ids = set()

    for i, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            errors.append(f"Plugin {i} must be a dictionary")
            continue

        # Required plugin fields
        required_plugin_fields = ["plugin_id", "name", "description", "package"]

        for field in required_plugin_fields:
            if field not in plugin:
                if field == "package":
                    errors.append(f"Plugin {i} missing required field: '{field}' (needed for plugin system security)")
                else:
                    errors.append(f"Plugin {i} missing required field: '{field}'")
            elif not plugin[field]:
                errors.append(f"Plugin {i} field '{field}' is empty")

        # Check for duplicate plugin IDs
        plugin_id = plugin.get("plugin_id")
        if plugin_id:
            if plugin_id in plugin_ids:
                errors.append(f"Duplicate plugin ID: '{plugin_id}'")
            else:
                plugin_ids.add(plugin_id)

            # Validate plugin ID format
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", plugin_id):
                errors.append(
                    f"Invalid plugin ID '{plugin_id}'. Must start with letter and contain only letters, numbers, and underscores."
                )

        # Validate package name format (PyPI naming conventions)
        package_name = plugin.get("package")
        if package_name:
            if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$", package_name):
                errors.append(
                    f"Invalid package name '{package_name}' for plugin {i}. Must follow PyPI naming conventions (letters, numbers, dots, hyphens, underscores)."
                )
            # Warn about common naming issues
            if package_name.startswith("-") or package_name.endswith("-"):
                errors.append(f"Package name '{package_name}' cannot start or end with hyphen")
            if package_name.startswith(".") or package_name.endswith("."):
                errors.append(f"Package name '{package_name}' cannot start or end with dot")
            if "__" in package_name:
                warnings.append(f"Package name '{package_name}' contains double underscores, which may cause issues")

        # Validate regex patterns (if provided for capability detection)
        patterns = plugin.get("patterns", [])
        for pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as e:
                errors.append(f"Plugin {i} has invalid regex pattern '{pattern}': {e}")

        # Validate input/output modes
        input_mode = plugin.get("input_mode", "text")
        output_mode = plugin.get("output_mode", "text")
        valid_modes = ["text", "multimodal"]

        if input_mode not in valid_modes:
            errors.append(f"Plugin {i} has invalid input_mode '{input_mode}'. Must be one of: {valid_modes}")
        if output_mode not in valid_modes:
            errors.append(f"Plugin {i} has invalid output_mode '{output_mode}'. Must be one of: {valid_modes}")

        # Validate middleware if present (deprecated in favor of middleware_override)
        if "middleware" in plugin:
            warnings.append(
                f"Plugin '{plugin_id}' uses deprecated 'middleware' field. Use 'middleware_override' instead."
            )
            validate_middleware_config(plugin["middleware"], plugin_id, errors, warnings)

        # Validate middleware_override if present
        if "middleware_override" in plugin:
            validate_middleware_config(plugin["middleware_override"], plugin_id, errors, warnings)

    click.echo(f"{click.style('✓', fg='green')} Found {len(plugins)} plugin(s)")


def validate_middleware_config(
    middleware: list[dict[str, Any]], plugin_id: str, errors: list[str], warnings: list[str]
):
    if not isinstance(middleware, list):
        errors.append(f"Plugin '{plugin_id}' middleware must be a list")
        return

    valid_middleware_types = {"rate_limit", "cache", "retry", "logging", "timing", "transform"}

    for mw in middleware:
        if not isinstance(mw, dict):
            errors.append(f"Plugin '{plugin_id}' middleware entry must be a dictionary")
            continue

        if "type" not in mw:
            errors.append(f"Plugin '{plugin_id}' middleware missing 'type' field")
            continue

        mw_type = mw["type"]
        if mw_type not in valid_middleware_types:
            warnings.append(f"Plugin '{plugin_id}' has unknown middleware type: '{mw_type}'")

        # Validate specific middleware configurations
        if mw_type == "rate_limit" and "requests_per_minute" in mw:
            try:
                rpm = int(mw["requests_per_minute"])
                if rpm <= 0:
                    errors.append(f"Plugin '{plugin_id}' rate limit must be positive")
            except (ValueError, TypeError):
                errors.append(f"Plugin '{plugin_id}' rate limit must be a number")

        if mw_type == "cache" and "ttl" in mw:
            try:
                ttl = int(mw["ttl"])
                if ttl <= 0:
                    errors.append(f"Plugin '{plugin_id}' cache TTL must be positive")
            except (ValueError, TypeError):
                errors.append(f"Plugin '{plugin_id}' cache TTL must be a number")


def validate_services_section(services: dict[str, Any], errors: list[str], warnings: list[str]):
    if not isinstance(services, dict):
        errors.append("Services must be a dictionary")
        return

    for service_name, service_config in services.items():
        if not isinstance(service_config, dict):
            errors.append(f"Service '{service_name}' configuration must be a dictionary")
            continue

        if "type" not in service_config:
            errors.append(f"Service '{service_name}' missing 'type' field")

        if "config" not in service_config:
            warnings.append(f"Service '{service_name}' has no configuration")

        # Validate specific service types
        service_type = service_config.get("type")

        if service_type == "database":
            if "config" in service_config:
                db_config = service_config["config"]
                if "url" not in db_config and "connection_string" not in db_config:
                    warnings.append(f"Database service '{service_name}' missing connection configuration")

    click.echo(f"{click.style('✓', fg='green')} Services configuration valid")


def validate_security_section(security: dict[str, Any], errors: list[str], warnings: list[str]):
    if not isinstance(security, dict):
        errors.append("Security must be a dictionary")
        return

    # Check if security is enabled
    if not security.get("enabled", False):
        click.echo(f"{click.style('✓', fg='green')} Security disabled")
        return

    # Validate auth configuration
    if "auth" not in security:
        errors.append("Security configuration missing 'auth' field when enabled")
        return

    auth = security["auth"]
    if not isinstance(auth, dict):
        errors.append("Security auth must be a dictionary")
        return

    # Check which auth types are configured
    auth_types = []
    if "api_key" in auth:
        auth_types.append("api_key")
        validate_api_key_auth(auth["api_key"], errors, warnings)
    if "jwt" in auth:
        auth_types.append("jwt")
        validate_jwt_auth(auth["jwt"], errors, warnings)
    if "oauth2" in auth:
        auth_types.append("oauth2")
        validate_oauth2_auth(auth["oauth2"], errors, warnings)

    if not auth_types:
        errors.append("No authentication method configured in security.auth")
    elif len(auth_types) > 1:
        warnings.append(f"Multiple auth methods configured: {', '.join(auth_types)}. Only one will be active.")

    # Validate scope hierarchy if present
    if "scope_hierarchy" in security:
        validate_scope_hierarchy(security["scope_hierarchy"], errors, warnings)

    click.echo(f"{click.style('✓', fg='green')} Security configuration valid")


def validate_api_key_auth(api_key_config: dict[str, Any], errors: list[str], warnings: list[str]):
    if "keys" not in api_key_config:
        errors.append("API key auth missing 'keys' field")
        return

    keys = api_key_config.get("keys", [])
    if not isinstance(keys, list) or not keys:
        errors.append("API key auth 'keys' must be a non-empty list")
        return

    for i, key_config in enumerate(keys):
        if not isinstance(key_config, dict):
            errors.append(f"API key {i} must be a dictionary")
            continue
        if "key" not in key_config:
            errors.append(f"API key {i} missing 'key' field")
        if "scopes" in key_config and not isinstance(key_config["scopes"], list):
            errors.append(f"API key {i} 'scopes' must be a list")


def validate_jwt_auth(jwt_config: dict[str, Any], errors: list[str], warnings: list[str]):
    if "secret_key" not in jwt_config:
        errors.append("JWT auth missing 'secret_key' field")

    if "algorithm" in jwt_config:
        valid_algorithms = {"HS256", "HS384", "HS512", "RS256", "RS384", "RS512", "ES256", "ES384", "ES512"}
        if jwt_config["algorithm"] not in valid_algorithms:
            warnings.append(f"Unknown JWT algorithm: {jwt_config['algorithm']}")


def validate_oauth2_auth(oauth2_config: dict[str, Any], errors: list[str], warnings: list[str]):
    if "validation_strategy" not in oauth2_config:
        errors.append("OAuth2 auth missing 'validation_strategy' field")

    if oauth2_config.get("validation_strategy") == "jwt":
        required_fields = ["jwks_url", "jwt_algorithm", "jwt_issuer"]
        for field in required_fields:
            if field not in oauth2_config:
                errors.append(f"OAuth2 JWT validation missing '{field}' field")


def validate_scope_hierarchy(scope_hierarchy: dict[str, Any], errors: list[str], warnings: list[str]):
    if not isinstance(scope_hierarchy, dict):
        errors.append("Scope hierarchy must be a dictionary")
        return

    for scope, children in scope_hierarchy.items():
        if not isinstance(children, list):
            errors.append(f"Scope '{scope}' children must be a list")


def check_environment_variables(config: dict[str, Any], errors: list[str], warnings: list[str]):
    env_var_pattern = re.compile(r"\$\{([^:}]+)(?::([^}]+))?\}")
    missing_vars = []

    def check_value(value: Any, path: str = ""):
        if isinstance(value, str):
            matches = env_var_pattern.findall(value)
            for var_name, default in matches:
                if not os.getenv(var_name) and not default:
                    missing_vars.append((var_name, path))
        elif isinstance(value, dict):
            for k, v in value.items():
                check_value(v, f"{path}.{k}" if path else k)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                check_value(item, f"{path}[{i}]")

    check_value(config)

    if missing_vars:
        click.echo(f"\n{click.style('Environment Variables:', fg='yellow')}")
        for var_name, path in missing_vars:
            warnings.append(f"Missing environment variable '{var_name}' referenced in {path}")
    else:
        click.echo(f"{click.style('✓', fg='green')} All environment variables present or have defaults")


def check_handler_implementations(plugins: list[dict[str, Any]], errors: list[str], warnings: list[str]):
    handlers_path = Path("src/agent/handlers.py")

    if not handlers_path.exists():
        errors.append("handlers.py not found at src/agent/handlers.py")
        return

    try:
        with open(handlers_path) as f:
            handlers_content = f.read()

        click.echo(f"\n{click.style('Handler Implementations:', fg='yellow')}")

        for plugin in plugins:
            plugin_id = plugin.get("plugin_id")
            if not plugin_id:
                continue

            # Check for handler registration
            if f'@register_handler("{plugin_id}")' in handlers_content:
                click.echo(f"{click.style('✓', fg='green')} Handler found for '{plugin_id}'")
            else:
                warnings.append(f"No handler implementation found for plugin '{plugin_id}'")

            # Check for handler function
            if f"def handle_{plugin_id}" not in handlers_content:
                warnings.append(f"Handler function 'handle_{plugin_id}' not found")

    except Exception as e:
        errors.append(f"Error checking handlers: {str(e)}")


def validate_ai_requirements(config: dict[str, Any], errors: list[str], warnings: list[str]):
    ai_provider = config.get("ai_provider", {})

    # If AI is configured, validate the configuration
    if ai_provider:
        # Validate AI provider configuration
        if "provider" not in ai_provider:
            errors.append("AI provider configuration missing 'provider' field")
        else:
            provider = ai_provider["provider"]

            # Validate provider-specific requirements
            if provider == "openai":
                if "api_key" not in ai_provider:
                    errors.append("OpenAI provider requires 'api_key' field")
            elif provider == "anthropic":
                if "api_key" not in ai_provider:
                    errors.append("Anthropic provider requires 'api_key' field")
            elif provider == "ollama":
                # Ollama doesn't require API key but might need base_url
                pass
            else:
                warnings.append(f"Unknown AI provider: '{provider}'")

            # Validate common AI provider fields
            if "model" not in ai_provider:
                warnings.append("AI provider configuration missing 'model' field - will use provider default")

    click.echo(f"{click.style('✓', fg='green')} AI requirements validated")


def validate_system_prompt_section(ai_config: dict[str, Any], errors: list[str], warnings: list[str]):
    if not isinstance(ai_config, dict):
        return

    system_prompt = ai_config.get("system_prompt")
    if not system_prompt:
        return  # System prompt is optional

    if not isinstance(system_prompt, str):
        errors.append("AI system_prompt must be a string")
        return

    # Validate prompt length
    if len(system_prompt) < 10:
        warnings.append("System prompt is very short (< 10 characters)")
    elif len(system_prompt) > 8000:
        warnings.append("System prompt is very long (> 8000 characters) - may impact performance")

    # Check for common prompt injection patterns
    dangerous_patterns = [
        "ignore previous instructions",
        "disregard",
        "forget everything",
        "jailbreak",
        "developer mode",
    ]

    prompt_lower = system_prompt.lower()
    for pattern in dangerous_patterns:
        if pattern in prompt_lower:
            warnings.append(f"System prompt contains potentially risky pattern: '{pattern}'")

    # Validate prompt structure
    if not any(word in prompt_lower for word in ["you are", "your role", "assistant", "help"]):
        warnings.append("System prompt may lack clear role definition")

    click.echo(f"{click.style('✓', fg='green')} System prompt validated")


def validate_middleware_section(
    middleware: dict[str, Any] | list[dict[str, Any]], errors: list[str], warnings: list[str]
):
    # Handle new object-based format
    if isinstance(middleware, dict):
        valid_middleware_sections = {
            "enabled",
            "rate_limiting",
            "caching",
            "cache",
            "retry",
            "logging",
            "timeout_seconds",
            "enable_metrics",
            "debug_mode",
            "custom_middleware",
        }

        for section_name, section_config in middleware.items():
            if section_name not in valid_middleware_sections:
                warnings.append(f"Unknown middleware section: '{section_name}'")

            # Special validation for enabled field
            if section_name == "enabled":
                if not isinstance(section_config, bool):
                    errors.append("Middleware 'enabled' field must be a boolean")
                continue

            # Other fields that are not objects
            if section_name in {"timeout_seconds", "enable_metrics", "debug_mode"}:
                continue

            # Validate nested objects
            if section_name in {"rate_limiting", "caching", "cache", "retry", "logging"} and not isinstance(
                section_config, dict
            ):
                errors.append(f"Middleware section '{section_name}' must be an object")
        return

    # Handle old list-based format
    if not isinstance(middleware, list):
        errors.append("Middleware section must be a list or object")
        return

    valid_middleware_names = {"timed", "cached", "rate_limited", "retryable"}

    for i, middleware_config in enumerate(middleware):
        if not isinstance(middleware_config, dict):
            errors.append(f"Middleware item {i} must be an object")
            continue

        if "name" not in middleware_config:
            errors.append(f"Middleware item {i} missing required 'name' field")
            continue

        middleware_name = middleware_config["name"]
        if middleware_name not in valid_middleware_names:
            warnings.append(
                f"Unknown middleware '{middleware_name}' in global config. Valid options: {', '.join(valid_middleware_names)}"
            )

        # Validate specific middleware parameters
        params = middleware_config.get("params", {})
        if middleware_name == "cached" and "ttl" in params:
            if not isinstance(params["ttl"], int) or params["ttl"] <= 0:
                errors.append("Cached middleware 'ttl' parameter must be a positive integer")

        elif middleware_name == "rate_limited" and "requests_per_minute" in params:
            if not isinstance(params["requests_per_minute"], int) or params["requests_per_minute"] <= 0:
                errors.append("Rate limited middleware 'requests_per_minute' parameter must be a positive integer")

    click.echo(
        f"{click.style('✓', fg='green')} Middleware configuration validated ({len(middleware)} middleware items)"
    )


def display_results(errors: list[str], warnings: list[str], strict: bool = False):
    click.echo(f"\n{click.style('Validation Results:', fg='bright_blue', bold=True)}")

    if errors:
        click.echo(f"\n{click.style('✗ Errors:', fg='red', bold=True)}")
        for error in errors:
            click.echo(f"  • {error}")

    if warnings:
        click.echo(f"\n{click.style('  Warnings:', fg='yellow', bold=True)}")
        for warning in warnings:
            click.echo(f"  • {warning}")

    if not errors and not warnings:
        click.echo(f"\n{click.style('✓ Configuration is valid!', fg='green', bold=True)}")
        click.echo("Your agent configuration passed all validation checks.")
    elif not errors:
        click.echo(f"\n{click.style('✓ Configuration is valid with warnings', fg='green')}")
        if strict:
            click.echo(f"{click.style('✗ Failed strict validation due to warnings', fg='red')}")
            exit(1)
    else:
        click.echo(f"\n{click.style('✗ Configuration is invalid', fg='red', bold=True)}")
        click.echo(f"Found {len(errors)} error(s) and {len(warnings)} warning(s)")
        exit(1)
