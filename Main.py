# Fix import syntax error and handle missing imports
import json

player_stats = {
    "health": 60,
    "corruption": 20,
    "reputation": 45,
    "sanity": 90
}

with open("stats.json", "w") as f:
    json.dump(player_stats, f)
import random
import os
# main.py
from player import Player
from story import jungle_intro
from battle import battle
from save_load import save_game, load_game
from ai_enemy_gen import generate_enemy
from Levelup_system import level_up, determine_roles
# Handle imports that may not exist
try:
    from events import daily_event
except ImportError:
    print("⚠️ events module not found. Using placeholder function.")
    def daily_event(player):
        print("No daily event today.")
        pass

try:
    from lore import whisper_from_hollow_flame
except ImportError:
    print("⚠️ lore module not found. Using placeholder function.")
    def whisper_from_hollow_flame(player):
        print("The hollow flame whispers are silent today.")
        pass

def main():
    player = load_game(Player)
    daily_event(player)
    whisper_from_hollow_flame(player)

    while player.is_alive():
        outcome = jungle_intro(player)
        if outcome == "combat":
            context = "A shadowy predator in Verdanth Hollow, mutated by a dead god."
            enemy_text = generate_enemy(context)
            print("\nGenerated Enemy:\n" + (enemy_text if enemy_text else "No enemy generated."))

            # Parsing could be improved, for now we'll fake it
            enemy = {
                "name": "Dyrath Wraith",
                "description": "A serpent of whispers and bone.",
                "health": 400
            }

            battle(player, enemy)
            # Level up the player after a successful battle.
            if player.is_alive():
                player_dict = level_up(player.to_dict())
                player.from_dict(player_dict)
                print(f"Level: {player.level}")
                print(f"Health: {player.health}/{player.max_health}")
                print(f"Stat Points: {player.stat_points}")
                print(f"Max Stat Limit: {player.max_stat}")
                print(f"Horde Mode: {player.hordes_unlocked}")
                print(f"Unlocked Roles: {player.available_roles}")
        else:
            print("You continue surviving the jungle...")

        save_game(player)

if __name__ == "__main__":
    main()

from supabase import create_client, Client
try:
    import AI as brain
    AI_AVAILABLE = True
    print("✅ AI module loaded successfully!")
except ImportError:
    print("⚠️ AI module not found. Using traditional encounters.")
    AI_AVAILABLE = False
    brain = None

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

def save_game_to_supabase(supabase, player_name, player_stats, inventory, character_health, character_points, current_stage):
    """Save game data to Supabase"""
    if not supabase:
        print("Supabase not connected, using local save instead")
        save_game_local(player_name, player_stats, inventory, character_health, character_points, current_stage)
        return

    try:
        save_data = {
            "player_name": player_name,
            "player_stats": player_stats,
            "inventory": inventory,
            "character_health": character_health,
            "character_points": character_points,
            "current_stage": current_stage
        }

        # Insert or update the save data
        result = supabase.table('game_saves').upsert(save_data, on_conflict='player_name').execute()
        print("Game saved to Supabase successfully!")

    except Exception as e:
        print(f"Failed to save to Supabase: {e}")
        print("Falling back to local save...")
        save_game_local(player_name, player_stats, inventory, character_health, character_points, current_stage)

def load_game_from_supabase(supabase, player_name):
    """Load game data from Supabase"""
    if not supabase:
        print("Supabase not connected, using local load instead")
        return load_game_local()

    try:
        result = supabase.table('game_saves').select('*').eq('player_name', player_name).execute()

        if result.data:
            save_data = result.data[0]
            print("Game loaded from Supabase successfully!")
            return (
                save_data["player_name"],
                save_data["player_stats"],
                save_data["inventory"],
                save_data["character_health"],
                save_data["character_points"],
                save_data.get("current_stage", "")
            )
        else:
            print("No saved game found in Supabase.")
            return None

    except Exception as e:
        print(f"Failed to load from Supabase: {e}")
        print("Falling back to local load...")
        return load_game_local()

