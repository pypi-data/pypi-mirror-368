from django.db import models

class CVE(models.Model):
    cve_number = models.CharField(max_length=20, unique=True)
    # cve_number = models.CharField(
    #     max_length=20,
    #     unique=True,
    #     validators=[RegexValidator(r"^CVE-\d{4}-\d{4,}$", "Format: CVE-YYYY-NNNN")]
    # )
    title = models.CharField(max_length=255)
    description = models.TextField()
    score = models.DecimalField(
        max_digits=4, decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    status = models.IntegerField(choices=[(0, 'Offen'), (1, 'Erledigt')])
    date_imported = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cve_number} – {self.title}"