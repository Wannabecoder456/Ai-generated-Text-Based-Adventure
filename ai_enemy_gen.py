
def jungle_intro(player):
    print("\n You awaken in the misty, blood slick jungle of a name you dont know, but be warned, no one who came here has gotten out alive")
    print("A shadow moves near the vines you woke up in")

    choices = {
        "1": "Sneak forward silently",
        "2": "Draw a nearby stick you found laying on the ground and prepare for attack",
        "3": "Run anywhere just not towards the shadow"
    }

    for key, value in choices.items():
        print(f"{key}: {value}")
    choice = input("Your choice: ")

    if choice == "1":
        if player.agility > 6:
            print("You move like wind. The shadow ignores you.")
        else:
            print("Your foot snaps a twig. A shriek erupts!")
    elif choice == "2":
        print("You hold your breath and ready yourself... combat begins!")
        return "combat"
    elif choice == "3":
        if player.luck > 7:
            print("Somehow, you find a forgotten exit path. You live — for now.")
        else:
            print("You trip, and the shadow lunges. Prepare to fight.")
            return "combat"
    else:
        print("You hesitate. The jungle does not forgive.")
        return "combat"

    return "continue"
