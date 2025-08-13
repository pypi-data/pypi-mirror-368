from django.views.generic import View

class AcceptJsonMixin:
    """
    Adds method to detect if JSON was requested in the Accept header
    """

    def json_response_requested(self: View) -> bool:
        """ does the request want JSON content back?"""
        if "HTTP_ACCEPT" in self.request.META:
            return self.request.META["HTTP_ACCEPT"] == "application/json"
        return False
