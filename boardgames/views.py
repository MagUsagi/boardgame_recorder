from django.shortcuts import render, redirect, get_object_or_404
from .models import Game, History, Expansion, Result, Player, Category, Mechanic
from .forms import GameForm, HistoryForm, ResultFormSet, PlayerForm, CategoryForm, MechanicForm, GameSearchForm
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Sum, F, Q
import random
from datetime import timedelta, date
from django.urls import reverse
from django.db.models.functions import Coalesce, Lower

# Create your views here.

def dashboard(request):
    add_game_form = GameForm()
    add_player_form = PlayerForm()

    # Overview data
    total_games = Game.objects.count()
    total_players = Player.objects.count()
    total_plays = History.objects.count()
    total_play_time_hours = round((History.objects.aggregate(Sum('duration'))['duration__sum'] or 0) / 60, 2)

    # Random Game Generator
    ten_days_ago = date.today() - timedelta(days=10)
    recent_games = History.objects.filter(play_date__gte=ten_days_ago).values_list('game_id', flat=True)
    all_games = list(Game.objects.all())

    # 確率調整：過去10日以内のゲームは1/3の確率にする
    weighted_games = []

    for game in all_games:
        if game.id in recent_games:
            weighted_games.extend([game] * 1)  # 重み1
        else:
            weighted_games.extend([game] * 3)  # 重み3

    random_game = random.choice(weighted_games) if weighted_games else None

    # Recently played games (3 most recent)
    recent_histories = History.objects.select_related('game').order_by('-play_date', '-play_time')[:3]
    recently_played_games = [{
        'title': history.game.title,
        'image': history.game.image,
        'last_played_date': history.play_date,
        'last_played_time': history.play_time,
        'slug': history.game.slug
    }
        for history in recent_histories
    ]

    # Most played games (by play count, top 3)
    most_played_games = Game.objects.annotate(play_count=Count('histories')).order_by('-play_count')[:3]

    # Never played games
    never_played_games = Game.objects.annotate(play_count=Count('histories')).filter(play_count=0)

    # Least recently played games (deduplicated, worst 3)
    played_games = History.objects.select_related('game') \
        .order_by('-play_date')

    seen_games = set()
    least_recently_played_games = []

    for history in played_games:
        if history.game.title not in seen_games:
            least_recently_played_games.append({
                'title': history.game.title,
                'image': history.game.image,
                'last_played_date': history.play_date,
                'slug': history.game.slug,
            })
            seen_games.add(history.game.title)
        if len(least_recently_played_games) == 3:
            break

    # Sort in ascending order to show the "worst" 3
    least_recently_played_games = sorted(least_recently_played_games, key=lambda x: x['last_played_date'])[:3]

    context = {
        'games': Game.objects.all(),
        'random_game': random_game,
        'weighted_games': weighted_games,
        'players': Player.objects.all(),
        'total_plays': total_plays,
        'total_play_time_hours': total_play_time_hours,
        'recently_played_games': recently_played_games,
        'most_played_games': most_played_games,
        'never_played_games': never_played_games,
        'least_recently_played_games': least_recently_played_games,
        'add_game_form': add_game_form,
        'form': add_player_form,
    }

    return render(request, 'boardgames/dashboard.html', context)


def add_record(request):
    if request.method == 'POST':
        history_form = HistoryForm(request.POST)
        result_formset = ResultFormSet(request.POST)
        if not result_formset.is_valid():
            print(result_formset.errors)
            print("Initial formset data:", result_formset.initial_forms)
            print("Received POST data:", request.POST)
        if history_form.is_valid() and result_formset.is_valid():
            history = history_form.save()
            history.expansions_used.set(history_form.cleaned_data['expansions'])

            results = result_formset.save(commit=False)
            for result in results:
                result.history = history
                result.score = result.score or 0
                result.save()

            messages.success(request, "Play record added successfully!")

            return redirect('game_detail', slug=history.game.slug)
        else:
            print(result_formset.errors)
            print("Initial formset data:", result_formset.initial_forms)
            print("Received POST data:", request.POST)
            print(history_form.errors)
            return JsonResponse({'error': 'Invalid request'}, status=400)


def get_expansions(request, game_id):
    expansions = Expansion.objects.filter(game_id=game_id).values('id', 'name')
    return JsonResponse({'expansions': list(expansions)})


