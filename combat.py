import random
import time

enemy_types =[{"name": "Goblin", "min_hp": 30, "max_hp": 50, "min_damage": 5, "max_damage": 10, "description": "A small creature with sharp teeth and claws, usually come in packs and often loot already dead people"}
              [{"name": "Goblin Leader", "min_hp": 50, "max_hp": 80, "min_damage": 10, "max_damage": 20, "description": "The leader of the goblins, comes with his workers who do the bidding for him, is practically useless without them"}
             {"name": "Orc", "min_hp": 50, "max_hp": 70, "min_damage": 10, "max_damage": 15, "description": "A large more loyal goblin, usually come with a wooden spiked bat in battle, and follows their leader, the Orc Leader"}
             {"name": "Orc Leader", "min_hp": 70, "max_hp": 90, "min_damage": 15, "max_damage": 20, "description": "The leader of the orcs, usally ckmes with a huge sword and a shield, and is very loyal to his pack, but mioslty is the only one left standing after a battle"}
             {"name": "Undead knight", "min_hp": 100, "max_hp": 150, "min_damage": 20, "max_damage": 30, "description ": "A knight who died in battle, but was brought back to life by a dark magic, and now fights for the dark side, and is very strong and loyal to his master"}
               {"name": "Undead Mage", "min_hp": 100, "max_hp": 150, "min_damage": 20, "max_damage": 30, "description": "The remains of a mage who died in battle, but was brought back to life by a dark magic, and now fights for the dark side, and is very strong and loyal to his master"}
             {"name": "Flesh Mage", "min_hp": 150, "max_hp": 200, "min_damage": 30, "max_damage": 40, "description":"Said to be the remains of strong mages who died but didnt lose their hope and their magic turned them back alive, just not perfect, they have new arts of magic, but are very rare to see"}
             {"name": "Fire Wrath", "min_hp": 200, "max_hp": 300, "min_damage": 40, "max_damage": 50, "description": "The remains of a huge fire cursed by a witch to be alive forever, the fire embodied the first thing it saw, the witch, and now it is a living flame, and will burn anything it sees"}
             {"name": "Dragon", "min_hp": 300, "max_hp": 400, "min_damage": 50, "max_damage": 60, "description":"A large fire breathing beast, usually comes from the depths of the jungle, and is very rare to see, but when you do, you know you are in trouble"}] 

               enemy_groups = [
                   [{"type": "Orc"}],

                   [{"type": "Orc"}, {"type": "Orc"}, {"type": "Orc"}, {"type": "Orc Leader"}],

                   [{"type": "Goblin"}, {"type": "Goblin"}, {"type": "Goblin"}, {"type": "Goblin Leader"}],

                   [{"type": "Undead Knight"}, {"type": "Undead Knight"}, {"type": "Undead Mage"}, {"type": "Undead Mage"}]
               ]
               def generate_enemy_group():
                 group_template = random.choice(enemy_groups)
                 group = []

                 for member in group_template:
                     base = next((et for et in enemy_types if et["name"] == member["type"]), None)
                     if base:
                         enemy = {
                             "name": base["name"],
                             "hp": random.randint(base["min_hp"], base["max_hp"]),
                             "attack": random.randint(base["min_damage"], base["max_damage"]),
                             "description": base["description"]
                         }
                         group.append(enemy)

                 return group
  

  

def generate_enemy():
  template = random.choice(enemy_types)
  enemy = {
    "name": template["name"],
    "health": random.randint(template["min_hp"], template["max_hp"]),
    "damage": random.randint(template["min_damage"], template["max_damage"]),
    "description": template["description"]
  }
  return enemy

    def fight(player, enemies):
      print("\n⚔️  You are ambushed by:")
      for idx, enemy in enumerate(enemies):
          print(f"  {idx + 1}. {enemy['name']} - {enemy['hp']} HP")

      while player["hp"] > 0 and any(e["hp"] > 0 for e in enemies):
          print("\nWhat do you want to do?")
          for idx, enemy in enumerate(enemies):
              if enemy["hp"] > 0:
                  print(f"{idx + 1}: Attack {enemy['name']} ({enemy['hp']} HP)")

          choice = input("Enter enemy number to attack (or 'r' to run): ").strip()
          if choice.lower() == "r":
              if random.random() < 0.5:
                  print("You escaped!")
                  return
              else:
                  print("You failed to escape!")

          elif choice.isdigit() and 1 <= int(choice) <= len(enemies):
              target = enemies[int(choice) - 1]
              if target["hp"] <= 0:
                  print("That enemy is already defeated!")
              else:
                  damage = random.randint(player["attack"] - 3, player["attack"] + 3)
                  target["hp"] -= damage
                  print(f"You hit the {target['name']} for {damage} damage!")

          else:
              print("Invalid choice.")

          # Enemies attack back
          for enemy in enemies:
              if enemy["hp"] > 0:
                  damage = random.randint(enemy["attack"] - 2, enemy["attack"] + 2)
                  player["hp"] -= damage
                  print(f"The {enemy['name']} hits you for {damage} damage! You now have {player['hp']} HP.")

      if player["hp"] <= 0:
          print("You died.")
      else:
          print("You survived the pack!")
