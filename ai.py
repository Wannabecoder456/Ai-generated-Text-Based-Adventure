import os
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def init_supabase():
    """Initialize Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ Supabase secrets not configured!")
        print("Please set SUPABASE_URL and SUPABASE_ANON_KEY in the Secrets tab.")
        return None

    try:
        print("🔍 Supabase secrets found! Attempting connection...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Successfully connected to Supabase!")
        return supabase
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        print("Please check your SUPABASE_URL and SUPABASE_ANON_KEY values.")
        return None

# Initialize Supabase client
supabase_client = init_supabase()

def normalize_context(context):
    """Normalize context data structure"""
    if not context:
        context = {}

    normalized = {
        "player_name": context.get("player_name"),
        "stats": context.get("stats", {}),
        "inventory": context.get("inventory", []),
        "location": context.get("location"),
        "recent_choices": context.get("recent_choices", [])
    }
    return normalized

def load_player_data(player_id):
    """Load player data from Supabase"""
    if not supabase_client:
        print("⚠️ Supabase client not available")
        return None

    try:
        data = supabase_client.from_("players").select("*").eq("id", player_id).single().execute()
        if data and data.data:
            return data.data
        else:
            print(f"No player data found for ID: {player_id}")
            return None
    except Exception as e:
        print(f"Error loading player data: {e}")
        return None

def abstractify(ctx):
    """Convert player context to abstract placeholders for AI prompt"""
    return {
        "player_name": "[player_name]",
        "stats": {k: f"[{k.lower()}]" for k in ctx["stats"]},
        "inventory": "[inventory_list]",
        "location": "[current_location]",
        "recent_choices": "[recent_choices_list]"
    }

def generate_story_prompt(player_context):
    """Generate a story prompt for the AI based on player context"""
    abstract_context = abstractify(player_context)

    prompt = f"""
Congrats! You are a fantasy story AI!
Player context:
{abstract_context}

Generate:

1. A 3-5 sentence scene that follows and is relevant to the recent scenes and players context
2. A list of 2-3 choices for the player to make next which are relevant to the scene and have their own consequences and rewards
3. Make it so that the players stats are helpful (e.g if they have a lot of luck, they can find treasure with a lot of character_points)

Return the response in a structured format.
"""
    return prompt

# OpenAI configuration
def init_openai():
    """Initialize OpenAI client if API key is available"""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    print(f"🔍 Checking for OPENAI_API_KEY...")
    print(f"Key exists: {openai_api_key is not None}")
    
    if openai_api_key:
        # Show partial key for verification (first 8 chars + ...)
        key_preview = openai_api_key[:8] + "..." if len(openai_api_key) > 8 else openai_api_key
        print(f"Key preview: {key_preview}")
        print(f"Key length: {len(openai_api_key)}")
        
        # Check if key starts with the correct format
        if openai_api_key.startswith("sk-"):
            print("✅ Key format looks correct (starts with 'sk-')")
        else:
            print("⚠️ Key format might be wrong (should start with 'sk-')")
    
    if not openai_api_key:
        print("❌ OpenAI API key not found!")
        print("Please set OPENAI_API_KEY in the Secrets tab to enable AI story generation.")
        return None
    
    try:
        print("🤖 OpenAI API key found! AI story generation available.")
        return openai_api_key
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI: {e}")
        return None

# Initialize OpenAI
openai_key = init_openai()

def get_ai_story(prompt, api_key):
    """Generate AI story using OpenAI API"""
    print(f"🔧 Attempting to use OpenAI API...")
    print(f"🔧 API key preview: {api_key[:15]}..." if api_key else "No API key")
    print(f"🔧 Key format check: {'✅ Correct format' if api_key and api_key.startswith('sk-') else '❌ Invalid format'}")
    
    # Import openai outside of try block to make it available for exception handling
    try:
        print("🔧 Attempting to import OpenAI library...")
        import openai
        print(f"✅ OpenAI library imported successfully (version: {openai.__version__})")
    except ImportError as e:
        print(f"❌ OpenAI library import error: {e}")
        print("Please install it using: pip install openai")
        return None
    
    try:
        print("🔧 Creating OpenAI client...")
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
        
        print("🔧 Making API call to gpt-4o-mini...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful fantasy story generator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.8,
        )
        print("✅ OpenAI API call successful!")
        result = response.choices[0].message.content.strip()
        print(f"✅ Received response: {len(result)} characters")
        return result
    except openai.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("Check if your OPENAI_API_KEY is correct and has sufficient credits")
        return None
    except openai.RateLimitError as e:
        print(f"❌ Rate Limit Error: {e}")
        print("You've exceeded your API rate limit")
        return None
    except openai.APIError as e:
        print(f"❌ OpenAI API Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return None

def generate_dynamic_encounter(player_stats, inventory, current_location="forest"):
    """Generate a dynamic encounter based on player context"""
    if not openai_key:
        # Fallback to random encounters if no AI
        return generate_random_encounter(player_stats, inventory)
    
    player_context = {
        "player_name": "[Player]",
        "stats": player_stats,
        "inventory": inventory,
        "location": current_location,
        "recent_choices": []
    }
    
    prompt = f"""
