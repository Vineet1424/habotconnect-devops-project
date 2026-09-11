from rest_framework import serializers
from .models import StudentOnboarding
from .dcyn.validators import DCYNField


class StudentOnboardingSerializer(serializers.ModelSerializer):
    """
    Deconstructs the raw student onboarding JSON payload into exactly
    validated fields. Every field has an explicit, exact limit — no
    field is left to default coercion, and no placeholder value (e.g.
    "TBD", "N/A", "test") is permitted through.
    """

    full_name = serializers.CharField(
        max_length=120,
        min_length=2,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    date_of_birth = serializers.DateField(
        required=True,
        input_formats=["%Y-%m-%d"],
    )

    guardian_email = serializers.EmailField(
        required=True,
        max_length=254,
    )

    guardian_phone = serializers.RegexField(
        regex=r"^\+?[1-9]\d{7,14}$",
        required=True,
        error_messages={
            "invalid": "Phone number must be in E.164 format, e.g. +919812345678."
        },
    )

    learning_difficulty_type = serializers.ChoiceField(
        choices=StudentOnboarding.LEARNING_DIFFICULTY_CHOICES,
        required=True,
    )

    # DCYN fields: strict booleans, zero tolerance for ambiguous input.
    consent_to_data_processing = DCYNField(required=True)
    requires_one_on_one_support = DCYNField(required=True)
    has_prior_lsa_engagement = DCYNField(required=True)

    assigned_analyst_email = serializers.EmailField(
        required=True,
        max_length=254,
    )

    class Meta:
        model = StudentOnboarding
        fields = [
            "full_name",
            "date_of_birth",
            "guardian_email",
            "guardian_phone",
            "learning_difficulty_type",
            "consent_to_data_processing",
            "requires_one_on_one_support",
            "has_prior_lsa_engagement",
            "assigned_analyst_email",
        ]

    def validate_consent_to_data_processing(self, value):
        if value is not True:
            raise serializers.ValidationError(
                "Consent must be explicitly true. Onboarding cannot "
                "proceed without affirmative, unambiguous consent."
            )
        return value

    def validate_full_name(self, value):
        placeholder_values = {"test", "n/a", "na", "tbd", "xxx", "asdf"}
        if value.strip().lower() in placeholder_values:
            raise serializers.ValidationError(
                "Placeholder names are not permitted in production onboarding data."
            )
        return value

    def validate(self, attrs):
        # Cross-field Poka-Yoke rule: if the child requires 1:1 support,
        # a prior-engagement flag of "no" combined with certain difficulty
        # types should route to manual review rather than silently pass.
        if (
            attrs["requires_one_on_one_support"] is True
            and attrs["has_prior_lsa_engagement"] is False
            and attrs["learning_difficulty_type"] == "AUTISM_SPECTRUM"
        ):
            attrs["_flag_for_manual_review"] = True
        return attrs
