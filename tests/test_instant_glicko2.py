# tests/test_instant_glicko2.py

import pytest
from instant_glicko2 import (
    PyGlickoSettings,
    PyRating,
    PyRatingEngine,
    PyMatchResult,
    PyPlayerHandle,
)
import time


def test_player1_wins(engine, register_two_players):
    base_time = time.time()
    player1, player2 = register_two_players(engine, base_time)

    # Initial ratings
    py_rating1_initial, _ = engine.player_rating_at(player1, base_time)
    py_rating2_initial, _ = engine.player_rating_at(player2, base_time)

    # Player 1 wins against Player 2
    result = PyMatchResult.win()
    event_time = base_time + 1  # Simulate the match happening 1 second later
    engine.register_result_at(player1, player2, result, event_time)

    # Updated ratings
    py_rating1_updated, _ = engine.player_rating_at(player1, event_time)
    py_rating2_updated, _ = engine.player_rating_at(player2, event_time)

    # Assertions
    assert (
        py_rating1_updated.rating > py_rating1_initial.rating
    ), "Player 1's rating should increase after a win."
    assert (
        py_rating2_updated.rating < py_rating2_initial.rating
    ), "Player 2's rating should decrease after a loss."


def test_player2_wins(engine, register_two_players):
    base_time = time.time()
    player1, player2 = register_two_players(engine, base_time)

    # Initial ratings
    py_rating1_initial, _ = engine.player_rating_at(player1, base_time)
    py_rating2_initial, _ = engine.player_rating_at(player2, base_time)

    # Player 2 wins against Player 1
    result = PyMatchResult.win()
    event_time = base_time + 1
    engine.register_result_at(player2, player1, result, event_time)

    # Updated ratings
    py_rating1_updated, _ = engine.player_rating_at(player1, event_time)
    py_rating2_updated, _ = engine.player_rating_at(player2, event_time)

    # Assertions
    assert (
        py_rating2_updated.rating > py_rating2_initial.rating
    ), "Player 2's rating should increase after a win."
    assert (
        py_rating1_updated.rating < py_rating1_initial.rating
    ), "Player 1's rating should decrease after a loss."


def test_players_draw(engine, register_two_players):
    base_time = time.time()
    player1, player2 = register_two_players(engine, base_time)

    # Initial ratings
    py_rating1_initial, _ = engine.player_rating_at(player1, base_time)
    py_rating2_initial, _ = engine.player_rating_at(player2, base_time)

    # Draw
    result = PyMatchResult.draw()
    event_time = base_time + 1
    engine.register_result_at(player1, player2, result, event_time)

    # Updated ratings
    py_rating1_updated, _ = engine.player_rating_at(player1, event_time)
    py_rating2_updated, _ = engine.player_rating_at(player2, event_time)

    # Assertions
    assert py_rating1_updated.rating == pytest.approx(
        py_rating1_initial.rating, abs=1e-4
    ), "Player 1's rating should remain the same after a draw."
    assert py_rating2_updated.rating == pytest.approx(
        py_rating2_initial.rating, abs=1e-4
    ), "Player 2's rating should remain the same after a draw."


def test_player1_wins_multiple_games(engine, register_two_players):
    base_time = time.time()
    player1, player2 = register_two_players(engine, base_time)

    # Initial ratings
    py_rating1_initial, _ = engine.player_rating_at(player1, base_time)

    # Player 1 wins multiple games
    result = PyMatchResult.win()
    for i in range(5):
        event_time = base_time + i + 1
        engine.register_result_at(player1, player2, result, event_time)

    # Updated rating
    py_rating1_updated, _ = engine.player_rating_at(player1, event_time)

    # Assertions
    assert (
        py_rating1_updated.rating > py_rating1_initial.rating
    ), "Player 1's rating should increase after multiple wins."


def test_player2_wins_and_rd_decay(short_period_engine, register_two_players):
    engine = short_period_engine
    base_time = time.time()
    player1, player2 = register_two_players(engine, base_time)

    # Player 2 wins multiple games
    result = PyMatchResult.win()
    for i in range(15):
        event_time = base_time + i + 1
        engine.register_result_at(player2, player1, result, event_time)

    # Player 2's rating after wins
    py_rating2_after_wins, _ = engine.player_rating_at(player2, event_time)
    rd2_after_wins = py_rating2_after_wins.deviation

    # Simulate inactivity
    inactivity_period = 90  # Simulate 90 seconds of inactivity
    future_time = event_time + inactivity_period
    py_rating2_final, _ = engine.player_rating_at(player2, future_time)
    rd2_final = py_rating2_final.deviation

    # Assertions
    assert (
        rd2_final > rd2_after_wins
    ), "Player 2's RD should increase over time when not playing."


