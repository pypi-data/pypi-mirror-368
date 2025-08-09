from yggflix_api import YggflixAPI
from typing import Dict, List, Optional, Tuple, Any

class TorrentSelector:
    def __init__(self):
        self.api = YggflixAPI()
        
        # Priorités pour les langues (plus le score est élevé, mieux c'est)
        self.language_priority = {
            'VFF': 10,      # Version française
            'MULTi': 9,     # Multi-langues
            'VOST': 8,      # Version originale sous-titrée
            'SUBFRENCH': 7, # Sous-titres français
            None: 5         # Non spécifié
        }
        
        # Priorités pour les résolutions
        self.resolution_priority = {
            '4k': 10,
            '2160p': 10,
            '1080p': 8,
            '720p': 6,
            '480p': 4,
            None: 2
        }
        
        # Priorités pour les sources
        self.source_priority = {
            'Bluray': 10,
            'WEB-DL': 8,
            'WEBRip': 7,
            'HDRip': 6,
            'DVDRip': 4,
            None: 3
        }
        
        # Priorités pour les codecs
        self.codec_priority = {
            'h265': 8,
            'h264': 7,
            'XviD': 4,
            None: 3
        }

    def is_content_available(self, tmdb_id: int, content_type: str = 'auto') -> Tuple[bool, str, Dict]:
        """
        Vérifie si le contenu est disponible sur YggFlix
        
        Args:
            tmdb_id: ID TMDB du contenu
            content_type: 'movie', 'tv' ou 'auto' pour détection automatique
            
        Returns:
            Tuple (disponible, type_détecté, détails_contenu)
        """
        try:
            if content_type == 'auto':
                # Essayer d'abord comme film
                try:
                    details = self.api.get_movie_detail(tmdb_id)
                    if details and 'id' in details:
                        return True, 'movie', details
                except:
                    pass
                
                # Puis comme série TV
                try:
                    details = self.api.get_tvshow_detail(tmdb_id)
                    if details and 'id' in details:
                        return True, 'tv', details
                except:
                    pass
                
                return False, 'unknown', {}
            
            elif content_type == 'movie':
                details = self.api.get_movie_detail(tmdb_id)
                if details and 'id' in details:
                    return True, 'movie', details
                    
            elif content_type == 'tv':
                details = self.api.get_tvshow_detail(tmdb_id)
                if details and 'id' in details:
                    return True, 'tv', details
            
            return False, content_type, {}
            
        except Exception as e:
            print(f"Erreur lors de la vérification de disponibilité: {e}")
            return False, 'error', {}

    def calculate_torrent_score(self, torrent: Dict, forced_resolution: Optional[str] = None) -> int:
        """
        Calcule un score de qualité pour un torrent
        
        Args:
            torrent: Dictionnaire contenant les infos du torrent
            forced_resolution: Résolution forcée ('1080p', '720p', '4k', etc.)
            
        Returns:
            Score de qualité (plus élevé = meilleur)
        """
        score = 0
        
        # Score basé sur la langue
        language = torrent.get('language')
        score += self.language_priority.get(language, 0)
        
        # Score basé sur la résolution avec gestion de résolution forcée
        resolution = torrent.get('resolution')
        if forced_resolution:
            # Si une résolution est forcée, donner un bonus énorme si elle correspond
            # et un malus si elle ne correspond pas
            if resolution == forced_resolution:
                score += 20  # Bonus énorme pour la résolution exacte
            else:
                score -= 5   # Malus pour les autres résolutions
        else:
            # Comportement normal si pas de résolution forcée
            score += self.resolution_priority.get(resolution, 0)
        
        # Score basé sur la source
        source = torrent.get('source')
        score += self.source_priority.get(source, 0)
        
        # Score basé sur le codec
        codec = torrent.get('codec')
        score += self.codec_priority.get(codec, 0)
        
        # Bonus pour les seeders (disponibilité)
        seeders = torrent.get('seeders', 0)
        if seeders > 100:
            score += 5
        elif seeders > 50:
            score += 3
        elif seeders > 10:
            score += 2
        elif seeders > 0:
            score += 1
        
        # Malus si pas de seeders
        if seeders == 0:
            score -= 10
        
        return score

    def get_movie_torrents(self, tmdb_id: int) -> List[Dict]:
        """
        Récupère tous les torrents pour un film
        """
        try:
            return self.api.get_movie_torrents(tmdb_id)
        except Exception as e:
            print(f"Erreur lors de la récupération des torrents du film: {e}")
            return []

    def get_tv_torrents(self, tmdb_id: int, season: Optional[int] = None, 
                       episode: Optional[int] = None) -> List[Dict]:
        """
        Récupère tous les torrents pour une série TV
        Peut filtrer par saison/épisode si spécifié
        """
        try:
            torrents = self.api.get_tvshow_torrents(tmdb_id)
            
            if season is not None and episode is not None:
                # Filtrer par saison et épisode spécifiques
                filtered_torrents = []
                for torrent in torrents:
                    if (torrent.get('season') == season and 
                        torrent.get('episode') == episode):
                        filtered_torrents.append(torrent)
                return filtered_torrents
            
            elif season is not None:
                # Filtrer par saison uniquement
                filtered_torrents = []
                for torrent in torrents:
                    if torrent.get('season') == season:
                        filtered_torrents.append(torrent)
                return filtered_torrents
            
            return torrents
            
        except Exception as e:
            print(f"Erreur lors de la récupération des torrents de la série: {e}")
            return []

    def get_best_torrent(self, tmdb_id: int, content_type: str = 'auto',
                        season: Optional[int] = None, 
                        episode: Optional[int] = None,
                        preferred_language: str = 'VFF',
                        forced_resolution: Optional[str] = None) -> Dict:
        """
        Trouve le meilleur torrent pour un contenu donné
        
        Args:
            tmdb_id: ID TMDB du contenu
            content_type: 'movie', 'tv' ou 'auto'
            season: Numéro de saison (pour les séries TV)
            episode: Numéro d'épisode (pour les séries TV)
            preferred_language: Langue préférée ('VFF', 'MULTi', 'VOST', etc.)
            forced_resolution: Résolution forcée ('1080p', '720p', '4k', '2160p', etc.)
            
        Returns:
            Dictionnaire avec les infos du meilleur torrent ou résultat d'erreur
        """
        # Vérifier la disponibilité
        available, detected_type, details = self.is_content_available(tmdb_id, content_type)
        
        if not available:
            return {
                'success': False,
                'error': 'Contenu non disponible sur YggFlix',
                'tmdb_id': tmdb_id
            }
        
        # Récupérer les torrents selon le type
        if detected_type == 'movie':
            torrents = self.get_movie_torrents(tmdb_id)
        elif detected_type == 'tv':
            torrents = self.get_tv_torrents(tmdb_id, season, episode)
        else:
            return {
                'success': False,
                'error': 'Type de contenu non reconnu',
                'tmdb_id': tmdb_id
            }
        
        if not torrents:
            return {
                'success': False,
                'error': 'Aucun torrent trouvé pour ce contenu',
                'tmdb_id': tmdb_id,
                'content_type': detected_type,
                'details': details
            }
        
        # Filtrer par résolution forcée si spécifiée
        if forced_resolution:
            filtered_torrents = [t for t in torrents if t.get('resolution') == forced_resolution]
            if not filtered_torrents:
                return {
                    'success': False,
                    'error': f'Aucun torrent trouvé en résolution {forced_resolution}',
                    'tmdb_id': tmdb_id,
                    'content_type': detected_type,
                    'details': details,
                    'total_torrents_found': len(torrents),
                    'available_resolutions': list(set([t.get('resolution') for t in torrents if t.get('resolution')]))
                }
            torrents = filtered_torrents
        
        # Ajuster les priorités selon la langue préférée
        if preferred_language in self.language_priority:
            temp_priority = self.language_priority.copy()
            temp_priority[preferred_language] = 15  # Boost pour la langue préférée
            original_priority = self.language_priority
            self.language_priority = temp_priority
        
        # Calculer le score pour chaque torrent
        scored_torrents = []
        for torrent in torrents:
            score = self.calculate_torrent_score(torrent, forced_resolution)
            scored_torrents.append((score, torrent))
        
        # Restaurer les priorités originales
        if preferred_language in self.language_priority:
            self.language_priority = original_priority
        
        # Trier par score décroissant
        scored_torrents.sort(key=lambda x: x[0], reverse=True)
        
        best_torrent = scored_torrents[0][1]
        best_score = scored_torrents[0][0]
        
        return {
            'success': True,
            'tmdb_id': tmdb_id,
            'content_type': detected_type,
            'content_details': details,
            'best_torrent': best_torrent,
            'quality_score': best_score,
            'total_torrents_found': len(torrents),
            'season': season,
            'episode': episode,
            'forced_resolution': forced_resolution
        }

    def format_size(self, size_bytes: int) -> str:
        """Formate la taille en octets vers une forme lisible"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def print_best_torrent_info(self, result: Dict):
        """Affiche les informations du meilleur torrent de façon lisible"""
        if not result['success']:
            print(f"❌ Erreur: {result['error']}")
            if 'available_resolutions' in result:
                print(f"   Résolutions disponibles: {', '.join(result['available_resolutions'])}")
            return
        
        details = result['content_details']
        torrent = result['best_torrent']
        
        print(f"✅ Contenu trouvé: {details['title']}")
        print(f"📅 Type: {result['content_type']}")
        if result.get('season') and result.get('episode'):
            print(f"📺 Saison {result['season']} - Épisode {result['episode']}")
        if result.get('forced_resolution'):
            print(f"🎯 Résolution forcée: {result['forced_resolution']}")
        
        print(f"\n🏆 Meilleur torrent (Score: {result['quality_score']}):")
        print(f"   📂 {torrent['title']}")
        print(f"   📐 Résolution: {torrent.get('resolution', 'N/A')}")
        print(f"   🌐 Langue: {torrent.get('language', 'N/A')}")
        print(f"   💿 Source: {torrent.get('source', 'N/A')}")
        print(f"   🎞️  Codec: {torrent.get('codec', 'N/A')}")
        print(f"   📊 Seeders: {torrent.get('seeders', 0)}")
        print(f"   📥 Taille: {self.format_size(torrent.get('size', 0))}")
        print(f"   📈 Téléchargements: {torrent.get('downloads', 0)}")

# Fonctions utilitaires pour une utilisation simple
def find_best_movie_torrent(tmdb_id: int, preferred_language: str = 'VFF', 
                           forced_resolution: Optional[str] = None) -> Dict:
    """
    Fonction simple pour trouver le meilleur torrent d'un film
    """
    selector = TorrentSelector()
    return selector.get_best_torrent(tmdb_id, 'movie', 
                                   preferred_language=preferred_language,
                                   forced_resolution=forced_resolution)

def find_best_episode_torrent(tmdb_id: int, season: int, episode: int, 
                             preferred_language: str = 'VFF',
                             forced_resolution: Optional[str] = None) -> Dict:
    """
    Fonction simple pour trouver le meilleur torrent d'un épisode
    """
    selector = TorrentSelector()
    return selector.get_best_torrent(tmdb_id, 'tv', season, episode, 
                                   preferred_language, forced_resolution)

def is_available_on_yggflix(tmdb_id: int) -> Tuple[bool, str]:
    """
    Fonction simple pour vérifier si un contenu est disponible
    """
    selector = TorrentSelector()
    available, content_type, _ = selector.is_content_available(tmdb_id)
    return available, content_type

# Exemple d'utilisation
if __name__ == "__main__":
    selector = TorrentSelector()
    
    print("=== Test Film: Retour vers le Futur en 1080p forcé ===")
    result = selector.get_best_torrent(105, preferred_language='VFF', forced_resolution='1080p')
    selector.print_best_torrent_info(result)
    
    print("\n=== Test Film: Retour vers le Futur en 4K forcé ===")
    result = selector.get_best_torrent(105, preferred_language='VFF', forced_resolution='4k')
    selector.print_best_torrent_info(result)
    
    print("\n=== Test Série: Dr. Stone - S04E15 en 1080p ===")
    result = selector.get_best_torrent(86031, 'tv', season=4, episode=15, 
                                     preferred_language='VOST', forced_resolution='1080p')
    selector.print_best_torrent_info(result)
    
    print("\n=== Test sans résolution forcée (automatique) ===")
    result = selector.get_best_torrent(398929, preferred_language='VFF')
    selector.print_best_torrent_info(result)
    
    print("\n=== Vérification de disponibilité ===")
    available, content_type = is_available_on_yggflix(398929)
    print(f"Alibi.com disponible: {available} (Type: {content_type})")
    
    available, content_type = is_available_on_yggflix(86031)
    print(f"Dr. Stone disponible: {available} (Type: {content_type})")