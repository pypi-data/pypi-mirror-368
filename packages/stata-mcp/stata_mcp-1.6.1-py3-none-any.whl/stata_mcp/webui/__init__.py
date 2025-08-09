import json

from flask import Flask, jsonify, redirect, render_template, request, url_for

from ..config import Config
from .utils.config_validator import (create_configuration_backup,
                                     validate_configuration)

app = Flask(__name__, static_folder="templates")
config_mgr = Config()


def _create_backup():
    """Create a backup of the current configuration."""
    try:
        backup_path = create_configuration_backup(config_mgr.CONFIG_FILE_PATH)
        return backup_path
    except Exception:
        return None


def _get_current_config():
    """Get complete current configuration structure."""
    return {
        'stata': {
            'stata_cli': config_mgr.get(
                'stata.stata_cli',
                '')},
        'stata-mcp': {
            'output_base_path': config_mgr.get(
                'stata-mcp.output_base_path',
                '')},
        'llm': {
            'LLM_TYPE': config_mgr.get(
                'llm.LLM_TYPE',
                'ollama'),
            'ollama': {
                'MODEL': config_mgr.get(
                    'llm.ollama.MODEL',
                    'qwen2.5-coder:7b'),
                'BASE_URL': config_mgr.get(
                    'llm.ollama.BASE_URL',
                    'http://localhost:11434')},
            'openai': {
                'MODEL': config_mgr.get(
                    'llm.openai.MODEL',
                    'gpt-3.5-turbo'),
                'BASE_URL': config_mgr.get(
                    'llm.openai.BASE_URL',
                    'https://api.openai.com/v1'),
                'API_KEY': config_mgr.get(
                    'llm.openai.API_KEY',
                    '<YOUR_OPENAI_API_KEY>')}}}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/config', methods=['GET', 'POST'])
def config():
    errors = {}
    current_config = _get_current_config()

    if request.method == 'POST':
        # Collect all form data
        new_config = {
            'stata': {
                'stata_cli': request.form.get('stata.stata_cli', '').strip()
            },
            'stata-mcp': {
                'output_base_path': request.form.get('stata-mcp.output_base_path', '').strip()
            },
            'llm': {
                'LLM_TYPE': request.form.get('llm.LLM_TYPE', 'ollama').strip(),
                'ollama': {
                    'MODEL': request.form.get('llm.ollama.MODEL', '').strip(),
                    'BASE_URL': request.form.get('llm.ollama.BASE_URL', '').strip()
                },
                'openai': {
                    'MODEL': request.form.get('llm.openai.MODEL', '').strip(),
                    'BASE_URL': request.form.get('llm.openai.BASE_URL', '').strip(),
                    'API_KEY': request.form.get('llm.openai.API_KEY', '').strip()
                }
            }
        }

        # Validate configuration
        validation_results = validate_configuration(new_config)

        # Check if all validations pass
        all_valid = True
        for section, fields in validation_results.items():
            for field, result in fields.items():
                if isinstance(result, dict):
                    if 'valid' in result and not result['valid']:
                        all_valid = False
                        errors[f"{section}.{field}"] = result['error']
                    elif 'valid' not in result:  # Nested structure
                        for sub_field, sub_result in result.items():
                            if isinstance(
                                    sub_result,
                                    dict) and 'valid' in sub_result and not sub_result['valid']:
                                all_valid = False
                                errors[f"{section}.{field}.{sub_field}"] = sub_result['error']
                elif not result['valid']:
                    all_valid = False
                    errors[f"{section}.{field}"] = result['error']

        if all_valid:
            # Create backup before saving
            _create_backup()

            try:
                # Save all configuration sections
                for section_name, fields in new_config.items():
                    for field_name, value in fields.items():
                        if isinstance(value, dict):
                            for sub_field_name, sub_value in value.items():
                                config_mgr.set(
                                    f'{section_name}.{field_name}.{sub_field_name}', str(sub_value))
                        else:
                            config_mgr.set(
                                f'{section_name}.{field_name}', str(value))

                return redirect(url_for('config', saved='1'))
            except Exception as e:
                errors['general'] = f"Failed to save configuration: {str(e)}"

    saved = request.args.get('saved') == '1'

    return render_template(
        'config.html',
        config=current_config,
        saved=saved,
        errors=errors
    )


@app.route('/api/validate', methods=['POST'])
def validate_config():
    """API endpoint for validating configuration fields."""
    data = request.get_json()

    # Validate complete configuration structure
    validation_results = validate_configuration(data)

    return jsonify(validation_results)


@app.route('/api/reset', methods=['POST'])
def reset_config():
    """Reset configuration to defaults."""
    try:
        _create_backup()
        default_config = config_mgr._default_config()

        # Save all default configuration sections
        for section, fields in default_config.items():
            for field, value in fields.items():
                if isinstance(value, dict):
                    for sub_field, sub_value in value.items():
                        config_mgr.set(
                            f'{section}.{field}.{sub_field}', str(sub_value))
                else:
                    config_mgr.set(f'{section}.{field}', str(value))

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/export')
def export_config():
    """Export current complete configuration as JSON."""
    config_data = _get_current_config()

    response = jsonify(config_data)
    response.headers['Content-Disposition'] = 'attachment; filename=stata-mcp-config.json'
    return response


@app.route('/api/import', methods=['POST'])
def import_config():
    """Import complete configuration from JSON."""
    try:
        if 'file' not in request.files:
            return jsonify(
                {'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify(
                {'success': False, 'error': 'No file selected'}), 400

        config_data = json.load(file)

        # Validate imported configuration
        validation_results = validate_configuration(config_data)

        # Check if all validations pass
        all_valid = True
        for _section_name, fields in validation_results.items():
            for _field_name, result in fields.items():
                if isinstance(result, dict):
                    for _sub_field_name, sub_result in result.items():
                        if not sub_result['valid']:
                            all_valid = False
                            break
                elif not result['valid']:
                    all_valid = False
                    break

        if not all_valid:
            return jsonify(
                {'success': False, 'errors': validation_results}), 400

        # Create backup before importing
        _create_backup()

        # Save all imported configuration
        for section, fields in config_data.items():
            for field, value in fields.items():
                if isinstance(value, dict):
                    for sub_field, sub_value in value.items():
                        config_mgr.set(
                            f'{section}.{field}.{sub_field}', str(sub_value))
                else:
                    config_mgr.set(f'{section}.{field}', str(value))

        return jsonify({'success': True})

    except json.JSONDecodeError:
        return jsonify({'success': False, 'error': 'Invalid JSON file'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