def save_game_local(player_name, player_stats, inventory, character_health, character_points, current_stage):
    save_data = {
        "player_name": player_name,
        "player_stats": player_stats,
        "inventory": inventory,
        "character_health": character_health,
        "character_points": character_points,
        "current_stage": current_stage
    }
    with open("save_game.json", "w") as save_file:
        json.dump(save_data, save_file)
        print("Game saved locally successfully!")

def load_game_local():
    try:
        with open("save_game.json", "r") as file:
            save_data = json.load(file)
        print("Game loaded from local file successfully!")
        return (
            save_data["player_name"],
            save_data["player_stats"],
            save_data["inventory"],
            save_data["character_health"],
            save_data["character_points"],
            save_data.get("current_stage", "")
        )
    except FileNotFoundError:
        print("No saved game found.")
        return None

# Initialize global variables
go_to_hut_next = False
player_name = ""
player_stats = {}
inventory = []
character_health = 100
character_points = 0
current_stage = ""

def auto_save(reason=None):
    save_game_to_supabase(supabase_client, player_name, player_stats, inventory, character_health, character_points, current_stage)
    if reason:
        print(f"Autosaved: {reason}")

def clean_inventory():
    """Remove duplicate items from inventory, keeping only one of each category"""
    global inventory

    # Defining em inventories like my life depends on it
    weapons = ["sword", "better sword", "excalibur", "enchanted excalibur"]
    armor = ["Dragon armour", "leather armor", "chain mail", "plate armor"]
    hats = ["cool hat", "wizard's hat", "pirate hat", "crown"]
    consumables = ["potion", "health potion", "mana potion", "elixir"]
    treasures = ["Treasure", "Fake, trap treasure chest", "gold coins", "jewels", "ancient artifact"]
    maps = ["map", "treasure map", "dungeon map", "world map"]
    tools = ["lockpick", "rope", "torch", "compass"]
    books = ["spellbook", "journal", "ancient tome", "scroll"]

    cleaned_inventory = []
    categories_found = {"weapons": False, "armor": False, "hats": False, "consumables": False, 
                       "treasures": False, "maps": False, "tools": False, "books": False}

    for item in inventory:
        if item in weapons and not categories_found["weapons"]:
            cleaned_inventory.append(item)
            categories_found["weapons"] = True
        elif item in armor and not categories_found["armor"]:
            cleaned_inventory.append(item)
            categories_found["armor"] = True
        elif item in hats and not categories_found["hats"]:
            cleaned_inventory.append(item)
            categories_found["hats"] = True
        elif item in consumables and not categories_found["consumables"]:
            cleaned_inventory.append(item)
            categories_found["consumables"] = True
        elif item in treasures and not categories_found["treasures"]:
            cleaned_inventory.append(item)
            categories_found["treasures"] = True
        elif item in maps and not categories_found["maps"]:
            cleaned_inventory.append(item)
            categories_found["maps"] = True
        elif item in tools and not categories_found["tools"]:
            cleaned_inventory.append(item)
            categories_found["tools"] = True
        elif item in books and not categories_found["books"]:
            cleaned_inventory.append(item)
            categories_found["books"] = True

    inventory = cleaned_inventory

