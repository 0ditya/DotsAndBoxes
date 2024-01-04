import random
import copy
import math
import time

class DotsBoxesGame:
    def __init__(self, rows, columns):
        self.play_dict = {}
        self.score_dict = {}
        self.row_count = rows
        self.column_count = columns
        self.player_1_score = 0
        self.player_2_score = 0

        self.initialize_play_dict()
        self.initialize_score_dict()

    def print_state(self):
        """
        Print the current state of the game.
        """
        self.render()
        print("\nPlayer 1: {} Player 2: {}".format(self.player_1_score, self.player_2_score))

    def get_future_state(self, start_point, end_point, player_1):
        """
        Get a new game state after making a move.
        """
        new_game = copy.deepcopy(self)
        new_game.make_play(start_point, end_point, player_1)
        return new_game

    def initialize_play_dict(self):
        for i in range(self.row_count):
            for j in range(self.column_count - 1):
                self.play_dict[((j + (i * self.column_count)), j + (i * self.column_count) + 1)] = 0

        for i in range(self.row_count - 1):
            for j in range(self.column_count):
                self.play_dict[(j + (i * self.column_count), j + self.column_count + (i * self.column_count))] = 0

    def initialize_score_dict(self):
        for i in range(self.row_count - 1):
            for j in range(self.column_count - 1):
                box = [(j + i * self.column_count, j + i * self.column_count + 1)]
                box.append((box[0][0], box[0][1] + self.column_count - 1))
                box.append((box[0][0] + 1, box[0][1] + self.column_count))
                box.append((box[0][0] + self.column_count, box[2][1]))
                self.score_dict[tuple(box)] = 0

    def render_row(self, i):
        left = (i * self.column_count)
        right = left + 1
        for j in range(self.column_count - 1):
            if self.play_dict[(left, right)] == 0:
                print("{:^3d}".format(left), end="   ")
            else:
                print("{:^3d} -".format(left), end=" ")
            left = right
            right = left + 1
        print("{:^3d}".format(left))

    def render_vertical(self, upper_left, upper_right):
        if self.play_dict[(upper_left, upper_right)] == 0:
            print("  ", end=" ")
        else:
            print(" |", end=" ")

    def render_middle_row(self, i):
        upper_left = (i * self.column_count)
        upper_right = upper_left + 1
        bottom_left = upper_left + self.column_count
        bottom_right = bottom_left + 1

        for j in range(self.column_count - 1):
            self.render_vertical(upper_left, bottom_left)

            top = (upper_left, upper_right)
            left = (upper_left, bottom_left)
            right = (upper_right, bottom_right)
            bottom = (bottom_left, bottom_right)
            score = self.score_dict[(top, left, right, bottom)]

            if score == 0:
                print("  ", end=" ")
            else:
                print(" " + str(score), end=" ")

            upper_left, bottom_left = upper_right, bottom_right
            upper_right += 1
            bottom_right += 1
        self.render_vertical(upper_left, bottom_left)
        print()

    def render(self):
        for i in range(self.row_count - 1):
            self.render_row(i)
            self.render_middle_row(i)

        self.render_row(self.row_count - 1)
        print("\nPlayer 1: {} Player 2: {}".format(self.player_1_score, self.player_2_score))

    def check_for_scores(self, player_1):
        player = 1 if player_1 else 2

        taken_set = {i for i in self.play_dict if self.play_dict[i] == 1}
        open_scores = [i for i in self.score_dict if self.score_dict[i] == 0]

        score_counter = 0

        for box in open_scores:
            if set(box).issubset(taken_set):
                score_counter += 1
                self.score_dict[box] = player
        return score_counter

    def make_play(self, start_point, end_point, player_1):
        try:
            if self.play_dict[(start_point, end_point)] == 1:
                return False
        except KeyError:
            return False

        self.play_dict[(start_point, end_point)] = 1

        score = self.check_for_scores(player_1)
        if player_1:
            self.player_1_score += score
        else:
            self.player_2_score += score
        return True

    def get_open_plays(self):
        return [i for i in self.play_dict if self.play_dict[i] == 0]

    def is_over(self):
        return self.player_1_score + self.player_2_score == len(self.score_dict)


