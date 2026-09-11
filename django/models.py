import uuid
from django.db import models


class StudentOnboarding(models.Model):

    LEARNING_DIFFICULTY_CHOICES = [
        ("DYSLEXIA", "Dyslexia"),
        ("DYSCALCULIA", "Dyscalculia"),
        ("DYSGRAPHIA", "Dysgraphia"),
        ("ADHD", "ADHD"),
        ("AUTISM_SPECTRUM", "Autism Spectrum"),
        ("OTHER", "Other"),
    ]

    student_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=120)
    date_of_birth = models.DateField()
    guardian_email = models.EmailField(max_length=254)
    guardian_phone = models.CharField(max_length=20)
    learning_difficulty_type = models.CharField(
        max_length=32, choices=LEARNING_DIFFICULTY_CHOICES
    )
    consent_to_data_processing = models.BooleanField()
    requires_one_on_one_support = models.BooleanField()
    has_prior_lsa_engagement = models.BooleanField()
    assigned_analyst_email = models.EmailField(max_length=254)
    ingested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_onboarding"
