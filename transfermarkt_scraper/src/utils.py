import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
from .constants import BASE_URL, HEADERS


# Helper function to get BeautifulSoup object from URL
def get_soup(url):
    """Get BeautifulSoup object from URL"""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error fetching URL {url}: {str(e)}")
        return None

# Helper function to convert minutes string to integer
def _convert_minutes(minutes_str):
    """
    Convert minutes string (e.g. "1.536'" or "90'") to integer
    """
    try:
        # Remove the quote mark and any dots
        clean_str = minutes_str.replace("'", "").replace(".", "")
        return int(clean_str) if clean_str else 0
    except:
        return 0

# Helper function to safely convert string to int
def safe_int_convert(value):
    value = value.get_text(strip=True)
    return int(value) if value and value != '-' else 0

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

# Function to scrape a single player's details
# def scrape_player_data(player_url):
#     response = requests.get(player_url, headers=HEADERS)
#     if response.status_code != 200:
#         print(f"Failed to fetch player data: {response.status_code}")
#         return None
#     
#     soup = BeautifulSoup(response.text, "html.parser")
#     
#     try:
#         # Extract player name
#         name = soup.find("h1").text.strip()
#         name = re.sub(r"^#\d+\s*", "", name)  # Removes "#10 ", "#7 ", etc.
# 
#         
#         # Extract market value and its update date
#         market_value = "N/A"
#         market_value_date = "N/A"
#         currency = "N/A"
#         
#         try:
#             # First find the market value box
#             # market_box = soup.find("div", class_="data-header__market-value")
#             print("youhou!!!!")
#             market_box = soup.find("div", class_="data-header__box--small")
#             if market_box:
#                 # Get the complete text content
#                 full_text = market_box.get_text(strip=True)
#                 # Split at "Last update:" to separate value from date
#                 if "Last update:" in full_text:
#                     parts = full_text.split("Last update:")
#                     value_text = parts[0].strip()
#                     market_value_date = parts[1].strip()
#                     
#                     # Extract currency (first character)
#                     currency = value_text[0]
#                     
#                     # Remove currency symbol and convert to number
#                     value_text = value_text[1:].strip()  # Remove currency symbol
#                     
#                     # Convert to numerical value
#                     if 'm' in value_text:
#                         # Convert millions
#                         number = float(value_text.replace('m', '').strip())
#                         market_value = int(number * 1000000)
#                     elif 'k' in value_text:
#                         # Convert thousands
#                         number = float(value_text.replace('k', '').strip())
#                         market_value = int(number * 1000)
#             
#         except Exception as e:
#             print(f"Error extracting market value: {e}")
# 
#         # Extract additional player details
#         info_table = soup.find("div", class_="info-table info-table--right-space")
#         age, position, foot, height, agent = "N/A", "N/A", "N/A", "N/A", "N/A"
# 
#         if info_table:
#             # Find age
#             age_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Date of birth/Age:")
#             if age_label and age_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
#                 age_text = age_label.find_next_sibling("span").get_text(strip=True)
#                 age = re.search(r'\((\d+)\)', age_text).group(1) if re.search(r'\((\d+)\)', age_text) else "N/A"
# 
#             # Find position
#             position_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Position:")
#             if position_label and position_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
#                 position = position_label.find_next_sibling("span").get_text(strip=True)
# 
#             # Find height
#             height_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Height:")
#             if height_label and height_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
#                 height_raw = height_label.find_next_sibling("span").get_text(strip=True)
#                 # Clean up height: remove 'm', replace comma with dot, remove non-breaking space (\xa0)
#                 height = height_raw.replace(',', '.').replace('\xa0', '').replace('m', '').strip()
# 
#             # Find foot
#             foot_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Foot:")
#             if foot_label and foot_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
#                 foot = foot_label.find_next_sibling("span").get_text(strip=True)
# 
#             # Find agent
#             agent_label = info_table.find("span", class_="info-table__content info-table__content--regular", string="Player agent:")
#             if agent_label and agent_label.find_next_sibling("span", class_="info-table__content info-table__content--bold"):
#                 agent = agent_label.find_next_sibling("span").get_text(strip=True)
# 
#         # Extract nationality
#         # nationality_section = soup.find("div", class_="data-header__details")
#         nationality_section = soup.find("div", class_="info-table info-table--right-space")
#         if nationality_section:
#             nationality_imgs = nationality_section.find_all("img", class_="flaggenrahmen")
#             nationalities = list(set([img.get("title", "").strip() 
#                                    for img in nationality_imgs 
#                                    if img.get("title")]))
#             nationality = ", ".join(nationalities) if nationalities else "N/A"
#         else:
#             nationality = "N/A"
# 
#         return {
#             "Name": name,
#             "Age": age,
#             "Position": position,
#             "Height": height,
#             "Foot": foot,
#             "Agent": agent,
#             "Nationality": nationality,
#             "Market Value": market_value,
#             "Currency": currency,
#             "Market Value Last Update": market_value_date,
#             "Profile URL": player_url
#         }
#         
#     except AttributeError:
#         print(f"Failed to extract details for {player_url}")
#         return None
# 
# Scrape performance statistics for a player in a given season    
# def scrape_player_performance(soup, season):
#     """
#     Scrape performance statistics for a player in a given season
#     """
#     performance_data = {}
#     
#     try:
#         # Find the stats table
#         stats_table = soup.find("div", class_="responsive-table")
#         if not stats_table:
#             return performance_data
#             
#         # Get all rows from the "Total" section
#         total_rows = stats_table.find_all("tr", class_=["odd", "even"])
#         
#         for row in total_rows:
#             columns = row.find_all("td")
#             if not columns:
#                 continue
#                 
#             # Get competition name
#             competition = columns[0].get_text(strip=True)
#             if competition == "Total":
#                 continue
#                 
#             # Extract statistics
#             stats = {
#                 "Games": int(columns[2].get_text(strip=True) or 0),
#                 "Goals": int(columns[3].get_text(strip=True) or 0),
#                 "Assists": int(columns[4].get_text(strip=True) or 0),
#                 "Yellow Cards": int(columns[5].get_text(strip=True) or 0),
#                 "Second Yellow Cards": int(columns[6].get_text(strip=True) or 0),
#                 "Red Cards": int(columns[7].get_text(strip=True) or 0),
#                 "Minutes": _convert_minutes(columns[8].get_text(strip=True))
#             }
#             
#             performance_data[competition] = stats
#             
#         return {
#             f"Season {season}": performance_data
#         }
#         
#     except Exception as e:
#         print(f"Error scraping performance data: {str(e)}")
#         return performance_data
# 
# 
# def scrape_player_full_stats(player_id, seasons=3):
#     """
#     Scrape performance statistics for multiple seasons
#     """
#     base_url = f"https://www.transfermarkt.com/player/leistungsdaten/spieler/{player_id}/plus/0"
#     all_stats = {}
#     
#     current_year = 2024  # You might want to make this dynamic
#     
#     for i in range(seasons):
#         season = current_year - i
#         url = f"{base_url}?saison={season}"
#         
#         # Use your existing get_soup function here
#         soup = get_soup(url)
#         if soup:
#             season_stats = scrape_player_performance(soup, season)
#             all_stats.update(season_stats)
#             
#     return all_stats
# 
# 
# # Function to scrape multiple players from a Transfermarkt page
# def scrape_players_from_page(page_url):
#     response = requests.get(page_url, headers=HEADERS)
#     if response.status_code != 200:
#         print(f"Failed to fetch page: {response.status_code}")
#         return []
#     
#     soup = BeautifulSoup(response.text, "html.parser")
#     players = []
# 
#     player_rows = soup.find_all("tr", class_=["odd", "even"])
#     
#     for row in player_rows:
#         try:
#             link_tag = row.find("td", class_="hauptlink").find("a")
#             player_name = link_tag.text.strip()
#             player_url = BASE_URL + link_tag["href"]
# 
#             player_data = scrape_player_data(player_url)
#             if player_data:
#                 players.append(player_data)
# 
#             # Respectful scraping: Random delay
#             time.sleep(random.uniform(1, 3))
#         except AttributeError:
#             continue
#     
#     return players
# 
# # Main function to scrape multiple pages
# def scrape_transfermarkt(num_pages=1):
#     all_players = []
#     
#     for page in range(1, num_pages + 1):
#         url = f"https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop?page={page}"
#         print(f"Scraping page {page}...")
# 
#         players = scrape_players_from_page(url)
#         all_players.extend(players)
# 
#         # Random delay to prevent IP ban
#         time.sleep(random.uniform(3, 6))
#     
#     return all_players