def add_unique_item(item):
    """Add an item to inventory, ensuring only one of each type exists"""
    global inventory

    # Define item categories - expanded to cover all game items
    weapons = ["sword", "better sword", "excalibur", "enchanted excalibur"]
    armor = ["Dragon armour", "leather armor", "chain mail", "plate armor"]
    hats = ["cool hat", "wizard's hat", "pirate hat", "crown"]
    consumables = ["potion", "health potion", "mana potion", "elixir"]
    treasures = ["Treasure", "Fake, trap treasure chest", "gold coins", "jewels", "ancient artifact"]
    maps = ["map", "treasure map", "dungeon map", "world map"]
    tools = ["lockpick", "rope", "torch", "compass"]
    books = ["spellbook", "journal", "ancient tome", "scroll"]

    # Removing existing stuff because it is unneccesary and it is just a waste of space
    if item in weapons:
        inventory = [i for i in inventory if i not in weapons]
    elif item in armor:
        inventory = [i for i in inventory if i not in armor]
    elif item in hats:
        inventory = [i for i in inventory if i not in hats]
    elif item in consumables:
        inventory = [i for i in inventory if i not in consumables]
    elif item in treasures:
        inventory = [i for i in inventory if i not in treasures]
    elif item in maps:
        inventory = [i for i in inventory if i not in maps]
    elif item in tools:
        inventory = [i for i in inventory if i not in tools]
    elif item in books:
        inventory = [i for i in inventory if i not in books]

    # Add the new item
    inventory.append(item)

def random_events_based_on_luck():
    global character_points
    global character_health
    luck = player_stats["Luck"]

    if luck >= 9:
        event = random.choices(["treasure", "trap", "nothing"], weights=[5, 1, 4])[0]
    elif luck >= 5:
        event = random.choices(["treasure", "trap", "nothing"], weights=[3, 3, 4])[0]
    else:
        event = random.choices(["treasure", "trap", "nothing"], weights=[1, 5, 4])[0]

    print(f"\nRandom Event Triggered: {event}")

    if event == "treasure":
        print("You find a mysterious glowing chest... It contains 10 points and a cool hat!")
        add_unique_item("cool hat")
        character_points += 10
        auto_save("Treasure event")

    elif event == "trap":
        print("You stepped on a trap! You lose 10 health.")
        character_health -= 10
        auto_save("Trap event")
        if character_health <= 0:
            print("You died from the trap. Game Over!")
            exit()

    else:
        print("Nothing happens. The silence makes it more scarier.")

def human_encounter():
    global character_health, go_to_hut_next, current_stage
    if character_health > 0:
        print("\nYou see a human. What do you do?")
        print("1. Talk")
        print("2. Attack")
        human = input("Enter your choice (1 or 2): ")

        if human == "1":
            print("\nThe human gave you a map to treasure!")
            add_unique_item("map")
            print("\nYour inventory:", inventory)
            auto_save("Inventory updated")
            current_stage = "human_talk"
            auto_save("Change happened")
        elif human == "2":
            fight_roll1 = random.randint(1,10) + player_stats["Strength"] + player_stats["Luck"] + player_stats["Agility"]
            if fight_roll1 >= 20:
                print("You killed the human and took the map")
                add_unique_item("map")
                print("\nYour inventory:", inventory)
                auto_save("Inventory updated")

                character_health = 50
                print("\nYour health is now", character_health)
                auto_save("Change happened")
                current_stage = "human_fight"
                go_to_hut_next = True
            elif fight_roll1 < 20:
                auto_save("To keep the game rage-quit proof")
                current_stage = "human_fight"
                print("You fought and lost! You died! Game Over!")
                character_health = 0
                return
        else:
            print("Invalid choice")

def dragon_encounter():
    global character_health, go_to_hut_next, current_stage
    if character_health > 0:
        print("\nYou see a dragon! What do you do?")
        print("1. Fight")
        print("2. Talk")
        dragon = input("Enter your choice (1 or 2): ")

        if dragon == "1":
            fight_roll2 = random.randint(1, 10) + player_stats["Strength"] + player_stats["Luck"] + player_stats["Agility"]
            if fight_roll2 >= 30:
                print("You somehow killed the dragon and took the sword, you also got dragon armour. You also decided to just destroy your other sword")
                add_unique_item("better sword")
                add_unique_item("Dragon armour")
                print("\nYour inventory:", inventory)
                current_stage = "dragon_fight"
                auto_save("Change happened")
                character_health = 150
                print("\nYour health is now", character_health)
                auto_save("Change happened")
                go_to_hut_next = True
            elif fight_roll2 <= 30:
                auto_save("To keep the game rage-quit proof")
                print("You fought valiantly but the dragon is too powerful. You died. Game Over!")
                character_health = 0
                current_stage = "game_over"
                auto_save("Player died - game over")
                return
        elif dragon == "2":
            print("The dragon gave you a better sword and you decided to leave your other sword.")
            add_unique_item("better sword")
            print("\nYour inventory:", inventory)
            current_stage = "dragon_talk"
            go_to_hut_next = True
            auto_save("Change happened")
        else:
            print("Invalid choice")

