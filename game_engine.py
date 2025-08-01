
import os
import openai
import re

# Get API key from environment
openai_api_key = os.environ.get('OPENAI_API_KEY')

def analyze_player_action(action, player_stats):
    """Analyze a player's typed action and determine stats required"""
    import random
    
    if not openai_api_key:
        # Fallback analysis without AI
        return analyze_action_fallback(action, player_stats)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        prompt = f"""Analyze this player action for a dark fantasy RPG: "{action}"

Player Stats:
- Strength: {player_stats['Strength']}
- Luck: {player_stats['Luck']}
- Agility: {player_stats['Agility']}

Determine:
1. Primary stat needed (Strength, Luck, or Agility)
2. Difficulty level (Easy, Medium, Hard, Very Hard)
3. Brief outcome prediction based on player's stat level
4. Any secondary stats that might help

Respond in this exact format:
PRIMARY_STAT: [stat name]
DIFFICULTY: [difficulty level]
PREDICTION: [2-3 sentence prediction]
SECONDARY: [optional secondary stats, comma separated or "None"]"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        analysis_text = response.choices[0].message.content
        return parse_action_analysis(analysis_text, player_stats)
        
    except Exception as e:
        print(f"Error analyzing action: {e}")
        return analyze_action_fallback(action, player_stats)

def parse_action_analysis(analysis_text, player_stats):
    """Parse AI analysis response into structured data"""
    try:
        lines = analysis_text.split('\n')
        
        primary_stat = "Luck"  # default
        difficulty = "Medium"
        prediction = "Unknown outcome"
        secondary_stats = []
        
        for line in lines:
            if line.startswith("PRIMARY_STAT:"):
                primary_stat = line.split(":", 1)[1].strip()
            elif line.startswith("DIFFICULTY:"):
                difficulty = line.split(":", 1)[1].strip()
            elif line.startswith("PREDICTION:"):
                prediction = line.split(":", 1)[1].strip()
            elif line.startswith("SECONDARY:"):
                secondary_text = line.split(":", 1)[1].strip()
                if secondary_text.lower() != "none":
                    secondary_stats = [s.strip() for s in secondary_text.split(",")]
        
        return {
            "primary_stat": primary_stat,
            "difficulty": difficulty,
            "outcome_prediction": prediction,
            "secondary_stats": secondary_stats
        }
    except Exception as e:
        print(f"Error parsing analysis: {e}")
        return analyze_action_fallback("", player_stats)

def analyze_action_fallback(action, player_stats):
    """Fallback action analysis without AI"""
    action_lower = action.lower()
    
    # Determine primary stat based on keywords
    if any(word in action_lower for word in ["fight", "attack", "punch", "strike", "force", "break", "smash", "lift", "push"]):
        primary_stat = "Strength"
    elif any(word in action_lower for word in ["dodge", "run", "quick", "fast", "escape", "sneak", "climb", "jump", "stealth"]):
        primary_stat = "Agility"
    elif any(word in action_lower for word in ["luck", "chance", "gamble", "risk", "try", "search", "find", "discover"]):
        primary_stat = "Luck"
    else:
        primary_stat = "Luck"  # default
    
    # Determine difficulty
    if len(action.split()) <= 2:
        difficulty = "Easy"
    elif len(action.split()) <= 4:
        difficulty = "Medium"
    else:
        difficulty = "Hard"
    
    stat_value = player_stats.get(primary_stat, 5)
    
    # Generate prediction
    if stat_value >= 8:
        prediction = f"With your high {primary_stat} ({stat_value}), you have an excellent chance of success!"
    elif stat_value >= 6:
        prediction = f"Your {primary_stat} ({stat_value}) gives you a good chance of success."
    elif stat_value >= 4:
        prediction = f"Your {primary_stat} ({stat_value}) makes this challenging but possible."
    else:
        prediction = f"With low {primary_stat} ({stat_value}), this action is quite risky."
    
    return {
        "primary_stat": primary_stat,
        "difficulty": difficulty,
        "outcome_prediction": prediction,
        "secondary_stats": []
    }

def process_choice(player_name, choice, player_stats=None):
    """Process player's choice and return result using OpenAI API with stat-based outcomes"""
    import random
    
    if not player_stats:
        player_stats = {"Strength": 5, "Luck": 5, "Agility": 5}
    
    # Determine which stat to use based on choice keywords
    stat_used = "Luck"  # default
    if any(word in choice.lower() for word in ["fight", "attack", "punch", "strike", "force"]):
        stat_used = "Strength"
    elif any(word in choice.lower() for word in ["dodge", "run", "quick", "fast", "escape", "sneak"]):
        stat_used = "Agility"
    elif any(word in choice.lower() for word in ["luck", "chance", "gamble", "risk", "try"]):
        stat_used = "Luck"
    
    # Roll dice (1d20 + stat)
    dice_roll = random.randint(1, 20)
    stat_bonus = player_stats.get(stat_used, 5)
    total_roll = dice_roll + stat_bonus
    
    # Determine success level
    if total_roll >= 25:
        success_level = "critical_success"
    elif total_roll >= 18:
        success_level = "great_success"
    elif total_roll >= 12:
        success_level = "success"
    elif total_roll >= 8:
        success_level = "partial_success"
    else:
        success_level = "failure"
    
    if not openai_api_key:
        # Fallback responses with roll results
        roll_text = f"\n🎲 Rolling {stat_used}: {dice_roll} + {stat_bonus} = {total_roll}"
        
        if success_level == "critical_success":
            return f"{player_name} {choice.lower()}s with incredible success! The outcome exceeds all expectations.{roll_text}"
        elif success_level == "great_success":
            return f"{player_name} {choice.lower()}s very successfully! Everything goes better than planned.{roll_text}"
        elif success_level == "success":
            return f"{player_name} {choice.lower()}s successfully and continues the adventure.{roll_text}"
        elif success_level == "partial_success":
            return f"{player_name} {choice.lower()}s with mixed results. There are both benefits and drawbacks.{roll_text}"
        else:
            return f"{player_name} {choice.lower()}s but things don't go as planned. The situation becomes more challenging.{roll_text}"
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        prompt = f"You are Zachor, a dark fantasy protagonist. You chose to '{choice}' using your {stat_used} (rolled {dice_roll} + {stat_bonus} = {total_roll}). This was a {success_level}. Continue the story in a dark fantasy tone with 2-3 sentences, incorporating the roll result and success level. Include the roll information at the end."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=200
        )
        
        result = response.choices[0].message.content
        roll_text = f"\n\n🎲 **{stat_used} Roll:** {dice_roll} + {stat_bonus} = {total_roll} ({success_level.replace('_', ' ').title()})"
        
        return result + roll_text
        
    except Exception as e:
        print(f"Error processing choice: {e}")
        roll_text = f"\n🎲 Rolling {stat_used}: {dice_roll} + {stat_bonus} = {total_roll}"
        return f"{player_name} {choice.lower()}s and continues the adventure...{roll_text}"

