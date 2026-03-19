from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Candidate, Position, Voter, Vote
import json


# -------------------------------
# HOME PAGE
# -------------------------------

def home(request):
    """Home page with statistics"""
    # Get all statistics
    total_voters = Voter.objects.count()
    total_positions = Position.objects.filter(is_active=True).count()
    total_candidates = Candidate.objects.count()
    voters_participated = Voter.objects.filter(has_voted=True).count()
    
    # Calculate turnout percentage
    if total_voters > 0:
        turnout = f"{round((voters_participated / total_voters * 100), 1)}%"
    else:
        turnout = "0%"
    
    # Get all active positions with candidate counts
    positions = Position.objects.filter(is_active=True).prefetch_related('candidates')
    
    context = {
        'total_voters': total_voters,
        'total_positions': total_positions,
        'total_candidates': total_candidates,
        'turnout': turnout,
        'positions': positions,
    }
    
    return render(request, 'voting/home.html', context)


# -------------------------------
# LOGIN VIEW (WITH LOGIC)
# -------------------------------

def login_view(request):
    if request.method == 'POST':
        reg_no = request.POST.get('reg_no')
        
        if not reg_no:
            return render(request, 'voting/login.html', {'error': 'Please enter registration number'})
        
        try:
            voter = Voter.objects.get(reg_no=reg_no)
            
            # Store voter info in session
            request.session['voter_id'] = voter.id
            request.session['reg_no'] = voter.reg_no
            request.session['is_admin'] = voter.is_admin
            
            # Check if voter is admin
            if voter.is_admin:
                return redirect('admin_welcome')
            else:
                # Redirect to voting page with their reg_no
                return redirect('vote', reg_no=reg_no)
                
        except Voter.DoesNotExist:
            return render(request, 'voting/login.html', {'error': 'Invalid Registration Number. Please try again.'})
    
    return render(request, 'voting/login.html')


# -------------------------------
# SIGNUP VIEW (WITH LOGIC)
# -------------------------------

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        reg_no = request.POST.get('reg_no')
        
        if not name or not reg_no:
            return render(request, 'voting/signup.html', {'error': 'All fields are required'})
        
        # Check if voter already exists
        if Voter.objects.filter(reg_no=reg_no).exists():
            return render(request, 'voting/signup.html', {'error': 'Registration number already exists'})
        
        # Create new voter
        voter = Voter.objects.create(
            reg_no=reg_no,
            name=name,
            is_admin=False,
            has_voted=False
        )
        
        return redirect('login')
    
    return render(request, 'voting/signup.html')


# -------------------------------
# ADMIN WELCOME
# -------------------------------

def admin_welcome(request):
    # Check if user is logged in via session
    if 'voter_id' not in request.session:
        return redirect('login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        return redirect('home')
    
    return render(request, 'voting/admin_welcome.html')


# -------------------------------
# ANALYSIS DASHBOARD VIEW
# -------------------------------

def analysis_view(request):
    # Check if user is logged in and is admin
    if 'voter_id' not in request.session or not request.session.get('is_admin', False):
        return redirect('login')

    # Votes per position
    positions = Position.objects.all()
    votes_per_position = {
        "labels": [p.name for p in positions],
        "data": [Vote.objects.filter(position=p).count() for p in positions]
    }

    # Top 5 candidates
    top_candidates_qs = Candidate.objects.order_by('-votes')[:5]
    top_candidates = {
        "labels": [c.name for c in top_candidates_qs],
        "data": [c.votes for c in top_candidates_qs]
    }

    # Voter participation
    total_voters = Voter.objects.count()
    voters_who_voted = Voter.objects.filter(has_voted=True).count()
    voter_participation = {
        "labels": ["Voted", "Not Voted"],
        "data": [voters_who_voted, total_voters - voters_who_voted]
    }

    # Convert to JSON for JavaScript
    context = {
        "votes_per_position": json.dumps(votes_per_position),
        "top_candidates": json.dumps(top_candidates),
        "voter_participation": json.dumps(voter_participation)
    }

    return render(request, 'voting/analysis.html', context)


# -------------------------------
# VOTING FUNCTIONS
# -------------------------------

def vote(request, reg_no):
    """Handle the voting process for a specific registration number"""
    # Check if voter exists
    try:
        voter = Voter.objects.get(reg_no=reg_no)
    except Voter.DoesNotExist:
        return HttpResponse("Invalid registration number", status=404)
    
    # Check if already voted
    if voter.has_voted or Vote.objects.filter(voter=voter).exists():
        return redirect('already_voted')
    
    if request.method == 'POST':
        # Get all positions
        positions = Position.objects.all()
        votes_created = 0
        
        # Process vote for each position
        for position in positions:
            candidate_id = request.POST.get(f'position_{position.id}')
            
            if candidate_id:  # Only process if a candidate was selected
                try:
                    candidate = Candidate.objects.get(id=candidate_id, position=position)
                    
                    # Create vote
                    Vote.objects.create(
                        voter=voter,
                        candidate=candidate,
                        position=position
                    )
                    
                    # Update candidate votes
                    candidate.votes += 1
                    candidate.save()
                    
                    votes_created += 1
                except Candidate.DoesNotExist:
                    continue
        
        # Mark voter as voted only if at least one vote was cast
        if votes_created > 0:
            voter.has_voted = True
            voter.save()
            return redirect('confirmation')
        else:
            # No votes were cast
            return render(request, 'voting/vote.html', {
                'positions': Position.objects.prefetch_related('candidates').all(),
                'reg_no': reg_no,
                'voter': voter,
                'error': 'Please select at least one candidate to vote for.'
            })
    
    # Display voting page with all positions and candidates
    positions = Position.objects.prefetch_related('candidates').all()
    context = {
        'positions': positions,
        'reg_no': reg_no,
        'voter': voter
    }
    return render(request, 'voting/vote.html', context)


def results(request):
    """Display voting results"""
    # Get results grouped by position
    positions = Position.objects.all()
    results_by_position = []
    
    for position in positions:
        candidates = Candidate.objects.filter(position=position).order_by('-votes')
        total_votes = sum(c.votes for c in candidates)
        
        candidate_data = []
        for candidate in candidates:
            percent = round((candidate.votes / total_votes * 100), 1) if total_votes > 0 else 0
            candidate_data.append({
                'candidate': candidate,
                'percent': percent
            })
        
        results_by_position.append({
            'position': position,
            'candidates': candidate_data,
            'total_votes': total_votes
        })
    
    total_votes = Vote.objects.count()
    total_voters = Voter.objects.count()
    voters_participated = Voter.objects.filter(has_voted=True).count()
    
    context = {
        'results_by_position': results_by_position,
        'total_votes': total_votes,
        'total_voters': total_voters,
        'voters_participated': voters_participated,
        'participation_rate': round((voters_participated / total_voters * 100), 2) if total_voters > 0 else 0
    }
    return render(request, 'voting/results.html', context)


def already_voted(request):
    """Display message for users who already voted"""
    return render(request, 'voting/already_voted.html')


def confirmation_view(request):
    """Display confirmation page after voting"""
    return render(request, 'voting/confirmation.html')