def hut_encounter():
    global character_health, go_to_hut_next, current_stage
    if go_to_hut_next and character_health > 0:
        print("\nYou go deeper in the forest and find a hut in the middle of the forest. What do you do?")
        print("1. Enter the hut")
        print("2. Destroy the hut")
        hut = input("Enter you choice (1 or 2): ")

        if hut == "1":
            print("There was a trap and you fall down but you barely survive. You find a potion do you drink it?.")
            character_health = 10
            print("Your health is now", character_health)
            add_unique_item("potion")
            print("\nYour inventory:", inventory)
            current_stage = "hut_enter"
            auto_save("Change happened")
            print("1. Yes")
            print("2. No")
            potion = input("Enter your choice (1 or 2): ")

            if potion == "1":
                print("You drank the potion and gained health")
                inventory.remove("potion")
                character_health = 100
                auto_save("Change happened")
                current_stage = "potion_drink"
                go_to_hut_next = False
                print("Your health is now", character_health)
                print("You found a ladder. Do you climb it?")
                print("1. Yes")
                print("2. No")
                ladder = input("Enter your choice (1 or 2): ")
                if ladder == "1":
                    auto_save("To keep the game rage-quit proof")
                    print("You climbed the ladder but a monster chopped off your head. Game Over!")
                    character_health = 0
                    return
                elif ladder == "2":
                    current_stage = "ladder_no_climb"
                    auto_save("Change happened")
                    print("You didnt climb the ladder and found a the stone where the legendary excalibur was. Do you pull it?")
                    print("1. Yes")
                    print("2. No")
                    excalibur = input("Enter your choice (1 or 2): ")
                    if excalibur == "1":
                        print("You pulled the sword and it was the legendary Excalibur, and let go of your 'better sword'. Also, a mysterious door opened in front of you. Do you go in it?")
                        add_unique_item("excalibur")

                        current_stage = "excalibur_pull"
                        print("\nYour inventory:", inventory)
                        auto_save("Change happened")
                        print("1. Yes")
                        print("2. No")
                        print("Also here is you inventory:")
                        print("\nYour inventory:", inventory)
                        door = input("Enter your choice (1 or 2): ")
                        if door == "1":
                            print("You went in the door and found the treasure")
                            add_unique_item("Fake, trap treasure chest")
                            print("\nThen the treasure chest opens up by itself and it surrounds you in a mist, making go to another dimension, where everything seems like hell, but you are alive")
                            print("\nYour inventory:", inventory)

                            auto_save("Change happened")
                            print("\nAs you wake up from that dimension, you find 1 monster, a very powerful one. Do you fight it?")
                            print("1. Yes")
                            print("2. No")
                            monster = input("Enter your choice (1 or 2): ")
                            if monster == "1":
                                print("You try to fight the monster...")
                                outcome = random.randint(20, 30) + player_stats["Strength"] + player_stats["Luck"] + player_stats["Agility"]
                                if outcome >= 50:
                                    print("You won!? YOUR HIM, AND NOW YOU GOT AN ENCHANTMENT ON YOUR EXCALIBUR! BRAVO!")
                                    add_unique_item("enchanted excalibur")
                                    auto_save("Change happened")
                                    print("\nYour inventory:", inventory)
                                elif outcome <= 50:
                                    auto_save("To keep the game rage-quit proof")
                                    print("The monster did some horrendous things to you and you killed yourself lol, imagine, COULD NOT BE ME")
                                    character_health = 0
                                    return
                            elif monster == "2":
                                auto_save("To keep the game rage-quit proof")
                                print("You ran away but the monster caught you. Game Over!")
                                character_health = 0
                                return
                        elif door == "2":
                            auto_save("To keep the game rage-quit proof")
                            print("You did not go in the door stayed in the cave for ever, dying of starvation, while your parents cried their eys out and your friends looked for you until you died.")
                            character_health = 0
                            return
                    elif excalibur == "2":
                        auto_save("To keep the game rage-quit proof")
                        print("You did not pull the sword and the stone collapsed on you. Game Over!")
                        character_health = 0
                        return
            elif potion == "2":
                auto_save("To keep the game rage-quit proof")
                print("You did not drink the potion and tripped on your imaginary shoelace.")
                character_health = 0
                return
        elif hut == "2":
            auto_save("To keep the game rage-quit proof")
            print("The hut literally fights back and swallows you, killing you")
            character_health = 0
            return

