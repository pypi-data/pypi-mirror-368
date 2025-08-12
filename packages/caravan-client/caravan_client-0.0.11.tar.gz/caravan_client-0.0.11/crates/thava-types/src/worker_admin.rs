use std::collections::HashSet;

use derive_more::{Deref, Display};
use serde::{Deserialize, Serialize};

use super::uid::Uid;

use super::stubs;

#[derive(
    Clone, Debug, Display, Default, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize,
)]
pub struct WorkerAdminId(pub Uid);

impl WorkerAdminId {
    pub fn new() -> WorkerAdminId {
        WorkerAdminId(Uid::new())
    }
}

impl From<i64> for WorkerAdminId {
    fn from(id: i64) -> WorkerAdminId {
        WorkerAdminId(Uid::from(id))
    }
}

impl From<WorkerAdminId> for i64 {
    fn from(id: WorkerAdminId) -> i64 {
        id.0.into()
    }
}

#[derive(Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Hash)]
pub struct WorkerGroupId(pub Uid);

impl From<i64> for WorkerGroupId {
    fn from(id: i64) -> WorkerGroupId {
        WorkerGroupId(Uid::from(id))
    }
}

impl From<WorkerGroupId> for i64 {
    fn from(id: WorkerGroupId) -> i64 {
        id.0.into()
    }
}

#[derive(Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Deref)]
pub struct Key(String);

impl Key {
    pub fn new(key: String) -> Key {
        Key(key)
    }
}

impl<'a> From<&'a Key> for &'a str {
    fn from(key: &'a Key) -> &'a str {
        &key.0
    }
}

impl From<&str> for Key {
    fn from(key: &str) -> Key {
        Key(String::from(key))
    }
}

impl From<Key> for String {
    fn from(key: Key) -> String {
        key.0
    }
}

impl From<String> for Key {
    fn from(key: String) -> Key {
        Key(key)
    }
}

#[derive(Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Deref)]
pub struct Group(String);

impl Group {
    pub fn new(group: String) -> Group {
        Group(group)
    }
}

impl<'a> From<&'a Group> for &'a str {
    fn from(group: &'a Group) -> &'a str {
        &group.0
    }
}

impl From<&str> for Group {
    fn from(group: &str) -> Group {
        Group(String::from(group))
    }
}

impl From<Group> for String {
    fn from(group: Group) -> String {
        group.0
    }
}

impl From<String> for Group {
    fn from(group: String) -> Group {
        Group(group)
    }
}

#[derive(Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Deref)]
pub struct Name(String);

impl Name {
    pub fn new(name: String) -> Name {
        Name(name)
    }
}

impl<'a> From<&'a Name> for &'a str {
    fn from(name: &'a Name) -> &'a str {
        &name.0
    }
}

impl From<&str> for Name {
    fn from(name: &str) -> Name {
        Name(String::from(name))
    }
}

impl From<Name> for String {
    fn from(name: Name) -> String {
        name.0
    }
}

impl From<String> for Name {
    fn from(name: String) -> Name {
        Name(name)
    }
}

#[derive(
    Clone, Debug, Display, Hash, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize, Deref,
)]
pub struct Email(pub String);

impl Email {
    pub fn new(email: String) -> Email {
        Email(email)
    }
}

impl<'a> From<&'a Email> for &'a str {
    fn from(email: &'a Email) -> &'a str {
        &email.0
    }
}

impl From<&str> for Email {
    fn from(email: &str) -> Email {
        Email(String::from(email))
    }
}

impl From<Email> for String {
    fn from(email: Email) -> String {
        email.0
    }
}

impl From<String> for Email {
    fn from(email: String) -> Email {
        Email(email)
    }
}

#[derive(Clone, Debug, Display, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub struct Password(String);

impl Password {
    pub fn new(password: String) -> Password {
        Password(password)
    }
}

impl<'a> From<&'a Password> for &'a str {
    fn from(password: &'a Password) -> &'a str {
        &password.0
    }
}

impl From<&str> for Password {
    fn from(password: &str) -> Password {
        Password(String::from(password))
    }
}

impl From<Password> for String {
    fn from(password: Password) -> String {
        password.0
    }
}

impl From<String> for Password {
    fn from(password: String) -> Password {
        Password(password)
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct WorkerAdmin {
    pub id: WorkerAdminId,
    pub name: Name,
    pub email: Email,
    pub password: Password,
    pub worker_groups: HashSet<WorkerGroupId>,
}

impl Default for WorkerAdmin {
    fn default() -> WorkerAdmin {
        WorkerAdmin {
            id: WorkerAdminId::new(),
            name: Name::new(String::from("")),
            email: Email::new(String::from("")),
            password: Password::new(String::from("")),
            worker_groups: HashSet::new(),
        }
    }
}

impl WorkerAdmin {
    pub fn new(name: Name, email: Email, password: Password) -> WorkerAdmin {
        WorkerAdmin {
            id: WorkerAdminId(Uid::new()),
            name,
            email,
            password,
            worker_groups: HashSet::new(),
        }
    }
}

impl From<stubs::worker_admin::WorkerAdmin> for WorkerAdmin {
    fn from(worker_admin: stubs::worker_admin::WorkerAdmin) -> WorkerAdmin {
        WorkerAdmin {
            id: WorkerAdminId(worker_admin.id.into()),
            name: Name::new(worker_admin.name),
            email: Email::new(worker_admin.email),
            password: Password::new(worker_admin.password),
            worker_groups: HashSet::new(),
        }
    }
}