def test_players_with_different_initial_ratings_draw(engine):
    base_time = time.time()
    # Register players with different ratings
    player_high, _ = engine.register_player_at(
        PyRating(rating=1600.0, deviation=200.0, volatility=0.06), base_time
    )
    player_low, _ = engine.register_player_at(
        PyRating(rating=1400.0, deviation=200.0, volatility=0.06), base_time
    )

    # Draw
    result = PyMatchResult.draw()
    event_time = base_time + 1
    engine.register_result_at(player_high, player_low, result, event_time)

    # Updated ratings
    py_rating_high_updated, _ = engine.player_rating_at(player_high, event_time)
    py_rating_low_updated, _ = engine.player_rating_at(player_low, event_time)

    # Assertions
    assert (
        py_rating_high_updated.rating < 1600.0
    ), "Higher-rated player's rating should decrease slightly after a draw."
    assert (
        py_rating_low_updated.rating > 1400.0
    ), "Lower-rated player's rating should increase slightly after a draw."


def test_rd_increases_on_inactivity(short_period_engine, register_two_players):
    engine = short_period_engine
    base_time = time.time()
    player1, _ = register_two_players(engine, base_time)

    # Initial RD
    py_rating_initial, _ = engine.player_rating_at(player1, base_time)
    rd_initial = py_rating_initial.deviation

    # Simulate inactivity
    inactivity_period = 10  # Simulate 10 seconds of inactivity
    future_time = base_time + inactivity_period
    py_rating_final, _ = engine.player_rating_at(player1, future_time)
    rd_final = py_rating_final.deviation

    # Assertions
    assert rd_final > rd_initial, "Player 1's RD should increase due to inactivity."


def test_volatility_changes_with_inconsistent_performance(engine, register_two_players):
    base_time = time.time()
    player1, player2 = register_two_players(engine, base_time)

    # Initial volatility
    py_rating1_initial, _ = engine.player_rating_at(player1, base_time)
    initial_volatility1 = py_rating1_initial.volatility

    # Simulate inconsistent results
    results = [
        PyMatchResult.win(),
        PyMatchResult.loss(),
        PyMatchResult.draw(),
        PyMatchResult.win(),
        PyMatchResult.loss(),
    ]
    for i, result in enumerate(results):
        event_time = base_time + i + 1
        engine.register_result_at(player1, player2, result, event_time)

    # Updated volatility
    event_time = base_time + len(results) + 1
    py_rating1_updated, _ = engine.player_rating_at(player1, event_time)
    updated_volatility1 = py_rating1_updated.volatility

    # Print the volatility for debugging
    print(f"Initial volatility: {initial_volatility1}")
    print(f"Updated volatility: {updated_volatility1}")
    print(f"Difference: {updated_volatility1 - initial_volatility1}")

    # Assertions
    assert (
        updated_volatility1 != initial_volatility1
    ), "Player 1's volatility should change due to inconsistent performance."