# Test Supabase connection at startup
print("🔍 Checking Supabase configuration...")
supabase_client = init_supabase()
if supabase_client:
    print("✅ Cloud save/load will be available!")
else:
    print("⚠️ Using local save files only.")
print("-" * 50)

def text_based_adventure_game():
    global character_health, go_to_hut_next

    print("Text Based Adventure Game")
    print("------------------------")
    print("Welcome", player_name, "to the Text-Based Adventure Game!")

    # Skip stat display and reroll for the developer
    if player_name.lower() == "developer":
        print("Proceeding with godlike powers...")
        return

    print("Your stats are:")
    print("Strength:", player_stats["Strength"])
    print("Luck:", player_stats["Luck"])
    print("Agility:", player_stats["Agility"])

    if player_stats["Strength"] == 10:
        print("Ah yes, an honor to meet you, the god of strength!")
    elif player_stats["Luck"] == 10:
        print("Dang you lucky, probably can find a chest with diamonds")
    elif player_stats["Agility"] == 10:
        print("We got flash before GTA 6")
    elif player_stats["Strength"] == 1:
        print("You are weak, be careful")
    elif player_stats["Luck"] < 5:
        print("You would probably die in a 50/50 chance")
    elif player_stats["Agility"] < 5:
        print("You are slow, so just dont try to run")

    reroll = input("Do you want to reroll your stats? (yes or no): ").lower()
    if reroll == "yes":
        player_stats["Strength"] = random.randint(1, 10)
        player_stats["Luck"] = random.randint(1, 10)
        player_stats["Agility"] = random.randint(1, 10)

        print("Your new stats are:")
        print("Strength:", player_stats["Strength"])
        print("Luck:", player_stats["Luck"])
        print("Agility:", player_stats["Agility"])

        if player_stats["Strength"] == 10:
            print("Ah yes, an honor to meet you, the god of strength!")
        elif player_stats["Luck"] == 10:
            print("Dang you lucky, probably can find a chest with diamonds")
        elif player_stats["Agility"] == 10:
            print("We got flash before GTA 6")
        elif player_stats["Strength"] == 1:
            print("You are weak, be careful")
        elif player_stats["Luck"] < 5:
            print("You would probably die in a 50/50 chance")
        elif player_stats["Agility"] < 5:
            print("You are slow, so just dont try to run")
        input("Press Enter to continue...")

    elif reroll == "no":
        print("Your stats are:")
        print("Strength:", player_stats["Strength"])
        print("Luck:", player_stats["Luck"])
        print("Agility:", player_stats["Agility"])

