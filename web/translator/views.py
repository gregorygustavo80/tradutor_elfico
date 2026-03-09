import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Import the core translator (added to sys.path via settings.py)
from translator_core import SindarinTranslator

# Module-level singleton — loaded once on startup
_translator = SindarinTranslator()


def index(request):
    """Render the main translator page."""
    return render(request, 'translator/index.html')


@require_POST
@csrf_exempt
def translate(request):
    """AJAX endpoint: receives {text, direction} and returns {result}."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        direction = data.get('direction', 'pt_to_sd')

        if not text:
            return JsonResponse({'result': ''})

        if direction == 'pt_to_sd':
            result = _translator.translate_pt_to_sd(text)
        else:
            result = _translator.translate_sd_to_pt(text)

        return JsonResponse({'result': result})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
