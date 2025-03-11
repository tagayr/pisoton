# import streamlit as st
import streamlit as st
import psycopg2
from typing import Optional

def get_player_from_db(name: str) -> Optional[dict]:
    """Get player data from SQLite database"""
    conn = psycopg2.connect(
        dbname="your_database",
        user="your_user",
        password="your_password",
        host="your_host",
        port="5432"
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT name, market_value, currency, market_value_last_update 
            FROM players 
            WHERE name LIKE ? 
            ORDER BY market_value_last_update DESC
            LIMIT 1
        """, (f'%{name}%',))
        
        result = cursor.fetchone()
        
        if result:
            return {
                'name': result[0],
                'market_value': result[1],
                'currency': result[2],
                'last_update': result[3]
            }
        return None
        
    finally:
        conn.close()

def predict_value(player_data: dict) -> float:
    """
    Predict player market value using trained model
    TODO: Implement actual model prediction
    """
    # Placeholder - replace with actual model prediction
    return player_data['market_value'] * 1.1

# App title
st.title('Football Player Market Value Predictor')

# Search box
player_name = st.text_input('Enter player name')

if player_name:
    player_data = get_player_from_db(player_name)
    
    if player_data:
        st.success(f"Found player: {player_data['name']}")
        
        # Display actual market value
        st.subheader('Current Market Value (Transfermarkt)')
        st.write(f"{player_data['market_value']:,} {player_data['currency']}")
        st.write(f"Last updated: {player_data['last_update']}")
        
        # Display predicted value
        predicted_value = predict_value(player_data)
        st.subheader('Predicted Market Value')
        st.write(f"{predicted_value:,} {player_data['currency']}")
        
        # Show difference
        diff = predicted_value - player_data['market_value']
        diff_percent = (diff / player_data['market_value']) * 100
        
        if diff > 0:
            st.write(f"Our model predicts a value **{diff_percent:.1f}%** higher than the current market value")
        else:
            st.write(f"Our model predicts a value **{abs(diff_percent):.1f}%** lower than the current market value")
            
    else:
        st.error(f"No player found with name '{player_name}'")
