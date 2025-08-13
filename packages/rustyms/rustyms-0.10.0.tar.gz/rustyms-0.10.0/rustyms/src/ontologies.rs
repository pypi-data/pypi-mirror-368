//! The available ontologies

use std::sync::LazyLock;

use bincode::config::Configuration;
use itertools::Itertools;

pub use crate::modification::OntologyModificationList;
use crate::{
    error::{Context, CustomError},
    modification::{Ontology, SimpleModification},
};

/// A database of custom modifications
pub type CustomDatabase = OntologyModificationList;

/// An empty list of modifications (needed for lifetime reasons)
static EMPTY_LIST: OntologyModificationList = Vec::new();

impl Ontology {
    /// Get the modifications lookup list for this ontology
    pub fn lookup(self, custom_database: Option<&CustomDatabase>) -> &OntologyModificationList {
        match self {
            Self::Gnome => &GNOME,
            Self::Psimod => &PSIMOD,
            Self::Unimod => &UNIMOD,
            Self::Resid => &RESID,
            Self::Xlmod => &XLMOD,
            Self::Custom => custom_database.map_or(&EMPTY_LIST, |c| c),
        }
    }

    /// Find the closest names in this ontology
    pub fn find_closest(self, code: &str, custom_database: Option<&CustomDatabase>) -> CustomError {
        CustomError::error(
            "Invalid modification",
            format!("The provided name does not exists in {}", self.name()),
            Context::show(code),
        )
        .with_suggestions(Self::similar_names(&[self], code, custom_database))
    }

    /// # Panics
    /// Asserts that the ontology list is not empty.
    pub fn find_closest_many(
        ontologies: &[Self],
        code: &str,
        custom_database: Option<&CustomDatabase>,
    ) -> CustomError {
        assert!(!ontologies.is_empty());
        let names = if ontologies.len() > 1 {
            let mut names = ontologies[..ontologies.len() - 1]
                .iter()
                .map(|o| o.name().to_string())
                .collect_vec();
            let last = names.len() - 1;
            names[last] = format!("{} or {}", names[last], ontologies.last().unwrap().name());
            names.join(", ")
        } else {
            ontologies[0].name().to_string()
        };
        CustomError::error(
            "Invalid modification",
            format!("The provided name does not exists in {names}"),
            Context::show(code),
        )
        .with_suggestions(Self::similar_names(ontologies, code, custom_database))
    }

    /// Get the closest similar names in the given ontologies. Finds both modifications and linkers
    pub fn similar_names(
        ontologies: &[Self],
        code: &str,
        custom_database: Option<&CustomDatabase>,
    ) -> Vec<String> {
        let mut resulting = Vec::new();
        for ontology in ontologies {
            let options: Vec<&str> = ontology
                .lookup(custom_database)
                .iter()
                .map(|option| option.1.as_str())
                .collect();
            resulting.extend(
                similar::get_close_matches(code, &options, 3, 0.7)
                    .iter()
                    .map(|o| format!("{}:{}", ontology.char(), o)),
            );
        }
        resulting
    }

    /// Find the given name in this ontology.
    pub fn find_name(
        self,
        code: &str,
        custom_database: Option<&CustomDatabase>,
    ) -> Option<SimpleModification> {
        let code = code.to_ascii_lowercase();
        for option in self.lookup(custom_database) {
            if option.1 == code {
                return Some(option.2.clone());
            }
        }
        None
    }

    /// Find the given id in this ontology
    pub fn find_id(
        self,
        id: usize,
        custom_database: Option<&CustomDatabase>,
    ) -> Option<SimpleModification> {
        for option in self.lookup(custom_database) {
            if option.0.is_some_and(|i| i == id) {
                return Some(option.2.clone());
            }
        }
        None
    }
}

/// Get the unimod ontology
/// # Panics
/// Panics when the modifications are not correctly provided at compile time, always report a panic if it occurs here.
static UNIMOD: LazyLock<OntologyModificationList> = LazyLock::new(|| {
    bincode::serde::decode_from_slice::<OntologyModificationList, Configuration>(
        include_bytes!("databases/unimod.dat"),
        Configuration::default(),
    )
    .unwrap()
    .0
});
/// Get the PSI-MOD ontology
/// # Panics
/// Panics when the modifications are not correctly provided at compile time, always report a panic if it occurs here.
static PSIMOD: LazyLock<OntologyModificationList> = LazyLock::new(|| {
    bincode::serde::decode_from_slice::<OntologyModificationList, Configuration>(
        include_bytes!("databases/psimod.dat"),
        Configuration::default(),
    )
    .unwrap()
    .0
});
/// Get the Gnome ontology
/// # Panics
/// Panics when the modifications are not correctly provided at compile time, always report a panic if it occurs here.
static GNOME: LazyLock<OntologyModificationList> = LazyLock::new(|| {
    bincode::serde::decode_from_slice::<OntologyModificationList, Configuration>(
        include_bytes!("databases/gnome.dat"),
        Configuration::default(),
    )
    .unwrap()
    .0
});
/// Get the Resid ontology
/// # Panics
/// Panics when the modifications are not correctly provided at compile time, always report a panic if it occurs here.
static RESID: LazyLock<OntologyModificationList> = LazyLock::new(|| {
    bincode::serde::decode_from_slice::<OntologyModificationList, Configuration>(
        include_bytes!("databases/resid.dat"),
        Configuration::default(),
    )
    .unwrap()
    .0
});
/// Get the Xlmod ontology
/// # Panics
/// Panics when the modifications are not correctly provided at compile time, always report a panic if it occurs here.
static XLMOD: LazyLock<OntologyModificationList> = LazyLock::new(|| {
    bincode::serde::decode_from_slice::<OntologyModificationList, Configuration>(
        include_bytes!("databases/xlmod.dat"),
        Configuration::default(),
    )
    .unwrap()
    .0
});
