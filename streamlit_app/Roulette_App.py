import streamlit as st
import random
import pandas as pd
import plotly.graph_objects as go

# === CORE FUNCTIONS ===

def spin_wheel():
    """Simulates a single roulette wheel spin.
    
    European roulette has numbers 0-36, where 0 is green.
    Returns a random number in this range.
    """
    return random.randint(0, 36)

def get_wheel_color(number):
    """Determines the color of a roulette number.
    
    In European roulette:
    - 0 is green (house advantage)
    - 18 numbers are red
    - 18 numbers are black
    
    The red numbers follow the actual roulette wheel layout.
    """
    if number == 0:
        return 'green'
    
    # These are the actual red numbers on a European roulette wheel
    red_numbers = {
        1, 3, 5, 7, 9, 12, 14, 16, 18,
        19, 21, 23, 25, 27, 30, 32, 34, 36
    }
    return 'red' if number in red_numbers else 'black'

# === PLAYER STRATEGIES ===

def random_color_strategy(player):
    """Strategy that randomly picks a color each round.
    
    This is a baseline strategy with no logic - pure gambling.
    Expected return: negative due to house edge (green).
    """
    color_choice = random.choice(['red', 'black', 'green'])
    return {
        'bet_type': 'color',
        'bet_value': color_choice,
        'amount': player['base_bet']
    }

def green_hunter_strategy(player):
    """Strategy that always bets on green (0).
    
    This is a high-risk, high-reward strategy.
    Green has 1/37 probability (~2.7%) but pays 35:1.
    Expected return is still negative but with high variance.
    """
    return {
        'bet_type': 'color',
        'bet_value': 'green',
        'amount': player['base_bet']
    }

def martingale_color_strategy(player):
    """Classic Martingale betting system.
    
    Core principle: double your bet after each loss, reset after a win.
    Goal: recover all previous losses plus one base bet profit.
    
    Major flaw: requires infinite bankroll and no table limits.
    A long losing streak will exhaust the player's balance quickly.
    """
    if player['last_result'] == 'loss':
        player['current_bet'] *= 2
    elif player['last_result'] in ('win', 'start'):
        player['current_bet'] = player['base_bet']
    
    return {
        'bet_type': 'color',
        'bet_value': player['target_color'],
        'amount': player['current_bet']
    }

# === SIMULATION ===

def play_round(players, round_num):
    """Executes one round of roulette for all active players.
    
    Process:
    1. Spin the wheel
    2. Each player places their bet according to their strategy
    3. Check if player has enough balance
    4. Resolve bets and update balances
    5. Track wins/losses for statistics
    
    Returns the number and color that came up.
    """
    number = spin_wheel()
    result_color = get_wheel_color(number)

    for player in players:
        # Skip players who went bankrupt (Martingale players stop playing)
        if not player.get('is_active', True):
            continue

        # Get the player's bet decision
        bet = player['strategy'](player)
        amount = bet['amount']
        bet_color = bet['bet_value']

        # Check if player can afford the bet
        if player['balance'] < amount:
            player['last_result'] = 'broke'
            # Record the round when player went broke
            if 'last_active_round' not in player:
                player['last_active_round'] = round_num
            # Martingale players stop playing when broke (others keep trying with $0 bets)
            if 'Marty' in player['name']:
                player['is_active'] = False
            continue

        # Place the bet (subtract from balance)
        player['balance'] -= amount

        # Check if the bet won
        if bet_color == result_color:
            # Green pays 35:1, red/black pay 1:1 (so 2x total with original bet)
            payout = 35 if result_color == 'green' else 2
            player['balance'] += amount * payout
            player['last_result'] = 'win'
            player['wins'] = player.get('wins', 0) + 1
        else:
            player['last_result'] = 'loss'

        player['rounds_played'] = player.get('rounds_played', 0) + 1
    
    return number, result_color

# === STREAMLIT UI ===

st.set_page_config(page_title="Roulette Simulator", page_icon="🎰", layout="wide")

st.title("🎰 European Roulette Simulator")
st.markdown("""
Compare different betting strategies in a realistic roulette simulation.
Each player starts with $1000 and bets $10 as starting bet.
""")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Simulation Settings")
    num_rounds = st.slider("Number of rounds", 10, 1000, 100, 10)
    update_freq = st.slider("Chart update frequency", 1, 20, 5, 1, 
                           help="Update chart every N rounds. Higher = faster, lower = smoother")
    
    st.markdown("---")
    st.markdown("### 📊 Players")
    st.markdown("""
    - **RandomBot** - Random color each round
    - **GreenHunter** - Always bets on green (0)
    - **MartyRed** - Martingale on red
    - **MartyBlack** - Martingale on black
    """)

