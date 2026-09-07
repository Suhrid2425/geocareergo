from django import forms
from django.utils import timezone

from .models import Job, JobApplication


class JobForm(forms.ModelForm):

    class Meta:
        model = Job

        fields = [
            "title",
            "location",
            "job_type",
            "degree",
            "qualification",
            "min_experience",
            "max_experience",
            "salary",
            "description",
            "application_type",
            "application_url",
            "last_date",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. GIS Analyst",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Kolkata, West Bengal / Remote",
                }
            ),

            "job_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "degree": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "qualification": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Required qualification, skills, degree, certifications...",
                }
            ),

            "min_experience": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "0",
                }
            ),

            "max_experience": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "e.g. 2",
                }
            ),

            "salary": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. ₹4-6 LPA",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Describe the job role, responsibilities, skills, benefits, etc.",
                }
            ),

            "application_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "application_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://company.com/careers/...",
                }
            ),

            "last_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        application_type = cleaned_data.get("application_type")
        application_url = cleaned_data.get("application_url")

        min_experience = cleaned_data.get("min_experience")
        max_experience = cleaned_data.get("max_experience")

        last_date = cleaned_data.get("last_date")

        # -----------------------------------------
        # EXPERIENCE VALIDATION
        # -----------------------------------------

        if (
            min_experience is not None
            and max_experience is not None
            and min_experience > max_experience
        ):
            raise forms.ValidationError(
                "Minimum experience cannot be greater than maximum experience."
            )

        # -----------------------------------------
        # APPLICATION URL
        # -----------------------------------------

        if application_type == "external":

            if not application_url:
                self.add_error(
                    "application_url",
                    "Application URL is required for external applications."
                )

        elif application_type == "internal":

            cleaned_data["application_url"] = ""

        # -----------------------------------------
        # DEADLINE
        # -----------------------------------------

        if last_date:

            if last_date < timezone.localdate():

                self.add_error(
                    "last_date",
                    "Application deadline cannot be in the past."
                )

        return cleaned_data


class JobApplicationForm(forms.ModelForm):

    class Meta:
        model = JobApplication

        fields = [
            "phone",
            "resume",
            "cover_message",
        ]

        widgets = {

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone number",
                }
            ),

            "resume": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx",
                }
            ),

            "cover_message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Cover message",
                }
            ),
        }