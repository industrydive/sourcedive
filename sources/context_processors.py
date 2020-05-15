from django.conf import settings


def sources_context_processor(request):
    context = {}
    context['test_env'] = settings.TEST_ENV

    return context
