# instant-glicko2-pyo3

Quick Pyo3 bindings for the rust crate [instant-glicko2](https://github.com/gpluscb/instant-glicko-2). Instant-glicko2 is essentially a performant, rust implementation of Glicko-2 with a fix for the 'rating period' issue. It adds support for frational rating periods, so that ratings can be updated directly after every game. 

Note: Do not use this in production. It has not been extensively tested and there are 0 guarantees about its memory safety or other behaviour

## 📚 Table of Contents


## 🌟 Features

- Instant-Glicko2 python bindings, with attempts at being Pythonic
- From brief testing higher performance than python impls of Glicko2
- Courtesy of upstream library, fractional rating updates


🛠 Installation

Ensure you have Python 3.10 or later installed or configure the .Toml to use an AIB targeting your version.


```bash
git clone https://github.com/yourusername/instant-glicko2-pyo3.git
cd to repo
pip install maturin pyo3
maturin build
pip install .
```

🚀 Quick Start

Here's a simple example to get you started with instant-glicko2:

```python
from instant_glicko2 import PyGlickoSettings, PyRatingEngine, PyRating, PyMatchResult

# Initialize Glicko-2 settings
settings = PyGlickoSettings(
    start_rating=PyRating(rating=1500.0, deviation=200.0, volatility=0.06),
    volatility_change=0.5,
    convergence_tolerance=0.0001,
    rating_period_duration=604800.0  # 1 week in seconds
)

# Create a RatingEngine instance
engine = PyRatingEngine(settings)

# Register two players (e.g., images)
player1, _ = engine.register_player(PyRating(rating=1500.0, deviation=200.0, volatility=0.06))
player2, _ = engine.register_player(PyRating(rating=1500.0, deviation=200.0, volatility=0.06))

# Player 1 wins against Player 2
result = PyMatchResult.win()
engine.register_result(player1, player2, result)

# Retrieve updated ratings
rating1, _ = engine.player_rating(player1)
rating2, _ = engine.player_rating(player2)

print(f"Player 1 Rating: {rating1.rating}, RD: {rating1.deviation}")
print(f"Player 2 Rating: {rating2.rating}, RD: {rating2.deviation}")
```

Output:

```yaml

Player 1 Rating: 1516.083..., RD: 189.837...
Player 2 Rating: 1483.916..., RD: 189.837...
```

## 📝 API Reference


### 🏷️ PyGlickoSettings

#### Description:

Configuration settings for the Glicko-2 rating system.

#### Attributes:

- `start_rating` (`PyRating`): The initial rating, RD, and volatility for new players.
- `volatility_change` (`float`): The rate at which volatility changes over time.
- `convergence_tolerance` (`float`): The tolerance for the convergence of the volatility parameter.
- `rating_period_duration` (`float`): Duration of a rating period in seconds.

#### Example:

```python
from instant_glicko2 import PyGlickoSettings, PyRating

settings = PyGlickoSettings(
    start_rating=PyRating(rating=1500.0, deviation=200.0, volatility=0.06),
    volatility_change=0.5,
    convergence_tolerance=0.0001,
    rating_period_duration=604800.0  # 1 week in seconds
)
```

### ⚙️ PyRatingEngine

#### Description:
Core engine managing player ratings, match results, and rating periods.

#### Methods:

- `register_player(rating: PyRating) -> Tuple[PyPlayerHandle, int]`: Registers a new player with the given rating.
- `register_result(winner: PyPlayerHandle, loser: PyPlayerHandle, result: PyMatchResult) -> None`: Records the outcome of a match between two players.
- `player_rating(player: PyPlayerHandle) -> Tuple[PyRating, int]`: Retrieves the current rating and closed periods for a player.
- `maybe_close_rating_periods() -> None`: Advances the engine to close rating periods based on the configured duration.

#### Example:
```python

from instant_glicko2 import PyRatingEngine, PyGlickoSettings, PyRating

# Initialize settings
settings = PyGlickoSettings(...)
engine = PyRatingEngine(settings)

# Register players
player1, _ = engine.register_player(PyRating(...))
player2, _ = engine.register_player(PyRating(...))

# Register a match result
engine.register_result(player1, player2, PyMatchResult.win())

# Retrieve player ratings
rating1, closed1 = engine.player_rating(player1)
rating2, closed2 = engine.player_rating(player2)
```

### 🧑‍🤝‍🧑 PyPlayerHandle

#### Description:

A handle representing a registered player within the PyRatingEngine. Use this handle to reference players in match results and rating queries.

#### Attributes:

`index` (`int`): Unique identifier for the player within the engine.

#### Example:

```python
print(f"Player 1 ID: {player1.index}")
```

### 📊 PyRating

#### Description:
Represents a player's rating, including their skill rating, rating deviation (RD), and volatility.

#### Attributes:

- rating (float): The player's skill rating.
- deviation (float): The uncertainty in the player's rating.
- volatility (float): The degree of expected fluctuation in the player's rating.

#### Example:

```python
from instant_glicko2 import PyRating

initial_rating = PyRating(rating=1500.0, deviation=200.0, volatility=0.06)
print(initial_rating)
```

#### Output:

```python
PyRating(rating=1500.0, deviation=200.0, volatility=0.06)
```

### 🏁 PyMatchResult

### Description:
Represents the outcome of a match between two players. It can be a win, loss, or draw.

#### Class Methods:

    PyMatchResult.win() -> PyMatchResult: Creates a match result indicating a win for the first player.
    PyMatchResult.draw() -> PyMatchResult: Creates a match result indicating a draw between players.

#### Example:

```python

from instant_glicko2 import PyMatchResult

# Player 1 wins
win_result = PyMatchResult.win()

# Players draw
draw_result = PyMatchResult.draw()
```

## License 
This project is licensed under the MIT License. See the LICENSE file for details.

#python #glicko2 #rating #django #webapp #gaming #image-ranking #pyO3 #documentation


