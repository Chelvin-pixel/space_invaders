import uuid
import random
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import numpy as np

class Prisoner:
    def __init__(self, strategy_name=None):
        self.id = uuid.uuid4()
        self.strategies = {
            'random': self.choose_response_random,
            'kind': self.choose_response_kind, 
            'greedy': self.choose_response_greedy,
            'tit_for_tat': self.choose_response_tit_for_tat,
            'generous_tit_for_tat': self.choose_response_generous_tit_for_tat,
            'pavlov': self.choose_response_pavlov,
            'grudger': self.choose_response_grudger
        }
        
        if strategy_name:
            self.choose_response = self.strategies[strategy_name]
            self.strategy_name = strategy_name
        else:
            self.strategy_name = random.choice(list(self.strategies.keys()))
            self.choose_response = self.strategies[self.strategy_name]
            
        self.rewards = []
        self.choices = []
        self.opponent_choices = []
        self.opponent_history = {}  # Track history with each opponent
        self.reputation_score = 0.5  # 0 = untrustworthy, 1 = trustworthy
        
    def reset_for_new_game(self):
        """Reset for a new game series"""
        self.choices = []
        self.opponent_choices = []
        
    def choose_response_random(self):
        choice = random.choice(["share", "take"])
        self.choices.append(choice)
        return choice
        
    def choose_response_kind(self):
        self.choices.append("share")
        return "share"
        
    def choose_response_greedy(self):
        self.choices.append("take")
        return "take"
        
    def choose_response_tit_for_tat(self):
        if len(self.opponent_choices) == 0:
            self.choices.append("share")
        else:
            opponent_last_choice = self.opponent_choices[-1]
            self.choices.append(opponent_last_choice)
        return self.choices[-1]
        
    def choose_response_generous_tit_for_tat(self):
        """Tit for tat but sometimes forgives defection"""
        if len(self.opponent_choices) == 0:
            self.choices.append("share")
        else:
            opponent_last_choice = self.opponent_choices[-1]
            if opponent_last_choice == "take" and random.random() < 0.1:  # 10% chance to forgive
                self.choices.append("share")
            else:
                self.choices.append(opponent_last_choice)
        return self.choices[-1]
        
    def choose_response_pavlov(self):
        """Win-stay, lose-shift strategy"""
        if len(self.rewards) == 0:
            self.choices.append("share")
        else:
            last_reward = self.rewards[-1]
            if last_reward >= 1:  # If did well, repeat last choice
                if len(self.choices) > 0:
                    self.choices.append(self.choices[-1])
                else:
                    self.choices.append("share")
            else:  # If did poorly, switch
                if len(self.choices) > 0:
                    last_choice = self.choices[-1]
                    new_choice = "take" if last_choice == "share" else "share"
                    self.choices.append(new_choice)
                else:
                    self.choices.append("take")
        return self.choices[-1]
        
    def choose_response_grudger(self):
        """Cooperate until opponent defects, then always defect"""
        if "take" in self.opponent_choices:
            self.choices.append("take")
        else:
            self.choices.append("share")
        return self.choices[-1]
    
    def receive_reward(self, reward):
        self.rewards.append(reward)
        # Update reputation based on performance
        if reward > 0:
            self.reputation_score = min(1.0, self.reputation_score + 0.001)
        else:
            self.reputation_score = max(0.0, self.reputation_score - 0.001)
    
    def get_strategy_name(self):
        return self.strategy_name.replace('_', ' ').title()

def get_payoff(prisoner_1_choice, prisoner_2_choice):
    """Standard prisoner's dilemma payoff matrix"""
    if prisoner_1_choice == "share" and prisoner_2_choice == "share":
        return (3, 3)  # Mutual cooperation - increased reward
    elif prisoner_1_choice == "take" and prisoner_2_choice == "take":
        return (1, 1)  # Mutual defection - small punishment
    elif prisoner_1_choice == "take" and prisoner_2_choice == "share":
        return (5, 0)  # Temptation vs sucker
    else:  # prisoner_1 shares, prisoner_2 takes
        return (0, 5)  # Sucker vs temptation

def run_tournament(strategies, rounds=1000, games_per_round=100):
    """Run a round-robin tournament where each strategy plays against every other"""
    results = defaultdict(list)
    matchup_results = defaultdict(list)
    
    # Create prisoners for each strategy
    prisoners = {}
    for strategy in strategies:
        prisoners[strategy] = Prisoner(strategy)
    
    # Round-robin tournament
    strategy_pairs = [(s1, s2) for s1 in strategies for s2 in strategies]
    
    for round_num in range(rounds):
        for strategy1, strategy2 in strategy_pairs:
            prisoner_a = prisoners[strategy1]
            prisoner_b = prisoners[strategy2]
            
            # Reset for new game
            prisoner_a.reset_for_new_game()
            prisoner_b.reset_for_new_game()
            prisoner_a.opponent_choices = prisoner_b.choices
            prisoner_b.opponent_choices = prisoner_a.choices
            
            round_scores_a = []
            round_scores_b = []
            
            # Play multiple games in this round
            for _ in range(games_per_round):
                choice_a = prisoner_a.choose_response()
                choice_b = prisoner_b.choose_response()
                
                reward_a, reward_b = get_payoff(choice_a, choice_b)
                prisoner_a.receive_reward(reward_a)
                prisoner_b.receive_reward(reward_b)
                
                round_scores_a.append(reward_a)
                round_scores_b.append(reward_b)
            
            # Store results for this matchup
            matchup_key = f"{strategy1} vs {strategy2}"
            matchup_results[matchup_key].extend(round_scores_a)
            
    return prisoners, matchup_results