class HumanPlayer:
    def __init__(self, player_1):
        self.player_1 = player_1
        self.playername = 1 if player_1 else 2

    def make_play(self, game):
        while True:
            move = input("Player {}, make your move (start point end point): ".format(self.playername))
            move = move.split()
            try:
                if len(move) != 2:
                    raise ValueError("Input must be of the form start point, endpoint")
                
                move = tuple(map(int, move))
                move = tuple(sorted(move))
                
            except ValueError as e:
                print("Error:", e)
                continue
            
            if move in game.get_open_plays():
                game.make_play(*move, self.player_1)
                return
            else:
                print("Error. That move does not exist. Try again")


class AlphaBetaPlayer:
    def __init__(self, player_1):
        self.player_1 = player_1

    def alphabeta(self, game, play, depth, alpha, beta, player_1):
        if game.is_over() or depth == 0:
            return game.player_1_score - game.player_2_score, play

        if player_1:
            value = -math.inf
            for move in game.get_open_plays():
                new_game = game.get_future_state(*move, True)
                new_game = copy.deepcopy(game)
                old_score = new_game.player_1_score
                new_game.make_play(*move, True)
                new_score = new_game.player_1_score

                if new_score == old_score:
                    new_play_results = self.alphabeta(new_game, move, depth - 1, alpha, beta, False)
                else:
                    new_play_results = self.alphabeta(new_game, move, depth - 1, alpha, beta, True)

                if value >= new_play_results[0]:
                    play = move
                    value = new_play_results[0]

                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value, play

        else:
            value = math.inf
            for move in game.get_open_plays():
                new_game = game.get_future_state(*move, False)
                new_game = copy.deepcopy(game)
                old_score = new_game.player_2_score
                new_game.make_play(*move, False)
                new_score = new_game.player_2_score

                if new_score == old_score:
                    move_results = self.alphabeta(new_game, move, depth - 1, alpha, beta, True)
                else:
                    move_results = self.alphabeta(new_game, move, depth - 1, alpha, beta, False)

                if value <= move_results[0]:
                    play = move
                    value = move_results[0]
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value, play

    def get_all_future_states(self, game):
        future_states = []
        for move in game.get_open_plays():
            future_state = game.get_future_state(*move, self.player_1)
            future_states.append(future_state)
        return future_states

    def make_play(self, game):
        start_time = time.time()
        play_space_size = len(game.get_open_plays())
        if play_space_size == 1:
            play = random.choice(game.get_open_plays())
            game.make_play(*play, self.player_1)
            return

        depth = math.floor(math.log(19000, play_space_size))

        play = self.alphabeta(game, (0, 0), depth, -math.inf, math.inf, self.player_1)[1]
        elapsed = time.time() - start_time

        if play == (0, 0):
            play = random.choice(game.get_open_plays())
        game.make_play(*play, self.player_1)

        player = 1 if self.player_1 else 2
        print("Player {}'s move: {} {}".format(player, *play))
        print("Time elapsed to make move: {}".format(elapsed))

        all_future_states = self.get_all_future_states(game)
        for idx, future_state in enumerate(all_future_states):
            print("\nFuture State {} After Move {}: {} {}".format(idx + 1, play, future_state.player_1_score, future_state.player_2_score))
            print(future_state)

class DotsBoxesGameController:
    def __init__(self, player_1_type="alphabeta", player_2_type="alphabeta", rows=5, columns=5):
        self.rows = rows
        self.columns = columns

        if player_1_type == "alphabeta":
            self.player_1 = AlphaBetaPlayer(True)
        else:
            self.player_1 = HumanPlayer(True)

        if player_2_type == "alphabeta":
            self.player_2 = AlphaBetaPlayer(False)
        else:
            self.player_2 = HumanPlayer(False)

    def play_game(self):
        game = DotsBoxesGame(self.rows, self.columns)

        print()
        game.render()
        print()

        while not game.is_over():
            while not game.is_over():
                old_score = game.player_1_score
                self.player_1.make_play(game)
                game.render()
                if old_score == game.player_1_score:
                    break

            while not game.is_over():
                old_score = game.player_2_score
                self.player_2.make_play(game)
                game.render()
                if old_score == game.player_2_score:
                    break

        if game.player_1_score == game.player_2_score:
            print("It's a tie!")
        elif game.player_1_score >= game.player_2_score:
            print("Player 1 wins!")
        else:
            print("Player 2 wins!")


def main():
    print("Welcome to Dots and Boxes!")

    play_again = "y"
    while play_again.lower() == "y":
        rows = 3
        columns = 3

        game_controller = DotsBoxesGameController("Human","alphabeta", rows, columns)
        game_controller.play_game()

        play_again = input("Play again? (y/n): ")

    print("Thank you for playing! :)")


if __name__ == "__main__":
    main()