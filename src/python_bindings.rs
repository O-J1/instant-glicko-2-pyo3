// use pyo3::exceptions::PyValueError;
// use pyo3::prelude::*;
// use pyo3::types::PyDateTime;
// use chrono::{DateTime, Utc};
// use std::time::{Duration, SystemTime, UNIX_EPOCH};

// use crate::{GlickoSettings, PublicRating, InternalRating};
// use crate::engine::{MatchResult, RatingEngine, PlayerHandle};

// /// Helper function to convert `DateTime<Utc>` to `SystemTime`.
// fn datetime_to_system_time(datetime: DateTime<Utc>) -> PyResult<SystemTime> {
//     let secs = datetime.timestamp();
//     let nanos = datetime.timestamp_subsec_nanos();
//     if secs < 0 {
//         return Err(PyErr::new::<PyValueError, _>("Datetime is before UNIX epoch"));
//     }
//     UNIX_EPOCH
//         .checked_add(Duration::new(secs as u64, nanos))
//         .ok_or_else(|| PyErr::new::<PyValueError, _>("Timestamp out of range"))
// }

// /// Python class for PublicRating.
// #[pyclass]
// #[derive(Clone, PartialEq, Debug)]
// pub struct PyPublicRating {
//     #[pyo3(get)]
//     rating: f64,
//     #[pyo3(get)]
//     deviation: f64,
//     #[pyo3(get)]
//     volatility: f64,
// }

// impl From<PublicRating> for PyPublicRating {
//     fn from(rating: PublicRating) -> Self {
//         PyPublicRating {
//             rating: rating.rating(),
//             deviation: rating.deviation(),
//             volatility: rating.volatility(),
//         }
//     }
// }

// /// Python class for InternalRating.
// #[pyclass]
// #[derive(Clone, PartialEq, Debug)]
// pub struct PyInternalRating {
//     #[pyo3(get)]
//     rating: f64,
//     #[pyo3(get)]
//     deviation: f64,
//     #[pyo3(get)]
//     volatility: f64,
// }

// impl From<InternalRating> for PyInternalRating {
//     fn from(rating: InternalRating) -> Self {
//         PyInternalRating {
//             rating: rating.rating(),
//             deviation: rating.deviation(),
//             volatility: rating.volatility(),
//         }
//     }
// }

// /// Python class for GlickoSettings.
// #[pyclass]
// #[derive(Clone, PartialEq, Debug)]
// pub struct PyGlickoSettings {
//     settings: GlickoSettings,
// }

// #[pymethods]
// impl PyGlickoSettings {
//     #[new]
//     fn new(
//         start_rating: (f64, f64, f64),
//         volatility_change: f64,
//         convergence_tolerance: f64,
//         rating_period_duration: u64,
//     ) -> PyResult<Self> {
//         if rating_period_duration == 0 {
//             return Err(PyErr::new::<PyValueError, _>("Rating period duration must be positive"));
//         }
//         if convergence_tolerance <= 0.0 {
//             return Err(PyErr::new::<PyValueError, _>("Convergence tolerance must be positive"));
//         }
//         let (rating, deviation, volatility) = start_rating;
//         if deviation <= 0.0 {
//             return Err(PyErr::new::<PyValueError, _>("Start rating deviation must be positive"));
//         }
//         if volatility <= 0.0 {
//             return Err(PyErr::new::<PyValueError, _>("Start rating volatility must be positive"));
//         }
//         let start_rating = PublicRating::new(rating, deviation, volatility);
//         Ok(PyGlickoSettings {
//             settings: GlickoSettings::new(
//                 start_rating,
//                 volatility_change,
//                 convergence_tolerance,
//                 Duration::from_secs(rating_period_duration),
//             ),
//         })
//     }

//     #[getter]
//     fn start_rating(&self) -> PyPublicRating {
//         self.settings.start_rating().into()
//     }

//     #[getter]
//     fn volatility_change(&self) -> f64 {
//         self.settings.volatility_change()
//     }

//     #[getter]
//     fn convergence_tolerance(&self) -> f64 {
//         self.settings.convergence_tolerance()
//     }

//     #[getter]
//     fn rating_period_duration(&self) -> u64 {
//         self.settings.rating_period_duration().as_secs()
//     }
// }

// /// Python class for RatingEngine.
// #[pyclass]
// #[derive(Clone, Debug)]
// pub struct PyRatingEngine {
//     engine: RatingEngine,
// }

// #[pymethods]
// impl PyRatingEngine {
//     #[new]
//     fn new(settings: PyGlickoSettings) -> Self {
//         PyRatingEngine {
//             engine: RatingEngine::start_new(settings.settings),
//         }
//     }

