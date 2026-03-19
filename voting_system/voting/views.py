from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from .models import Candidate, Voter

def home(request):
    return render(request, "voting/home.html")

def vote(request, reg_no):
    voter = get_object_or_404(Voter, reg_no=reg_no)
    if voter.has_voted:
        return render(request, "voting/already_voted.html", {"voter": voter})
    if request.method == "POST":
        candidate_id = request.POST.get("candidate")
        candidate = get_object_or_404(Candidate, id=candidate_id)
        candidate.votes += 1
        candidate.save()
        voter.has_voted = True
        voter.save()
        return redirect("results")
    candidates = Candidate.objects.all()
    return render(request, "voting/vote.html", {"voter": voter, "candidates": candidates})

def results(request):
    candidates = Candidate.objects.all()
    total_votes = sum(c.votes for c in candidates)
    results = []
    for c in candidates:
        percent = round((c.votes / total_votes) * 100, 2) if total_votes > 0 else 0
        results.append({
            "candidate": c,
            "percent": percent
        })
    return render(request, "voting/results.html", {
        "results": results,
        "total_votes": total_votes
    })

def login_view(request):
    if request.method == "POST":
        reg_no = request.POST.get("reg_no")
        if reg_no:
            return redirect("vote", reg_no=reg_no)
    return render(request, "voting/login.html")

def already_voted(request):
    return render(request, "voting/already_voted.html")

def signup(request):
    error = ""
    if request.method == "POST":
        name = request.POST.get("name")
        reg_no = request.POST.get("reg_no")
        if name and reg_no:
            try:
                Voter.objects.create(name=name, reg_no=reg_no)
                return redirect("login")
            except IntegrityError:
                error = "Registration number already exists."
        else:
            error = "Please enter all fields."
    return render(request, "voting/signup.html", {"error": error})
