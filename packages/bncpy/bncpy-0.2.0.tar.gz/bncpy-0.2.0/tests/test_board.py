from unittest.mock import patch

import pytest

from bnc.board import Board, BoardRow


class TestBoardRow:
    """Test cases for the BoardRow dataclass."""

    def test_board_row_initialization(self):
        """Test BoardRow initialization with default values."""
        row = BoardRow(guess=[1, 2, 3, 4])
        assert row.guess == [1, 2, 3, 4]
        assert row.bulls == 0
        assert row.cows == 0
        assert row.is_filled is False

    def test_board_row_with_custom_values(self):
        """Test BoardRow initialization with custom values."""
        row = BoardRow(guess=[1, 2, 3, 4], bulls=2, cows=1, is_filled=True)
        assert row.bulls == 2
        assert row.cows == 1
        assert row.is_filled is True

    def test_is_winning_row_true(self):
        """Test is_winning_row property when row is winning."""
        row = BoardRow(guess=[1, 2, 3, 4], bulls=4, cows=0, is_filled=True)
        assert row.is_winning_row is True

    def test_is_winning_row_false_not_filled(self):
        """Test is_winning_row property when row is not filled."""
        row = BoardRow(guess=[1, 2, 3, 4], bulls=4, cows=0, is_filled=False)
        assert row.is_winning_row is False

    def test_is_winning_row_false_partial_bulls(self):
        """Test is_winning_row property with partial bulls."""
        row = BoardRow(guess=[1, 2, 3, 4], bulls=2, cows=2, is_filled=True)
        assert row.is_winning_row is False


