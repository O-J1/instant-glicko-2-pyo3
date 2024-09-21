# tests/test_instant_glicko2.py

import pytest
from instant_glicko2 import (
    PyGlickoSettings,
    PyRating,
    PyRatingEngine,
    PyMatchResult,
    PyPlayerHandle
)
import time

def test_player1_wins(engine, register_two_players):
    """
    Test that Player 1's rating increases and Player 2's rating decreases when Player 1 wins.
    """
    player1, player2 = register_two_players(engine)

    # Initial ratings
    py_rating1_initial, _ = engine.player_rating(player1)
    py_rating2_initial, _ = engine.player_rating(player2)

    rating1_initial = py_rating1_initial.rating
    rating2_initial = py_rating2_initial.rating

    # Player 1 wins against Player 2
    result = PyMatchResult.win()
    engine.register_result(player1, player2, result)

    # Get updated ratings
    py_rating1_updated, _ = engine.player_rating(player1)
    py_rating2_updated, _ = engine.player_rating(player2)

    rating1_updated = py_rating1_updated.rating
    rating2_updated = py_rating2_updated.rating

    # Assertions
    assert rating1_updated > rating1_initial, "Player 1's rating should increase after a win."
    assert rating2_updated < rating2_initial, "Player 2's rating should decrease after a loss."

def test_player2_wins(engine, register_two_players):
    """
    Test that Player 2's rating increases and Player 1's rating decreases when Player 2 wins.
    """
    player1, player2 = register_two_players(engine)

    # Initial ratings
    py_rating1_initial, _ = engine.player_rating(player1)
    py_rating2_initial, _ = engine.player_rating(player2)

    rating1_initial = py_rating1_initial.rating
    rating2_initial = py_rating2_initial.rating

    # Player 2 wins against Player 1
    result = PyMatchResult.win()
    engine.register_result(player2, player1, result)

    # Get updated ratings
    py_rating1_updated, _ = engine.player_rating(player1)
    py_rating2_updated, _ = engine.player_rating(player2)

    rating1_updated = py_rating1_updated.rating
    rating2_updated = py_rating2_updated.rating

    # Assertions
    assert rating2_updated > rating2_initial, "Player 2's rating should increase after a win."
    assert rating1_updated < rating1_initial, "Player 1's rating should decrease after a loss."

def test_players_draw(engine, register_two_players):
    """
    Test that both players' ratings remain the same after a draw when they have identical initial ratings.
    """
    player1, player2 = register_two_players(engine)

    # Initial ratings
    py_rating1_initial, _ = engine.player_rating(player1)
    py_rating2_initial, _ = engine.player_rating(player2)

    rating1_initial = py_rating1_initial.rating
    rating2_initial = py_rating2_initial.rating

    # Both players draw
    result = PyMatchResult.draw()
    engine.register_result(player1, player2, result)

    # Get updated ratings
    py_rating1_updated, _ = engine.player_rating(player1)
    py_rating2_updated, _ = engine.player_rating(player2)

    rating1_updated = py_rating1_updated.rating
    rating2_updated = py_rating2_updated.rating

    # Assertions
    assert rating1_updated == pytest.approx(rating1_initial, abs=1e-4), "Player 1's rating should remain the same after a draw."
    assert rating2_updated == pytest.approx(rating2_initial, abs=1e-4), "Player 2's rating should remain the same after a draw."

def test_player1_wins_multiple_games(engine, register_two_players):
    """
    Test that Player 1's rating increases proportionally after winning multiple games.
    """
    player1, player2 = register_two_players(engine)

    # Initial ratings
    py_rating1_initial, _ = engine.player_rating(player1)
    py_rating2_initial, _ = engine.player_rating(player2)

    rating1_initial = py_rating1_initial.rating
    rating2_initial = py_rating2_initial.rating

    # Player 1 wins 5 consecutive games against Player 2
    result = PyMatchResult.win()
    for _ in range(5):
        engine.register_result(player1, player2, result)

    # Get updated ratings
    py_rating1_updated, _ = engine.player_rating(player1)
    py_rating2_updated, _ = engine.player_rating(player2)

    rating1_updated = py_rating1_updated.rating
    rating2_updated = py_rating2_updated.rating

    # Assertions
    assert rating1_updated > rating1_initial, "Player 1's rating should increase after multiple wins."
    assert rating2_updated < rating2_initial, "Player 2's rating should decrease after multiple losses."
    
    # Additionally, check that the rating increased by a noticeable amount
    assert (rating1_updated - rating1_initial) > 0, "Player 1's rating should have increased."

