from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('get_expansions/<int:game_id>/', views.get_expansions, name='get_expansions'),
    path('all_games/', views.all_games, name='all_games'),
    path('games/<slug:slug>', views.game_detail, name='game_detail'),
    path('add_game/', views.add_game, name='add_game'),
    path('games/<slug:slug>/edit', views.edit_game, name='edit_game'),
    path('games/<slug:slug>/delete', views.delete_game, name='delete_game'),
    path('add_record/', views.add_record, name='add_record'),
    path('history/<int:history_id>/edit/', views.edit_history, name='edit_history'),
    path('history/<int:history_id>/delete/', views.delete_history, name='delete_history'),
    path('players/', views.players, name='players'),
    path('add_player/', views.add_player, name='add_player'),
    path('records/', views.records, name='records'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)