def all_games(request):
    games = Game.objects.all()
    add_game_form = GameForm()
    search_form = GameSearchForm(request.GET)
    categories = Category.objects.annotate(game_count=Count('game')).order_by(Lower('name'))
    mechanics = Mechanic.objects.annotate(game_count=Count('game')).order_by(Lower('name'))
       
    # Get the selected filters from request.GET
    selected_categories = request.GET.getlist("search_category")
    selected_mechanics = request.GET.getlist("search_mechanic")
    selected_players = request.GET.getlist("search_players")
    selected_durations = request.GET.getlist("search_duration") 


    if search_form.is_valid():
        query = search_form.cleaned_data.get('key_word')
        search_categories = search_form.cleaned_data.get('search_category')
        search_mechanics = search_form.cleaned_data.get('search_mechanic')
        search_players = selected_players
        search_durations = selected_durations   

        if query:
            games = games.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(summary__icontains=query)).distinct()

        if search_categories:
            games = games.filter(category__in=search_categories).distinct()

        if search_mechanics:
            games = games.filter(mechanic__in=search_mechanics).distinct()

        if search_players:
            search_players = [int(p) for p in search_players]
            conditions=Q(min_players__lte=max(search_players), max_players__gte=min(search_players))
            if 10 in search_players:
                conditions |= Q(max_players__gte=10)  # Include 10 or more players
            games = games.filter(conditions)

        if search_durations:
            search_durations = [int(d) for d in search_durations]
            conditions=Q(min_duration__lte=max(search_durations), max_duration__gte=min(search_durations))
            if 5 in search_durations:
                conditions |= Q(max_duration__lte=5)  # Include games 5 minutes or shorter
            if 90 in search_durations:
                conditions |= Q(min_duration__gte=90)  # Include games 90 minutes or longer
            games = games.filter(conditions)
    
    # Pass the selected filters and other context to the template
    context = {
        'games': games,
        'add_game_form': add_game_form,
        'search_form': search_form,
        'categories': categories,
        'mechanics': mechanics,
        "player_numbers": list(range(1, 11)),
        "durations": [5, 15, 30, 45, 60, 75, 90],
        'selected_categories': selected_categories,
        'selected_mechanics': selected_mechanics,
        'selected_players': selected_players,
        'selected_durations': selected_durations,
    }
           
    return render(request, 'boardgames/all_games.html', context)

def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    games = Game.objects.all()
    histories = History.objects.filter(game=game).prefetch_related('results').order_by('-play_date', '-id')
    players = Player.objects.all()
    expansions = Expansion.objects.filter(game=game)
    edit_game_form = GameForm(instance=game)

    paginator = Paginator(histories, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'boardgames/game_detail.html', {
        'game': game,
        'games': games,
        'histories': page_obj,
        'players': players,
        'expansions': expansions,
        'edit_game_form': edit_game_form,
    })

def edit_history(request, history_id):

    if request.method == 'POST':
        # History fields
        history = get_object_or_404(History, id=history_id)
        history.play_date = request.POST.get('play_date')
        history.duration = request.POST.get('duration')
        expansion_ids = request.POST.getlist('expansions')
        history.expansions_used.set(Expansion.objects.filter(id__in=expansion_ids))
        history.save()

        # Update results
        Result.objects.filter(history=history).delete()

        players = request.POST.getlist('player')
        scores = request.POST.getlist('score')
        is_winners = [key.split('_')[1] for key in request.POST.keys() if key.startswith('winner_')]
            
        for i in range(len(players)):
            player_name = players[i]
            score = scores[i] if scores[i] else 0
            is_winner = player_name in is_winners

            player = Player.objects.filter(name=player_name).first()
            if player:
                Result.objects.create(
                    history=history,
                    player=player,
                    score=score,
                    is_winner=is_winner
                )
        
        # Add success message after the record is updated
        messages.success(request, "Play record updated successfully!")

        return redirect('game_detail', slug=history.game.slug)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)


def delete_history(request, history_id):
    history = get_object_or_404(History, id=history_id)
    game_slug = history.game.slug
    history.delete()
    messages.error(request, "Play record deleted")

    return redirect('game_detail', slug=game_slug)


def add_game(request):
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        
        if form.is_valid():
            game = form.save(commit=False)
            game.save()
            form.save_m2m()

            messages.success(request, "Game added successfully")

            expansion_names = request.POST.getlist('expansions')
            for name in expansion_names:
                if name.strip():
                    Expansion.objects.create(game=game, name=name.strip())

            return JsonResponse({'success': True, 'slug': game.slug})
        else:
            errors = {field: [str(error) for error in error_list] for field, error_list in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})
   
    else:
        form = GameForm()
    return render(request, 'boardgames/all_games.html', {'games': Game.objects.all(), 'add_game_form': form})