Generate a fantasy encounter for a player with these stats:
- Strength: {player_stats['Strength']}
- Luck: {player_stats['Luck']} 
- Agility: {player_stats['Agility']}
- Inventory: {inventory}
- Location: {current_location}

Create:
1. A brief 2-3 sentence encounter description
2. Exactly 3 choices with different outcomes based on player stats
3. Make choices favor different stats (strength, luck, agility)

Format as:
SCENE: [description]
CHOICE1: [choice] (Strength-based)
CHOICE2: [choice] (Luck-based) 
CHOICE3: [choice] (Agility-based)

and also, make it lore accurate from my book, after the players gets after it, go wild, and i mean it- • Prologue: A nurse, aware of an ancient prophecy, secretly swaps a newborn royal prince with a peasant boy born under mysterious circumstances, sending the true heir to the mines and setting the stage for unforeseen events.
• Chapter 1: Zachor, the switched noble child, grows up in the brutal Mine of Slokia, enduring horrific abuse, witnessing his family's destruction, and developing a hardened resolve against a world that punishes weakness.
• Chapter 2: During a devastating dragon attack on the mines, Zachor is flung into a mysterious, untouched jungle where he begins to navigate its strange, often peaceful, ecosystem while coming to terms with his isolated survival.
• Chapter 3 (Verdant Hollow): Forced deeper into the jungle by its shifting paths, Zachor encounters wild animals, embracing a "psychotic", brutal fighting style born from his past trauma to survive its dangers and arriving at a mysterious scroll.
• Chapter 4: The jungle relentlessly draws Zachor toward its heart, where he battles a tribe of cannibals, realizing he possesses a potent, wild side that allows him to conquer them, yet still struggles with his untamed magic.
• Chapter 5 (Hollow Flames): Zachor is transported to a bizarre dimension where his "psychotic side" reveals himself as Hollow Flame, the Prophecy Energy trapped within him, and begins a brutal training regimen of endless running and death-revival cycles.
• Chapter 6 (True Training): Under Hollow Flame's relentless instruction, Zachor endures countless deaths and revivals while fighting hordes of monsters, learning to strategize and exploit weaknesses, leading to him unleashing a devastating magical attack.
• Chapter 7 (The Creature): Zachor faces a new threat of merging monsters and a powerful abomination that adapts to his fighting style, forcing him to strategically self-destruct repeatedly to defeat it, which finally transforms Hollow Flame's dimension into a lush, peaceful landscape.
• Chapter 8 (Grass and Godhood): Hollow Flame reveals Zachor has accumulated 630 million monsters to fight, which manifest as a single colossal entity that vaporizes Zachor repeatedly until he learns to endure its poisonous breath and ultimately defeats it through a final strategic self-detonation.
• Chapter 9 (The Center Stirs): Returning to the real jungle, Zachor is now exceptionally powerful and encounters Adrian and Lily, two adventurers, protecting them from adapted creatures while learning the jungle itself reacts to his presence.
• Chapter 10 (Sister of Flame): Zachor, Adrian, and Lily arrive at the jungle's center, where Zachor is transported to a mindscape by Eleneth, Hollow Flame's powerful sister, who reveals his identity as the true noble heir and tries to recruit him, an offer he politely refuses.
• Chapter 11 (The Offer): Adrian and Lily reveal their noble status, welcome Zachor into their family, and offer to sponsor his enrollment in the prestigious Noble Academy of Kings, a chance for him to realize his dream and change his fate.

also give names for the stages/choices, as it gets saved in supabase and it really helps in saving the players data

make rolls in fight/combat, e.g if you fight a goblin then give options like, pucnh is fro strenght, kick is for agility, and dodge is for luck, and then give the rolls, e.g if you punch a goblin, then the roll is 1d20 + strength, and if you kick a goblin, then the roll is 1d20 + agility, and if the player dodges, then the roll is 1d20 + luck

make it so that the players stats are helpful (e.g if they have a lot of luck, they can find treasure with a lot of character_points)

Make sure to include the following:
- SCENE: [description]
- CHOICE1: [choice] (Strength-based)
- CHOICE2: [choice] (Luck-based)
- CHOICE3: [choice] (Agility-based)

also make a \n with in between choices and the scene, so that it is easy to read

