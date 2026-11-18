from django.test import SimpleTestCase
from drf_spectacular.generators import SchemaGenerator


class OpenApiRequestSchemaTests(SimpleTestCase):
    """Checks that custom API request bodies are present in OpenAPI."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schema = SchemaGenerator().get_schema(request=None, public=True)

    def get_request_schema(self, method, path):
        request_body = self.schema["paths"][path][method]["requestBody"]
        request_schema = request_body["content"]["application/json"]["schema"]

        if "$ref" in request_schema:
            component = request_schema["$ref"].rsplit("/", 1)[-1]
            return self.schema["components"]["schemas"][component]

        return request_schema

    def test_action_request_bodies_include_required_fields(self):
        cases = {
            ("patch", "/api/administradores/alunos/{aluno_id}/creditos/"): {
                "quantidade",
            },
            ("delete", "/api/responsaveis/{id}/inscricoes/cancelar/"): {
                "aluno_id",
                "sessao_id",
                "motivo",
            },
            ("patch", "/api/sessoes/{id}/presencas/{aluno_id}/"): {
                "status",
            },
        }

        for (method, path), expected_fields in cases.items():
            with self.subTest(method=method, path=path):
                request_schema = self.get_request_schema(method, path)
                self.assertTrue(
                    expected_fields <= set(request_schema["properties"])
                )
                self.assertTrue(
                    expected_fields <= set(request_schema.get("required", []))
                )

    def test_administrative_registration_documents_each_input_shape(self):
        request_schema = self.get_request_schema(
            "post",
            "/api/administradores/usuarios/",
        )
        self.assertEqual(len(request_schema["oneOf"]), 6)

        variants = [
            self.schema["components"]["schemas"][
                reference["$ref"].rsplit("/", 1)[-1]
            ]
            for reference in request_schema["oneOf"]
        ]
        required_fields = [set(variant.get("required", [])) for variant in variants]

        self.assertTrue(
            any({"password", "username"} <= fields for fields in required_fields)
        )
        self.assertTrue(
            any(
                {"tipo", "alunos", "email", "dataNascimento", "username"}
                <= fields
                for fields in required_fields
            )
        )
        self.assertTrue(
            all(
                any(field in fields for fields in required_fields)
                for field in ("especialidade", "CREFITO", "CRP", "CRN")
            )
        )
