import json
import unittest

from app.services.registration_service import response_fields, validate_responses

BASIC_LIST = json.dumps([{"id": 1, "status": "ok"}, {"id": 2, "status": "ok"}])
PREMIUM_LIST = json.dumps([{"id": 1, "status": "ok", "extra": 1}, {"id": 2, "status": "ok", "extra": 2}])


class ResponseFieldsTest(unittest.TestCase):
    def test_object_fields(self):
        self.assertEqual(response_fields({"a": 1, "b": 2}), {"a", "b"})

    def test_list_fields_are_the_union(self):
        self.assertEqual(response_fields([{"a": 1}, {"a": 2, "b": 3}]), {"a", "b"})


class ValidateResponsesTest(unittest.TestCase):
    def test_valid_lists(self):
        self.assertEqual(validate_responses(BASIC_LIST, PREMIUM_LIST), [])

    def test_valid_objects(self):
        self.assertEqual(validate_responses('{"a": 1}', '{"a": 1, "b": 2}'), [])

    def test_invalid_json(self):
        errors = validate_responses("{nao e json", PREMIUM_LIST)
        self.assertEqual(errors, ["A resposta do plano básico não é um JSON válido."])

    def test_empty_text_is_invalid_json(self):
        errors = validate_responses(BASIC_LIST, "")
        self.assertEqual(errors, ["A resposta do plano premium não é um JSON válido."])

    def test_wrong_types(self):
        for text in ["42", '"texto"', "[1, 2]", "null", "[]", "{}", "[{}]"]:
            errors = validate_responses(text, PREMIUM_LIST)
            self.assertEqual(
                errors,
                ["A resposta do plano básico deve ser um objeto ou uma lista não vazia de objetos."],
                text,
            )

    def test_premium_must_contain_basic_fields(self):
        errors = validate_responses('{"a": 1, "b": 2}', '{"a": 1, "c": 3}')
        self.assertEqual(errors, ["O plano premium deve conter todos os campos do plano básico."])

    def test_premium_equal_to_basic(self):
        errors = validate_responses(BASIC_LIST, BASIC_LIST)
        self.assertEqual(errors, ["O plano premium deve ter pelo menos um campo a mais que o básico."])

    def test_size_limit(self):
        big = json.dumps([{"a": "x" * 21000}])
        errors = validate_responses(big, PREMIUM_LIST)
        self.assertEqual(errors, ["A resposta do plano básico deve ter até 20 KB."])


if __name__ == "__main__":
    unittest.main()
