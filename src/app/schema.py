from drf_spectacular.openapi import AutoSchema


class DeleteBodyAutoSchema(AutoSchema):
    """Keep custom action request schemas accurate for the API's input methods."""

    def _get_request_body(self, direction="request"):
        action = getattr(self.view, "action", None)
        needs_body_override = (
            self.method == "DELETE" and action == "cancelar_inscricao"
        ) or (
            self.method == "PATCH"
            and action in {"gerenciar_creditos", "registrar_presenca"}
        )

        if needs_body_override:
            # Spectacular omits DELETE bodies and treats every PATCH as partial.
            self.method = "POST"
            try:
                return super()._get_request_body(direction)
            finally:
                self.method = "DELETE" if action == "cancelar_inscricao" else "PATCH"

        return super()._get_request_body(direction)
