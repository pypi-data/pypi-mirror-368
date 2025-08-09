"""
YggFlix - API client for YggTorrent with smart torrent selection
"""

from .yggflix_result import YggflixResult
from .yggflix_service import YggflixService  
from .yggflix_api import YggflixAPI
from .yggflix import TorrentSelector, find_best_movie_torrent, find_best_episode_torrent, is_available_on_yggflix

__version__ = "0.1.0"
__all__ = ["YggflixResult", "YggflixService", "YggflixAPI", "TorrentSelector", "find_best_movie_torrent", "find_best_episode_torrent", "is_available_on_yggflix"]