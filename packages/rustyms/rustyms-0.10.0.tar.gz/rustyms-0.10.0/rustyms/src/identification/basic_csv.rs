use std::path::{Path, PathBuf};

use crate::{
    error::CustomError, ontologies::CustomDatabase, system::usize::Charge, CompoundPeptidoformIon,
};
use serde::{Deserialize, Serialize};

use super::{
    common_parser::{Location, OptionalColumn},
    csv::{parse_csv, CsvLine},
    BoxedIdentifiedPeptideIter, IdentifiedPeptide, IdentifiedPeptideSource, MetaData,
};

static NUMBER_ERROR: (&str, &str) = (
    "Invalid CSV line",
    "This column is not a number but it is required to be a number in this format",
);

format_family!(
    /// The format for any basic CSV file
    BasicCSVFormat,
    /// The data from any basic CSV file
    BasicCSVData,
    BasicCSVVersion, [&BASIC], b',', None;
    required {
        scan_index: usize, |location: Location, _| location.parse::<usize>(NUMBER_ERROR);
        sequence: CompoundPeptidoformIon, |location: Location, custom_database: Option<&CustomDatabase>|location.parse_with(|location| CompoundPeptidoformIon::pro_forma(
            location.as_str(),
            custom_database,
        ));
        raw_file: PathBuf, |location: Location, _| Ok(Path::new(&location.get_string()).to_owned());
        z: Charge, |location: Location, _| location.parse::<usize>(NUMBER_ERROR).map(Charge::new::<crate::system::e>);
    }
    optional {
        mode: String, |location: Location, _| Ok(location.get_string());
    }
);

impl From<BasicCSVData> for IdentifiedPeptide {
    fn from(value: BasicCSVData) -> Self {
        Self {
            score: None,
            local_confidence: None,
            metadata: MetaData::BasicCSV(value),
        }
    }
}

/// All possible basic CSV versions
#[derive(Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Default, Serialize, Deserialize)]
pub enum BasicCSVVersion {
    /// msms.txt
    #[default]
    Basic,
}

impl std::fmt::Display for BasicCSVVersion {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::result::Result<(), std::fmt::Error> {
        write!(
            f,
            "{}",
            match self {
                Self::Basic => "Basic",
            }
        )
    }
}

/// msms.txt
pub const BASIC: BasicCSVFormat = BasicCSVFormat {
    version: BasicCSVVersion::Basic,
    scan_index: "scan_index",
    sequence: "sequence",
    raw_file: "raw_file",
    z: "z",
    mode: OptionalColumn::Optional("mode"),
};
