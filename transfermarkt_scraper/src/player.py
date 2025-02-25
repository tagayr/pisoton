from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Player:
    """Class representing a football player with their data and statistics"""
    
    # Basic information
    player_id: str
    name: str
    age: int
    position: str
    height: str
    foot: str
    agent: str
    nationality: str
    
    # Market value information
    market_value: int
    currency: str
    market_value_last_update: str
    
    # URL for reference
    profile_url: str
    
    # Performance statistics by season
    performance_stats: Dict[str, Dict[str, Dict[str, int]]] = None
    
    @classmethod
    def from_scraper_data(cls, basic_data: Dict[str, Any], stats: Optional[Dict] = None):
        """
        Create a Player instance from scraped data
        
        Args:
            basic_data: Dictionary containing basic player information
            stats: Dictionary containing performance statistics by season
        """
        player = cls(
            player_id=basic_data['Player ID'],
            name=basic_data['Name'],
            age=int(basic_data['Age']),
            position=basic_data['Position'],
            height=basic_data['Height'],
            foot=basic_data['Foot'],
            agent=basic_data['Agent'],
            nationality=basic_data['Nationality'],
            market_value=basic_data['Market Value'],
            currency=basic_data['Currency'],
            market_value_last_update=basic_data['Market Value Last Update'],
            profile_url=basic_data['Profile URL'],
            performance_stats=stats or {}
        )
        return player
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player data to dictionary format"""
        return {
            'basic_info': {
                'player_id': self.player_id,
                'name': self.name,
                'age': self.age,
                'position': self.position,
                'height': self.height,
                'foot': self.foot,
                'agent': self.agent,
                'nationality': self.nationality,
            },
            'market_value_info': {
                'value': self.market_value,
                'currency': self.currency,
                'last_update': self.market_value_last_update
            },
            'profile_url': self.profile_url,
            'performance_stats': self.performance_stats
        }
    
    def save_to_json(self, filename: Optional[str] = None):
        """Save player data to JSON file"""
        import json
        import os
        
        if filename is None:
            # Generate filename based on player name and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.name.replace(' ', '_')}_{timestamp}.json"
        
        # Ensure output directory exists
        os.makedirs('transfermarkt_scraper/data/output', exist_ok=True)
        filepath = os.path.join('transfermarkt_scraper/data/output', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            
        return filepath
    
    def get_season_stats(self, season: str) -> Dict[str, Dict[str, int]]:
        """Get statistics for a specific season"""
        return self.performance_stats.get(f"Season {season}", {})
    
    def get_total_goals(self) -> int:
        """Calculate total goals across all seasons and competitions"""
        total = 0
        for season in self.performance_stats.values():
            for competition in season.values():
                total += competition.get('Goals', 0)
        return total