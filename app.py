import streamlit as st
import random
import os
import json
from game_engine import generate_ai_story, process_choice
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def init_supabase():
    """Initialize Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.warning("⚠️ Supabase secrets not configured! Game data will be saved locally only.")
        return None

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {e}")
        return None

# Initialize Supabase client
supabase_client = init_supabase()

def save_game_to_supabase(player_name, player_stats, player_class, character_health, character_points, story_history, current_story, current_choices):
    """Save game data to Supabase"""
    if not supabase_client:
        st.error("❌ Supabase client not available. Saving locally instead...")
        save_game_local(player_name, player_stats, player_class, character_health, character_points, story_history, current_story, current_choices)
        return

    try:
        # Convert complex data to JSON strings
        story_history_json = json.dumps(story_history)
        current_choices_json = json.dumps(current_choices)

        data = {
            "player_name": player_name,
            "strength": player_stats["Strength"],
            "luck": player_stats["Luck"],
            "agility": player_stats["Agility"],
            "player_class": player_class,
            "character_health": character_health,
            "character_points": character_points,
            "story_history": story_history_json,
            "current_story": current_story,
            "current_choices": current_choices_json
        }

        # First try to check if player exists
        existing = supabase_client.table('streamlit_saves').select('player_name').eq('player_name', player_name).execute()

        if existing.data:
            # Update existing record
            result = supabase_client.table('streamlit_saves').update(data).eq('player_name', player_name).execute()
        else:
            # Insert new record
            result = supabase_client.table('streamlit_saves').insert(data).execute()

        st.success("✅ Game saved to cloud successfully!")

    except Exception as e:
        error_message = str(e)
        st.error(f"Failed to save to Supabase: {e}")

        if "does not exist" in error_message:
            st.error("❌ The 'streamlit_saves' table doesn't exist in your Supabase database.")
            st.info("📋 **Instructions to create the table in Supabase:**")
            st.write("1. Go to your **Supabase Dashboard**")
            st.write("2. Navigate to **SQL Editor** (in the left sidebar)")
            st.write("3. Click **New Query**")
            st.write("4. Copy and paste this SQL command:")

            # Show the create table command
            st.code("""
-- First, drop the existing table if it has wrong structure
DROP TABLE IF EXISTS public.streamlit_saves;

