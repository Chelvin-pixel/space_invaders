import uuid
import random
class Prisoner:
    def __init__(self):
        self.id = uuid.uuid4()
        self.strategies = [self.choose_response_random, self.choose_response_kind, self.choose_response_greedy, self.choose_response_tit_for_tat]
        self.choose_response = random.choice(self.strategies)
        self.rewards = []
        self.choices = []
        self.opponent_choices = []
        print (f"I am a Prisoner. My id is:{self.id}")
    def choose_response_random(self):
        possible_responses = ["share", "take"]
        choice = random.choice(possible_responses)
        self.choices.append(choice)
        return choice
    def choose_response_kind(self):
        self.choices.append("share")
        return "share"
    def choose_response_tit_for_tat(self):
        # Start by being kind, then copy whatever your opponant did in the previous round.
        if len(self.choices) == 0:
            self.choices.append("share")
        else:
            opponent_last_choice = self.opponent_choices[-1]
            self.choices.append(opponent_last_choice)
        return self.choices[-1]
    def choose_response_greedy(self):
        self.choices.append("take")
        return "take"
    def receive_reward(self, reward):
        self.rewards.append(reward)
    def get_strategy_name(self):
        if self.choose_response == self.choose_response_kind:
            return "Kind"
        elif self.choose_response == self.choose_response_greedy:
            return "Greedy"
        elif self.choose_response == self.choose_response_random:
            return "Random"
        elif self.choose_response == self.choose_response_tit_for_tat:
            return "Tit for Tat"
def get_payoff(prisoner_1_choice, prisoner_2_choice):
    if prisoner_1_choice == "share" and prisoner_2_choice == "share":
        return (1, 1)  # Both get 1 apple
    elif prisoner_1_choice == "take" and prisoner_2_choice == "take":
        return (0, 0)  # Both get nothing
    elif prisoner_1_choice == "take" and prisoner_2_choice == "share":
        return (2, 0)  # Player 1 gets 2, Player 2 gets 0
    else:  # player1 shares, player2 takes
        return (0, 2)  # Player 1 gets 0, Player 2 gets 2

if __name__ == "__main__":
    rounds = 10000
    prisoner_1 = Prisoner()
    prisoner_1.choose_response = prisoner_1.choose_response_kind
    prisoner_2 = Prisoner()
    prisoner_2.choose_response = prisoner_2.choose_response_random
    prisoner_3 = Prisoner()
    prisoner_3.choose_response = prisoner_3.choose_response_greedy
    prisoner_4 = Prisoner()
    prisoner_4.choose_response = prisoner_4.choose_response_tit_for_tat
    prisoners = [prisoner_1, prisoner_2, prisoner_3, prisoner_4]
    for round_index in range(rounds):
        #print(prisoner_1.choose_response())
        #print(prisoner_2.choose_response())
        # if both prisoners share, they both get 1 apple.
        # if both prisoners take, they both get nothing.
        # if one prisoner takes, and the other shares, the prisoner that takes gets 2 apples, and the one that shares gets nothing.
        prisoner_a = random.choice(prisoners)
        prisoner_b = random.choice(prisoners)
        prisoner_a.choices = []
        prisoner_b.choices = []
        prisoner_a.opponent_choices = prisoner_b.choices
        prisoner_b.opponent_choices = prisoner_a.choices
        for game_index in range(100):

            prisoner_a.choose_response()
            prisoner_b.choose_response()
            prisoner_a_reward, prisoner_b_reward = get_payoff(prisoner_a.choices[-1], prisoner_b.choices[-1])
            #print(f"prisoner 1 reward is: {prisoner_1_reward}")
            #print(f"prisoner 2 reward is: {prisoner_2_reward}")
            prisoner_a.receive_reward(prisoner_a_reward)
            prisoner_b.receive_reward(prisoner_b_reward)
    print(f"prisoner 1 {prisoner_1.get_strategy_name()} total reward: {sum(prisoner_1.rewards)}")
    print(f"prisoner 2 {prisoner_2.get_strategy_name()} total reward: {sum(prisoner_2.rewards)}")
    print(f"prisoner 3 {prisoner_3.get_strategy_name()} total reward: {sum(prisoner_3.rewards)}")
    print(f"prisoner 4 {prisoner_4.get_strategy_name()} total reward: {sum(prisoner_4.rewards)}")
