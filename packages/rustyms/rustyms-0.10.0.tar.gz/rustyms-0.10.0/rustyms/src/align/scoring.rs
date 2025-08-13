use serde::{Deserialize, Serialize};

use crate::{system::OrderedMass, AminoAcid, MassMode, Tolerance};

/// The type of a single match step
#[derive(
    Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Default, Serialize, Deserialize,
)]
pub enum MatchType {
    /// Aminoacid + Mass identity
    FullIdentity,
    /// Aminoacid + Mass mismatch
    IdentityMassMismatch,
    /// Full mismatch
    #[default]
    Mismatch,
    /// Set of aminoacids + mods with the same mass but different sequence
    Isobaric,
    /// Set of aminoacids + mods in a different order in the two sequences
    Rotation,
    /// A gap
    Gap,
}

/// The scoring parameters for the mass alignment.
///
/// Design parameters for the scoring systems are as follows:
/// * A positive `mass_base` is needed to ensure breaking up of adjecent isobaric/rotated parts.
///   For example `IGG` vs `LN` should be `1i2:1i` not `3:2i`.
/// * A higher score for `rotated` is needed to ensure rotation preference over `isobaric`.
/// * The `matrix` should be chosen to have higher scores than the rotated score to prevent spurious
///   rotations from being added.
#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug)]
pub struct AlignScoring<'a> {
    /// The score for a mismatch, this is used as the full score of that step.
    ///
    /// Default: -1.
    pub mismatch: i8,
    /// The score for a step if the amino acids are identical but the mass of the sequence elements
    /// are not the same. This is the case if either of the peptides has a modification at this
    /// location.
    ///
    /// Default: 2.
    pub mass_mismatch: i8,
    /// The base score for mass based steps, added to both rotated and isobaric steps.
    ///
    /// Default: 1.
    pub mass_base: i8,
    /// The per position score for a rotated step match. The full score is calculated as follows
    /// `mass_base + rotated * len_a`.
    ///
    /// Default: 3.
    pub rotated: i8,
    /// The per position score for an isobaric step match. The full score is calculated as follows
    /// `mass_base + isobaric * (len_a + len_b) / 2`.
    ///
    /// Default: 2.
    pub isobaric: i8,
    /// The gap start score for affine gaps, this is the score for starting any gap. The total score
    /// for a full gap will be `gap_start + gap_extend * len`.
    ///
    /// Default: -4.
    pub gap_start: i8,
    /// The gap extend for affine gaps.
    ///
    /// Default: -1.
    pub gap_extend: i8,
    /// The matrix to find the score for matching any amino acid to any other aminoacid. It is
    /// indexed by the amino acid.
    ///
    /// Default: BLOSUM62.
    pub matrix: &'a [[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER],
    /// The tolerance of mass equality.
    ///
    /// Default: 10ppm.
    pub tolerance: Tolerance<OrderedMass>,
    /// The mass mode for the alignment.
    ///
    /// Default: Monoisotopic.
    pub mass_mode: MassMode,
}

impl Default for AlignScoring<'static> {
    fn default() -> Self {
        Self {
            mismatch: -1,
            mass_mismatch: 2,
            mass_base: 1,
            rotated: 3,
            isobaric: 2,
            gap_start: -4,
            gap_extend: -1,
            matrix: matrices::BLOSUM62,
            tolerance: crate::Tolerance::new_ppm(10.0),
            mass_mode: MassMode::Monoisotopic,
        }
    }
}

/// Matrices from: <https://www.ncbi.nlm.nih.gov/IEB/ToolBox/CPP_DOC/lxr/source/src/util/tables/> and <https://www.ncbi.nlm.nih.gov/IEB/ToolBox/C_DOC/lxr/source/data/>.
/// The UO columns are added by me (see top left for the original matrix used by me) (B/J/Z is the rounded down average of the corresponding non ambiguous AAs) (All these are exactly the same for all matrices).
pub mod matrices {
    use crate::AminoAcid;
    /// BLOSUM45 matrix
    pub const BLOSUM45: &[[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER] =
        include!("matrices/blosum45.txt");
    /// BLOSUM50 matrix
    pub const BLOSUM50: &[[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER] =
        include!("matrices/blosum50.txt");
    /// BLOSUM62 matrix
    pub const BLOSUM62: &[[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER] =
        include!("matrices/blosum62.txt");
    /// BLOSUM80 matrix
    pub const BLOSUM80: &[[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER] =
        include!("matrices/blosum80.txt");
    /// BLOSUM90 matrix
    pub const BLOSUM90: &[[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER] =
        include!("matrices/blosum90.txt");
    /// Identity matrix (9 for equal, -5 for not equal)
    pub const IDENTITY: &[[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER] =
        include!("matrices/identity.txt");
    /// PAM30 matrix
    pub const PAM30: &[[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER] =
        include!("matrices/pam30.txt");
    /// PAM70 matrix
    pub const PAM70: &[[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER] =
        include!("matrices/pam70.txt");
    /// PAM250 matrix
    pub const PAM250: &[[i8; AminoAcid::TOTAL_NUMBER]; AminoAcid::TOTAL_NUMBER] =
        include!("matrices/pam250.txt");
}