def edit_game(request, slug):
    game = get_object_or_404(Game, slug=slug)
    expansions = Expansion.objects.filter(game=game)

    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            game = form.save()

            messages.success(request, "Game updated successfully")

            Expansion.objects.filter(game=game).delete()
            expansion_names = request.POST.getlist('expansions')
            for name in expansion_names:
                if name.strip():
                    Expansion.objects.create(game=game, name=name.strip())
            # JSON response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Game updated successfully!',
                    'slug': game.slug,
                    'game': {
                        'title': game.title,
                        'min_players': game.min_players,
                        'max_players': game.max_players,
                        'min_duration': game.min_duration,
                        'max_duration': game.max_duration,
                        'expansions': [name.strip() for name in expansion_names if name.strip()],
                    }
                })
            
            return HttpResponseRedirect(reverse('game_detail', kwargs={'slug': game.slug}))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    else:
        form = GameForm(instance=game)

    return render(request, 'boardgames/game_detail.html', {
        'game': game,
        'edit_game_form': form,
        'expansions': expansions,
    })


def delete_game(request, slug):
    game = get_object_or_404(Game, slug=slug)
    if request.method == 'POST':
        game.delete()
        messages.error(request, "Game deleted")

        return redirect('all_games')
    return render(request, 'boardgames/game_detail.html', {'game': game})


def players(request):
    players = Player.objects.annotate(
        total_games=Count('results__history'),
        total_wins=Count('results', filter=F('results__is_winner')),
        total_duration=Coalesce(Sum('results__history__duration'), 0),
    ).order_by('name')

    player_stats = []
    for player in players:
        win_rate = (player.total_wins / player.total_games * 100) if player.total_games > 0 else 0
        total_hours = round(player.total_duration / 60, 2)

        favorite_games = (History.objects
                          .filter(results__player=player)
                          .values('game__title')
                          .annotate(game_count=Count('game'))
                          .order_by('-game_count')[:3])
        
        player_stats.append({
            'player': player,
            'win_rate': round(win_rate, 2),
            'total_games': player.total_games,
            'total_hours': total_hours,
            'favorite_games': favorite_games,
        })

    return render(request, 'boardgames/players.html', {'player_stats': player_stats})


def add_player(request):
    form = PlayerForm()
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Player added successfully")
            return JsonResponse({'success': True})
    
        else:
            errors = {field: [str(error) for error in error_list if str(error).strip()] for field, error_list in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})

    return JsonResponse({'success': False, 'errors': {'non_field_errors': ['Invalid request']}})


def settings(request):
    categories = Category.objects.all()
    category_form = CategoryForm()

    mechanics = Mechanic.objects.all()
    mechanic_form = MechanicForm()

    return render(request, 'boardgames/settings.html', {
        'categories': categories,
        'category_form': category_form,
        'mechanics': mechanics,
        'mechanic_form': mechanic_form,
    })

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully")
            return redirect(reverse('settings'))
    return redirect(reverse('settings'))

def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.save()
        messages.success(request, "Category updated successfully")
        return redirect('settings')
    return render(request, 'boardgames/settings.html', {'categories': Category.objects.all()})

def delete_category(request):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=request.POST.get('category_id'))
        category.delete()
        messages.error(request, "Category deleted")
        return redirect(reverse('settings'))
    return redirect(reverse('settings'))

def add_mechanic(request):
    if request.method == 'POST':
        form = MechanicForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Mechanic added successfully")
            return redirect(reverse('settings'))
    return redirect(reverse('settings'))

def edit_mechanic(request, mechanic_id):
    mechanic = get_object_or_404(Mechanic, id=mechanic_id)
    if request.method == 'POST':
        mechanic.name = request.POST.get('name')
        mechanic.description = request.POST.get('description')
        mechanic.save()
        messages.success(request, "Mechanic updated successfully")
        return redirect('settings')
    return render(request, 'boardgames/settings.html', {'mechanics': Mechanic.objects.all()})

def delete_mechanic(request):
    if request.method == 'POST':
        mechanic = get_object_or_404(Mechanic, id=request.POST.get('mechanic_id'))
        mechanic.delete()
        messages.error(request, "Mechanic deleted")
        return redirect(reverse('settings'))
    return redirect(reverse('settings'))

