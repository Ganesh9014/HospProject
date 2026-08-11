from django.http import JsonResponse

from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def check_gpt_version(request):
    # client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # model_info = client.models.retrieve("gpt-4o-mini")

    return JsonResponse({
        # "id": model_info.id,
        # "created": model_info.created,
        # "owner": model_info.owned_by
    })
