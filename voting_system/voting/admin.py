from django.contrib import admin
from .models import Candidate, Voter

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "votes")

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ("name", "reg_no", "has_voted")
