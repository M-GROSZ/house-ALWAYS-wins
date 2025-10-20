import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

# === MAIN ===

def main():
    # Get simulation parameters from user
    try:
        num_rounds = int(input("Enter number of rounds to simulate: "))
    except ValueError:
        print("Invalid input. Defaulting to 100 rounds.")
        num_rounds = 100
    
    try:
        update_freq = int(input("Update chart every N rounds (1-20, default 5): ") or "5")
        update_freq = max(1, min(20, update_freq))
    except ValueError:
        update_freq = 5
    
    try:
        print_freq_input = input("Print round results every N rounds (1=all, 10=default, 0=none): ") or "10"
        print_freq = int(print_freq_input)
        print_freq = max(0, print_freq)
    except ValueError:
        print_freq = 10

    # Set up players with different strategies
    # Each starts with $1000 and bets $10 per round
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
    # Using dict instead of DataFrame for better performance during simulation
    balance_history = {player['name']: [player['balance']] for player in players}

    # Set up real-time plotting
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create line objects for each player
    lines = {}
    for player in players:
        line, = ax.plot([], [], label=player['name'], color=player['color'], linewidth=2)
        lines[player['name']] = line
    
    ax.set_title("Player Balances Over Time", fontsize=14, fontweight='bold')
    ax.set_xlabel("Round", fontsize=12)
    ax.set_ylabel("Balance ($)", fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # Add reference lines for context
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Bankrupt Line')
    ax.axhline(y=1000, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='Starting Balance')
    
    print(f"\nStarting simulation with {num_rounds} rounds...")
    print(f"Chart will update every {update_freq} round(s)")
    if print_freq > 0:
        print(f"Round results will print every {print_freq} round(s)\n")
    else:
        print("Round results printing disabled\n")

    # Run the simulation
    for round_num in range(1, num_rounds + 1):
        number, result_color = play_round(players, round_num)
        
        # Print results if requested
        if print_freq > 0 and round_num % print_freq == 0:
            print(f"Round {round_num}: {number} ({result_color})")
        
        # Record current balances
        # For bankrupt players, carry forward their last balance
        for player in players:
            balance = player['balance'] if player.get('is_active', True) else balance_history[player['name']][-1]
            balance_history[player['name']].append(balance)

        # Update the chart periodically (not every round for performance)
        if round_num % update_freq == 0 or round_num == num_rounds:
            x_data = range(len(balance_history[players[0]['name']]))
            
            for player in players:
                lines[player['name']].set_data(x_data, balance_history[player['name']])
            
            # Recalculate axes limits based on new data
            ax.relim()
            ax.autoscale_view()
            
            # Refresh the plot without blocking execution
            plt.draw()
            plt.pause(0.001)

    # Simulation complete - switch to blocking mode
    plt.ioff()
    print("\n✓ Simulation complete! Close the chart window to see statistics.\n")
    plt.show()

    # Save results to CSV for further analysis
    balance_df = pd.DataFrame(balance_history)
    balance_df.to_csv("roulette_simulation.csv", index_label="Round")
    print("✓ Data exported to roulette_simulation.csv\n")

    # Display final statistics for each player
    print("="*60)
    print("PLAYER STATISTICS")
    print("="*60)
    
    for player in players:
        rounds_played = player.get('rounds_played', 0)
        wins = player.get('wins', 0)
        win_rate = (wins / rounds_played * 100) if rounds_played else 0
        profit = player['balance'] - 1000
        last_round = player.get('last_active_round', 'active until end')

        print(f"\n🎲 {player['name'].upper()}")
        print(f"   {'─' * 50}")
        print(f"   Rounds played:    {rounds_played}")
        print(f"   Wins:             {wins} ({win_rate:.1f}%)")
        print(f"   Total profit/loss: ${profit:+.2f}")
        print(f"   Final balance:    ${player['balance']:.2f}")
        
        if 'Marty' in player['name']:
            print(f"   Stopped at round: {last_round}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()