and never say "You encounter something mysterious in the forest..." its annoying, make it so that it is unique and interesting, e.g "You stumble upon a hidden cave, the air inside is thick with dust and the smell of ancient magic, the walls are lined with glowing runes that seem to pulse with an otherworldly energy, the cave is filled with the sounds of distant whispers and the occasional rustle of unseen creatures, you can feel the weight of history pressing down on you as you take your first steps into the cave, the air grows colder and the runes seem to glow brighter, you can't shake the feeling that you are not alone in this place" like creative, also as said before use the \n to make it easy to read

Also make there be be lore and history in the encounters, e.g "You stumble upon a hidden cave, the air inside is thick with dust and the smell of ancient magic, the walls are lined with glowing runes that seem to pulse with an otherworldly energy" also there should be battles every few times, like goblins, orcs, undead knights or the hordes

If the player has a high luck stat, and he chooses to explore, make there be a chance for him getting a secret quest, like a chest or a map he needs to find, and if he has a high agility stat, make there be a chance for him to escape from a battle, and if he has a high strength stat, make there be a chance for him to win a battle, and if he has low strenght stats, make there be a chance for him to lose a battle, and if he has low agility stats, make there be a chance for him to get caught in a battle, and if he has low luck stats, make there be a chance for him to miss out on a secret quest, like a chest or a map he needs to find. 

also make it so that the encounters are unique, and not repetitive, e.g if the player has already fought a goblin, then make it so that the next encounter is not a goblin, but something else, like an orc or an undead knight or the hordes.

and last but not least, DONT MAKE ANYTHING REPETETIVE, MAKE IT SO THAT THE PLAYER CAN HAVE A UNIQUE EXPERIENCE EVERY TIME THEY PLAY THE GAME AND NO TUTORIALS OR PLAYTHROUGHS CAN HELP THEM, MAKE IT SO THAT THEY HAVE TO PLAY THE GAME TO GET THE FULL EXPERIENCE
"""
    
    ai_response = get_ai_story(prompt, openai_key)
    if ai_response:
        return parse_ai_encounter(ai_response)
    else:
        return generate_random_encounter(player_stats, inventory)

def parse_ai_encounter(ai_text):
    """Parse AI response into usable encounter data"""
    lines = ai_text.split('\n')
    scene = ""
    choices = []
    
    for line in lines:
        if line.startswith("SCENE:"):
            scene = line.replace("SCENE:", "").strip()
        elif line.startswith("CHOICE"):
            choice_text = line.split(":", 1)[1].strip() if ":" in line else line
            choices.append(choice_text)
    
    return {
        "scene": scene if scene else "You encounter something mysterious in the forest...",
        "choices": choices if len(choices) >= 2 else [
            "Fight with strength",
            "Try your luck", 
            "Use agility to escape"
        ]
    }

def generate_random_encounter(player_stats, inventory):
    """Fallback random encounter generator"""
    import random
    
    encounters = [
        {
            "scene": "A goblin jumps out from behind a tree, wielding a rusty dagger!",
            "choices": [
                "Attack with your weapon",
                "Try to negotiate", 
                "Dodge and counter-attack"
            ]
        },
        {
            "scene": "You find a mysterious glowing chest half-buried in the ground.",
            "choices": [
                "Force it open with strength",
                "Trust your luck and open it",
                "Carefully examine it first"
            ]
        },
        {
            "scene": "A wounded traveler sits by the path, asking for help.",
            "choices": [
                "Help them directly",
                "Offer them an item from your inventory",
                "Approach cautiously"
            ]
        }
    ]
    
    return random.choice(encounters)

def execute_choice_outcome(choice_index, player_stats, inventory):
    """Execute the outcome of a player's choice"""
    import random
    
    outcomes = {
        0: "strength",  # Choice 1 uses strength
        1: "luck",      # Choice 2 uses luck  
        2: "agility"    # Choice 3 uses agility
    }
    
    stat_used = outcomes.get(choice_index, "luck")
    stat_value = player_stats.get(stat_used.title(), 5)
    
    # Calculate success based on stat + randomness
    roll = random.randint(1, 10) + stat_value
    
    if roll >= 15:
        return "great_success"
    elif roll >= 10:
        return "success"
    else:
        return "failure"

def main():
    """Main function to run the AI brain functionality"""
    # Example usage
    player_stats = {"Strength": 7, "Luck": 5, "Agility": 8}
    inventory = ["sword", "potion"]
    
    encounter = generate_dynamic_encounter(player_stats, inventory)
    
    print("🎮 AI-Generated Encounter:")
    print(f"Scene: {encounter['scene']}")
    print("\nChoices:")
    for i, choice in enumerate(encounter['choices'], 1):
        print(f"{i}. {choice}")

if __name__ == "__main__":
    main()