def test_paper_example():
    """
    Test the example calculation in Glickman's paper.
    """
    from datetime import datetime, timezone

    # Set up Glicko-2 settings
    settings = PyGlickoSettings(
        start_rating=PyRating(rating=1500.0, deviation=350.0, volatility=0.06),
        volatility_change=0.5,  # τ (tau) parameter
        convergence_tolerance=0.000001,
        rating_period_duration=1.0,  # 1 second
    )
    engine = PyRatingEngine(settings)

    # Set the start time to UNIX_EPOCH (January 1, 1970)
    start_time = 0.0  # UNIX timestamp

    # Register players at the start time
    player, _ = engine.register_player_at(
        PyRating(rating=1500.0, deviation=200.0, volatility=0.06), start_time
    )
    opponent_a, _ = engine.register_player_at(
        PyRating(rating=1400.0, deviation=30.0, volatility=0.06), start_time
    )
    opponent_b, _ = engine.register_player_at(
        PyRating(rating=1550.0, deviation=100.0, volatility=0.06), start_time
    )
    opponent_c, _ = engine.register_player_at(
        PyRating(rating=1700.0, deviation=300.0, volatility=0.06), start_time
    )

    # Register match results at the start time
    engine.register_result_at(player, opponent_a, PyMatchResult.win(), start_time)
    engine.register_result_at(player, opponent_b, PyMatchResult.loss(), start_time)
    engine.register_result_at(player, opponent_c, PyMatchResult.loss(), start_time)

    # Calculate the player's new rating at the end of the rating period
    rating_period_end_time = start_time + 1.0  # 1 second later
    new_rating, _ = engine.player_rating_at(player, rating_period_end_time)

    # Assertions with tolerance
    assert abs(new_rating.rating - 1464.06) <= 0.05, f"Expected rating ~1464.06, got {new_rating.rating}"
    assert abs(new_rating.deviation - 151.52) <= 0.15, f"Expected deviation ~151.52, got {new_rating.deviation}"
    assert abs(new_rating.volatility - 0.05999) <= 0.0001, f"Expected volatility ~0.05999, got {new_rating.volatility}"


def test_rating_period_close():
    """
    Test that rating doesn't radically change across rating periods.
    """
    import time

    # Glicko-2 settings with a 1-second rating period
    settings = PyGlickoSettings(
        start_rating=PyRating(rating=1500.0, deviation=200.0, volatility=0.06),
        volatility_change=0.06,
        convergence_tolerance=0.0001,
        rating_period_duration=1.0,  # 1 second
    )
    engine = PyRatingEngine(settings)

    # Start time
    start_time = time.time()

    # Register players at start time
    player, _ = engine.register_player_at(settings.start_rating, start_time)
    opponent, _ = engine.register_player_at(
        PyRating(rating=1400.0, deviation=30.0, volatility=0.06), start_time
    )

    # Register a win for the player
    engine.register_result_at(player, opponent, PyMatchResult.win(), start_time)

    # Get ratings just before the rating period ends
    right_before = start_time + 0.999999  # Just before 1 second
    rating_right_before, _ = engine.player_rating_at(player, right_before)

    # Get ratings just after the rating period ends
    right_after = start_time + 1.000001  # Just after 1 second
    rating_right_after, _ = engine.player_rating_at(player, right_after)

    # Assertions
    assert (
        abs(rating_right_before.rating - rating_right_after.rating) <= 1e-6
    ), "Ratings should not change significantly across rating periods."
    assert (
        abs(rating_right_before.deviation - rating_right_after.deviation) <= 1e-6
    ), "Rating deviations should not change significantly across rating periods."
    assert (
        abs(rating_right_before.volatility - rating_right_after.volatility) <= 1e-6
    ), "Volatility should not change significantly across rating periods."


def test_time_change():
    """
    Test that rating deviation increases over time when the player is inactive.
    """
    import time

    # Glicko-2 settings with a 1-hour rating period
    settings = PyGlickoSettings(
        start_rating=PyRating(rating=1500.0, deviation=200.0, volatility=0.06),
        volatility_change=0.06,
        convergence_tolerance=0.0001,
        rating_period_duration=3600.0,  # 1 hour in seconds
    )
    engine = PyRatingEngine(settings)

    # Start time
    start_time = time.time()

    # Register player at start time
    player, _ = engine.register_player_at(settings.start_rating, start_time)

    # Get rating at start time
    rating_at_start, _ = engine.player_rating_at(player, start_time)

    # Simulate a year of inactivity
    year_in_seconds = 365 * 24 * 3600
    end_time = start_time + year_in_seconds

    # Get rating after a year
    rating_after_year, _ = engine.player_rating_at(player, end_time)

    # Assertions
    # Rating should remain the same
    assert (
        abs(rating_at_start.rating - rating_after_year.rating) <= 1e-6
    ), "Rating should not change due to inactivity."
    # Deviation should increase
    assert (
        rating_after_year.deviation > rating_at_start.deviation
    ), "Rating deviation should increase due to inactivity."
    # Volatility should remain the same
    assert (
        abs(rating_at_start.volatility - rating_after_year.volatility) <= 1e-6
    ), "Volatility should not change due to inactivity."