run_button = st.button("🎲 Run Simulation", type="primary", use_container_width=True)

if run_button:
    # Set up players with different strategies
    players = [
        {
            'name': 'RandomBot',
            'strategy': random_color_strategy,
            'color': 'blue',
            'balance': 1000,
            'base_bet': 10,
            'last_result': 'start'
        },
        {
            'name': 'GreenHunter',
            'strategy': green_hunter_strategy,
            'color': 'green',
            'balance': 1000,
            'base_bet': 10,
            'last_result': 'start'
        },
        {
            'name': 'MartyRed',
            'strategy': martingale_color_strategy,
            'color': 'red',
            'balance': 1000,
            'base_bet': 10,
            'current_bet': 10,
            'last_result': 'start',
            'target_color': 'red',
            'is_active': True
        },
        {
            'name': 'MartyBlack',
            'strategy': martingale_color_strategy,
            'color': 'black',
            'balance': 1000,
            'base_bet': 10,
            'current_bet': 10,
            'last_result': 'start',
            'target_color': 'black',
            'is_active': True
        }
    ]

    # Track balance history for plotting
    balance_history = {player['name']: [player['balance']] for player in players}
    
    # Create placeholders for dynamic updates
    chart_placeholder = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Initialize Plotly figure
    fig = go.Figure()
    for player in players:
        fig.add_trace(go.Scatter(
            x=[0],
            y=[player['balance']],
            mode='lines',
            name=player['name'],
            line=dict(color=player['color'], width=2)
        ))
    
    fig.update_layout(
        title="Player Balances Over Time",
        xaxis_title="Round",
        yaxis_title="Balance ($)",
        hovermode='x unified',
        height=500,
        # Reference lines
        shapes=[
            # Bankruptcy line at $0
            dict(
                type='line',
                x0=0, x1=num_rounds,
                y0=0, y1=0,
                line=dict(color='red', width=2, dash='dash'),
            ),
            # Starting balance line at $1000
            dict(
                type='line',
                x0=0, x1=num_rounds,
                y0=1000, y1=1000,
                line=dict(color='gray', width=1, dash='dot'),
            )
        ]
    )

    # Run the simulation
    for round_num in range(1, num_rounds + 1):
        number, result_color = play_round(players, round_num)
        
        # Record current balances
        # For bankrupt players, carry forward their last balance
        for player in players:
            balance = player['balance'] if player.get('is_active', True) else balance_history[player['name']][-1]
            balance_history[player['name']].append(balance)

        # Update chart periodically (not every round for performance)
        if round_num % update_freq == 0 or round_num == num_rounds:
            for idx, player in enumerate(players):
                fig.data[idx].x = list(range(len(balance_history[player['name']])))
                fig.data[idx].y = balance_history[player['name']]
            
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            status_text.text(f"Round {round_num}: {number} ({result_color})")
        
        # Update progress bar
        progress_bar.progress(round_num / num_rounds)

    status_text.success("✓ Simulation complete!")
    progress_bar.empty()

    # Export data to CSV
    balance_df = pd.DataFrame(balance_history)
    balance_df.index.name = 'Round'
    
    csv = balance_df.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Download Balance History (CSV)",
        data=csv,
        file_name='roulette_simulation.csv',
        mime='text/csv',
        use_container_width=True
    )

    # Display final statistics
    st.markdown("---")
    st.subheader("📊 Final Statistics")

    cols = st.columns(4)
    for idx, player in enumerate(players):
        with cols[idx]:
            rounds_played = player.get('rounds_played', 0)
            wins = player.get('wins', 0)
            win_rate = (wins / rounds_played * 100) if rounds_played else 0
            profit = player['balance'] - 1000
            last_round = player.get('last_active_round', 'active until end')
            
            st.markdown(f"### 🎲 {player['name']}")
            
            if profit > 0:
                delta_text = f"📈 +${abs(profit):.2f}"
            elif profit < 0:
                delta_text = f"📉 -${abs(profit):.2f}"
            else:
                delta_text = f"➡️ $0.00"
            
            st.metric("Final Balance", 
                      f"${player['balance']:.2f}", 
                      delta=delta_text)
            
            st.write(f"**Rounds played:** {rounds_played}")
            st.write(f"**Wins:** {wins} ({win_rate:.1f}%)")
            
            if 'Marty' in player['name']:
                st.write(f"**Stopped at:** Round {last_round}")
            