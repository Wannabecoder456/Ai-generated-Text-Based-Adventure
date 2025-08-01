
from datetime import datetime

def daily_event(player):
    now = datetime.now()
    delta = now - player.last_login

    if delta.days >= 1:
        print("\nThe jungle shifts. A new day dawns")
        player.corruption += 1
        player.last_login = now
