from unittest.mock import Mock, patch

import pytest

from bnc.game import CurrentGameStatus, Game
from bnc.player import Player


class TestGame:
    """Test cases for the Game class."""

    def test_game_initialization_single_player(self):
        """Test Game initialization with single player."""
        player = Mock(spec=Player)
        game = Game([player])

        assert game.players == [player]
        assert game.state == CurrentGameStatus.SETUP
        assert game.winner is None
        assert len(game.winners) == 0
        player.set_secret_code_to_board.assert_called_once_with(None)

    def test_game_initialization_multiple_players(self):
        """Test Game initialization with multiple players."""
        players = [Mock(spec=Player) for _ in range(3)]
        game = Game(players, secret_code="1234")

        assert game.players == players
        for player in players:
            player.set_secret_code_to_board.assert_called_once_with("1234")

    def test_game_initialization_no_players(self):
        """Test Game initialization with no players."""
        with pytest.raises(ValueError, match="Players cannot be empty"):
            Game([])

    def test_set_secret_code_for_all_players(self):
        """Test set_secret_code_for_all_players method."""
        players = [Mock(spec=Player) for _ in range(2)]
        game = Game(players)

        # Reset mock calls from initialization
        for player in players:
            player.reset_mock()

        game.set_secret_code_for_all_players("5678")
        for player in players:
            player.set_secret_code_to_board.assert_called_once_with("5678")

    def test_state_transitions(self):
        """Test game state transitions."""
        player = Mock(spec=Player)
        player.game_over = False
        player.name = "TestPlayer"
        game = Game([player])

        # Initial state
        assert game.state == CurrentGameStatus.SETUP

        # After first guess
        game.submit_guess(player, "1234")
        assert game.state == CurrentGameStatus.IN_PROGRESS

        # After game over
        player.game_over = True
        assert game.state == CurrentGameStatus.FINISHED

    def test_submit_guess_normal_flow(self):
        """Test submit_guess in normal flow."""
        player = Mock(spec=Player)
        player.game_over = False
        player.game_won = False
        player.name = "TestPlayer"

        game = Game([player])
        game.submit_guess(player, "1234")

        player.make_guess.assert_called_once_with("1234")

    @patch("bnc.game.logger")
    def test_submit_guess_winning_player(self, mock_logger):
        """Test submit_guess when player wins."""
        player = Mock(spec=Player)
        player.game_over = False
        player.game_won = True
        player.name = "Winner"

        game = Game([player])
        game.submit_guess(player, "1234")

        assert player in game.winners
        assert game.winner == player
        mock_logger.info.assert_called_with(
            "%s won the game in %s place!", "Winner", "first"
        )

    @patch("bnc.game.logger")
    def test_submit_guess_multiple_winners(self, mock_logger):
        """Test submit_guess with multiple winners."""
        players = []
        for i in range(3):
            player = Mock(spec=Player)
            player.game_over = False
            player.game_won = True
            player.name = f"Player{i + 1}"
            players.append(player)

        game = Game(players)

        # Submit guesses for all players
        for i, player in enumerate(players):
            game.submit_guess(player, "1234")
            position_text = ["first", "second", "third"][i]
            mock_logger.info.assert_any_call(
                "%s won the game in %s place!", player.name, position_text
            )

        assert len(game.winners) == 3
        assert game.winner == players[0]  # First winner

    @patch("bnc.game.logger")
    def test_submit_guess_already_won(self, mock_logger):
        """Test submit_guess for player who already won."""
        player = Mock(spec=Player)
        player.game_over = False
        player.game_won = True
        player.name = "Winner"

        game = Game([player])
        game.submit_guess(player, "1234")  # First win

        # Try to submit another guess
        player.make_guess.reset_mock()
        game.submit_guess(player, "5678")

        player.make_guess.assert_not_called()
        mock_logger.info.assert_called_with("%s already won the game", "Winner")

    @patch("bnc.game.logger")
    def test_submit_guess_game_over_no_win(self, mock_logger):
        """Test submit_guess when player's game is over without winning."""
        player = Mock(spec=Player)
        player.game_over = True
        player.game_won = False
        player.name = "Loser"

        game = Game([player])
        game.submit_guess(player, "1234")

        player.make_guess.assert_not_called()
        mock_logger.info.assert_called_with("%s can no longer play.", "Loser")

    @patch("bnc.game.logger")
    def test_submit_guess_player_loses_after_guess(self, mock_logger):
        """Test submit_guess when player loses after making guess."""
        player = Mock(spec=Player)
        player.game_over = False
        player.game_won = False
        player.name = "Player1"

        # Configure player to be game_over after make_guess
        def side_effect(guess):
            player.game_over = True

        player.make_guess.side_effect = side_effect

        game = Game([player])
        game.submit_guess(player, "1234")

        mock_logger.info.assert_called_with("%s has no more guesses.", "Player1")
