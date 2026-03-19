from django.db import models

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.department})"


class Voter(models.Model):
    name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=20, unique=True)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.reg_no}"
