import unittest

from panoply.resources import (list_resources, list_fields)


class TestMetadata(unittest.TestCase):

    def test_list_resources(self):

        test_cases = [
            ([{"title": "Customer", "id": "customer"},
              {"title": "Account", "id": "account"}],
             [{"name": "Customer", "value": "customer",
               "disabled": False, "required": False, "requires": []},
              {"name": "Account", "value": "account",
               "disabled": False, "required": False, "requires": []}
              ]),
            ([{"title": "Customer", "id": "customer", "available": False},
              {"title": "Account", "id": "account", "requires": ["Billing"]}],
             [{"name": "Customer", "value": "customer",
               "disabled": True, "required": False, "requires": []},
              {"name": "Account", "value": "account",
               "disabled": False, "required": False, "requires": ["Billing"]}
              ]),
            ([], None)
        ]

        for test_case, expected in test_cases:
            self.assertEqual(expected, list_resources(test_case))

    def test_list_fields(self):

        test_cases = [
            ([{"name": "id", "is_mandatory": True}, {"name": "name"}],
             [{"name": "id", "value": "id", "type": None,
               "is_mandatory": True, "disabled": False},
              {"name": "name", "value": "name", "type": None,
               "is_mandatory": False, "disabled": False}
              ]),
            ([{"name": "id", "type": "int", "is_mandatory": True},
              {"name": "name", "type": "str"},
              {"name": "billing", "type": "list", "is_available": False}],
             [{"name": "id [int]", "value": "id", "type": "int",
               "is_mandatory": True, "disabled": False},
              {"name": "name [str]", "value": "name", "type": "str",
               "is_mandatory": False, "disabled": False},
              {"name": "billing [list]", "value": "billing", "type": "list",
               "is_mandatory": False, "disabled": True}]),
            ([], None)
        ]

        for test_case, expected in test_cases:
            self.assertEqual(expected, list_fields(test_case))
