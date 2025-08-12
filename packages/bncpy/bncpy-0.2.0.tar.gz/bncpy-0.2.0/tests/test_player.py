from unittest.mock import Mock, patch

from bnc.board import Board
from bnc.player import Player


class TestPlayer:
    """Test cases for the Player class."""

    def test_player_initialization(self):
        """Test Player initialization."""
        board = Mock(spec=Board)
        player = Player("TestPlayer", board)

        assert player.name == "TestPlayer"
        assert player.board == board

    def test_game_over_property(self):
        """Test game_over property delegation."""
        board = Mock(spec=Board)
        board.game_over = True
        player = Player("TestPlayer", board)

        assert player.game_over is True

    def test_game_won_property(self):
        """Test game_won property delegation."""
        board = Mock(spec=Board)
        board.game_won = True
        player = Player("TestPlayer", board)

        assert player.game_won is True

    def test_set_secret_code_to_board(self):
        """Test set_secret_code_to_board delegation."""
        board = Mock(spec=Board)
        player = Player("TestPlayer", board)

        player.set_secret_code_to_board("1234")
        assert board.secret_code == "1234"

    @patch("bnc.player.logger")
    def test_make_guess_normal(self, mock_logger):
        """Test make_guess in normal conditions."""
        board = Mock(spec=Board)
        board.game_over = False
        board.current_board_row_index = 0

        player = Player("TestPlayer", board)
        player.make_guess("1234")

        board.evaluate_guess.assert_called_once_with(0, "1234")
        mock_logger.info.assert_not_called()

    @patch("bnc.player.logger")
    def test_make_guess_game_over(self, mock_logger):
        """Test make_guess when game is over."""
        board = Mock(spec=Board)
        board.game_over = True

        player = Player("TestPlayer", board)
        player.make_guess("1234")

        board.evaluate_guess.assert_not_called()
        mock_logger.info.assert_called_once_with(
            "%s has no more guesses.", "TestPlayer"
        )