-- Create the table with correct structure
CREATE TABLE public.streamlit_saves (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    player_name TEXT UNIQUE NOT NULL,
    player_class TEXT,
    character_health INTEGER DEFAULT 100,
    character_points INTEGER DEFAULT 0,
    strength INTEGER NOT NULL,
    luck INTEGER NOT NULL,
    agility INTEGER NOT NULL,
    story_history TEXT,
    current_story TEXT,
    current_choices TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Disable Row Level Security (RLS) for this table
ALTER TABLE public.streamlit_saves DISABLE ROW LEVEL SECURITY;

-- Grant permissions
GRANT ALL ON public.streamlit_saves TO authenticated;
GRANT ALL ON public.streamlit_saves TO anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;
            """, language="sql")

            st.write("5. Click **Run** to execute the query")
            st.write("6. Try saving your game again!")
        else:
            st.info("The 'streamlit_saves' table may not exist in your Supabase database. Creating local backup...")

        save_game_local(player_name, player_stats, player_class, character_health, character_points, story_history, current_story, current_choices)

def load_game_from_supabase(player_name):
    """Load game data from Supabase"""
    if not supabase_client:
        return load_game_local(player_name)

    try:
        result = supabase_client.from_("streamlit_saves").select("*").eq("player_name", player_name).execute()

        if result.data and len(result.data) > 0:
            data = result.data[0]

            # Reconstruct player_stats from separate columns
            player_stats = {
                "Strength": data["strength"],
                "Luck": data["luck"],
                "Agility": data["agility"]
            }

            story_history = json.loads(data["story_history"]) if data["story_history"] else []
            current_choices = json.loads(data["current_choices"]) if data["current_choices"] else []

            return {
                "player_name": data["player_name"],
                "player_stats": player_stats,
                "player_class": data["player_class"],
                "character_health": data["character_health"],
                "character_points": data["character_points"],
                "story_history": story_history,
                "current_story": data["current_story"],
                "current_choices": current_choices
            }
        else:
            st.info("No saved game found in cloud.")
            return None

    except Exception as e:
        st.error(f"Failed to load from Supabase: {e}")
        return load_game_local(player_name)

def save_game_local(player_name, player_stats, player_class, character_health, character_points, story_history, current_story, current_choices):
    """Save game data locally"""
    save_data = {
        "player_name": player_name,
        "player_stats": player_stats,
        "player_class": player_class,
        "character_health": character_health,
        "character_points": character_points,
        "story_history": story_history,
        "current_story": current_story,
        "current_choices": current_choices
    }

    filename = f"streamlit_save_{player_name.lower().replace(' ', '_')}.json"
    with open(filename, "w") as save_file:
        json.dump(save_data, save_file)
    st.success("Game saved locally!")

def load_game_local(player_name):
    """Load game data from local file"""
    filename = f"streamlit_save_{player_name.lower().replace(' ', '_')}.json"
    try:
        with open(filename, "r") as file:
            save_data = json.load(file)
        st.success("Game loaded from local file!")
        return save_data
    except FileNotFoundError:
        st.info("No local saved game found.")
        return None

st.title("Zachor: AI Text Adventure")

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'startup'
    st.session_state.story_history = []
    st.session_state.current_story = ""
    st.session_state.current_choices = []
    st.session_state.player_stats = {}
    st.session_state.player_class = ""
    st.session_state.character_health = 100
    st.session_state.character_points = 0

# Get player name
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""

# Startup screen - choose between new game or load game
if st.session_state.game_state == 'startup':
    st.write("## Welcome to Zachor!")
    st.write("Choose how you want to begin your adventure:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🆕 Start New Game", type="primary"):
            st.session_state.game_state = 'name_entry'
            st.rerun()

    with col2:
        if st.button("📁 Load Saved Game"):
            st.session_state.game_state = 'load_game'
            st.rerun()

# Load game screen
elif st.session_state.game_state == 'load_game':
    st.write("## Load Saved Game")

    load_name = st.text_input("Enter your character name:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Load Game") and load_name:
            loaded_data = load_game_from_supabase(load_name)
            if loaded_data:
                # Restore all game state
                st.session_state.player_name = loaded_data["player_name"]
                st.session_state.player_stats = loaded_data["player_stats"]
                st.session_state.player_class = loaded_data["player_class"]
                st.session_state.character_health = loaded_data["character_health"]
                st.session_state.character_points = loaded_data["character_points"]
                st.session_state.story_history = loaded_data.get("story_history", [])
                st.session_state.current_story = loaded_data.get("current_story", "")
                st.session_state.current_choices = loaded_data.get("current_choices", [])
                st.session_state.game_state = 'playing'
                st.rerun()

    with col2:
        if st.button("Back to Main Menu"):
            st.session_state.game_state = 'startup'
            st.rerun()

# Character Creation Flow
if st.session_state.game_state == 'name_entry':
    player_name = st.text_input("Enter your name:", value=st.session_state.player_name)

    if player_name:
        st.session_state.player_name = player_name

        if st.button("Continue to Character Creation"):
            # Generate initial stats
            st.session_state.player_stats = {
                "Strength": random.randint(1, 10),
                "Luck": random.randint(1, 10),
                "Agility": random.randint(1, 10)
            }
            st.session_state.game_state = 'stat_display'
            st.rerun()

elif st.session_state.game_state == 'stat_display':
    st.write(f"**Welcome, {st.session_state.player_name}!**")
    st.write("Your initial stats have been rolled:")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Strength", st.session_state.player_stats["Strength"])
    with col2:
        st.metric("Luck", st.session_state.player_stats["Luck"])
    with col3:
        st.metric("Agility", st.session_state.player_stats["Agility"])

    # Stat commentary
    if st.session_state.player_stats["Strength"] == 10:
        st.success("Ah yes, an honor to meet you, the god of strength!")
    elif st.session_state.player_stats["Luck"] == 10:
        st.success("Dang you lucky, probably can find a chest with diamonds")
    elif st.session_state.player_stats["Agility"] == 10:
        st.success("We got flash before GTA 6")
    elif st.session_state.player_stats["Strength"] == 1:
        st.warning("You are weak, be careful")
    elif st.session_state.player_stats["Luck"] < 5:
        st.warning("You would probably die in a 50/50 chance")
    elif st.session_state.player_stats["Agility"] < 5:
        st.warning("You are slow, so just dont try to run")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reroll Stats"):
            st.session_state.player_stats = {
                "Strength": random.randint(1, 10),
                "Luck": random.randint(1, 10),
                "Agility": random.randint(1, 10)
            }
            st.rerun()

    with col2:
        if st.button("Continue to Class Selection"):
            st.session_state.game_state = 'class_selection'
            st.rerun()

elif st.session_state.game_state == 'class_selection':
    st.write(f"**Choose your class, {st.session_state.player_name}:**")

    # Define classes
    classes = {
        "Warrior": {
            "bonus": {"Strength": 3},
            "description": "Born with fists of steel and the temper of a storm. +3 Strength"
        },
        "Oracle": {
            "bonus": {"Luck": 3},
            "description": "Blessed by fate itself, fortune follows in their wake. +3 Luck"
        },
        "Thief": {
            "bonus": {"Agility": 3},
            "description": "Silent as shadow, quick as regret. +3 Agility"
        }
    }

    # Display class options
    for class_name, class_info in classes.items():
        with st.expander(f"{class_name} - {class_info['description']}"):
            temp_stats = st.session_state.player_stats.copy()
            for stat, bonus in class_info['bonus'].items():
                temp_stats[stat] = min(10, temp_stats[stat] + bonus)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Strength", temp_stats["Strength"])
            with col2:
                st.metric("Luck", temp_stats["Luck"])
            with col3:
                st.metric("Agility", temp_stats["Agility"])

            if st.button(f"Choose {class_name}", key=f"choose_{class_name}"):
                # Apply class bonuses
                for stat, bonus in class_info['bonus'].items():
                    st.session_state.player_stats[stat] = min(10, st.session_state.player_stats[stat] + bonus)

                st.session_state.player_class = class_name
                st.session_state.game_state = 'start_adventure'
                st.rerun()

elif st.session_state.game_state == 'start_adventure':
    st.write(f"**Character Created Successfully!**")
    st.write(f"**Name:** {st.session_state.player_name}")
    st.write(f"**Class:** {st.session_state.player_class}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Strength", st.session_state.player_stats["Strength"])
    with col2:
        st.metric("Luck", st.session_state.player_stats["Luck"])
    with col3:
        st.metric("Agility", st.session_state.player_stats["Agility"])

    if st.button("Begin Your Adventure!", type="primary"):
        st.session_state.game_state = 'playing'
        st.rerun()

# Main Game Loop
elif st.session_state.game_state == 'playing':
    player_name = st.session_state.player_name

    # Display character info sidebar
    with st.sidebar:
        st.write("**Character Info**")
        st.write(f"**Name:** {st.session_state.player_name}")
        st.write(f"**Class:** {st.session_state.player_class}")
        st.write(f"**Health:** {st.session_state.character_health}")
        st.write(f"**Points:** {st.session_state.character_points}")

        st.write("**Stats:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("STR", st.session_state.player_stats["Strength"])
        with col2:
            st.metric("LCK", st.session_state.player_stats["Luck"])
        with col3:
            st.metric("AGL", st.session_state.player_stats["Agility"])

    # Collapsible stat bars section in main area
    with st.expander("📊 Character Stat Bars", expanded=False):
        # Health bar with heart icon and visual progress
        health_percentage = min(100, max(0, st.session_state.character_health)) / 100
        
        col1, col2 = st.columns([1, 8])
        with col1:
            # Heart icon with color based on health
            if health_percentage > 0.7:
                st.markdown("❤️", unsafe_allow_html=True)
            elif health_percentage > 0.3:
                st.markdown("🧡", unsafe_allow_html=True)  
            else:
                st.markdown("💔", unsafe_allow_html=True)
        
        with col2:
            st.write(f"**Health: {st.session_state.character_health}/100**")
            # Create a green-tinted progress bar
            st.progress(health_percentage)
        
        st.write("")
        
        # Points bar with gem icon
        points_percentage = min(100, max(0, (st.session_state.character_points / 1000) * 100)) / 100
        col1, col2 = st.columns([1, 8])
        with col1:
            st.markdown("💎", unsafe_allow_html=True)
        with col2:
            st.write(f"**Points: {st.session_state.character_points}/1000**")
            st.progress(points_percentage)
        
        st.write("")
        st.write("**Combat Stats:**")
        
        # Individual stat bars with icons
        stat_icons = {
            "Strength": "💪",
            "Luck": "🍀", 
            "Agility": "⚡"
        }
        
        for stat_name, stat_value in st.session_state.player_stats.items():
            stat_percentage = min(100, max(0, (stat_value / 10) * 100)) / 100
            
            col1, col2 = st.columns([1, 8])
            with col1:
                st.markdown(stat_icons.get(stat_name, "⚔️"), unsafe_allow_html=True)
            with col2:
                st.write(f"**{stat_name}: {stat_value}/10**")
                st.progress(stat_percentage)
        
        st.write("")
        
        # Total power bar
        total_stats = sum(st.session_state.player_stats.values())
        total_percentage = min(100, max(0, (total_stats / 30) * 100)) / 100
        
        col1, col2 = st.columns([1, 8])
        with col1:
            st.markdown("🔥", unsafe_allow_html=True)
        with col2:
            st.write(f"**Total Power: {total_stats}/30**")
            st.progress(total_percentage)

        st.write("---")
        st.write("**Game Controls**")

        if st.button("💾 Save Game", help="Save your progress to cloud/local storage"):
            save_game_to_supabase(
                st.session_state.player_name,
                st.session_state.player_stats,
                st.session_state.player_class,
                st.session_state.character_health,
                st.session_state.character_points,
                st.session_state.story_history,
                st.session_state.current_story,
                st.session_state.current_choices
            )

        load_name = st.text_input("Load Game (Enter Name):", key="load_name_input")
        if st.button("📁 Load Game") and load_name:
            loaded_data = load_game_from_supabase(load_name)
            if loaded_data:
                # Restore all game state
                st.session_state.player_name = loaded_data["player_name"]
                st.session_state.player_stats = loaded_data["player_stats"]
                st.session_state.player_class = loaded_data["player_class"]
                st.session_state.character_health = loaded_data["character_health"]
                st.session_state.character_points = loaded_data["character_points"]
                st.session_state.story_history = loaded_data.get("story_history", [])
                st.session_state.current_story = loaded_data.get("current_story", "")
                st.session_state.current_choices = loaded_data.get("current_choices", [])
                st.session_state.game_state = 'playing'
                st.rerun()

    # Generate initial story if not already generated
    if not st.session_state.current_story:
        with st.spinner("Generating your adventure..."):
            story, choices = generate_ai_story(
                player_name, 
                st.session_state.player_stats, 
                st.session_state.story_history
            )
            st.session_state.current_story = story
            st.session_state.current_choices = choices

    # Display current story
    st.write("**Current Story:**")
    st.write(st.session_state.current_story)

    # Display story history if exists
    if st.session_state.story_history:
        st.write("**Previous Events:**")
        for i, event in enumerate(st.session_state.story_history[-3:]):  # Show last 3 events
            st.write(f"*{i+1}. {event}*")

    # Initialize action analysis state
    if 'pending_action' not in st.session_state:
        st.session_state.pending_action = None
    if 'action_analysis' not in st.session_state:
        st.session_state.action_analysis = None

    # Show free-form action input
    st.write("**What do you want to do?**")
    st.write("Type your action (e.g., 'attack the goblin', 'sneak past quietly', 'try to negotiate')")

    player_action = st.text_input("Your action:", key="player_action_input", placeholder="Type what you want to do...")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Analyze Action", type="primary") and player_action:
            # Analyze the action with AI
            with st.spinner("Analyzing your action..."):
                from game_engine import analyze_player_action
                analysis = analyze_player_action(player_action, st.session_state.player_stats)
                st.session_state.pending_action = player_action
                st.session_state.action_analysis = analysis
                st.rerun()

    # Show action analysis if available
    if st.session_state.action_analysis and st.session_state.pending_action:
        st.write("---")
        st.write("**Action Analysis:**")
        st.write(f"**Your Action:** {st.session_state.pending_action}")

        analysis = st.session_state.action_analysis
        st.write(f"**Primary Stat Required:** {analysis['primary_stat']}")
        st.write(f"**Your {analysis['primary_stat']} Score:** {st.session_state.player_stats[analysis['primary_stat']]}")
        st.write(f"**Difficulty:** {analysis['difficulty']}")
        st.write(f"**Prediction:** {analysis['outcome_prediction']}")

        if analysis.get('secondary_stats'):
            st.write(f"**Secondary Stats:** {', '.join(analysis['secondary_stats'])}")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("✅ Confirm Action", type="primary"):
                # Process the confirmed action
                with st.spinner("Processing your action..."):
                    result = process_choice(player_name, st.session_state.pending_action, st.session_state.player_stats)

                    # Add to history
                    st.session_state.story_history.append(f"You chose: {st.session_state.pending_action}")
                    st.session_state.story_history.append(result)

                    # Generate new story continuation with context
                    new_story, new_choices = generate_ai_story(
                        player_name,
                        st.session_state.player_stats,
                        st.session_state.story_history
                    )
                    st.session_state.current_story = new_story
                    st.session_state.current_choices = new_choices

                    # Clear action state
                    st.session_state.pending_action = None
                    st.session_state.action_analysis = None

                    # Auto-save after each choice
                    save_game_to_supabase(
                        st.session_state.player_name,
                        st.session_state.player_stats,
                        st.session_state.player_class,
                        st.session_state.character_health,
                        st.session_state.character_points,
                        st.session_state.story_history,
                        st.session_state.current_story,
                        st.session_state.current_choices
                    )

                    # Force rerun to update display
                    st.rerun()

        with col2:
            if st.button("❌ Cancel"):
                st.session_state.pending_action = None
                st.session_state.action_analysis = None
                st.rerun()

        with col3:
            if st.button("🔄 Try Different Action"):
                st.session_state.pending_action = None
                st.session_state.action_analysis = None
                st.rerun()

        with col2:
            if st.button("New Adventure"):
                # Reset the game completely
                st.session_state.game_state = 'name_entry'
                st.session_state.story_history = []
                st.session_state.current_story = ""
                st.session_state.current_choices = []
                st.session_state.player_stats = {}
                st.session_state.player_class = ""
                st.session_state.character_health = 100
                st.session_state.character_points = 0
                st.session_state.player_name = ""
                st.rerun()

else:
    st.write("Please enter your name to begin your adventure!")

# Handle other game states
if st.session_state.game_state not in ['startup', 'load_game', 'name_entry', 'stat_display', 'class_selection', 'start_adventure', 'playing']:
    st.session_state.game_state = 'startup'
    st.rerun()
