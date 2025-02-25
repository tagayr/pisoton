from .utils import get_soup, _convert_minutes, safe_int_convert
from .constants import BASE_URL, HEADERS
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from .player import Player
from typing import List, Optional
from .database import Database

class TransfermarktScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        
        # Initialize database
        self.db = Database()
        self.db.init_db()

    # def scrape_player_data(self, player_url):
    #     """Scrape basic player information"""
    #     soup = get_soup(player_url)
    #     if not soup:
    #         return None
            
    #     # Your existing scrape_player_data code here
    #     pass


    # Function to scrape a single player's details
    def scrape_player_data(self, player_url):
        response = requests.get(player_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch player data: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        try:
            # Extract player_id from URL
            player_id = player_url.split('/spieler/')[-1].split('/')[0]            
            
            # Extract player name
            name = soup.find("h1").text.strip()
            name = re.sub(r"^#\d+\s*", "", name)  # Removes "#10 ", "#7 ", etc.

            
            # Extract market value and its update date
            market_value = "N/A"
            market_value_date = "N/A"
            currency = "N/A"
            
            try:
                # First find the market value box
                # market_box = soup.find("div", class_="data-header__market-value")
                market_box = soup.find("div", class_="data-header__box--small")
                if market_box:
                    # Get the complete text content
                    full_text = market_box.get_text(strip=True)
                    # Split at "Last update:" to separate value from date
                    if "Last update:" in full_text:
                        parts = full_text.split("Last update:")
                        value_text = parts[0].strip()
                        market_value_date = parts[1].strip()
                        
                        # Extract currency (first character)
                        currency = value_text[0]
                        
                        # Remove currency symbol and convert to number
                        value_text = value_text[1:].strip()  # Remove currency symbol
                        
                        # Convert to numerical value
                        if 'm' in value_text:
                            # Convert millions
                            number = float(value_text.replace('m', '').strip())
                            market_value = int(number * 1000000)
                        elif 'k' in value_text:
                            # Convert thousands
                            number = float(value_text.replace('k', '').strip())
                            market_value = int(number * 1000)
                
            except Exception as e:
                print(f"Error extracting market value: {e}")

            # Extract additional player details
            info_table = soup.find("div", class_="info-table info-table--right-space")
            age, position, foot, height, agent = "N/A", "N/A", "N/A", "N/A", "N/A"

            if info_table:
                # Find age
                age_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Date of birth/Age:")
                if age_label and age_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
                    age_text = age_label.find_next_sibling("span").get_text(strip=True)
                    age = re.search(r'\((\d+)\)', age_text).group(1) if re.search(r'\((\d+)\)', age_text) else "N/A"

                # Find position
                position_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Position:")
                if position_label and position_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
                    position = position_label.find_next_sibling("span").get_text(strip=True)

                # Find height
                height_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Height:")
                if height_label and height_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
                    height_raw = height_label.find_next_sibling("span").get_text(strip=True)
                    # Clean up height: remove 'm', replace comma with dot, remove non-breaking space (\xa0)
                    height = height_raw.replace(',', '.').replace('\xa0', '').replace('m', '').strip()

                # Find foot
                foot_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Foot:")
                if foot_label and foot_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
                    foot = foot_label.find_next_sibling("span").get_text(strip=True)

                # Find agent
                agent_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Player agent:")
                if agent_label and agent_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
                    agent = agent_label.find_next_sibling("span").get_text(strip=True)

            # Extract nationality
            # nationality_section = soup.find("div", class_="data-header__details")
            nationality_section = soup.find("div", class_="info-table info-table--right-space")
            if nationality_section:
                nationality_imgs = nationality_section.find_all("img", class_="flaggenrahmen")
                nationalities = list(set([img.get("title", "").strip() 
                                    for img in nationality_imgs 
                                    if img.get("title")]))
                nationality = ", ".join(nationalities) if nationalities else "N/A"
            else:
                nationality = "N/A"

            return {
                "Player ID": player_id,
                "Name": name,
                "Age": age,
                "Position": position,
                "Height": height,
                "Foot": foot,
                "Agent": agent,
                "Nationality": nationality,
                "Market Value": market_value,
                "Currency": currency,
                "Market Value Last Update": market_value_date,
                "Profile URL": player_url
            }
            
        except AttributeError:
            print(f"Failed to extract details for {player_url}")
            return None

    def scrape_player_performance(self, soup, season):
        """
        Scrape performance statistics for a player in a given season
        """
        performance_data = {}
        
        try:
            # Find the stats table
            print("Looking for stats table...")
            stats_table = soup.find("div", class_="responsive-table")
            print("Stats table found:", stats_table is not None)
            # if stats_table:
            #     print("Stats table HTML:", stats_table.prettify())
            
            # if not stats_table:
            #     print("No stats table found")
            #     return performance_data
                
            # Get all rows from the "Total" section
            print("Looking for rows...")
            total_rows = stats_table.find_all("tr", class_=["odd", "even"])
            print(f"Found {len(total_rows)} rows")
            
            for idx, row in enumerate(total_rows):
                print(f"\nProcessing row {idx + 1}")
                columns = row.find_all("td")
                print(f"Found {len(columns)} columns")
                
                if not columns:
                    print("No columns found in this row")
                    continue
                    
                # Get competition name
                # competition = columns[0].get_text(strip=True)
                competition = columns[1].get_text(strip=True)
                print(f"Competition: {competition}")
                
                if competition == "Total":
                    print("Skipping Total row")
                    continue
                    
                # Print all column values before extraction
                print("Column values:")
                for i, col in enumerate(columns):
                    print(f"Column {i}: {col.get_text(strip=True)}")
                    
                # Extract statistics
                try:
                    stats = {
                        "Games": safe_int_convert(columns[2]),
                        "Goals": safe_int_convert(columns[3]),
                        "Assists": safe_int_convert(columns[4]),
                        "Yellow Cards": safe_int_convert(columns[5]),
                        "Second Yellow Cards": safe_int_convert(columns[6]),
                        "Red Cards": safe_int_convert(columns[7]),                        
                        "Minutes": _convert_minutes(columns[8].get_text(strip=True)) or 0
                    }
                    # print (stats)
                    print(f"Successfully extracted stats for {competition}")
                except Exception as e:
                    print(f"Error extracting stats: {str(e)}")
                    continue
                
                performance_data[competition] = stats
                
            return {
                f"Season {season}": performance_data
            }
            
        except Exception as e:
            print(f"Error scraping performance data: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return performance_data
        
    def scrape_player_full_stats(self, player_id, seasons=5):
        """
        Scrape performance statistics for multiple seasons
        """
        base_url = f"https://www.transfermarkt.com/player/leistungsdaten/spieler/{player_id}/plus/0"
        all_stats = {}
        
        current_year = 2024  # I might want to make this dynamic
        
        for i in range(seasons):
            season = current_year - i
            url = f"{base_url}?saison={season}"
            
            # Use the existing get_soup function
            soup = get_soup(url)
            if soup:
                print(f"Scraping season {season}...")
                season_stats = self.scrape_player_performance(soup, season)
                all_stats.update(season_stats)
                
        return all_stats

    def get_player(self, player_url: str, include_stats: bool = True) -> Player:
        """
        Get complete player information including basic data and performance stats
        
        Args:
            player_url: URL of the player's profile
            include_stats: Whether to include performance statistics
        """
        # Get basic player data
        basic_data = self.scrape_player_data(player_url)
        
        # Get performance stats if requested
        stats = None
        if include_stats:
            player_id = player_url.split('/spieler/')[-1]
            stats = self.scrape_player_full_stats(player_id)
        
        # Create and return Player instance
        return Player.from_scraper_data(basic_data, stats)


    def get_player_urls_from_page(self, page_number: int) -> List[str]:
        """
        Get player URLs from a specific page of TransferMarkt's player list
        """
        base_url = "https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop"
        url = f"{base_url}?page={page_number}"

        # https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop/plus/0/galerie/0?ausrichtung=alle&spielerposition_id=alle&altersklasse=alle&jahrgang=0&land_id=0&kontinent_id=2&yt0=Show&page=15
        
        print(f"Fetching player list from: {url}")
        soup = get_soup(url)
        if not soup:
            print("Failed to get soup from URL")
            return []
            
        player_urls = []
        try:
            # Find the main content table
            table = soup.find("div", class_="responsive-table")  # Changed this line
            if table:
                # Find all player links within the table
                player_links = table.find_all("a", title=True, href=True)  # Changed this line
                print(f"Found {len(player_links)} potential player links")
                
                for link in player_links:
                    href = link.get("href")
                    # Only include links that lead to player profiles
                    if href and "/profil/spieler/" in href:
                        if not href.startswith("https"):
                            full_url = f"https://www.transfermarkt.com{href}"
                        else:
                            full_url = href
                        if full_url not in player_urls:  # Avoid duplicates
                            player_urls.append(full_url)
                
                print(f"Extracted {len(player_urls)} unique player URLs")
            else:
                print("Could not find the player table")
        
        except Exception as e:
            print(f"Error getting player URLs from page {page_number}: {str(e)}")
        
        return player_urls

    def scrape_all_players(self, num_pages: int = 1, save_to_json: bool = True) -> List[Player]:
        """
        Scrape data for all players across multiple pages
        """
        all_players = []
        failed_urls = []

        for page in range(1, num_pages + 1):
            print(f"\nScraping page {page}/{num_pages}")
            
            # Get player URLs from this page
            player_urls = self.get_player_urls_from_page(page)
            
            if not player_urls:
                print(f"No player URLs found on page {page}")
                continue
                
            print(f"Found {len(player_urls)} players on page {page}")
            print("First few URLs:", player_urls[:3])  # Debug print
            
            # Scrape each player
            for url in player_urls:
                try:
                    print(f"\nScraping player from {url}")
                    player = self.get_player(url)
                    
                    # if player:
                    #     print(f"Successfully scraped data for {player.name}")
                    #     all_players.append(player)
                    #     if save_to_json:
                    #         json_file = player.save_to_json()
                    #         print(f"Saved player data to {json_file}")
                    if player:
                        # Store in database
                        if self.db.store_player(player):
                            print(f"Stored {player.name} in database")
                            all_players.append(player)
                        else:
                            print(f"Failed to store {player.name} in database")
                            failed_urls.append(url)                            
                    else:
                        failed_urls.append(url)
                        print(f"Failed to scrape player from {url}")
                        
                except Exception as e:
                    failed_urls.append(url)
                    print(f"Error scraping player from {url}: {str(e)}")
                
                # Add a delay to be nice to the server
                time.sleep(2)
            
            # Add a longer delay between pages
            time.sleep(5)
        
        # Print summary
        print(f"\nScraping complete!")
        print(f"Successfully scraped {len(all_players)} players")
        if failed_urls:
            print(f"Failed to scrape {len(failed_urls)} players:")
            for url in failed_urls:
                print(f"  - {url}")
        
        return all_players

# Function to scrape multiple players from a Transfermarkt page
#     def scrape_players_from_page(self, page_url):
#         response = requests.get(page_url, headers=HEADERS)
#         if response.status_code != 200:
#             print(f"Failed to fetch page: {response.status_code}")
#             return []
#         
#         soup = BeautifulSoup(response.text, "html.parser")
#         players = []
# 
#         player_rows = soup.find_all("tr", class_=["odd", "even"])
#         
#         for row in player_rows:
#             try:
#                 link_tag = row.find("td", class_="hauptlink").find("a")
#                 player_name = link_tag.text.strip()
#                 player_url = BASE_URL + link_tag["href"]
# 
#                 player_data = self.scrape_player_data(player_url)
#                 if player_data:
#                     players.append(player_data)
# 
#                 # Respectful scraping: Random delay
#                 time.sleep(random.uniform(1, 3))
#             except AttributeError:
#                 continue
#         
#         return players

# Main function to scrape multiple pages
#     def scrape_transfermarkt(self, num_pages=1):
#         all_players = []
#         
#         for page in range(1, num_pages + 1):
#             url = f"https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop?page={page}"
#             print(f"Scraping page {page}...")
# 
#             players = self.scrape_players_from_page(url)
#             all_players.extend(players)
# 
#             # Random delay to prevent IP ban
#             time.sleep(random.uniform(3, 6))
#         
#         return all_players



# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------  

    # def scrape_player_performance(self, player_id, season):
    #     """Scrape performance statistics for a single season"""
    #     url = f"{self.base_url}/player/leistungsdaten/spieler/{player_id}/plus/0?saison={season}"
    #     soup = get_soup(url)
    #     if not soup:
    #         return None
            
    #     # Your existing scrape_player_performance code here
    #     pass

    # def scrape_player_full_stats(self, player_id, seasons=3):
    #     """Scrape performance statistics for multiple seasons"""
    #     all_stats = {}
    #     current_year = 2024  # You might want to make this dynamic
        
    #     for i in range(seasons):
    #         season = current_year - i
    #         season_stats = self.scrape_player_performance(player_id, season)
    #         if season_stats:
    #             all_stats.update(season_stats)
                
    #     return all_stats