def display_stat_bars(player_stats, health, points):
    """Display visual stat bars in console format"""
    print("=" * 50)
    print("CHARACTER STATUS BARS")
    print("=" * 50)
    
    # Health bar
    health_percentage = min(100, max(0, health))
    health_blocks = int(health_percentage / 5)  # 20 blocks total
    health_bar = "█" * health_blocks + "░" * (20 - health_blocks)
    print(f"Health:    [{health_bar}] {health}/100")
    
    # Points bar (scale to 1000 max)
    points_percentage = min(100, max(0, (points / 1000) * 100))
    points_blocks = int(points_percentage / 5)
    points_bar = "█" * points_blocks + "░" * (20 - points_blocks)
    print(f"Points:    [{points_bar}] {points}/1000")
    
    print("-" * 50)
    print("COMBAT STATS")
    print("-" * 50)
    
    # Stat bars
    for stat_name, stat_value in player_stats.items():
        stat_percentage = min(100, max(0, (stat_value / 10) * 100))
        stat_blocks = int(stat_percentage / 5)
        stat_bar = "█" * stat_blocks + "░" * (20 - stat_blocks)
        print(f"{stat_name:<8}: [{stat_bar}] {stat_value}/10")
    
    # Total power
    total_stats = sum(player_stats.values())
    total_percentage = min(100, max(0, (total_stats / 30) * 100))
    total_blocks = int(total_percentage / 5)
    total_bar = "█" * total_blocks + "░" * (20 - total_blocks)
    print("-" * 50)
    print(f"Power:     [{total_bar}] {total_stats}/30")
    print("=" * 50)

