# tests/conftest.py

import pytest
from instant_glicko2 import (
    PyGlickoSettings,
    PyRating,
    PyRatingEngine,
    PyMatchResult,
    PyPlayerHandle
)

@pytest.fixture
def default_settings():
    """
    Fixture to create default GlickoSettings with a one-week rating period.
    """
    return PyGlickoSettings(
        start_rating=PyRating(rating=1500.0, deviation=200.0, volatility=0.06),
        volatility_change=0.5,
        convergence_tolerance=0.0001,
        rating_period_duration=604800.0  # 1 week in seconds
    )

@pytest.fixture
def short_period_settings():
    """
    Fixture to create GlickoSettings with a short rating period (1 second) for testing.
    """
    return PyGlickoSettings(
        start_rating=PyRating(rating=1500.0, deviation=200.0, volatility=0.06),
        volatility_change=0.5,
        convergence_tolerance=0.0001,
        rating_period_duration=1.0  # 1 second per rating period
    )

@pytest.fixture
def engine(default_settings):
    """
    Fixture to initialize the RatingEngine with default settings.
    """
    return PyRatingEngine(default_settings)

@pytest.fixture
def short_period_engine(short_period_settings):
    """
    Fixture to initialize the RatingEngine with short period settings for time-based tests.
    """
    return PyRatingEngine(short_period_settings)

@pytest.fixture
def register_two_players():
    """
    Fixture that returns a function to register two players to a given engine.
    """
    def _register(engine):
        player1, _ = engine.register_player(PyRating(rating=1500.0, deviation=300.0, volatility=0.06))
        player2, _ = engine.register_player(PyRating(rating=1500.0, deviation=300.0, volatility=0.06))
        return player1, player2
    return _register
