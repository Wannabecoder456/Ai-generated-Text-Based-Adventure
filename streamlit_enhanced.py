import streamlit as st


def create_enhanced_progress_bar(value, max_value, label, color_scheme="default"):
    """Create an enhanced progress bar with customizable color schemes using Streamlit native components"""
    percentage = min(100, max(0, (value/max_value) * 100))

    if color_scheme == "health":
        if percentage > 80:
            color = "🟢"
            status = "Excellent"
        elif percentage > 60:
            color = "🟡" 
            status = "Good"
        elif percentage > 30:
            color = "🟠"
            status = "Injured"
        else:
            color = "🔴"
            status = "Critical"
    elif color_scheme == "stat":
        if percentage > 80:
            color = "💙"
            status = "Exceptional"
        elif percentage > 60:
            color = "💚"
            status = "Strong"
        elif percentage > 40:
            color = "💛"
            status = "Average"
        else:
            color = "❤️"
            status = "Weak"
    else:
        color = "🔵"
        status = "Normal"
    
    col1, col2, col3 = st.columns([1, 6, 2])
    with col1:
        st.markdown(f"{color}")
    with col2:
        st.write(f"**{label}:** {value}/{max_value}")
        st.progress(percentage / 100)
    with col3:
        st.markdown(f"**{status}**")
    return percentage, status


def display_enhanced_stat_dashboard(player_stats, health, points, player_class):
    """Enhanced stat dashboard with better organization"""
    st.markdown("### 📊 Character Dashboard")

    # Character overview in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Class",
            value=player_class,
            help="Your character class"
        )
        
    with col2:
        total_stats = sum(player_stats.values())
        st.metric(
            label="Power Level",
            value=f"{total_stats}/30",
            delta=f"+{total_stats-15}" if total_stats > 15 else f"{total_stats-15}" if total_stats < 15 else "0",
            help="Total of all combat stats"
        )
        
    with col3:
        health_status = "Healthy" if health > 70 else "Injured" if health > 30 else "Critical"
        st.metric(
            label="Health Status", 
            value=health_status,
            delta=f"{health}/100 HP"
        )
        
    with col4:
        points_rank = "Novice" if points < 100 else "Adventurer" if points < 500 else "Hero"
        st.metric(
            label="Rank",
            value=points_rank, 
            delta=f"{points} pts"
        )

    st.markdown("---")
    
    # Enhanced stat bars
    st.markdown("### Combat Statistics")
    
    for stat_name, stat_value in player_stats.items():
        percentage, status = create_enhanced_progress_bar(stat_value, 10, stat_name, "stat")
        if stat_name == "Strength" and stat_value >= 8:
            st.success("Exceptional physical power - combat bonuses active!")
        elif stat_name == "Luck" and stat_value >= 8:
            st.success("Fortune favors you - treasure finding enhanced!")
        elif stat_name == "Agility" and stat_value >= 8:
            st.success("Lightning reflexes - escape chances increased!")
        elif stat_value <= 3:
            st.warning(f"Low {stat_name} - consider focusing on other approaches")
            
    # Additional info
    st.markdown("### Vital Statistics")
    create_enhanced_progress_bar(health, 100, "Health", "health")

    st.markdown("### Adventure Progress")  
    create_enhanced_progress_bar(min(points, 1000), 1000, "Points", "default")


def create_combat_dashboard(player_combatant, enemy_combatant, turn_number):
    """Enhanced combat interface with visual feedback"""
    st.markdown("### ⚔️ Combat Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**🛡️ {player_combatant.name}**")
        player_health_pct = player_combatant.health / player_combatant.max_health
        create_enhanced_progress_bar(
            player_combatant.health, 
            player_combatant.max_health, 
            "Health", 
            "health"
        )
        st.metric("Attack Power", player_combatant.attack_power)
        st.metric("Defense", player_combatant.defense)
        
    with col2:
        st.markdown(f"**👹 {enemy_combatant.name}**")
        enemy_health_pct = enemy_combatant.health / enemy_combatant.max_health
        create_enhanced_progress_bar(
            enemy_combatant.health, 
            enemy_combatant.max_health, 
            "Health", 
            "health"
        )
        st.metric("Attack Power", enemy_combatant.attack_power)
        st.metric("Defense", enemy_combatant.defense)
    
    st.markdown(f"**Turn:** {turn_number}")
    
    return player_health_pct, enemy_health_pct