//     /// Register a new player at a specific timestamp.
//     fn register_player_at(
//         &mut self,
//         rating: (f64, f64, f64),
//         timestamp: DateTime<Utc>,
//     ) -> PyResult<usize> {
//         let (rating_val, deviation, volatility) = rating;
//         if deviation <= 0.0 {
//             return Err(PyErr::new::<PyValueError, _>("Deviation must be positive"));
//         }
//         if volatility <= 0.0 {
//             return Err(PyErr::new::<PyValueError, _>("Volatility must be positive"));
//         }
//         let public_rating = PublicRating::new(rating_val, deviation, volatility);
        
//         let start_time = datetime_to_system_time(timestamp)?;
        
//         let (handle, _) = self.engine.register_player_at(public_rating, start_time);
//         Ok(handle.0)
//     }

//     /// Register a match result at a specific timestamp.
//     fn register_result_at(
//         &mut self,
//         player1: usize,
//         player2: usize,
//         result: &str,
//         timestamp: DateTime<Utc>,
//     ) -> PyResult<()> {
//         let match_result = match result.to_lowercase().as_str() {
//             "win" => MatchResult::Win,
//             "loss" => MatchResult::Loss,
//             "draw" => MatchResult::Draw,
//             _ => return Err(PyErr::new::<PyValueError, _>("Invalid match result")),
//         };
    
//         let time = datetime_to_system_time(timestamp)?;
        
//         let num_players = self.engine.player_handles().count();
//         if player1 >= num_players {
//             return Err(PyErr::new::<PyValueError, _>("player1 handle is invalid"));
//         }
//         if player2 >= num_players {
//             return Err(PyErr::new::<PyValueError, _>("player2 handle is invalid"));
//         }
        
//         self.engine.register_result_at(PlayerHandle(player1), PlayerHandle(player2), &match_result, time);
//         Ok(())
//     }

//     /// Get the player's public rating.
//     fn get_player_rating(&mut self, player: usize) -> PyResult<PyPublicRating> {
//         let num_players = self.engine.player_handles().count();
//         if player >= num_players {
//             return Err(PyErr::new::<PyValueError, _>("player handle is invalid"));
//         }
//         let (rating, _) = self.engine.player_rating(PlayerHandle(player));
//         Ok(rating.into())
//     }

//     /// Get the player's internal rating.
//     fn get_player_internal_rating(&mut self, player: usize) -> PyResult<PyInternalRating> {
//         let num_players = self.engine.player_handles().count();
//         if player >= num_players {
//             return Err(PyErr::new::<PyValueError, _>("player handle is invalid"));
//         }
//         let (rating, _) = self.engine.player_rating(PlayerHandle(player));
//         Ok(rating.into())
//     }

//     /// Get the number of elapsed rating periods at a specific timestamp.
//     fn get_elapsed_periods_at(&self, timestamp: DateTime<Utc>) -> PyResult<f64> {
//         let time = datetime_to_system_time(timestamp)?;
//         Ok(self.engine.elapsed_periods_at(time))
//     }

//     /// Maybe close rating periods at a specific timestamp.
//     fn maybe_close_rating_periods_at(&mut self, timestamp: DateTime<Utc>) -> PyResult<(f64, u32)> {
//         let time = datetime_to_system_time(timestamp)?;
//         Ok(self.engine.maybe_close_rating_periods_at(time))
//     }

//     /// List all players with their public ratings.
//     fn list_players(&self) -> PyResult<Vec<(usize, PyPublicRating)>> {
//         let handles: Vec<PlayerHandle> = self.engine.player_handles().collect();
//         let mut players = Vec::with_capacity(handles.len());
//         for handle in handles {
//             let (rating, _) = self.engine.player_rating(handle);
//             players.push((handle.0, rating.into()));
//         }
//         Ok(players)
//     }
// }

// /// Python module implemented in Rust.
// #[pymodule]
// fn instant_glicko2(py: Python, m: &PyModule) -> PyResult<()> {
//     // Initialize the datetime API.
//     PyDateTime::init(py)?;
    
//     m.add("__doc__", "Instant Glicko-2 rating system bindings for Python")?;
    
//     // Classes
//     m.add_class::<PyPublicRating>()?;
//     m.add_class::<PyInternalRating>()?;
//     m.add_class::<PyGlickoSettings>()?;
//     m.add_class::<PyRatingEngine>()?;
    
//     Ok(())
// }

// src/python_bindings.rs

// src/python_bindings.rs

use pyo3::prelude::*;
use crate::engine::{RatingEngine, PlayerHandle, MatchResult};
use crate::{GlickoSettings, Rating, Public};
use std::time::Duration;

