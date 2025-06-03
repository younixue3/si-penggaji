import pprint
import json
from django.http import HttpResponse
from django.utils.html import escape

def dd(*args):
    html = """
    <html><head><title>Dumped Variables</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        function toggleCollapse(element) {
            const arrow = element.querySelector('.arrow');
            arrow.classList.toggle('rotate-[-90deg]');
            const content = element.nextElementSibling;
            content.classList.toggle('hidden');
        }
    </script>
    <style>
        .arrow { transition: transform 0.2s; }
        .group:hover { background: rgba(255,255,255,0.03); }
        body { color-scheme: dark; }
    </style>
    </head>
    <body class="bg-gray-950 text-gray-200 font-mono p-8">
    <div class="bg-gray-900 rounded-lg p-5 mb-5 shadow-xl border border-gray-800">
        <div class="text-pink-500 text-xl mb-3 font-semibold">dd()</div>
    """

    def format_value(value, depth=0):
        indent = "  " * depth
        if isinstance(value, (dict, list)):
            is_dict = isinstance(value, dict)
            items = value.items() if is_dict else enumerate(value)
            type_name = "dict" if is_dict else "list"
            length = len(value)
            
            result = f'<div class="group rounded p-1">'
            result += f'<div class="cursor-pointer select-none flex items-center" onclick="toggleCollapse(this)">'
            result += f'<span class="arrow inline-block mr-1">▼</span>'
            result += f'<span class="italic text-purple-500">{type_name}</span> '
            result += f'<span class="text-gray-600">({length} items)</span>'
            result += '</div>'
            result += f'<div class="ml-6 space-y-1">'
            
            for k, v in items:
                key = f'<span class="text-green-500">{escape(repr(k))}</span>: ' if is_dict else ""
                result += f'<div>{indent}{key}{format_value(v, depth + 1)}</div>'
            
            result += '</div></div>'
            return result
        elif isinstance(value, str):
            return f'<span class="text-yellow-400">{escape(repr(value))}</span>'
        elif isinstance(value, (int, float)):
            return f'<span class="text-purple-500">{escape(str(value))}</span>'
        elif isinstance(value, bool):
            return f'<span class="text-pink-500">{str(value).lower()}</span>'
        elif value is None:
            return f'<span class="text-gray-600">null</span>'
        else:
            type_name = type(value).__name__
            return f'<span class="text-red-500">{type_name}</span>: <span class="text-yellow-400">{escape(repr(value))}</span>'

    for arg in args:
        html += f'<div class="mb-2">{format_value(arg)}</div>'

    html += "</div></body></html>"
    return HttpResponse(html)
