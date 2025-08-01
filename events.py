
import random

def battle(player, enemy):
    print(f"\nYou are battling: {enemy['name']}")
    print(enemy['description'])

    while player.health > 0 and enemy['health'] > 0:
        action = input("Do you [attack], [dodge], or [use item]? ").lower()

        if action == "attack":
            damage = player.strength + random.randint(1, 6)
            enemy['health'] -= damage
            print(f"You strike! Enemy takes {damage} damage.")
        elif action == "dodge":
            if random.randint(0, 10) < player.agility:
                print("You dodge the enemy's blow!")
                continue
            else:
                print("You try to dodge but fail.")
        elif action == "use item":
            print("Inventory system coming soon...")
        else:
            print("Hesitation is death.")

        # Enemy attacks back (only if not dodged successfully)
        if action != "dodge" or random.randint(0, 10) >= player.agility:
            enemy_damage = random.randint(5, 15)
            player.health -= enemy_damage
            print(f"The {enemy['name']} hits you for {enemy_damage} damage.")

    # Check battle outcome
    if player.health <= 0:
        print("You collapse. The jungle reclaims you.")
    else:
        print(f"You have defeated the {enemy['name']}!")