def dynamic_forest_path():
    """New dynamic forest path using AI-generated encounters"""
    global character_health, go_to_hut_next, current_stage

    print("\nHello young adventurer, do you accept to take on one of the most fearsome adventures of your life?")
    print("1. Yes")
    print("2. No")
    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        encounter_count = 0
        while character_health > 0 and encounter_count < 10:  # Limit encounters to prevent infinite loop
            if AI_AVAILABLE and brain and brain.openai_key:
                print("🤖 Using AI-generated encounter...")
                encounter = brain.generate_dynamic_encounter(player_stats, inventory, "dark forest")
                print(f"\n{encounter['scene']}")

                for i, choice_text in enumerate(encounter['choices'], 1):
                    print(f"{i}. {choice_text}")

                try:
                    player_choice = int(input("Enter your choice: ")) - 1
                    outcome = brain.execute_choice_outcome(player_choice, player_stats, inventory)
                    handle_encounter_outcome(outcome, player_choice)
                    encounter_count += 1

                    # Check if player wants to continue
                    if character_health > 0:
                        continue_choice = input("\nContinue deeper into the forest? (yes/no): ").lower()
                        if continue_choice != "yes":
                            print("You decide to rest and end your adventure here. Well done!")
                            break
                except (ValueError, IndexError):
                    print("Invalid choice, defaulting to option 1")
                    outcome = brain.execute_choice_outcome(0, player_stats, inventory)
                    handle_encounter_outcome(outcome, 0)
                    encounter_count += 1
            else:
                # Fallback to original system
                forest_path_original()
                break

        if encounter_count >= 10:
            print("\nYou've had many adventures! You decide to head home with your treasures.")

    elif choice == "2":
        print("You walk away from the adventure. Maybe next time!")
    else:
        print("Invalid choice")

def handle_encounter_outcome(outcome, choice_index):
    """Handle the results of an encounter based on AI outcome"""
    global character_health, character_points

    if outcome == "great_success":
        print("🎉 Outstanding success! You handled that perfectly!")
        character_health += 10
        character_points += 20
        reward = random.choice(["sword", "potion", "map", "cool hat"])
        add_unique_item(reward)
        print(f"You gained health, points, and found a {reward}!")

    elif outcome == "success":
        print("✅ Success! You managed the situation well.")
        character_points += 10
        if random.random() < 0.5:  # 50% chance of item
            reward = random.choice(["potion", "map", "rope"])
            add_unique_item(reward)
            print(f"You found a {reward}!")

    else:  # failure
        print("❌ That didn't go as planned...")
        damage = random.randint(10, 20)
        character_health -= damage
        print(f"You lost {damage} health. Current health: {character_health}")

        if character_health <= 0:
            print("You died! Game Over!")
            return

def forest_path():
    """Updated forest path that uses dynamic encounters"""
    if AI_AVAILABLE and brain and brain.openai_key:
        print("🤖 AI mode activated - using dynamic encounters!")
        dynamic_forest_path()
    else:
        if AI_AVAILABLE and brain:
            if not brain.openai_key:
                print("⚠️ OpenAI key is None - check your OPENAI_API_KEY secret")
            else:
                print("⚠️ Unknown AI issue")
        print("📚 Using traditional story path")
        forest_path_original()

