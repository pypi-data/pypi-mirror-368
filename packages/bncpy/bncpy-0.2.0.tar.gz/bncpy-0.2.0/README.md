# bncpy

Benjamin and Charlotte

## Installation

```bash
pip install bncpy
```

## Usage

```python
from bnc import Board, Game, Player
from bnc.utils import generate_guess, get_random_number

# Game configuration
config = {
  "code_length": 4,
  "num_of_colors": 6,
  "num_of_guesses": 10
}

# Create players with boards
players = [
  Player(name="Jae", board=Board(**config)),
  Player(name="Soo", board=Board(**config)),
  Player(name="Benjamin", board=Board(**config)),
  Player(name="Charlotte", board=Board(**config))
]

# Create game with secret code
secret_code = get_random_number(length=4, max_value=5)  # Random 4-digit code
game = Game(players, secret_code=secret_code)

# Submit guesses
game.submit_guess(players[0], "1234")
game.submit_guess(players[1], generate_guess(code_length, num_of_colors))  # Random guess

# Check game state
print(game.state)
players[0].board.display_board()

# Check winners
if game.winners:
  for winner in game.winners:
    print(f"Winner: {winner.name}")
```

## Setting the secret code

- **Multiple ways to set secret codes:**
  - Via Game initialization: `Game(players, secret_code="1234")`
  - Per player: `player.set_secret_code_to_board("1234")`
  - Random generation: `game.set_random_secret_code()`

## Dependencies

- [httpx](https://github.com/encode/httpx)
