from django.utils import translation

# from django.utils.translation import gettext as _


def get_language(request):
    language = translation.get_language()
    translation.activate(language)
    context = {"language": language}
    return context
