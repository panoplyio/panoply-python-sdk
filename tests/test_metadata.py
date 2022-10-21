import unittest

from panoply.resources import convert_to_ui_format


class TestMetadata(unittest.TestCase):

    def test_list_resources(self):

        test_cases = [
            ([{"title": "Customer", "id": "customer"},
              {"title": "Account", "id": "account"}],
             [{"name": "Customer", "value": "customer",
               "disabled": False, "requires": []},
              {"name": "Account", "value": "account",
               "disabled": False, "requires": []}
              ]),
            ([{"title": "Customer", "id": "customer", "available": False},
              {"title": "Account", "id": "account", "requires": ["Billing"]}],
             [{"name": "Customer", "value": "customer",
               "disabled": True, "requires": []},
              {"name": "Account", "value": "account",
               "disabled": False, "requires": ["Billing"]}
              ]),
            ([], None)
        ]

        for resources, expected in test_cases:
            self.assertEqual(expected, convert_to_ui_format(resources,
                                                            lambda resource: resource["title"],
                                                            lambda resource: resource["id"],
                                                            lambda resource: not resource.get("available", True),
                                                            lambda resource: resource.get("requires", [])
                                                            ))

    def test_list_fields(self):

        test_cases = [
            ([{"name": "id", "is_mandatory": True}, {"name": "name"}],
             [{"name": "id", "value": "id", "disabled": False, "requires": []},
              {"name": "name", "value": "name", "disabled": False, "requires": []}]),
            ([{"name": "id", "type": "int", "is_mandatory": True},
              {"name": "name", "type": "str"},
              {"name": "billing", "type": "list", "is_available": False}],
             [{"name": "id [int]", "value": "id", "disabled": False, "requires": []},
              {"name": "name [str]", "value": "name", "disabled": False, "requires": []},
              {"name": "billing [list]", "value": "billing", "disabled": True, "requires": []}]),
            ([], None)
        ]

        for fields, expected in test_cases:
            self.assertEqual(expected, convert_to_ui_format(fields,
                                                            lambda field: f"{field['name']} [{field['type']}]"
                                                            if field.get("type") else field["name"],
                                                            lambda field: field["name"],
                                                            lambda field: not field.get("is_available", True)
                                                            ))
