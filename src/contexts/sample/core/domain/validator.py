from pyvaru import ValidationRule, Validator


class SampleIsRunning(ValidationRule):
    def apply(self) -> bool | tuple[bool, str]:
        return True


class AddGuessValidator(Validator):
    def get_rules(self, data: dict) -> list:
        return [
            SampleIsRunning(
                {"sample": data["sample"]},
                label="sample_is_running",
                error_message="Error",
            ),
        ]
