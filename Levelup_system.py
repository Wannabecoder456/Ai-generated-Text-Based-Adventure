
def level_up(player):
    """
    Handles logic when a player levels up.
    - Increases level and stat points
    - Increases stat cap and triggers horde mode at level > 5
    - Fully heals the player
    - Unlocks available roles
    """

    player['level'] += 1
    player['stat_points'] += 1

    # Full health regeneration
    player['health'] = player['max_health']

    # Unlock stat cap increase and horde mode
    if player['level'] > 5:
        player['max_stat'] = 15
        player['hordes_unlocked'] = True

    # Check for new roles based on reputation and corruption
    player['available_roles'] = determine_roles(player)

    return player


def determine_roles(player):
    """
    Returns a list of roles available to the player based on reputation and corruption.
    """

    roles = []

    if player['reputation'] >= 7 and player['corruption'] >= 7:
        roles.append('Politician')
    if player['reputation'] >= 6 and player['corruption'] <= 2:
        roles.append('Priest')
    if player['corruption'] >= 9:
        roles.append('Dark Cultist')
    if player['reputation'] <= 2:
        roles.append('Outcast')

    return roles
