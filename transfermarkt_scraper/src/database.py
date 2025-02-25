from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from .config import DB_CONFIG 
Base = declarative_base()

class PlayerDB(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String, unique=True)  # TransferMarkt ID
    name = Column(String)
    age = Column(Integer)
    position = Column(String)
    height = Column(String)
    foot = Column(String)
    agent = Column(String)
    nationality = Column(String)
    market_value = Column(Integer)
    currency = Column(String)
    market_value_last_update = Column(DateTime)
    profile_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with performances
    performances = relationship("PerformanceDB", back_populates="player")

class PerformanceDB(Base):
    __tablename__ = 'performances'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(String, ForeignKey('players.player_id'))
    season = Column(String)
    competition = Column(String)
    games = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    yellow_cards = Column(Integer)
    second_yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    minutes_played = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with player
    player = relationship("PlayerDB", back_populates="performances")

class Database:
    def __init__(self):
        # Construct connection string from config
        connection_string = (
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
            f"/{DB_CONFIG['database']}"
        )
        
        # You can also add additional parameters for the connection
        self.engine = create_engine(
            connection_string,
            echo=DB_CONFIG.get('echo', False),  # SQL query logging
            pool_size=DB_CONFIG.get('pool_size', 5),  # Connection pool size
            max_overflow=DB_CONFIG.get('max_overflow', 10),  # Max extra connections
            pool_timeout=DB_CONFIG.get('pool_timeout', 30)  # Timeout waiting for connection
        )
        self.Session = sessionmaker(bind=self.engine)
        
    def init_db(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        
    def store_player(self, player):
        """Store a player and their performance data"""
        session = self.Session()
        try:
            # Convert market value date string to datetime
            market_value_date = datetime.strptime(
                player.market_value_last_update, 
                "%b %d, %Y"
            ) if player.market_value_last_update != "N/A" else None
            
            # Create player record
            player_db = PlayerDB(
                player_id=player.player_id,
                name=player.name,
                age=player.age,
                position=player.position,
                height=player.height,
                foot=player.foot,
                agent=player.agent,
                nationality=player.nationality,
                market_value=player.market_value,
                currency=player.currency,
                market_value_last_update=market_value_date,
                profile_url=player.profile_url
            )
            
            # Add performances
            for season, competitions in player.performance_stats.items():
                for competition, stats in competitions.items():
                    performance = PerformanceDB(
                        season=season,
                        competition=competition,
                        games=stats.get('Games', 0),
                        goals=stats.get('Goals', 0),
                        assists=stats.get('Assists', 0),
                        yellow_cards=stats.get('Yellow Cards', 0),
                        second_yellow_cards=stats.get('Second Yellow Cards', 0),
                        red_cards=stats.get('Red Cards', 0),
                        minutes_played=stats.get('Minutes', 0)
                    )
                    player_db.performances.append(performance)
            
            session.merge(player_db)  # Use merge instead of add to handle updates
            session.commit()
            return True
            
        except Exception as e:
            print(f"Error storing player {player.name}: {str(e)}")
            session.rollback()
            return False
            
        finally:
            session.close()