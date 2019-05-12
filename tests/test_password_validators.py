from django.test import TestCase
from django.core.exceptions import ValidationError

from ..validators import LocalUserPasswordValidator, MaximumLengthValidator


class TestCharacterSetValidator(TestCase):

    def test_valid_password_passes(self):
        valid_passwords = [
            "AAbb11",
            "AAbb$$",
            "AA$$11",
            "bb$$11",
            "apasswordthatonlytriggerstherestrictedcharactersetrules",
        ]
        validator = LocalUserPasswordValidator()
        for password in valid_passwords:
            try:
                validator.validate(password)
            except ValidationError:
                self.fail("Validator did not accept a valid password: {}".format(password))

    def test_incorrect_passwords_fail(self):
        invalid_passwords = [
            "AAbb11%",  # Fails the restricted set rules (%).
            'AAbb11"',  # Fails the restricted set rules (").
            "AAbb11=",  # Fails the restricted set rules (=).
            "AAbb11+",  # Fails the restricted set rules (+).
            "AAbb",  # Doesn't match 3 of 4 criteria.
            "AA11",  # Doesn't match 3 of 4 criteria.
            "bb11",  # Doesn't match 3 of 4 criteria.
            "AA$$",  # Doesn't match 3 of 4 criteria.
            "bb$$",  # Doesn't match 3 of 4 criteria.
        ]
        validator = LocalUserPasswordValidator()
        for password in invalid_passwords:
            with self.assertRaises(ValidationError):
                validator.validate(password)


class TestMaxLengthValidator(TestCase):

    def test_valid_password_passes(self):
        # 10-character password should succeed.
        password = "abcdefghij"
        validator = MaximumLengthValidator(max_length=10)
        try:
            validator.validate(password)
        except ValidationError:
            self.fail("Validator did not accept a valid password.")

    def test_invalid_password_fails(self):
        # 11-character password should fail.
        password = "abcdefghijk"
        validator = MaximumLengthValidator(max_length=10)
        with self.assertRaises(ValidationError):
            validator.validate(password)
