
import streamlit as st
import json
import os
from game_engine import display_stat_bars, display_action_analysis_with_bars

def load_game_stats(player_name=None):
    """Load player stats from saved game or return defaults"""
    if player_name:
        # Try to load from saved game file
        filename = f"streamlit_save_{player_name.lower().replace(' ', '_')}.json"
        if os.path.exists(filename):
            try:
                with open(filename, "r") as file:
                    save_data = json.load(file)
                return {
                    "player_name": save_data.get("player_name", player_name),
                    "health": save_data.get("character_health", 100),
                    "points": save_data.get("character_points", 0),
                    "player_class": save_data.get("player_class", "Unknown"),
                    "stats": save_data.get("player_stats", {"Strength": 5, "Luck": 5, "Agility": 5})
                }
            except:
                pass
    
    # Default stats if no save found
    return {
        "player_name": player_name or "Zachor",
        "health": 100,
        "points": 0,
        "player_class": "Warrior",
        "stats": {"Strength": 7, "Luck": 5, "Agility": 6}
    }

def create_progress_bar(value, max_value, label, color="blue"):
    """Create a custom progress bar with label"""
    percentage = min(100, max(0, (value / max_value) * 100))
    
    # Color coding for health
    if label == "Health":
        if percentage > 70:
            color = "green"
        elif percentage > 30:
            color = "orange" 
        else:
            color = "red"
    elif label == "Points":
        color = "purple"
    
    st.write(f"**{label}:** {value}/{max_value}")
    st.progress(percentage / 100)
    
    return percentage

def display_stat_bar_ui(stat_name, stat_value, max_stat=10):
    """Display individual stat bar"""
    percentage = min(100, max(0, (stat_value / max_stat) * 100))
    
    # Visual bar using Unicode characters
    filled_blocks = int(percentage / 5)  # 20 blocks total (100/5)
    empty_blocks = 20 - filled_blocks
    
    bar_visual = "█" * filled_blocks + "░" * empty_blocks
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{stat_name}:** [{bar_visual}]")
    with col2:
        st.write(f"{stat_value}/{max_stat}")

def main():
    st.set_page_config(
        page_title="Zachor: Character Stats",
        page_icon="⚔️",
        layout="wide"
    )
    
    st.title("⚔️ Zachor: Echoes of the Hollow")
    st.subheader("Character Status Dashboard")
    
    # Player name input
    player_name = st.text_input("Enter character name to load stats:", placeholder="Enter your character name")
    
    # Load stats
    game_data = load_game_stats(player_name if player_name else None)
    
    # Display character info
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Character Information")
        st.write(f"**Name:** {game_data['player_name']}")
        st.write(f"**Class:** {game_data['player_class']}")
        st.write("---")
        
        # Health bar
        st.write("### Vital Stats")
        create_progress_bar(game_data['health'], 100, "Health")
        st.write("")
        
        # Points display
        create_progress_bar(min(game_data['points'], 1000), 1000, "Points")
        
    with col2:
        st.write("### Combat Stats")
        
        # Display each stat with visual bars
        for stat_name, stat_value in game_data['stats'].items():
            display_stat_bar_ui(stat_name, stat_value)
        
        st.write("---")
        
        # Overall power level
        total_stats = sum(game_data['stats'].values())
        st.write(f"**Total Power:** {total_stats}/30")
        create_progress_bar(total_stats, 30, "Overall Power", "gold")
    
    st.write("---")
    
    # Interactive stat bars using the game engine
    if st.button("🎯 Show Detailed Stat Analysis"):
        st.write("### Detailed Character Analysis")
        
        # Use the game engine's display function
        with st.expander("Character Status Bars", expanded=True):
            # Capture the output of the game engine function
            import io
            from contextlib import redirect_stdout
            
            output = io.StringIO()
            with redirect_stdout(output):
                display_stat_bars(game_data['stats'], game_data['health'], game_data['points'])
            
            # Display the formatted output
            stat_display = output.getvalue()
            st.code(stat_display, language=None)
    
    # Action analysis section
    st.write("---")
    st.write("### Action Analysis Tool")
    
    player_action = st.text_input("Enter an action to analyze:", placeholder="e.g., 'attack the goblin', 'sneak past quietly'")
    
    if st.button("🔍 Analyze Action") and player_action:
        st.write("### Action Analysis Results")
        
        # Use the game engine's analysis function
        with st.expander("Analysis Results", expanded=True):
            import io
            from contextlib import redirect_stdout
            
            output = io.StringIO()
            with redirect_stdout(output):
                display_action_analysis_with_bars(player_action, game_data['stats'], game_data['health'], game_data['points'])
            
            analysis_output = output.getvalue()
            st.code(analysis_output, language=None)
    
    # Refresh button
    if st.button("🔄 Refresh Stats"):
        st.rerun()
    
    # Footer
    st.write("---")
    st.write("*Stats are loaded from your saved game file. Play the main game in `app.py` to update your character.*")

if __name__ == "__main__":
    main()
