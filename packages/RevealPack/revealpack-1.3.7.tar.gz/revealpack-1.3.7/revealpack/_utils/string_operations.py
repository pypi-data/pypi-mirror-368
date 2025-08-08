import json
import re
from textwrap import indent

def dict_to_js_notation(d, indent=0):
    lines = []
    for key, value in d.items():
        if isinstance(value, dict):
            lines.append(f'{"  " * indent}{key}: {{')
            lines.append(dict_to_js_notation(value, indent + 1))
            lines.append(f'{"  " * indent}}},')
        elif isinstance(value, list):
            lines.append(f'{"  " * indent}{key}: [')
            for item in value:
                if isinstance(item, dict):
                    lines.append(f'{"  " * (indent + 1)}{{')
                    lines.append(dict_to_js_notation(item, indent + 2))
                    lines.append(f'{"  " * (indent + 1)}}},')
                else:
                    lines.append(f'{"  " * (indent + 1)}{json.dumps(item)},')
            lines.append(f'{"  " * indent}],')
        else:
            lines.append(f'{"  " * indent}{key}: {json.dumps(value)},')
    return "\n".join(lines)

def sanitize_name(name):
    """Replace spaces and invalid filename characters with underscores."""
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Replace invalid filename characters with underscores
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name

def add_offset_to_string(input_string, offset):
    """Add a constant offset to every line of the input string."""
    offset_string = ' ' * offset
    wrapped_string = indent(input_string, offset_string)
    return wrapped_string

def get_blank_scss_template():
    return """
/**
 * Custom theme for Reveal.js presentations.
 *
 * Starter theme file for RevealPack
 */

// Default mixins and settings -----------------
@import '../template/mixins';
@import '../template/settings';

// Override theme settings (see ../template/settings.scss) 
// See https://github.com/hakimel/reveal.js/blob/master/css/theme/README.md

// Theme template ------------------------------
@import '../template/theme';
// ---------------------------------------------

// include other scss/css with @import  url('<localfile.scss>') -----------

// End of Theme
"""