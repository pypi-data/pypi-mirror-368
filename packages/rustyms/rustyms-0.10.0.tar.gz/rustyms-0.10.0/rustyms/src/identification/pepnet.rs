use crate::{
    error::CustomError,
    identification::{IdentifiedPeptide, IdentifiedPeptideSource, MetaData},
    ontologies::CustomDatabase,
    system::Ratio,
    Peptidoform, SemiAmbiguous, SloppyParsingParameters,
};

use serde::{Deserialize, Serialize};

use super::{
    common_parser::Location,
    csv::{parse_csv, CsvLine},
    BoxedIdentifiedPeptideIter,
};

static NUMBER_ERROR: (&str, &str) = (
    "Invalid PepNet line",
    "This column is not a number but it is required to be a number in this format",
);

format_family!(
    /// The format for any PepNet file
    PepNetFormat,
    /// The data from any PepNet file
    PepNetData,
    PepNetVersion, [&PEPNET_V1_0], b'\t', None;
    required {
        peptide: Peptidoform<SemiAmbiguous>, |location: Location, custom_database: Option<&CustomDatabase>| Peptidoform::sloppy_pro_forma(
            location.full_line(),
            location.location.clone(),
            custom_database,
            &SloppyParsingParameters::default(),
        );
        score: f64, |location: Location, _| location.parse::<f64>(NUMBER_ERROR);
        local_confidence: Vec<f64>, |location: Location, _| location
            .trim_start_matches("[").trim_end_matches("]")
            .array(',')
            .map(|l| l.parse::<f64>(NUMBER_ERROR))
            .collect::<Result<Vec<_>, _>>();
        ppm_diff: Ratio, |location: Location, _| location.parse::<f64>(NUMBER_ERROR).map(Ratio::new::<crate::system::ratio::ppm>);
    }
    optional { }
);

impl From<PepNetData> for IdentifiedPeptide {
    fn from(value: PepNetData) -> Self {
        Self {
            score: Some(value.score),
            local_confidence: Some(value.local_confidence.clone()),
            metadata: MetaData::PepNet(value),
        }
    }
}

/// The only known version of PepNet
pub const PEPNET_V1_0: PepNetFormat = PepNetFormat {
    version: PepNetVersion::V1_0,
    peptide: "denovo",
    score: "score",
    local_confidence: "positional score",
    ppm_diff: "ppm difference",
};

/// All possible PepNet versions
#[derive(Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Default, Serialize, Deserialize)]
pub enum PepNetVersion {
    #[default]
    /// PepNet version 1.0
    V1_0,
}

impl std::fmt::Display for PepNetVersion {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::result::Result<(), std::fmt::Error> {
        write!(
            f,
            "{}",
            match self {
                Self::V1_0 => "v1.0",
            }
        )
    }
}
