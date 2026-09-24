import unittest
from app.engine.validator import validate_workflow


class ValidatorTest(unittest.TestCase):
    def test_missing_fields_are_collected(self):
        self.assertEqual(len(validate_workflow({})), 2)

    def test_errors_in_multiple_states(self):
        errors = validate_workflow({"StartAt": "Missing", "States": {
            "A": {"Type": "Task", "Next": "Missing"},
            "B": {"Type": "Wait", "End": True}, "C": {},
            "D": {"Type": "Parallel", "End": True},
            "E": {"Type": "Choice"}}})
        for text in ("StartAt", "Resource", "Next", "Seconds", "Type", "Branches", "Choices"):
            self.assertTrue(any(text in e["path"] or text in e["message"] for e in errors), text)

    def test_nested_scope(self):
        errors = validate_workflow({"StartAt": "P", "States": {
            "P": {"Type": "Parallel", "End": True, "Branches": [
                {"StartAt": "A", "States": {"A": {"Type": "Pass", "Next": "P"}}}
            ]}}})
        self.assertEqual(len(errors), 1)
        self.assertIn("Branches[0]", errors[0]["path"])

    def test_terminals(self):
        for state in ({"Type": "Pass", "End": True}, {"Type": "Succeed"}, {"Type": "Fail", "End": True}):
            self.assertEqual(validate_workflow({"StartAt": "A", "States": {"A": state}}), [])

    def test_malformed_values(self):
        for state in ([], None, {"Type": []}, {"Type": "Task", "Resource": [], "Next": []}):
            self.assertTrue(validate_workflow({"StartAt": "A", "States": {"A": state}}))


if __name__ == "__main__":
    unittest.main()
