# Third Parties
from rest_framework.renderers import JSONRenderer


class APIRenderer(JSONRenderer):
    def _parse_successful_response(self, data):
        parsed_result = data
        if isinstance(data, str):
            parsed_result = {"message": data, "data": []}
        elif isinstance(data, list):
            parsed_result = {"message": None, "data": data}
        elif isinstance(data, dict):
            message = data.pop("message", None)
            parsed_result = {"message": message, "data": [data]}
        return parsed_result

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """Renders all responses and wraps it inside a defined consistent
        structure."""
        response = {"result": None, "error": None}
        is_success_response = 200 <= renderer_context["response"].status_code <= 299
        if is_success_response:
            response["result"] = self._parse_successful_response(data)
        else:
            response["error"] = data.get("error", data)

        return super().render(response, accepted_media_type, renderer_context)
