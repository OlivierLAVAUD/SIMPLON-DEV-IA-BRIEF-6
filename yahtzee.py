class YahtzeeGame:
    def __init__(self, num_players, num_faces):
        self.num_players = num_players
        self.num_faces = num_faces
        self.players = [self.create_player() for _ in range(num_players)]
        self.current_turn = 1
        self.total_turns = 13
        self.game_history = []

    @staticmethod
    def create_player():
        return {
            "upper_section": {i: None for i in range(1, 7)},
            "lower_section": {"Brelan": None, "Carré": None, "Full House": None, "Petite Suite": None,
                              "Grande Suite": None, "YAHTZEE": None, "Chance": None},
            "total_score": 0,
            "bonus": 0,
            "lower_section_total": 0,
            "upper_section_total": 0,
            "combined_total": 0,
            "triple_yahtzee_total": 0,
            "previous_combined_total": 0
        }

    def roll_dice(self, num_dice):
        return [random.randint(1, self.num_faces) for _ in range(num_dice)]

    def display_scorecard(self, player_index):
        player = self.players[player_index]
        print("\n=== Scorecard for Player", player_index + 1, "===", f"(Turn {self.current_turn})")
        print("Upper Section:")
        for key, value in player["upper_section"].items():
            print(f"{key}: {value if value is not None else '-'}")
        print("\nLower Section:")
        for key, value in player["lower_section"].items():
            print(f"{key}: {value if value is not None else '-'}")
        print("\nTotal Score:", player["total_score"])
        print("Bonus:", player["bonus"])
        print("Total (Upper Section):", player["upper_section_total"])
        print("Lower Section Total:", player["lower_section_total"])
        print("Upper Section Total:", player["upper_section_total"])
        print("Combined Total:", player["combined_total"])
        print("Triple YAHTZEE Total:", player["triple_yahtzee_total"])

    def choose_dice_to_keep(self, dice):
        print("\nCurrent Dice:", dice)
        keep_indices_input = input("Enter the dice indices to keep (e.g., 2 3 to keep dice 2 and 3): ")
        keep_indices_list = [int(i) - 1 for i in keep_indices_input.replace(',', ' ').split()]
        return [dice[i] for i in keep_indices_list]

    def calculate_score(self, combination, dice):
        if combination in self.upper_section:
            value = int(combination)
            score = dice.count(value) * value
        elif combination == "Brelan":
            score = sum(dice) if any(dice.count(value) >= 3 for value in dice) else 0
        elif combination == "Carré":
            score = sum(dice) if any(dice.count(value) >= 4 for value in dice) else 0
        elif combination == "Full House":
            three_of_a_kind = any(dice.count(value) >= 3 for value in dice)
            two_of_a_kind = any(dice.count(value) >= 2 for value in dice)
            score = 25 if three_of_a_kind and two_of_a_kind else 0
        elif combination == "Petite Suite":
            sorted_dice = sorted(dice)
            score = 30 if any(b - a != 1 for a, b in zip(sorted_dice, sorted_dice[1:])) else 0
        elif combination == "Grande Suite":
            sorted_dice = sorted(dice)
            score = 40 if sorted_dice in ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6]) else 0
        elif combination == "YAHTZEE":
            score = 50 if any(dice.count(value) == 5 for value in dice) else 0
        elif combination == "Chance":
            score = sum(dice)
        else:
            score = 0
        return score

    def play_turn(self, player_index):
        print("\n=== Player", player_index + 1, "'s Turn Start ===")
        player = self.players[player_index]
        kept_dice = []

        for _ in range(3):
            dice = self.roll_dice(5 - len(kept_dice))  # Ne relancer que les dés non gardés

            # Player decides which dice to keep for the next roll
            kept_dice += self.choose_dice_to_keep(dice)
            
            print(f"Dices kept are: {kept_dice}")

            # If it's the third roll or all dice are kept, exit the loop
            if len(kept_dice) == 5:
                break

        # Affiche les combinaisons disponibles
        print("\nAvailable Combinations:")
        for key in player["upper_section"]:
            print(f"{key} - {player['upper_section'][key]}")

        for key in player["lower_section"]:
            print(f"{key} - {player['lower_section'][key]}")

        # Player chooses a combination and calculates the score
        valid_combinations = {key: key for key in [*player["upper_section"], *player["lower_section"]]}
    
        while True:
            combination_key = input("\nEnter the combination (e.g., B for Brelan, P for Petite Suite, etc.): ").upper()

            if combination_key in valid_combinations:
                break
            else:
                print("Invalid combination. Please choose a valid combination.")

        combination = valid_combinations[combination_key]
    
        score = self.calculate_score(combination, kept_dice)

        # Update the scorecard
        if combination in player["upper_section"]:
            player["upper_section"][combination] = score
            player["upper_section_total"] = sum(filter(None, player["upper_section"].values()))
            if player["upper_section_total"] >= 63:
                player["bonus"] = 35
                player["total_score"] = player["upper_section_total"] + player["lower_section_total"] + player["bonus"]
            elif combination in player["lower_section"]:
                player["lower_section"][combination] = score
                player["lower_section_total"] = sum(filter(None, player["lower_section"].values()))
                player["total_score"] = player["upper_section_total"] + player["lower_section_total"] + player["bonus"]
        elif combination == "Triple YAHTZEE":
            player["triple_yahtzee_total"] = player["previous_combined_total"] + player["combined_total"]

        # Update the combined total
        player["combined_total"] = player["upper_section_total"] + player["lower_section_total"]

        # Display the updated scorecard
        self.display_scorecard(player_index)

        # Save game state to history
        game_state = {
            "timestamp": str(datetime.now()),
            "turn": self.current_turn,
            "player_index": player_index,
            "combination": combination,
            "score": score,
            "player_state": player.copy()
        }
        self.game_history.append(game_state)

        # Save the current state of the game to a file
        with open(f"yahtzee_game_state_turn_{self.current_turn}_player_{player_index + 1}.json", "w") as file:
            json.dump(game_state, file)
        
    def play_game(self):
        for turn in range(1, self.total_turns + 1):
            print("\n=== Turn", turn, "===")
            for player_index in range(self.num_players):
                self.play_turn(player_index)
                self.players[player_index]["previous_combined_total"] = self.players[player_index]["combined_total"]
            self.current_turn += 1

        # Determine the winner
        max_score = max(player["total_score"] for player in self.players)
        winners = [i + 1 for i, player in enumerate(self.players) if player["total_score"] == max_score]

        print("\nGame Over. Final Scores:")
        for i, player in enumerate(self.players):
            print(f"Player {i + 1}: {player['total_score']} points")

        # Save game history to a JSON file
        with open("yahtzee_game_history.json", "w") as file:
            json.dump(self.game_history, file)

if __name__ == "__main__":
    num_players = 1  #int(input("Enter the number of players: "))
    num_faces = 6   #int(input("Enter the number of faces on each die: "))
    yahtzee_game = YahtzeeGame(num_players, num_faces)
    yahtzee_game.play_game()
