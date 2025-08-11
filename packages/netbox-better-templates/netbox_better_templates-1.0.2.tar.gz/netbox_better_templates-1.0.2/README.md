# Netbox Better Templates Plugin
Adds some functionality to netbox templates and config render.
The plugin uses `Monkey-patching` and injects extensions into the netbox render method.

## Installation

1. Install plugin with pip

```bash
cd /opt/netbox
source venv/bin/activate
pip install netbox_better_templates
```

2. Add `netbox_better_templates` to `local_requirements.txt` file

3. Edit the `PLUGINS` in `configuration.py`
```python
PLUGINS = [
    'netbox_better_templates'
]
```


## Added Functions

- **datetime**: adds datetime to config templates.
```jinja3
{{ datetime.now() }}
```

- **now**: standard now function of datetime.
```jinja3
{{ now() }}
```

contributors are welcome. fork for any changes you want to make