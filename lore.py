def whisper_from_hollow_flame(player):
  if player.corruption > 5:
      print("\n A voice echoes in your mind: 'You are more me than you now.'")
      player.sanity -= 1
  elif player.reputation < 0:
      print("\n You hear someone in your head say: 'Even the damned find you unworthy.'")
