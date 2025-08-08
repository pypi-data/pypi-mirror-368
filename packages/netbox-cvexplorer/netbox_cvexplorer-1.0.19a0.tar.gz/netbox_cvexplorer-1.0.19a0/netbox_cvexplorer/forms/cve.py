from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from ..models import CVE  # wichtig: relativer Import aus dem Nachbarordner

class CVEForm(forms.ModelForm):

    cve_number = forms.CharField(
        label="CVE",
        max_length=20,
        validators=[RegexValidator(r"^CVE-\d{4}-\d{4,}$", "Format: CVE-YYYY-NNNN")]
    )

    class Meta:
        model = CVE
        fields = ["cve_number", "title", "description", "score", "status"]
        labels = {
            "title": "Titel",
            "description": "Beschreibung",
            "score": "CVSS Score (0.0 – 10.0)",
            "status": "Status",
        }
        widgets = {
            "cve_number": forms.TextInput(attrs={"required": True}),
            "title": forms.TextInput(attrs={"required": True}),
            "description": forms.Textarea(attrs={"rows": 4, "required": True}),
            "score": forms.NumberInput(attrs={"step": "0.1", "min": "0.0", "max": "10.0", "required": True}),
            "status": forms.Select(attrs={"required": True}),
        }

    def clean_score(self):
        s = self.cleaned_data.get("score")
        if s is None:
            return s
        if s < 0 or s > 10:
            raise ValidationError("Score muss zwischen 0.0 und 10.0 liegen.")
        return s
