from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Student, Position, Candidate, Vote, ElectionStatus, AuditLog
from .forms import StudentRegistrationForm
from django.contrib.auth.forms import AuthenticationForm


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            AuditLog.objects.create(
                user=user,
                username=user.username,
                action='register',
                detail=f"New registration — Student ID: {user.student_id}",
                ip_address=get_client_ip(request),
            )
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'election/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                AuditLog.objects.create(
                    user=user,
                    username=user.username,
                    action='login',
                    detail="Successful login",
                    ip_address=get_client_ip(request),
                )
                return redirect('dashboard')
        else:
            # Log failed login attempt
            attempted_username = request.POST.get('username', '')
            AuditLog.objects.create(
                username=attempted_username,
                action='failed_login',
                detail="Failed login attempt",
                ip_address=get_client_ip(request),
            )
    else:
        form = AuthenticationForm()
    return render(request, 'election/login.html', {'form': form})


def logout_view(request):
    AuditLog.objects.create(
        user=request.user,
        username=request.user.username,
        action='logout',
        detail="User logged out",
        ip_address=get_client_ip(request),
    )
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    positions = Position.objects.all()
    election_status = ElectionStatus.objects.first()

    # Check which positions the user has already voted for
    voted_positions = Vote.objects.filter(voter=request.user).values_list('position_id', flat=True)

    # Dashboard statistics
    total_voters = Student.objects.filter(is_superuser=False, is_staff=False).count()
    votes_cast = Vote.objects.values('voter').distinct().count()
    total_candidates = Candidate.objects.count()
    participation_pct = round((votes_cast / total_voters * 100), 1) if total_voters > 0 else 0

    context = {
        'positions': positions,
        'voted_positions': voted_positions,
        'election_status': election_status,
        'is_verified': request.user.is_verified,
        'total_voters': total_voters,
        'votes_cast': votes_cast,
        'total_candidates': total_candidates,
        'participation_pct': participation_pct,
    }
    return render(request, 'election/dashboard.html', context)


@login_required
def vote_view(request, position_id):
    position = get_object_or_404(Position, id=position_id)
    election_status = ElectionStatus.objects.first()

    if not election_status or not election_status.is_currently_open():
        messages.error(request, "Voting is currently closed.")
        return redirect('dashboard')

    if not request.user.is_verified:
        messages.error(request, "Your account is not verified. Please contact the administrator.")
        return redirect('dashboard')

    if Vote.objects.filter(voter=request.user, position=position).exists():
        messages.warning(request, f"You have already voted for {position.name}.")
        return redirect('dashboard')

    candidates = Candidate.objects.filter(position=position)

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        if candidate_id:
            candidate = get_object_or_404(Candidate, id=candidate_id)
            Vote.objects.create(voter=request.user, candidate=candidate, position=position)
            AuditLog.objects.create(
                user=request.user,
                username=request.user.username,
                action='vote',
                detail=f"Voted for '{candidate.name}' ({position.name})",
                ip_address=get_client_ip(request),
            )
            messages.success(request, f"Your vote for {candidate.name} has been cast.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please select a candidate.")

    return render(request, 'election/vote.html', {'position': position, 'candidates': candidates})


def results_view(request):
    election_status = ElectionStatus.objects.first()

    if not election_status or (not election_status.results_published and not request.user.is_staff):
        messages.info(request, "The election results have not been published yet. Please check back later.")
        return redirect('dashboard')

    positions = Position.objects.all()
    results = []
    grand_total_votes = 0

    for pos in positions:
        pos_results = Candidate.objects.filter(position=pos).annotate(vote_count=Count('vote')).order_by('-vote_count')
        total_votes = Vote.objects.filter(position=pos).count()
        grand_total_votes += total_votes

        candidates_data = []
        for cand in pos_results:
            pct = round((cand.vote_count / total_votes * 100), 1) if total_votes > 0 else 0
            candidates_data.append({'candidate': cand, 'pct': pct})

        results.append({
            'position': pos,
            'candidates': candidates_data,
            'total_votes': total_votes,
        })

    return render(request, 'election/results.html', {
        'results': results,
        'election_status': election_status,
        'grand_total_votes': grand_total_votes,
    })
