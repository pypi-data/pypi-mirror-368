# YggFlix

YggFlix est un client API Python pour YggTorrent avec sélection intelligente de torrents.

## Installation

```bash
pip install yggflix
```

## Utilisation rapide

```python
from yggflix import find_best_movie_torrent, find_best_episode_torrent

# Meilleur torrent d'un film (par ID TMDb)
result = find_best_movie_torrent(
    tmdb_id=550, # Retour vers le futur
    preferred_language='VFF')

# Rechercher le meilleur torrent d'un épisode
result = find_best_episode_torrent(
    tmdb_id=1399,  # Game of Thrones
    season=1,
    episode=1,
    preferred_language='VFF'
)
```

## Fonctionnalités

- Recherche intelligente de torrents avec scoring automatique
- Support des films et séries TV
- Priorité configurable pour les langues, résolutions et sources
- Détection automatique des langues et qualités
- API simple et intuitive