def forest_path_original():
    """Original hardcoded forest path as fallback"""
    global character_health, go_to_hut_next, current_stage

    while True:
        print("\nHello young adventurer, do you accept to take on one of the most fearsome adventures of your life?")
        print("1. Yes")
        print("2. No")
        choice = input("Enter your choice (1 or 2): ")

        if choice == "1":
            print("\nYou are in a dark forest. You see a path to the left and a path to the right.")
            print("1. Left")
            print("2. Right")
            if player_name.lower() == "developer":
                print("Ah yes mighty one, thank you for joining the journey, it will be easy for you, so shall you not worry")
            path = input("Enter your choice (1 or 2): ")

            if path == "1":
                random_events_based_on_luck()
                print("\nYou see a goblin. What do you do?")
                print("1. Fight")
                print("2. Run")
                goblin = input("Enter your choice (1 or 2): ")

                if goblin == "1":
                    print("You try to stab the goblin...")
                    current_stage = "goblin_fight"
                    outcome = random.randint(1, 10) + player_stats["Agility"] + 2
                    if outcome >= 12:
                        outcome = "stab"
                        if player_name.lower() == "developer":
                            print("The goblin begged on its knees for mercy and then ran away")
                            character_health = 10**6
                        auto_save("Change happened")
                    elif outcome < 10:
                        outcome = "dodge"
                        auto_save("To keep the game rage-quit proof")
                        if player_name.lower() == "developer":
                            print("The goblin hits you with his sword but it breaks and you kill him")

                    if outcome == "stab":
                        fight_roll = random.randint(1, 10) + player_stats["Strength"] + player_stats["Luck"]
                        if fight_roll >= 15:
                            print("You fought and won! You get a sword!")
                            add_unique_item("sword")
                            character_health = 75
                            print("\nYour health is now", character_health)
                            print("\nYour inventory:", inventory)
                            auto_save("Change happened")

                            # Call the encounter functions
                            human_encounter()
                            if character_health > 0:
                                dragon_encounter()
                            if character_health > 0:
                                hut_encounter()

                        elif fight_roll < 15:
                            auto_save("To keep the game rage-quit proof")
                            print("You fought and lost! You died! Game Over!")
                            character_health = 0
                            break
                    else:
                        auto_save("To keep the game rage-quit proof")
                        print("The goblin dodged your attack and killed you. Game Over!")
                        random_events_based_on_luck()
                        character_health = 0
                        break

                elif goblin == "2":
                    auto_save("To keep the game rage-quit proof")
                    print("You ran and tripped on a stone. The goblin caught you. Game Over!")
                    character_health = 0                
                    break
                else:
                    print("Invalid choice")

            elif path == "2":
                auto_save("To keep the game rage-quit proof")
                print("You chose the wrong path. A dragon burned you. Game Over!")
                character_health = 0
                break
            else:
                print("Invalid choice")

        elif choice == "2":
            print("You walk away from the adventure. Maybe next time!")
            break
        else:
            print("Invalid choice")

        if character_health == 0:
            print("\nYou are dead. Game Over!")
            break

        restart = input("Do you want to restart the game? (yes or no): ").lower()
        if restart != "yes":
            print("Thanks for playing! Goodbye!")
            break

def resume_from_stage(stage):
    """Resume the game from a specific stage"""
    global go_to_hut_next, current_stage, character_health

    if stage == "goblin_fight":
        print("Resuming after goblin fight...")
        go_to_hut_next = False
        human_encounter()
        if character_health > 0:
            dragon_encounter()
        if character_health > 0:
            hut_encounter()
    elif stage == "human_talk":
        print("Resuming after talking to human...")
        go_to_hut_next = True
        dragon_encounter()
        if character_health > 0:
            hut_encounter()
    elif stage == "dragon_fight" or stage == "dragon_talk":
        print("Resuming after dragon encounter...")
        go_to_hut_next = True
        hut_encounter()
    elif stage == "hut_enter":
        print("Resuming in the hut...")
        go_to_hut_next = True
        hut_encounter()
    elif stage == "potion_drink":
        print("Resuming after drinking potion...")
        print("You found a ladder. Do you climb it?")
        print("1. Yes")
        print("2. No")
        ladder = input("Enter your choice (1 or 2): ")
        if ladder == "1":
            auto_save("To keep the game rage-quit proof")
            print("You climbed the ladder but a monster chopped off your head. Game Over!")
            character_health = 0
            return
        elif ladder == "2":
            current_stage = "ladder_no_climb"
            auto_save("Change happened")
            print("You didnt climb the ladder and found a the stone where the legendary excalibur was. Do you pull it?")
            print("1. Yes")
            print("2. No")
            excalibur = input("Enter your choice (1 or 2): ")
            if excalibur == "1":
                print("You pulled the sword and it was the legendary Excalibur, and let go of your 'better sword'. Also, a mysterious door opened in front of you. Do you go in it?")
                add_unique_item("excalibur")
                current_stage = "excalibur_pull"
                print("\nYour inventory")
