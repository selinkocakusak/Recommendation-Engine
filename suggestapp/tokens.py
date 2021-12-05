from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, email, timestamp):
        return (
            six.text_type(email) + six.text_type(timestamp)
            # six.text_type(reader.email) + six.text_type(timestamp) +
            # six.text_type(reader.confirmation)
        )


activation_token = AccountActivationTokenGenerator()