def display_action_analysis_with_bars(action, player_stats, health, points):
    """Display action analysis with visual stat representation"""
    print("=" * 60)
    print("ACTION ANALYSIS DASHBOARD")
    print("=" * 60)
    
    # Analyze the action
    analysis = analyze_player_action(action, player_stats)
    
    print(f"Action: {action}")
    print("-" * 60)
    print(f"Primary Stat Required: {analysis['primary_stat']}")
    print(f"Difficulty Level: {analysis['difficulty']}")
    print(f"Prediction: {analysis['outcome_prediction']}")
    
    if analysis.get('secondary_stats'):
        print(f"Secondary Stats: {', '.join(analysis['secondary_stats'])}")
    
    print("-" * 60)
    print("RELEVANT STAT ANALYSIS")
    print("-" * 60)
    
    # Highlight the primary stat
    primary_stat = analysis['primary_stat']
    primary_value = player_stats.get(primary_stat, 5)
    
    # Create enhanced bar for primary stat
    stat_percentage = min(100, max(0, (primary_value / 10) * 100))
    stat_blocks = int(stat_percentage / 5)
    stat_bar = "█" * stat_blocks + "░" * (20 - stat_blocks)
    
    # Color indicators (text-based)
    if primary_value >= 8:
        status = "EXCELLENT"
        indicator = "🟢"
    elif primary_value >= 6:
        status = "GOOD"
        indicator = "🟡"
    elif primary_value >= 4:
        status = "FAIR"
        indicator = "🟠"
    else:
        status = "POOR"
        indicator = "🔴"
    
    print(f"{primary_stat} (PRIMARY): [{stat_bar}] {primary_value}/10 {indicator} {status}")
    
    # Show other stats for context
    for stat_name, stat_value in player_stats.items():
        if stat_name != primary_stat:
            other_percentage = min(100, max(0, (stat_value / 10) * 100))
            other_blocks = int(other_percentage / 5)
            other_bar = "█" * other_blocks + "░" * (20 - other_blocks)
            print(f"{stat_name:<8}:     [{other_bar}] {stat_value}/10")
    
    print("-" * 60)
    
    # Success probability estimate
    difficulty_modifiers = {
        "Easy": 0.8,
        "Medium": 0.6,
        "Hard": 0.4,
        "Very Hard": 0.2
    }
    
    base_chance = (primary_value / 10) * difficulty_modifiers.get(analysis['difficulty'], 0.5)
    success_percentage = min(95, max(5, base_chance * 100))
    
    success_blocks = int(success_percentage / 5)
    success_bar = "█" * success_blocks + "░" * (20 - success_blocks)
    
    print(f"Success Est: [{success_bar}] {success_percentage:.1f}%")
    print("=" * 60)

def generate_ai_story(player_name, player_stats=None, story_history=None, current_context=""):
    """Generate AI story using OpenAI API with context"""
    if not openai_api_key:
        return "No AI story available - API key not configured", ["Continue on your own", "Explore the area", "Rest"]
    
    if not player_stats:
        player_stats = {"Strength": 5, "Luck": 5, "Agility": 5}
    
    if not story_history:
        story_history = []
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Build context from story history
        context_text = ""
        if story_history:
            recent_events = story_history[-6:]  # Last 6 events for context
            context_text = f"\n\nRecent events in the story:\n" + "\n".join(recent_events)
        
        # Build stats context
        stats_text = f"\nPlayer Stats - Strength: {player_stats['Strength']}, Luck: {player_stats['Luck']}, Agility: {player_stats['Agility']}"
        
        # Create dynamic prompt based on context
        prompt = f"""You are an AI storyteller for Zachor, a dark fantasy text adventure. The protagonist is {player_name}.

LORE CONTEXT: Zachor was switched at birth - a noble child raised in the brutal Mine of Slokia. After surviving a dragon attack, he found himself in a mysterious jungle with shifting paths and magical creatures. He has an inner power called "Hollow Flame" and his true noble heritage awaits discovery.

{stats_text}
{context_text}

Generate a NEW story continuation that:
1. Follows logically from recent events
2. Introduces fresh challenges/encounters (never repeat scenarios)
3. Creates 3 unique choices that utilize different stats
4. Uses vivid, dark fantasy descriptions
5. Advances the overarching narrative toward the jungle's heart

Make each choice distinctly different:
- One should favor Strength (combat/force)
- One should favor Luck (chance/discovery) 
- One should favor Agility (speed/stealth)

Format: Story description first, then exactly:
1. [Strength-based choice]
2. [Luck-based choice] 
3. [Agility-based choice]

Make this story segment completely unique - no repeated encounters or generic scenarios."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative dark fantasy storyteller who creates unique, non-repetitive adventures with meaningful stat-based choices."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=400
        )

        story_text = response.choices[0].message.content

        # Parse the story text to extract main story and choices
        if story_text and "1." in story_text and "2." in story_text and "3." in story_text:
            parts = story_text.split("\n")
            main_story = "\n".join(part for part in parts if not part.strip().startswith(("1.", "2.", "3.")))
            choices = [line.split(".", 1)[1].strip() for line in parts if line.strip().startswith(("1.", "2.", "3."))]
            return main_story.strip(), choices[:3]  # Ensure only 3 choices
        else:
            # If parsing fails, return the full text with stat-based default choices
            return story_text or "Adventure awaits...", [
                "Use brute force to overcome the obstacle",
                "Trust in fate and take a risky chance", 
                "Use speed and cunning to find another way"
            ]
    
    except Exception as e:
        print(f"Error generating AI story: {e}")
        return "No AI story available - API error occurred", [
            "Press forward with determination",
            "Search for hidden opportunities", 
            "Move quickly and quietly"
        ]
