from django import forms

from .models import JobApplication


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
                    "placeholder": "Enter your phone number",
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
                    "placeholder": (
                        "Write a short message to the employer "
                        "(optional)"
                    ),
                }
            ),
        }

        labels = {

            "phone": "Phone Number",

            "resume": "Resume",

            "cover_message": "Cover Message",
        }

        help_texts = {

            "resume": (
                "Upload your resume in PDF, DOC or DOCX format."
            ),

            "cover_message": (
                "Optional: Introduce yourself briefly."
            ),
        }


    def clean_resume(self):

        resume = self.cleaned_data.get("resume")

        if not resume:
            raise forms.ValidationError(
                "Please upload your resume."
            )

        allowed_extensions = [
            ".pdf",
            ".doc",
            ".docx",
        ]

        file_name = resume.name.lower()

        if not any(
            file_name.endswith(extension)
            for extension in allowed_extensions
        ):
            raise forms.ValidationError(
                "Only PDF, DOC and DOCX files are allowed."
            )

        # 5 MB maximum
        max_size = 5 * 1024 * 1024

        if resume.size > max_size:
            raise forms.ValidationError(
                "Resume must be smaller than 5 MB."
            )

        return resume