def run_evolutionary_simulation(initial_populations, generations=100, games_per_generation=50):
    """Simulate evolution of strategies over time"""
    population_history = []
    
    # Initialize population
    current_pop = dict(initial_populations)
    
    for generation in range(generations):
        population_history.append(dict(current_pop))
        
        # Create prisoners based on current population
        all_prisoners = []
        for strategy, count in current_pop.items():
            for _ in range(count):
                all_prisoners.append(Prisoner(strategy))
        
        # Play random games
        for _ in range(games_per_generation * sum(current_pop.values())):
            prisoner_a, prisoner_b = random.sample(all_prisoners, 2)
            prisoner_a.reset_for_new_game()
            prisoner_b.reset_for_new_game()
            prisoner_a.opponent_choices = prisoner_b.choices
            prisoner_b.opponent_choices = prisoner_a.choices
            
            # Play one game
            choice_a = prisoner_a.choose_response()
            choice_b = prisoner_b.choose_response()
            reward_a, reward_b = get_payoff(choice_a, choice_b)
            prisoner_a.receive_reward(reward_a)
            prisoner_b.receive_reward(reward_b)
        
        # Calculate fitness (average reward) for each strategy
        strategy_fitness = defaultdict(list)
        for prisoner in all_prisoners:
            if prisoner.rewards:
                avg_reward = sum(prisoner.rewards) / len(prisoner.rewards)
                strategy_fitness[prisoner.strategy_name].append(avg_reward)
        
        # Calculate new population based on fitness
        strategy_avg_fitness = {}
        for strategy, rewards in strategy_fitness.items():
            strategy_avg_fitness[strategy] = sum(rewards) / len(rewards) if rewards else 0
        
        # Proportional selection for next generation
        total_fitness = sum(strategy_avg_fitness.values())
        if total_fitness > 0:
            new_pop = {}
            total_pop = sum(current_pop.values())
            for strategy in current_pop.keys():
                fitness_proportion = strategy_avg_fitness.get(strategy, 0) / total_fitness
                new_count = max(1, round(fitness_proportion * total_pop))
                new_pop[strategy] = new_count
            current_pop = new_pop
    
    return population_history

def analyze_results(prisoners, matchup_results):
    """Analyze and display comprehensive results"""
    print("=== TOURNAMENT RESULTS ===")
    
    # Overall performance
    strategy_totals = {}
    for strategy, prisoner in prisoners.items():
        total_reward = sum(prisoner.rewards)
        avg_reward = total_reward / len(prisoner.rewards) if prisoner.rewards else 0
        strategy_totals[strategy] = {
            'total': total_reward, 
            'average': avg_reward,
            'games': len(prisoner.rewards)
        }
    
    # Sort by average reward
    sorted_strategies = sorted(strategy_totals.items(), key=lambda x: x[1]['average'], reverse=True)
    
    print("\nOverall Performance (by average reward per game):")
    for strategy, stats in sorted_strategies:
        print(f"{strategy.replace('_', ' ').title():20}: "
              f"Avg: {stats['average']:.3f}, "
              f"Total: {stats['total']:,}, "
              f"Games: {stats['games']:,}")
    
    # Head-to-head analysis
    print("\n=== HEAD-TO-HEAD ANALYSIS ===")
    strategies = list(prisoners.keys())
    for i, strategy1 in enumerate(strategies):
        for strategy2 in strategies[i:]:
            key1 = f"{strategy1} vs {strategy2}"
            key2 = f"{strategy2} vs {strategy1}"
            
            if key1 in matchup_results:
                scores1 = matchup_results[key1]
                scores2 = matchup_results[key2] if key2 in matchup_results else []
                
                avg1 = sum(scores1) / len(scores1) if scores1 else 0
                avg2 = sum(scores2) / len(scores2) if scores2 else 0
                
                print(f"{strategy1.replace('_', ' ').title()} vs {strategy2.replace('_', ' ').title()}: "
                      f"{avg1:.3f} vs {avg2:.3f}")

def visualize_results(population_history):
    """Create visualizations of the evolutionary simulation"""
    if not population_history:
        return
        
    generations = range(len(population_history))
    strategies = list(population_history[0].keys())
    
    plt.figure(figsize=(12, 8))
    
    for strategy in strategies:
        populations = [gen_pop.get(strategy, 0) for gen_pop in population_history]
        plt.plot(generations, populations, label=strategy.replace('_', ' ').title(), linewidth=2)
    
    plt.xlabel('Generation')
    plt.ylabel('Population Size')
    plt.title('Evolution of Prisoner\'s Dilemma Strategies')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    # Define strategies to test
    strategies = ['kind', 'greedy', 'tit_for_tat', 'random', 'generous_tit_for_tat', 'pavlov', 'grudger']
    
    print("Running tournament simulation...")
    prisoners, matchup_results = run_tournament(strategies, rounds=100, games_per_round=50)
    analyze_results(prisoners, matchup_results)
    
    print("\n" + "="*60)
    print("Running evolutionary simulation...")
    
    # Initial population for evolution
    initial_pop = {strategy: 20 for strategy in strategies}
    population_history = run_evolutionary_simulation(initial_pop, generations=50, games_per_generation=10)
    
    print(f"\nEvolutionary Results (Generation 0 -> {len(population_history)-1}):")
    print("Starting population:", population_history[0])
    print("Final population:", population_history[-1])
    
    # Uncomment to show visualization (requires matplotlib)
    # visualize_results(population_history)