use serde::{Deserialize, Serialize};

use derive_more::{derive::Deref, Display};

use chrono::Utc;
use rand::Rng;

#[derive(
    Copy, Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Hash, Deref,
)]
pub struct Uid(i64);

impl Uid {
    /// Generates a new unique identifier as a 64-bit positive signed integer.
    /// For the first 32 bits, the first 12 digits are zero to be positive and
    /// avoid issues with Firestore's Number precision issues. The
    /// next digit is chosen at random from 1-9 (excluding zero) and the
    /// remaining bits are chosen at random.
    /// For the second 32 bits, the current timestamp is used.
    pub fn new() -> Uid {
        // First digit (1-9)
        let mut rng = rand::thread_rng();
        let first_digit: f64 = rng.gen();
        let first_digit = (first_digit * 9.0) as i64 + 1;
        let first_digit = (first_digit << 16) as i64; // first 8 bits are 0, then 4 bits for 1-8

        // 32 random bits
        let id_rand_half = rng.gen::<u32>();
        let id_rand_half = (id_rand_half & 0x000FFFFF) as i64; // last 28 bits
        let id_rand_half = (id_rand_half | first_digit) << 32; // attach first digit as MSB and move to front

        let id_time_half = Utc::now().timestamp() as u32;
        let id_time_half = id_time_half as i64;

        let id = id_rand_half | id_time_half; // combine both halves

        Uid(id)
    }
}

impl From<Uid> for i64 {
    fn from(uid: Uid) -> i64 {
        uid.0
    }
}

impl From<i64> for Uid {
    fn from(id: i64) -> Uid {
        Uid(id)
    }
}

impl Default for Uid {
    fn default() -> Self {
        Self::from(0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new() {
        let uid = Uid::new();
        assert!(uid.0 > 0);
    }

    #[test]
    fn test_positive() {
        for _ in 0..100 {
            let uid = Uid::new();
            assert!(uid.0 > 0);
        }
    }
}
