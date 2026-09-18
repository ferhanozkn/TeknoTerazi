from django.contrib.staticfiles import finders
from django.http import HttpResponse, HttpResponseNotFound


def service_worker(request):
    """Service worker'ı site köküne servis eder (PWA scope'u tüm siteyi kapsasın diye)."""
    path = finders.find("js/sw.js")
    if not path:
        return HttpResponseNotFound()
    with open(path, "rb") as f:
        content = f.read()
    response = HttpResponse(content, content_type="application/javascript")
    response["Service-Worker-Allowed"] = "/"
    return response
