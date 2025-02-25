from src.scraper import TransfermarktScraper
from datetime import datetime
import json

def main():
    transfermarkt_scraper = TransfermarktScraper()
    
    # # Get player data - version 1 
    # # Scrape player basic info
    # player_url = "https://www.transfermarkt.com/harry-kane/profil/spieler/132098"
    # player_data = transfermarkt_scraper.scrape_player_data(player_url)
    # print("Player data:", player_data)
    
    # # Scrape player performance stats
    # player_id = "132098"
    # stats = transfermarkt_scraper.scrape_player_full_stats(player_id, seasons=5) # 5 seasons
    # print("Performance stats:", stats)

    # ---------------------------------------------------------------------
    # ---------------------------------------------------------------------
    # ---------------------------------------------------------------------

    # # Get player data - version 2 - using player class
    # # player_url = "https://www.transfermarkt.com/bradley-barcola/profil/spieler/708265"
    # player_url = "https://www.transfermarkt.com/lamine-yamal/profil/spieler/937958"
    # player = transfermarkt_scraper.get_player(player_url)
    
    # # Access player information
    # print(f"Player: {player.name}")
    # print(f"Current value: {player.currency}{player.market_value:,}")
    # print(f"Total goals: {player.get_total_goals()}")
    
    # # Save to JSON
    # json_file = player.save_to_json()
    # print(f"Data saved to {json_file}")
 


    # # Get player data - version 3 - scraping multiple players
    scraper = TransfermarktScraper()
    
    # # Scrape first 5 pages (about 125 players)
    players = scraper.scrape_all_players(max_pages=20, continents=range(1, 7)) # 20 pages
    
    # # Save summary of all players
    summary = {
        "scrape_date": datetime.now().isoformat(),
        "total_players": len(players),
        "players": [
            {
                "id": p.player_id,
                "name": p.name,
                "market_value": p.market_value,
                "currency": p.currency
            }
            for p in players
        ]
    }
    
    with open("transfermarkt_scraper/data/output/scraping_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)
    
    print(f"\nScraping summary saved to data/output/scraping_summary.json")


if __name__ == "__main__":
    main()