from django.contrib import admin
from .models import Candidate, Voter, Position, Vote

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'candidate_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    
    def candidate_count(self, obj):
        return obj.candidates.count()
    candidate_count.short_description = 'Number of Candidates'

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'department', 'votes')
    list_filter = ('position', 'department')
    search_fields = ('name', 'department')
    ordering = ('position', 'name')
    readonly_fields = ('votes',)  # Prevent manual vote manipulation

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'reg_no', 'has_voted', 'is_admin', 'positions_voted_count')
    search_fields = ('name', 'reg_no')
    list_filter = ('has_voted', 'is_admin')
    filter_horizontal = ('voted_positions',)
    
    def positions_voted_count(self, obj):
        return obj.voted_positions.count()
    positions_voted_count.short_description = 'Positions Voted'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'position', 'candidate', 'voted_at')
    list_filter = ('position', 'voted_at')
    search_fields = ('voter__name', 'voter__reg_no', 'candidate__name')
    date_hierarchy = 'voted_at'
    readonly_fields = ('voter', 'position', 'candidate', 'voted_at')  # Make votes immutable
    
    def has_add_permission(self, request):
        # Prevent manual vote creation through admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete votes
        return request.user.is_superuser