/// Initializes the Python module by adding all necessary classes.
pub fn instant_glicko2(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyRatingEngine>()?;
    m.add_class::<PyPlayerHandle>()?;
    m.add_class::<PyGlickoSettings>()?;
    m.add_class::<PyMatchResult>()?;
    m.add_class::<PyRating>()?;
    Ok(())
}

#[pyclass]
struct PyRatingEngine {
    engine: RatingEngine,
}

#[pymethods]
impl PyRatingEngine {
    #[new]
    fn new(settings: PyGlickoSettings) -> Self {
        PyRatingEngine {
            engine: RatingEngine::start_new(settings.settings),
        }
    }

    fn register_player(&mut self, rating: PyRating) -> (PyPlayerHandle, u32) {
        let (player_handle, closed_periods) = self.engine.register_player(rating.into());
        (PyPlayerHandle(player_handle), closed_periods)
    }

    fn register_result(
        &mut self,
        player1: PyPlayerHandle,
        player2: PyPlayerHandle,
        score: PyMatchResult,
    ) -> u32 {
        self.engine.register_result::<MatchResult>(player1.0, player2.0, &score.into())
    }

    fn player_rating(&mut self, player: PyPlayerHandle) -> (PyRating, u32) {
        let (rating, closed) = self.engine.player_rating::<Public>(player.0);
        (PyRating::from(rating), closed)
    }

    fn maybe_close_rating_periods(&mut self) -> (f64, u32) {
        self.engine.maybe_close_rating_periods()
    }

    fn elapsed_periods(&self) -> f64 {
        self.engine.elapsed_periods()
    }
}

#[pyclass]
#[derive(Clone, Copy)]
struct PyPlayerHandle(PlayerHandle);

#[pymethods]
impl PyPlayerHandle {
    #[getter]
    fn index(&self) -> usize {
        self.0 .0
    }
}

#[pyclass]
#[derive(Clone)]
struct PyGlickoSettings {
    settings: GlickoSettings,
}

#[pymethods]
impl PyGlickoSettings {
    #[new]
    fn new(
        start_rating: PyRating,
        volatility_change: f64,
        convergence_tolerance: f64,
        rating_period_duration: f64, // seconds
    ) -> Self {
        PyGlickoSettings {
            settings: GlickoSettings::new(
                start_rating.into(),
                volatility_change,
                convergence_tolerance,
                Duration::from_secs_f64(rating_period_duration),
            ),
        }
    }

    #[getter]
    fn start_rating(&self) -> PyRating {
        self.settings.start_rating.into()
    }

    #[getter]
    fn volatility_change(&self) -> f64 {
        self.settings.volatility_change
    }

    #[getter]
    fn convergence_tolerance(&self) -> f64 {
        self.settings.convergence_tolerance
    }

    #[getter]
    fn rating_period_duration(&self) -> f64 {
        self.settings.rating_period_duration.as_secs_f64()
    }
}

#[pyclass]
#[derive(Clone)]
struct PyMatchResult {
    result: MatchResult,
}

#[pymethods]
impl PyMatchResult {
    #[staticmethod]
    fn win() -> Self {
        PyMatchResult {
            result: MatchResult::Win,
        }
    }

    #[staticmethod]
    fn draw() -> Self {
        PyMatchResult {
            result: MatchResult::Draw,
        }
    }

    #[staticmethod]
    fn loss() -> Self {
        PyMatchResult {
            result: MatchResult::Loss,
        }
    }

    fn invert(&self) -> Self {
        PyMatchResult {
            result: self.result.invert(),
        }
    }
}

#[pyclass]
#[derive(Clone)]
struct PyRating {
    rating: Rating<Public>,
}

#[pymethods]
impl PyRating {
    #[new]
    fn new(rating: f64, deviation: f64, volatility: f64) -> Self {
        PyRating {
            rating: Rating::new(rating, deviation, volatility),
        }
    }

    #[getter]
    fn rating(&self) -> f64 {
        self.rating.rating()
    }

    #[getter]
    fn deviation(&self) -> f64 {
        self.rating.deviation()
    }

    #[getter]
    fn volatility(&self) -> f64 {
        self.rating.volatility()
    }
}

impl From<Rating<Public>> for PyRating {
    fn from(r: Rating<Public>) -> Self {
        PyRating { rating: r }
    }
}

impl From<PyRating> for Rating<Public> {
    fn from(r: PyRating) -> Self {
        r.rating
    }
}

impl From<PyMatchResult> for MatchResult {
    fn from(r: PyMatchResult) -> Self {
        r.result
    }
}
