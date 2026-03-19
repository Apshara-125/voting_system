from django.db import models

class Position(models.Model):
    """Different positions students can vote for"""
    name = models.CharField(max_length=100)  # e.g., "President", "Vice President"
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    manifesto = models.TextField(blank=True)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.position.name}"
    
    class Meta:
        ordering = ['position', 'name']

class Voter(models.Model):
    name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=20, unique=True)
    has_voted = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    voted_positions = models.ManyToManyField(Position, blank=True, related_name='voters_who_voted')
    
    def __str__(self):
        return f"{self.name} - {self.reg_no}"
    
    def has_voted_for_position(self, position):
        """Check if voter has already voted for a specific position"""
        return self.voted_positions.filter(id=position.id).exists()

class Vote(models.Model):
    """Track individual votes for audit purposes (without revealing who voted for whom)"""
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['voter', 'position']  # One vote per position per voter