class TestBoard:
    """Test cases for the Board class."""

    def test_board_initialization_default(self):
        """Test Board initialization with default parameters."""
        board = Board()
        assert board.code_length == 4
        assert board.num_of_colors == 6
        assert board.num_of_guesses == 10
        assert board.secret_code is None
        assert len(board.board) == 10
        assert board.game_won is False
        assert board.game_over is False

    def test_board_initialization_custom(self):
        """Test Board initialization with custom parameters."""
        board = Board(
            code_length=5, num_of_colors=8, num_of_guesses=12, secret_code="12345"
        )
        assert board.code_length == 5
        assert board.num_of_colors == 8
        assert board.num_of_guesses == 12
        assert board.secret_code == "12345"
        assert len(board.board) == 12

    def test_board_initialization_invalid_code_length(self):
        """Test Board initialization with invalid code_length."""
        with pytest.raises(ValueError, match="code_length must be at least 3"):
            Board(code_length=2)

    def test_board_initialization_invalid_num_of_colors(self):
        """Test Board initialization with invalid num_of_colors."""
        with pytest.raises(ValueError, match="num_of_colors must be at least 5"):
            Board(num_of_colors=4)

    def test_board_initialization_invalid_num_of_guesses(self):
        """Test Board initialization with invalid num_of_guesses."""
        with pytest.raises(ValueError, match="num_of_guesses must be at least 1"):
            Board(num_of_guesses=0)

    @patch("bnc.board.validate_secret_code")
    def test_secret_code_setter(self, mock_validate):
        """Test secret code setter with validation."""
        mock_validate.return_value = [1, 2, 3, 4]
        board = Board()
        board.secret_code = "1234"

        assert board.secret_code == "1234"
        mock_validate.assert_called_once_with("1234", 4, 6)

    def test_current_board_row_index(self):
        """Test current_board_row_index property."""
        board = Board()
        assert board.current_board_row_index == 0

        # Fill first row
        board.set_board_row(2, 2, [1, 2, 3, 4], 0)
        assert board.current_board_row_index == 1

        # Fill all rows
        for i in range(1, 10):
            board.set_board_row(0, 0, [1, 1, 1, 1], i)
        assert board.current_board_row_index == -1

    def test_create_new_board(self):
        """Test create_new_board method."""
        original_board = Board(
            code_length=5, num_of_colors=7, num_of_guesses=8, secret_code="12345"
        )
        new_board = original_board.create_new_board()

        assert new_board.code_length == original_board.code_length
        assert new_board.num_of_colors == original_board.num_of_colors
        assert new_board.num_of_guesses == original_board.num_of_guesses
        assert new_board.secret_code == original_board.secret_code
        assert new_board is not original_board

    def test_set_board_row(self):
        """Test set_board_row method."""
        board = Board()
        board.set_board_row(2, 1, [1, 2, 3, 4], 0)

        row = board.board[0]
        assert row.guess == [1, 2, 3, 4]
        assert row.bulls == 2
        assert row.cows == 1
        assert row.is_filled is True

    def test_calculate_bulls_and_cows_no_secret(self):
        """Test calculate_bulls_and_cows without secret code."""
        board = Board()
        with pytest.raises(ValueError, match="Secret code must be set"):
            board.calculate_bulls_and_cows([1, 2, 3, 4])

    @patch("bnc.board.validate_secret_code")
    def test_calculate_bulls_and_cows_exact_match(self, mock_validate):
        """Test calculate_bulls_and_cows with exact match."""
        mock_validate.return_value = [1, 2, 3, 4]
        board = Board()
        board.secret_code = "1234"

        bulls, cows = board.calculate_bulls_and_cows([1, 2, 3, 4])
        assert bulls == 4
        assert cows == 0

    @patch("bnc.board.validate_secret_code")
    def test_calculate_bulls_and_cows_partial_match(self, mock_validate):
        """Test calculate_bulls_and_cows with partial match."""
        mock_validate.return_value = [1, 2, 3, 4]
        board = Board()
        board.secret_code = "1234"

        bulls, cows = board.calculate_bulls_and_cows([1, 3, 2, 4])
        assert bulls == 2  # positions 0 and 3
        assert cows == 2  # digits 2 and 3 in wrong positions

    @patch("bnc.board.validate_secret_code")
    def test_calculate_bulls_and_cows_no_match(self, mock_validate):
        """Test calculate_bulls_and_cows with no match."""
        mock_validate.return_value = [1, 2, 3, 4]
        board = Board()
        board.secret_code = "1234"

        bulls, cows = board.calculate_bulls_and_cows([5, 6, 7, 8])
        assert bulls == 0
        assert cows == 0

    @patch("bnc.board.validate_secret_code")
    def test_calculate_bulls_and_cows_duplicate_digits(self, mock_validate):
        """Test calculate_bulls_and_cows with duplicate digits."""
        mock_validate.return_value = [1, 1, 2, 2]
        board = Board()
        board.secret_code = "1122"

        bulls, cows = board.calculate_bulls_and_cows([1, 2, 1, 2])
        assert bulls == 2
        assert cows == 2

    @patch("bnc.board.check_board_row_index")
    @patch("bnc.board.validate_code_input")
    @patch("bnc.board.validate_secret_code")
    def test_evaluate_guess_winning(
        self, mock_validate_secret, mock_validate_input, mock_check_index
    ):
        """Test evaluate_guess with winning guess."""
        mock_validate_secret.return_value = [1, 2, 3, 4]
        mock_validate_input.return_value = [1, 2, 3, 4]
        mock_check_index.return_value = True

        board = Board()
        board.secret_code = "1234"
        board.evaluate_guess(0, "1234")

        assert board.game_won is True
        assert board.game_over is True

    @patch("bnc.board.check_board_row_index")
    @patch("bnc.board.validate_code_input")
    @patch("bnc.board.validate_secret_code")
    def test_evaluate_guess_last_row_not_winning(
        self, mock_validate_secret, mock_validate_input, mock_check_index
    ):
        """Test evaluate_guess on last row without winning."""
        mock_validate_secret.return_value = [1, 2, 3, 4]
        mock_validate_input.return_value = [5, 6, 7, 8]
        mock_check_index.return_value = True

        board = Board(num_of_guesses=1)
        board.secret_code = "1234"
        board.evaluate_guess(0, "5678")

        assert board.game_won is False
        assert board.game_over is True

    @patch("bnc.board.check_board_row_index")
    def test_evaluate_guess_invalid_index(self, mock_check_index):
        """Test evaluate_guess with invalid row index."""
        mock_check_index.return_value = False
        board = Board()

        with pytest.raises(ValueError, match="Row index is out of range"):
            board.evaluate_guess(10, "1234")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
