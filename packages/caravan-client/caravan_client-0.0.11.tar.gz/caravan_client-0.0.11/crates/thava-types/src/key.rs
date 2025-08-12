use derive_more::Display;
use passwords::PasswordGenerator;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Hash)]
pub struct SharingKey(String);

impl SharingKey {
    pub fn new() -> SharingKey {
        let generated_password = PasswordGenerator::new()
            .length(8)
            .numbers(true)
            .lowercase_letters(true)
            .uppercase_letters(true)
            .generate_one()
            .unwrap();

        SharingKey(generated_password)
    }
}

impl From<SharingKey> for String {
    fn from(key: SharingKey) -> String {
        key.0
    }
}

impl From<String> for SharingKey {
    fn from(key: String) -> SharingKey {
        SharingKey(key)
    }
}

impl Default for SharingKey {
    fn default() -> Self {
        Self::from("".to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_key() {
        let key = SharingKey::new();
        assert!(key.0.len() == 8);
    }
}