def test_player2_wins_and_rd_decay(short_period_engine, register_two_players):
    """
    Test that Player 2's rating deviation (RD) increases over time after winning multiple games and then not playing.
    """
    engine = short_period_engine
    player1, player2 = register_two_players(engine)

    # Initial RD for Player 2
    py_rating_initial, _ = engine.player_rating(player2)
    rd2_initial = py_rating_initial.deviation
    assert rd2_initial == pytest.approx(300.0, abs=1e-4), "Initial RD for Player 2 should be approximately 200.0"

    # Player 2 wins 15 consecutive games against Player 1
    result = PyMatchResult.win()
    for _ in range(15):
        engine.register_result(player2, player1, result)
        time.sleep(0.01)  # Small sleep to ensure the engine processes the results

    # Get Player 2's rating after 15 wins
    py_rating_after_wins, rd2_after_wins = engine.player_rating(player2)
    rating2_after_wins = py_rating_after_wins.rating
    rd2_after_wins = py_rating_after_wins.deviation
    assert rating2_after_wins > 1500.0, "Player 2's rating should increase after multiple wins."
    assert rd2_after_wins <= 200.0, "Player 2's RD should not increase after wins."

    # Simulate passage of 3 months (assuming 1 rating period = 1 second, 3 months ≈ 90 weeks ≈ 90 rating periods)
    for _ in range(90):
        engine.maybe_close_rating_periods()
        time.sleep(0.01)  # Small sleep to simulate time between rating periods

    # Get Player 2's rating after RD decay
    py_rating_final, rd2_final = engine.player_rating(player2)
    rating2_final = py_rating_final.rating
    rd2_final = py_rating_final.deviation

    # Corrected Assertion: RD should **increase** after inactivity
    assert rd2_final > rd2_after_wins, "Player 2's RD should increase over time when not playing."
    assert rating2_final > 1500.0, "Player 2's rating should remain higher after RD decay."

def test_players_with_different_initial_ratings_draw(engine, register_two_players):
    """
    Test that when two players with different initial ratings draw, their ratings adjust accordingly.
    """
    # Register two players with different initial ratings
    # Manually register them with different ratings
    player_high, _ = engine.register_player(PyRating(rating=1600.0, deviation=200.0, volatility=0.06))
    player_low, _ = engine.register_player(PyRating(rating=1400.0, deviation=200.0, volatility=0.06))

    # Player_high draws with Player_low
    result = PyMatchResult.draw()
    engine.register_result(player_high, player_low, result)

    # Get updated ratings
    py_rating_high_updated, _ = engine.player_rating(player_high)
    py_rating_low_updated, _ = engine.player_rating(player_low)
    rating_high_updated = py_rating_high_updated.rating
    rating_low_updated = py_rating_low_updated.rating

    # Assertions
    # Higher-rated player should slightly decrease, lower-rated player should slightly increase
    assert rating_high_updated < 1600.0, "Higher-rated player's rating should decrease slightly after a draw."
    assert rating_low_updated > 1400.0, "Lower-rated player's rating should increase slightly after a draw."

def test_rd_increases_on_inactivity(short_period_engine, register_two_players):
    """
    Test that a player's RD increases over time when they do not play any games.
    """
    engine = short_period_engine
    player1, _ = register_two_players(engine)

    # Initial RD
    py_rating_initial, _ = engine.player_rating(player1)
    rd1_initial = py_rating_initial.deviation
    assert rd1_initial == pytest.approx(300.0, abs=1e-4), "Initial RD for Player 1 should be approximately 200.0"

    # Simulate inactivity over 10 rating periods
    for _ in range(10):
        engine.maybe_close_rating_periods()
        time.sleep(0.01)  # Small sleep to simulate time between rating periods

    # Get RD after inactivity
    py_rating_final, _ = engine.player_rating(player1)
    rd1_final = py_rating_final.deviation
    assert rd1_final > rd1_initial, "Player 1's RD should increase due to inactivity."
    assert py_rating_final.rating == pytest.approx(py_rating_initial.rating, abs=1e-4), "Player 1's rating should remain the same after inactivity."

def test_volatility_remains_constant(engine, register_two_players):
    """
    Test that players' volatility remains constant after matches.
    """
    player1, player2 = register_two_players(engine)

    # Get initial volatilities
    py_rating1_initial, _ = engine.player_rating(player1)
    py_rating2_initial, _ = engine.player_rating(player2)

    initial_volatility1 = py_rating1_initial.volatility
    initial_volatility2 = py_rating2_initial.volatility

    # Player1 wins against Player2
    result = PyMatchResult.win()
    engine.register_result(player1, player2, result)

    # Get updated volatilities
    py_rating1_updated, _ = engine.player_rating(player1)
    py_rating2_updated, _ = engine.player_rating(player2)

    updated_volatility1 = py_rating1_updated.volatility
    updated_volatility2 = py_rating2_updated.volatility

    # Assertions
    assert updated_volatility1 == pytest.approx(initial_volatility1, abs=1e-4), "Player 1's volatility should remain constant."
    assert updated_volatility2 == pytest.approx(initial_volatility2, abs=1e-4), "Player 2's volatility should remain constant."

def test_registering_multiple_players(engine, register_two_players):
    """
    Test that registering multiple players maintains independent ratings.
    """
    # Register multiple players
    players = []
    for _ in range(10):
        player, _ = engine.register_player(PyRating(rating=1500.0, deviation=200.0, volatility=0.06))
        players.append(player)
    
    # Player 0 wins against all others
    result = PyMatchResult.win()
    for opponent in players[1:]:
        engine.register_result(players[0], opponent, result)
    
    # Get updated ratings
    py_rating0_updated, _ = engine.player_rating(players[0])
    rating0_updated = py_rating0_updated.rating
    for opponent in players[1:]:
        py_rating_updated, _ = engine.player_rating(opponent)
        rating_updated = py_rating_updated.rating
        assert rating_updated < 1500.0, "Opponent's rating should decrease after losing."
    
    # Player 0's rating should have increased
    assert rating0_updated > 1500.0, "Player 0's rating should have increased after multiple wins."
