from django.urls import path
from .views import PokemonListView,  PokemonDetailView

urlpatterns = [
    path('api/pokemon/', PokemonListView.as_view(), name='pokemon-list-api'),
    path('api/pokemon/<int:pokemon_id>/', PokemonDetailView.as_view(), name='pokemon-detail-api'),
    path('', PokemonListView.pokemon_list_html_view, name='pokemon-list-html'),
    path('/<int:pokemon_id>/', PokemonDetailView.pokemon_detail_html_view, name='pokemon-detail-html'),
]