from unittest.mock import patch

from bnc.board import Board
from bnc.game import CurrentGameStatus, Game
from bnc.player import Player


class TestIntegration:
    """Integration tests for the complete game system."""

    @patch("bnc.board.validate_secret_code")
    @patch("bnc.board.validate_code_input")
    @patch("bnc.board.check_board_row_index")
    def test_complete_game_flow_single_winner(
        self, mock_check_index, mock_validate_input, mock_validate_secret
    ):
        """Test complete game flow with a single winner."""
        # Setup mocks
        mock_check_index.return_value = True
        mock_validate_secret.return_value = [1, 2, 3, 4]
        mock_validate_input.side_effect = [
            [5, 6, 7, 8],  # Wrong guess
            [1, 2, 3, 4],  # Correct guess
        ]

        # Create game with two players
        board1 = Board()
        board2 = Board()
        player1 = Player("Alice", board1)
        player2 = Player("Bob", board2)

        game = Game([player1, player2], secret_code="1234")

        # Initial state
        assert game.state == CurrentGameStatus.SETUP

        # Player 1 makes wrong guess
        game.submit_guess(player1, "5678")
        assert game.state == CurrentGameStatus.IN_PROGRESS
        assert player1.game_won is False

        # Player 2 makes correct guess
        game.submit_guess(player2, "1234")
        assert player2.game_won is True
        assert game.winner == player2
        assert len(game.winners) == 1

        # Game continues for other player
        assert game.state == CurrentGameStatus.IN_PROGRESS

    @patch("bnc.board.validate_secret_code")
    @patch("bnc.board.validate_code_input")
    @patch("bnc.board.check_board_row_index")
    def test_complete_game_flow_all_players_lose(
        self, mock_check_index, mock_validate_input, mock_validate_secret
    ):
        """Test complete game flow where all players lose."""
        # Setup mocks
        mock_check_index.return_value = True
        mock_validate_secret.return_value = [1, 2, 3, 4]
        mock_validate_input.return_value = [5, 6, 7, 8]  # Always wrong

        # Create game with one guess allowed
        board = Board(num_of_guesses=1)
        player = Player("Alice", board)
        game = Game([player], secret_code="1234")

        # Make wrong guess
        game.submit_guess(player, "5678")

        assert player.game_won is False
        assert player.game_over is True
        assert game.state == CurrentGameStatus.FINISHED
        assert game.winner is None
