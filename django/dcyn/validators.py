"""
DCYN — Deconstructed Clean Yes/No validation library.

Purpose: incoming onboarding forms often represent yes/no answers
inconsistently ("Yes", "Y", "true", 1, "maybe", empty string). This
library enforces that every yes/no field is deconstructed down to a
strict Python bool with no in-between state, so no human has to
interpret an ambiguous value later.
"""

from rest_framework import serializers


def dcyn_validate(value):
    """
    Accepts ONLY the literal booleans True or False.
    Any string, integer, or null representation is rejected outright —
    there is no silent coercion, so ambiguity cannot slip through.
    """
    if value is True:
        return True
    if value is False:
        return False
    raise serializers.ValidationError(
        "This field must be a strict boolean (true or false in JSON). "
        "String or numeric stand-ins for yes/no are not accepted."
    )


class DCYNField(serializers.BooleanField):
    """
    Drop-in replacement for DRF's BooleanField that removes its default
    lenient coercion (which normally accepts 'true', 'yes', 1, etc.).
    Use this for every field where a human might otherwise have to
    interpret intent — consent, eligibility flags, binary declarations.
    """

    def to_internal_value(self, data):
        return dcyn_validate(data)
