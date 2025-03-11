import streamlit as st
import pandas as pd
import pickle

# Load the model and data
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load player database 
players_df = pd.read_csv('players_database.csv')  # Adjust filename as needed

# Set up the Streamlit page
st.title('Football Player Value Predictor')

# Create a search box
search_name = st.text_input('Search for a player:')

if search_name:
    # Filter players based on search input
    filtered_players = players_df[players_df['name'].str.contains(search_name, case=False, na=False)]
    
    if len(filtered_players) > 0:
        # Display matching players in a selectbox
        selected_player = st.selectbox(
            'Select a player:',
            filtered_players['name'].tolist()
        )
        
        if selected_player:
            # Get player data
            player_data = filtered_players[filtered_players['name'] == selected_player].iloc[0]
            
            # Display player information
            st.write('### Player Information')
            st.write(f"Current Market Value: €{player_data['market_value']:,.2f}")
            
            # Prepare features for prediction
            features = player_data[model.feature_names_]  # Adjust based on your model features
            
            # Make prediction
            predicted_value = model.predict([features])[0]
            
            st.write(f"Predicted Market Value: €{predicted_value:,.2f}")
            
            # Calculate difference
            difference = predicted_value - player_data['market_value']
            difference_percent = (difference / player_data['market_value']) * 100
            
            st.write(f"Difference: €{difference:,.2f} ({difference_percent:.1f}%)")
            
    else:
        st.write('No players found matching your search.')

# Add some instructions
st.sidebar.markdown("""
## How to use
1. Enter a player's name in the search box
2. Select the player from the dropdown
3. View the current and predicted market values
""")
