//! Handle fragment related issues, access provided if you want to dive deeply into fragments in your own code.

use std::{
    borrow::Cow,
    cmp::Ordering,
    fmt::{Debug, Display, Write},
    sync::LazyLock,
};

use itertools::Itertools;
use ordered_float::OrderedFloat;
use serde::{Deserialize, Serialize};

#[cfg(feature = "glycan-render")]
use crate::glycan::GlycanSelection;
use crate::{
    glycan::{GlycanBranchIndex, GlycanBranchMassIndex, MonoSaccharide},
    model::{ChargeRange, PossiblePrimaryIons},
    molecular_charge::{CachedCharge, MolecularCharge},
    system::{
        f64::{MassOverCharge, Ratio},
        usize::Charge,
        OrderedMassOverCharge,
    },
    AmbiguousLabel, AminoAcid, Chemical, IsAminoAcid, MassMode, Modification, MolecularFormula,
    Multi, MultiChemical, NeutralLoss, SemiAmbiguous, SequenceElement, SequencePosition, Tolerance,
};

/// A theoretical fragment
#[derive(Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Debug, Serialize, Deserialize, Default)]
pub struct Fragment {
    /// The theoretical composition
    pub formula: Option<MolecularFormula>,
    /// The charge
    pub charge: Charge,
    /// The annotation for this fragment
    pub ion: FragmentType,
    /// The peptidoform this fragment comes from, saved as the index into the list of peptidoform in the overarching [`crate::CompoundPeptidoformIon`] struct
    pub peptidoform_ion_index: Option<usize>,
    /// The peptide this fragment comes from, saved as the index into the list of peptides in the overarching [`crate::PeptidoformIon`] struct
    pub peptidoform_index: Option<usize>,
    /// Any neutral losses applied
    pub neutral_loss: Vec<NeutralLoss>,
    /// m/z deviation, if known (from mzPAF)
    pub deviation: Option<Tolerance<OrderedMassOverCharge>>,
    /// Confidence in this annotation (from mzPAF)
    pub confidence: Option<OrderedFloat<f64>>,
    /// If this is an auxiliary fragment (from mzPAF)
    pub auxiliary: bool,
}

impl Fragment {
    /// Write the fragment as an mzPAF string
    #[allow(non_snake_case)]
    pub fn to_mzPAF(&self) -> String {
        let mut output = String::new();
        if self.auxiliary {
            output.push('&');
        }
        // Push the ion type info (plus maybe some neutral losses if needed)
        match &self.ion {
            FragmentType::a(pos, variant)
            | FragmentType::b(pos, variant)
            | FragmentType::c(pos, variant)
            | FragmentType::x(pos, variant)
            | FragmentType::y(pos, variant) => write!(
                &mut output,
                "{}{}{}",
                self.ion.kind(),
                pos.series_number,
                if *variant == 0 {
                    String::new()
                } else {
                    format!("{variant:+}H")
                }
            )
            .unwrap(),
            FragmentType::z(pos, variant) => write!(
                &mut output,
                "{}{}{}",
                self.ion.kind(),
                pos.series_number,
                if *variant == 1 {
                    String::new()
                } else {
                    format!("{:+}H", variant - 1)
                }
            )
            .unwrap(),
            FragmentType::d(pos, aa, distance, variant, label) => {
                if *distance == 0 {
                    write!(
                        &mut output,
                        "d{label}{}{}",
                        pos.series_number,
                        if *variant == 0 {
                            String::new()
                        } else {
                            format!("{variant:+}H")
                        }
                    )
                    .unwrap();
                } else if let Some(loss) = aa
                    .satellite_ion_fragments(
                        pos.sequence_index,
                        self.peptidoform_index.unwrap_or_default(),
                    )
                    .and_then(|fragments| {
                        fragments
                            .iter()
                            .find(|f| f.0 == *label)
                            .map(|(_, loss)| loss.clone())
                    })
                {
                    write!(
                        &mut output,
                        "a{}-{loss}{}",
                        pos.series_number,
                        if *variant == 0 {
                            String::new()
                        } else {
                            format!("{variant:+}H")
                        }
                    )
                    .unwrap();
                } else {
                    write!(&mut output, "?",).unwrap();
                }
            }
            FragmentType::v(pos, aa, distance, variant) => {
                if *distance == 0 {
                    write!(
                        &mut output,
                        "v{}{}",
                        pos.series_number,
                        if *variant == 0 {
                            String::new()
                        } else {
                            format!("{variant:+}H")
                        }
                    )
                    .unwrap();
                } else {
                    write!(
                        &mut output,
                        "y{}-{}{}",
                        pos.series_number,
                        aa.formulas()
                            .first()
                            .map(|f| f - LazyLock::force(&crate::aminoacid::BACKBONE))
                            .unwrap_or_default(),
                        if *variant == 0 {
                            String::new()
                        } else {
                            format!("{variant:+}H")
                        }
                    )
                    .unwrap();
                }
            }
            FragmentType::w(pos, aa, distance, variant, label) => {
                if *distance == 0 {
                    write!(
                        &mut output,
                        "w{label}{}{}",
                        pos.series_number,
                        if *variant == 0 {
                            String::new()
                        } else {
                            format!("{variant:+}H")
                        }
                    )
                    .unwrap();
                } else if let Some(loss) = aa
                    .satellite_ion_fragments(
                        pos.sequence_index,
                        self.peptidoform_index.unwrap_or_default(),
                    )
                    .and_then(|fragments| {
                        fragments
                            .iter()
                            .find(|f| f.0 == *label)
                            .map(|(_, loss)| loss.clone())
                    })
                {
                    write!(
                        &mut output,
                        "z{}-{loss}{}",
                        pos.series_number,
                        if *variant == 0 {
                            String::new()
                        } else {
                            format!("{variant:+}H")
                        }
                    )
                    .unwrap();
                } else {
                    write!(&mut output, "?",).unwrap();
                }
            }
            FragmentType::Precursor => write!(&mut output, "p").unwrap(),
            FragmentType::PrecursorSideChainLoss(_, aa) => {
                write!(&mut output, "p-r[sidechain_{aa}]").unwrap();
            }
            FragmentType::Immonium(_, seq) => write!(
                &mut output,
                "I{}{}",
                seq.aminoacid,
                seq.modifications.iter().map(|m| format!("[{m}]")).join("") // TODO: how to handle ambiguous mods? maybe store somewhere which where applied for this fragment
            )
            .unwrap(),
            FragmentType::Unknown(num) => write!(
                &mut output,
                "?{}",
                num.map_or(String::new(), |u| u.to_string())
            )
            .unwrap(),
            FragmentType::Diagnostic(_)
            | FragmentType::B { .. }
            | FragmentType::BComposition(_, _)
            | FragmentType::Y(_)
            | FragmentType::YComposition(_, _) => {
                if let Some(formula) = &self.formula {
                    // TODO: better way of storing?
                    write!(&mut output, "f{{{formula}}}",).unwrap();
                } else {
                    write!(&mut output, "?",).unwrap();
                }
            }
            FragmentType::Internal(Some(name), a, b) => write!(
                &mut output,
                "m{}:{}{}",
                a.sequence_index + 1,
                b.sequence_index + 1,
                match name {
                    (BackboneNFragment::a, BackboneCFragment::x)
                    | (BackboneNFragment::b, BackboneCFragment::y)
                    | (BackboneNFragment::c, BackboneCFragment::z) => "",
                    (BackboneNFragment::a, BackboneCFragment::y) => "-CO",
                    (BackboneNFragment::a, BackboneCFragment::z) => "-CHNO",
                    (BackboneNFragment::b, BackboneCFragment::x) => "+CO",
                    (BackboneNFragment::b, BackboneCFragment::z) => "-NH",
                    (BackboneNFragment::c, BackboneCFragment::x) => "+CHNO",
                    (BackboneNFragment::c, BackboneCFragment::y) => "+NH",
                }
            )
            .unwrap(),
            FragmentType::Internal(None, a, b) => write!(
                &mut output,
                "m{}:{}",
                a.sequence_index + 1,
                b.sequence_index + 1
            )
            .unwrap(),
        }
        // More losses
        for loss in &self.neutral_loss {
            match loss {
                NeutralLoss::SideChainLoss(_, aa) => {
                    write!(&mut output, "-r[sidechain_{aa}]").unwrap();
                }
                l => write!(&mut output, "{l}").unwrap(),
            }
        }
        // Isotopes: not handled
        // Charge state
        if self.charge.value != 1 {
            write!(&mut output, "^{}", self.charge.value).unwrap();
        }
        // Deviation
        match self.deviation {
            Some(Tolerance::Absolute(abs)) => write!(&mut output, "/{}", abs.value).unwrap(),
            Some(Tolerance::Relative(ppm)) => write!(&mut output, "/{}ppm", ppm.value).unwrap(),
            None => (),
        }
        // Confidence
        if let Some(confidence) = self.confidence {
            write!(&mut output, "*{confidence}").unwrap();
        }
        output
    }

    /// Get the mz
    pub fn mz(&self, mode: MassMode) -> Option<MassOverCharge> {
        self.formula.as_ref().map(|f| {
            f.mass(mode)
                / crate::system::f64::Charge::new::<crate::system::charge::e>(
                    self.charge.value as f64,
                )
        })
    }

    /// Get the ppm difference between two fragments
    pub fn ppm(&self, other: &Self, mode: MassMode) -> Option<Ratio> {
        self.mz(mode)
            .and_then(|mz| other.mz(mode).map(|omz| (mz, omz)))
            .map(|(mz, omz)| mz.ppm(omz))
    }

    /// Create a new fragment
    #[must_use]
    pub fn new(
        theoretical_mass: MolecularFormula,
        charge: Charge,
        peptidoform_ion_index: usize,
        peptidoform_index: usize,
        ion: FragmentType,
    ) -> Self {
        Self {
            formula: Some(theoretical_mass),
            charge,
            ion,
            peptidoform_ion_index: Some(peptidoform_ion_index),
            peptidoform_index: Some(peptidoform_index),
            neutral_loss: Vec::new(),
            deviation: None,
            confidence: None,
            auxiliary: false,
        }
    }

    /// Generate a list of possible fragments from the list of possible preceding termini and neutral losses
    /// # Panics
    /// When the charge range results in a negative charge
    #[expect(clippy::too_many_arguments)]
    #[must_use]
    pub fn generate_all(
        theoretical_mass: &Multi<MolecularFormula>,
        peptidoform_ion_index: usize,
        peptidoform_index: usize,
        annotation: &FragmentType,
        termini: &Multi<MolecularFormula>,
        neutral_losses: &[Vec<NeutralLoss>],
        charge_carriers: &mut CachedCharge,
        charge_range: ChargeRange,
    ) -> Vec<Self> {
        termini
            .iter()
            .cartesian_product(theoretical_mass.iter())
            .cartesian_product(charge_carriers.range(charge_range))
            .cartesian_product(std::iter::once(None).chain(neutral_losses.iter().map(Some)))
            .map(|(((term, mass), charge), losses)| Self {
                formula: Some(
                    term + mass
                        + charge.formula_inner(SequencePosition::default(), peptidoform_index)
                        + losses
                            .iter()
                            .flat_map(|l| l.iter())
                            .sum::<MolecularFormula>(),
                ),
                charge: Charge::new::<crate::system::e>(charge.charge().value.try_into().unwrap()),
                ion: annotation.clone(),
                peptidoform_ion_index: Some(peptidoform_ion_index),
                peptidoform_index: Some(peptidoform_index),
                neutral_loss: losses.cloned().unwrap_or_default(),
                deviation: None,
                confidence: None,
                auxiliary: false,
            })
            .collect()
    }
    /// Generate a list of possible fragments from the list of possible preceding termini and neutral losses
    /// # Panics
    /// When the charge range results in a negative charge
    #[must_use]
    pub fn generate_series(
        theoretical_mass: &Multi<MolecularFormula>,
        peptidoform_ion_index: usize,
        peptidoform_index: usize,
        annotation: &FragmentType,
        termini: &Multi<MolecularFormula>,
        charge_carriers: &mut CachedCharge,
        settings: &PossiblePrimaryIons,
    ) -> Vec<Self> {
        termini
            .iter()
            .cartesian_product(theoretical_mass.iter())
            .cartesian_product(charge_carriers.range(settings.1))
            .cartesian_product(std::iter::once(None).chain(settings.0.iter().map(Some)))
            .cartesian_product(settings.2.iter())
            .map(|((((term, mass), charge), losses), variant)| Self {
                formula: Some(
                    term + mass
                        + charge.formula_inner(SequencePosition::default(), peptidoform_index)
                        + losses
                            .iter()
                            .flat_map(|l| l.iter())
                            .sum::<MolecularFormula>()
                        + molecular_formula!(H 1) * variant,
                ),
                charge: Charge::new::<crate::system::e>(charge.charge().value.try_into().unwrap()),
                ion: annotation.with_variant(*variant),
                peptidoform_ion_index: Some(peptidoform_ion_index),
                peptidoform_index: Some(peptidoform_index),
                neutral_loss: losses.cloned().unwrap_or_default(),
                deviation: None,
                confidence: None,
                auxiliary: false,
            })
            .collect()
    }

    /// Create a copy of this fragment with the given charge
    /// # Panics
    /// If the charge is negative.
    #[must_use]
    fn with_charge(&self, charge: &MolecularCharge) -> Self {
        let formula = charge
            .formula()
            .with_labels(&[AmbiguousLabel::ChargeCarrier(charge.formula())]);
        let c = Charge::new::<crate::system::charge::e>(
            usize::try_from(formula.charge().value).unwrap(),
        );
        Self {
            formula: Some(self.formula.clone().unwrap_or_default() + &formula),
            charge: c,
            ..self.clone()
        }
    }

    /// Create a copy of this fragment with the given charges
    pub fn with_charge_range(
        self,
        charge_carriers: &mut CachedCharge,
        charge_range: ChargeRange,
    ) -> impl Iterator<Item = Self> {
        charge_carriers
            .range(charge_range)
            .into_iter()
            .map(move |c| self.with_charge(&c))
    }

    /// Create a copy of this fragment with the given neutral loss
    #[must_use]
    pub fn with_neutral_loss(&self, neutral_loss: &NeutralLoss) -> Self {
        let mut new_neutral_loss = self.neutral_loss.clone();
        new_neutral_loss.push(neutral_loss.clone());
        Self {
            formula: Some(self.formula.clone().unwrap_or_default() + neutral_loss),
            neutral_loss: new_neutral_loss,
            ..self.clone()
        }
    }

    /// Create copies of this fragment with the given neutral losses (and a copy of this fragment itself)
    #[must_use]
    pub fn with_neutral_losses(&self, neutral_losses: &[NeutralLoss]) -> Vec<Self> {
        let mut output = Vec::with_capacity(neutral_losses.len() + 1);
        output.push(self.clone());
        output.extend(
            neutral_losses
                .iter()
                .map(|loss| self.with_neutral_loss(loss)),
        );
        output
    }
}

impl Display for Fragment {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}@{}{:+}{}",
            self.ion,
            self.mz(MassMode::Monoisotopic)
                .map_or(String::new(), |mz| mz.value.to_string()),
            self.charge.value,
            self.neutral_loss
                .iter()
                .map(std::string::ToString::to_string)
                .join("")
        )
    }
}

// /// An isotope annotation.
// #[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
// pub struct MatchedIsotopeDistribution {
//     /// The index of the matched peak in the spectrum, if found
//     pub peak_index: Option<usize>,
//     /// The isotope offset in whole daltons from the monoisotopic peak
//     pub isotope_offset: usize,
//     /// The theoretical abundance of this isotope (normalised to 1 for the whole distribution)
//     pub theoretical_isotope_abundance: OrderedFloat<f64>,
// }

/// The definition of the position of an ion
#[derive(
    Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Default, Debug, Serialize, Deserialize,
)]
#[non_exhaustive]
pub struct PeptidePosition {
    /// The sequence index (0 based into the peptide sequence)
    pub sequence_index: SequencePosition,
    /// The series number (1 based from the ion series terminal)
    pub series_number: usize,
    /// The length of the whole sequence
    pub sequence_length: usize,
}

impl PeptidePosition {
    /// Generate a position for N terminal ion series
    pub const fn n(sequence_index: SequencePosition, length: usize) -> Self {
        Self {
            sequence_index,
            series_number: match sequence_index {
                SequencePosition::NTerm => 0,
                SequencePosition::Index(i) => i + 1,
                SequencePosition::CTerm => length,
            },
            sequence_length: length,
        }
    }
    /// Generate a position for C terminal ion series
    pub const fn c(sequence_index: SequencePosition, length: usize) -> Self {
        Self {
            sequence_index,
            series_number: match sequence_index {
                SequencePosition::NTerm => length,
                SequencePosition::Index(i) => length - i,
                SequencePosition::CTerm => 0,
            },
            sequence_length: length,
        }
    }
    /// Check if this position is on the N terminus
    pub fn is_n_terminal(&self) -> bool {
        self.sequence_index == SequencePosition::NTerm
    }
    /// Check if this position is on the C terminus
    pub fn is_c_terminal(&self) -> bool {
        self.sequence_index == SequencePosition::CTerm
    }
    /// Flip to the other series (N->C and C->N)
    #[must_use]
    pub const fn flip_terminal(self) -> Self {
        Self {
            sequence_index: self.sequence_index,
            series_number: self.sequence_length + 1 - self.series_number,
            sequence_length: self.sequence_length,
        }
    }
}

include!("shared/glycan_position.rs");

impl GlycanPosition {
    /// Get the branch names
    /// # Panics
    /// Panics if the first branch number is outside the range of the greek alphabet (small and caps together).
    pub fn branch_names(&self) -> String {
        self.branch
            .iter()
            .enumerate()
            .map(|(i, (_, b))| {
                if i == 0 {
                    char::from_u32(
                        (0x03B1..=0x03C9)
                            .chain(0x0391..=0x03A9)
                            .nth(*b)
                            .expect("Too many branches in glycan, out of greek letters"),
                    )
                    .unwrap()
                    .to_string()
                } else if i == 1 {
                    "\'".repeat(*b)
                } else {
                    format!(",{b}")
                }
            })
            .collect::<String>()
    }
    /// Generate the label for this glycan position, example: `1α'`
    /// # Panics
    /// Panics if the first branch number is outside the range of the greek alphabet (small and caps together).
    pub fn label(&self) -> String {
        format!("{}{}", self.series_number, self.branch_names())
    }
    /// Generate the label for this glycan attachment eg N1 (1 based numbering) or an empty string if the attachment is unknown
    pub fn attachment(&self) -> String {
        self.attachment
            .map(|(aa, pos)| format!("{aa}{pos}"))
            .unwrap_or_default()
    }
}

/// Any position on a glycan or a peptide
#[derive(Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Serialize, Deserialize)]
pub enum DiagnosticPosition {
    /// A position on a glycan
    Glycan(GlycanPosition, MonoSaccharide),
    /// A position on a compositional glycan (attachment AA + sequence index + the sugar)
    GlycanCompositional(MonoSaccharide, Option<(AminoAcid, SequencePosition)>),
    /// A position on a peptide
    Peptide(PeptidePosition, AminoAcid),
    /// Labile modification
    Labile(Modification),
    /// Reporter ion
    Reporter,
}

/// A label for a satellite ion, none for most amino acids but a or b for Thr and Ile
#[derive(
    Clone, Copy, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Serialize, Deserialize, Default,
)]
pub enum SatelliteLabel {
    /// No label needed
    #[default]
    None,
    /// Heaviest of the two options
    A,
    /// Lightest of the two options
    B,
}

impl std::fmt::Display for SatelliteLabel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}",
            match self {
                Self::None => "",
                Self::A => "a",
                Self::B => "b",
            }
        )
    }
}

/// The possible types of fragments
#[derive(Clone, Eq, PartialEq, Hash, Debug, Serialize, Deserialize, Default)]
#[expect(non_camel_case_types)]
pub enum FragmentType {
    /// a
    a(PeptidePosition, i8),
    /// b
    b(PeptidePosition, i8),
    /// c
    c(PeptidePosition, i8),
    /// d a position, originating amino acid, distance from a break, variant,
    d(PeptidePosition, AminoAcid, u8, i8, SatelliteLabel),
    /// v
    v(PeptidePosition, AminoAcid, u8, i8),
    /// w
    w(PeptidePosition, AminoAcid, u8, i8, SatelliteLabel),
    /// x
    x(PeptidePosition, i8),
    /// y
    y(PeptidePosition, i8),
    /// z
    z(PeptidePosition, i8),
    // glycan A fragment (Never generated)
    //A(GlycanPosition),
    /// glycan B fragment
    // B(GlycanPosition),
    // glycan C fragment (Never generated)
    //C(GlycanPosition),
    // glycan X fragment (Never generated)
    //X(GlycanPosition),
    /// glycan Y fragment, generated by one or more branches broken
    Y(Vec<GlycanPosition>),
    // glycan Z fragment (Never generated)
    // Z(GlycanPosition),
    /// B glycan fragment, potentially with additional Y breakages
    B {
        /// The root break
        b: GlycanPosition,
        /// The branch breakages
        y: Vec<GlycanPosition>,
        /// All branches that are not broken
        end: Vec<GlycanPosition>,
    },
    /// A B or internal glycan fragment for a glycan where only the composition is known, also saves the attachment (AA + sequence index)
    BComposition(
        Vec<(MonoSaccharide, isize)>,
        Option<(AminoAcid, SequencePosition)>,
    ),
    /// A B or internal glycan fragment for a glycan where only the composition is known, also saves the attachment (AA + sequence index)
    YComposition(
        Vec<(MonoSaccharide, isize)>,
        Option<(AminoAcid, SequencePosition)>,
    ),
    /// Immonium ion
    Immonium(PeptidePosition, SequenceElement<SemiAmbiguous>),
    /// Precursor with amino acid side chain loss
    PrecursorSideChainLoss(PeptidePosition, AminoAcid),
    /// Diagnostic ion for a given position
    Diagnostic(DiagnosticPosition),
    /// An internal fragment, potentially with the named bonds that resulted in this fragment
    Internal(
        Option<(BackboneNFragment, BackboneCFragment)>,
        PeptidePosition,
        PeptidePosition,
    ),
    /// An unknown series, with potentially the series number
    Unknown(Option<usize>),
    /// precursor
    #[default]
    Precursor,
}

impl std::cmp::Ord for FragmentType {
    fn cmp(&self, other: &Self) -> Ordering {
        // Sort of type first (precursor/abcxyz/dw/v)
        match (self, other) {
            // Peptide
            (Self::Precursor, Self::Precursor) => Ordering::Equal,
            (Self::Precursor, _) => Ordering::Less,
            (_, Self::Precursor) => Ordering::Greater,
            (Self::a(s, sv), Self::a(o, ov)) => s.cmp(o).then(sv.cmp(ov)),
            (Self::a(_, _), _) => Ordering::Less,
            (_, Self::a(_, _)) => Ordering::Greater,
            (Self::b(s, sv), Self::b(o, ov)) => s.cmp(o).then(sv.cmp(ov)),
            (Self::b(_, _), _) => Ordering::Less,
            (_, Self::b(_, _)) => Ordering::Greater,
            (Self::c(s, sv), Self::c(o, ov)) => s.cmp(o).then(sv.cmp(ov)),
            (Self::c(_, _), _) => Ordering::Less,
            (_, Self::c(_, _)) => Ordering::Greater,
            (Self::x(s, sv), Self::x(o, ov)) => s.cmp(o).then(sv.cmp(ov)),
            (Self::x(_, _), _) => Ordering::Less,
            (_, Self::x(_, _)) => Ordering::Greater,
            (Self::y(s, sv), Self::y(o, ov)) => s.cmp(o).then(sv.cmp(ov)),
            (Self::y(_, _), _) => Ordering::Less,
            (_, Self::y(_, _)) => Ordering::Greater,
            (Self::z(s, sv), Self::z(o, ov)) => s.cmp(o).then(sv.cmp(ov)),
            (Self::z(_, _), _) => Ordering::Less,
            (_, Self::z(_, _)) => Ordering::Greater,
            (Self::d(s, _, sd, sv, sl), Self::d(o, _, od, ov, ol)) => {
                s.cmp(o).then(sd.cmp(od)).then(sv.cmp(ov)).then(sl.cmp(ol))
            }
            (Self::d(_, _, _, _, _), _) => Ordering::Less,
            (_, Self::d(_, _, _, _, _)) => Ordering::Greater,
            (Self::w(s, _, sd, sv, sl), Self::w(o, _, od, ov, ol)) => {
                s.cmp(o).then(sd.cmp(od)).then(sv.cmp(ov)).then(sl.cmp(ol))
            }
            (Self::w(_, _, _, _, _), _) => Ordering::Less,
            (_, Self::w(_, _, _, _, _)) => Ordering::Greater,
            (Self::v(s, _, sd, sv), Self::v(o, _, od, ov)) => {
                s.cmp(o).then(sd.cmp(od)).then(sv.cmp(ov))
            }
            (Self::v(_, _, _, _), _) => Ordering::Less,
            (_, Self::v(_, _, _, _)) => Ordering::Greater,
            (Self::Immonium(s, _), Self::Immonium(o, _)) => s.cmp(o),
            (Self::Immonium(_, _), _) => Ordering::Less,
            (_, Self::Immonium(_, _)) => Ordering::Greater,
            (Self::PrecursorSideChainLoss(s, _), Self::PrecursorSideChainLoss(o, _)) => s.cmp(o),
            (Self::PrecursorSideChainLoss(_, _), _) => Ordering::Less,
            (_, Self::PrecursorSideChainLoss(_, _)) => Ordering::Greater,
            (Self::Internal(st, sa, sb), Self::Internal(ot, oa, ob)) => {
                sa.cmp(oa).then(sb.cmp(ob)).then(st.cmp(ot))
            }
            (Self::Internal(_, _, _), _) => Ordering::Less,
            (_, Self::Internal(_, _, _)) => Ordering::Greater,
            // Glycans
            (Self::B { b: sb, y: sy, .. }, Self::B { b: ob, y: oy, .. }) => {
                sy.len().cmp(&oy.len()).then(sb.cmp(ob))
            }
            (Self::Y(s), Self::Y(o)) => s.len().cmp(&o.len()),
            (Self::B { y: sy, .. }, Self::Y(o)) => {
                (sy.len() + 1).cmp(&o.len()).then(Ordering::Greater)
            }
            (Self::Y(s), Self::B { y: oy, .. }) => {
                s.len().cmp(&(oy.len() + 1)).then(Ordering::Less)
            }
            (Self::B { .. }, _) => Ordering::Less,
            (_, Self::B { .. }) => Ordering::Greater,
            (Self::Y(_), _) => Ordering::Less,
            (_, Self::Y(_)) => Ordering::Greater,
            (Self::BComposition(s, sl), Self::BComposition(o, ol))
            | (Self::YComposition(s, sl), Self::YComposition(o, ol)) => {
                s.len().cmp(&o.len()).then(sl.cmp(ol))
            }
            (Self::BComposition(s, sl), Self::YComposition(o, ol)) => s
                .len()
                .cmp(&o.len())
                .then(sl.cmp(ol))
                .then(Ordering::Greater),
            (Self::YComposition(s, sl), Self::BComposition(o, ol)) => {
                s.len().cmp(&o.len()).then(sl.cmp(ol)).then(Ordering::Less)
            }
            (Self::BComposition(_, _), _) => Ordering::Less,
            (_, Self::BComposition(_, _)) => Ordering::Greater,
            (Self::YComposition(_, _), _) => Ordering::Less,
            (_, Self::YComposition(_, _)) => Ordering::Greater,
            // Other
            (Self::Diagnostic(s), Self::Diagnostic(o)) => s.cmp(o),
            (Self::Diagnostic(_), _) => Ordering::Less,
            (_, Self::Diagnostic(_)) => Ordering::Greater,
            (Self::Unknown(s), Self::Unknown(o)) => s.cmp(o),
        }
    }
}

impl std::cmp::PartialOrd for FragmentType {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl FragmentType {
    /// Get a main ion series fragment with the specified variant, or pass the fragment type through unchanged
    #[must_use]
    pub fn with_variant(&self, variant: i8) -> Self {
        match self {
            Self::a(p, _) => Self::a(*p, variant),
            Self::b(p, _) => Self::b(*p, variant),
            Self::c(p, _) => Self::c(*p, variant),
            Self::d(p, a, d, _, l) => Self::d(*p, *a, *d, variant, *l),
            Self::v(p, a, d, _) => Self::v(*p, *a, *d, variant),
            Self::w(p, a, d, _, l) => Self::w(*p, *a, *d, variant, *l),
            Self::x(p, _) => Self::x(*p, variant),
            Self::y(p, _) => Self::y(*p, variant),
            Self::z(p, _) => Self::z(*p, variant),
            other => other.clone(),
        }
    }

    /// Get the position of this ion (or None if it is a precursor ion)
    pub const fn position(&self) -> Option<&PeptidePosition> {
        match self {
            Self::a(n, _)
            | Self::b(n, _)
            | Self::c(n, _)
            | Self::d(n, _, _, _, _)
            | Self::v(n, _, _, _)
            | Self::w(n, _, _, _, _)
            | Self::x(n, _)
            | Self::y(n, _)
            | Self::z(n, _)
            | Self::Diagnostic(DiagnosticPosition::Peptide(n, _))
            | Self::Immonium(n, _)
            | Self::PrecursorSideChainLoss(n, _) => Some(n),
            _ => None,
        }
    }

    /// Get the root glycan position of this ion (or None if not applicable), Y is not defined as it does not have a root break
    pub const fn glycan_position(&self) -> Option<&GlycanPosition> {
        match self {
            Self::Diagnostic(DiagnosticPosition::Glycan(b, _)) | Self::B { b, .. } => Some(b),
            _ => None,
        }
    }

    /// Get the glycan break positions of this ion (or None if not applicable), gives the sequence index, the root break, and the branch breaks.
    /// Only available with feature 'glycan-render'.
    #[cfg(feature = "glycan-render")]
    pub fn glycan_break_positions(
        &self,
    ) -> Option<(Option<SequencePosition>, GlycanSelection<'_>)> {
        match self {
            Self::Diagnostic(DiagnosticPosition::Glycan(n, _)) => Some((
                n.attachment.map(|(_, p)| p),
                GlycanSelection::SingleSugar(n),
            )),
            Self::Y(breaks) => Some((
                breaks.first().and_then(|p| p.attachment.map(|(_, p)| p)),
                GlycanSelection::Subtree(None, breaks),
            )),
            Self::B { b, y, .. } => Some((
                b.attachment.map(|(_, p)| p),
                GlycanSelection::Subtree(Some(b), y),
            )),
            _ => None,
        }
    }

    /// Get the position label, unless it is a precursor ion
    pub fn position_label(&self) -> Option<String> {
        match self {
            Self::a(n, _)
            | Self::b(n, _)
            | Self::c(n, _)
            | Self::d(n, _, _, _, _)
            | Self::v(n, _, _, _)
            | Self::w(n, _, _, _, _)
            | Self::x(n, _)
            | Self::y(n, _)
            | Self::z(n, _)
            | Self::Diagnostic(DiagnosticPosition::Peptide(n, _))
            | Self::Immonium(n, _)
            | Self::PrecursorSideChainLoss(n, _) => Some(n.series_number.to_string()),
            Self::Diagnostic(DiagnosticPosition::Glycan(n, _)) => Some(n.label()),
            Self::Y(bonds) => Some(bonds.iter().map(GlycanPosition::label).join("Y")),
            Self::B { b, y, end } => Some(
                b.label()
                    + "Y"
                    + &y.iter()
                        .chain(end.iter())
                        .map(GlycanPosition::label)
                        .join("Y"),
            ),
            Self::YComposition(sugars, _) | Self::BComposition(sugars, _) => Some(
                sugars
                    .iter()
                    .map(|(sugar, amount)| format!("{sugar}{amount}"))
                    .join(""),
            ),
            Self::Internal(_, pos1, pos2) => {
                Some(format!("{}:{}", pos1.sequence_index, pos2.sequence_index,))
            }
            Self::Precursor
            | Self::Unknown(_)
            | Self::Diagnostic(
                DiagnosticPosition::Labile(_)
                | DiagnosticPosition::GlycanCompositional(_, _)
                | DiagnosticPosition::Reporter,
            ) => None,
        }
    }

    /// Get the label for this fragment type, the first argument is the optional superscript prefix, the second is the main label
    pub fn label(&self) -> (Option<String>, Cow<str>) {
        let get_label = |ion: &'static str, v: i8| {
            if v == 0 {
                Cow::Borrowed(ion)
            } else {
                Cow::Owned(format!(
                    "{ion}{}",
                    if v < 0 {
                        "\'".repeat((-v) as usize)
                    } else {
                        "·".repeat(v as usize)
                    }
                ))
            }
        };

        match self {
            Self::a(_, v) => (None, get_label("a", *v)),
            Self::b(_, v) => (None, get_label("b", *v)),
            Self::c(_, v) => (None, get_label("c", *v)),
            Self::d(_, _, n, v, l) => (
                (*n != 0).then_some(n.to_string()),
                Cow::Owned(format!(
                    "d{l}{}",
                    if *v < 0 {
                        "\'".repeat((-v) as usize)
                    } else {
                        "·".repeat(*v as usize)
                    }
                )),
            ),
            Self::v(_, _, n, v) => ((*n != 0).then_some(n.to_string()), get_label("v", *v)),
            Self::w(_, _, n, v, l) => (
                (*n != 0).then_some(n.to_string()),
                Cow::Owned(format!(
                    "w{l}{}",
                    if *v < 0 {
                        "\'".repeat((-v) as usize)
                    } else {
                        "·".repeat(*v as usize)
                    }
                )),
            ),
            Self::x(_, v) => (None, get_label("x", *v)),
            Self::y(_, v) => (None, get_label("y", *v)),
            Self::z(_, v) => (None, get_label("z", *v)),
            Self::B { .. } | Self::BComposition(_, _) => (None, Cow::Borrowed("B")),
            Self::Y(_) | Self::YComposition(_, _) => (None, Cow::Borrowed("Y")),
            Self::Diagnostic(DiagnosticPosition::Peptide(_, aa)) => (
                None,
                Cow::Owned(
                    aa.one_letter_code()
                        .map(|c| format!("d{c}"))
                        .or_else(|| aa.three_letter_code().map(|c| format!("d{c}")))
                        .unwrap_or_else(|| format!("d{}", aa.name())),
                ),
            ),
            Self::Diagnostic(DiagnosticPosition::Reporter) => (None, Cow::Borrowed("r")),
            Self::Diagnostic(DiagnosticPosition::Labile(m)) => (None, Cow::Owned(format!("d{m}"))),
            Self::Diagnostic(
                DiagnosticPosition::Glycan(_, sug)
                | DiagnosticPosition::GlycanCompositional(sug, _),
            ) => (None, Cow::Owned(format!("d{sug}"))),
            Self::Immonium(_, aa) => (
                None,
                Cow::Owned(
                    aa.aminoacid
                        .one_letter_code()
                        .map(|c| format!("i{c}"))
                        .or_else(|| aa.aminoacid.three_letter_code().map(|c| format!("i{c}")))
                        .unwrap_or_else(|| format!("i{}", aa.aminoacid.name())),
                ),
            ),
            Self::PrecursorSideChainLoss(_, aa) => (
                None,
                Cow::Owned(
                    aa.one_letter_code()
                        .map(|c| format!("p-s{c}"))
                        .or_else(|| aa.three_letter_code().map(|c| format!("p-s{c}")))
                        .unwrap_or_else(|| format!("p-s{}", aa.name())),
                ),
            ),
            Self::Precursor => (None, Cow::Borrowed("p")),
            Self::Internal(fragmentation, _, _) => (
                None,
                Cow::Owned(format!(
                    "m{}",
                    fragmentation.map_or(String::new(), |(n, c)| format!("{n}:{c}")),
                )),
            ),
            Self::Unknown(series) => (
                None,
                Cow::Owned(format!(
                    "?{}",
                    series.map_or(String::new(), |s| s.to_string()),
                )),
            ),
        }
    }

    /// Get the kind of fragment, easier to match against
    pub const fn kind(&self) -> FragmentKind {
        match self {
            Self::a(_, _) => FragmentKind::a,
            Self::b(_, _) => FragmentKind::b,
            Self::c(_, _) => FragmentKind::c,
            Self::d(_, _, _, _, _) => FragmentKind::d,
            Self::v(_, _, _, _) => FragmentKind::v,
            Self::w(_, _, _, _, _) => FragmentKind::w,
            Self::x(_, _) => FragmentKind::x,
            Self::y(_, _) => FragmentKind::y,
            Self::z(_, _) => FragmentKind::z,
            Self::Y(_) | Self::YComposition(_, _) => FragmentKind::Y,
            Self::Diagnostic(
                DiagnosticPosition::Glycan(_, _) | DiagnosticPosition::GlycanCompositional(_, _),
            )
            | Self::B { .. }
            | Self::BComposition(_, _) => FragmentKind::B,
            Self::Diagnostic(_) => FragmentKind::diagnostic,
            Self::Immonium(_, _) => FragmentKind::immonium,
            Self::PrecursorSideChainLoss(_, _) => FragmentKind::precursor_side_chain_loss,
            Self::Precursor => FragmentKind::precursor,
            Self::Internal(_, _, _) => FragmentKind::internal,
            Self::Unknown(_) => FragmentKind::unknown,
        }
    }
}

impl Display for FragmentType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let (sup, label) = self.label();
        write!(
            f,
            "{}{}{}",
            sup.unwrap_or_default(),
            label,
            self.position_label().unwrap_or_default()
        )
    }
}

/// The possible kinds of N terminal backbone fragments.
#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Serialize, Deserialize)]
#[expect(non_camel_case_types)]
pub enum BackboneNFragment {
    /// a
    a,
    /// b
    b,
    /// c
    c,
}

impl Display for BackboneNFragment {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}",
            match self {
                Self::a => "a",
                Self::b => "b",
                Self::c => "c",
            }
        )
    }
}

/// The possible kinds of C terminal backbone fragments.
#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Serialize, Deserialize)]
#[expect(non_camel_case_types)]
pub enum BackboneCFragment {
    /// x
    x,
    /// y
    y,
    /// z and z·
    z,
}

impl Display for BackboneCFragment {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}",
            match self {
                Self::x => "x",
                Self::y => "y",
                Self::z => "z",
            }
        )
    }
}

/// The possible kinds of fragments, same options as [`FragmentType`] but without any additional data
#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Serialize, Deserialize)]
#[expect(non_camel_case_types)]
pub enum FragmentKind {
    /// a
    a,
    /// b
    b,
    /// c
    c,
    /// d
    d,
    /// v
    v,
    /// w
    w,
    /// x
    x,
    /// y
    y,
    /// z and z·
    z,
    /// glycan Y fragment, generated by one or more branches broken
    Y,
    /// B or glycan diagnostic ion or Internal glycan fragment, meaning both a B and Y breakages (and potentially multiple of both), resulting in a set of monosaccharides
    B,
    /// Immonium ion
    immonium,
    /// Precursor with amino acid side chain loss
    precursor_side_chain_loss,
    /// Diagnostic ion for a given position
    diagnostic,
    /// Internal ion
    internal,
    /// precursor
    precursor,
    /// unknown fragment
    unknown,
}

impl Display for FragmentKind {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}",
            match self {
                Self::a => "a",
                Self::b => "b",
                Self::c => "c",
                Self::d => "d",
                Self::x => "x",
                Self::y => "y",
                Self::v => "v",
                Self::w => "w",
                Self::z => "z",
                Self::Y => "Y",
                Self::B => "oxonium",
                Self::immonium => "immonium",
                Self::precursor_side_chain_loss => "precursor side chain loss",
                Self::diagnostic => "diagnostic",
                Self::internal => "m",
                Self::precursor => "precursor",
                Self::unknown => "unknown",
            }
        )
    }
}

/// All positions where a glycan can break
#[derive(Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Serialize, Deserialize)]
pub enum GlycanBreakPos {
    /// No breaks just until the end of a chain
    End(GlycanPosition),
    /// Break at a Y position
    Y(GlycanPosition),
    /// Break at a B position
    B(GlycanPosition),
}

impl GlycanBreakPos {
    /// Get the position of this breaking position
    pub const fn position(&self) -> &GlycanPosition {
        match self {
            Self::B(p) | Self::End(p) | Self::Y(p) => p,
        }
    }

    /// Get the label for this breaking position
    pub const fn label(&self) -> &str {
        match self {
            Self::End(_) => "End",
            Self::Y(_) => "Y",
            Self::B(_) => "B",
        }
    }
}

impl std::fmt::Display for GlycanBreakPos {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}{}", self.label(), self.position().label())
    }
}

#[cfg(test)]
#[expect(clippy::missing_panics_doc)]
mod tests {

    use crate::{AminoAcid, MultiChemical};

    use super::*;

    #[test]
    fn neutral_loss() {
        let a = Fragment::new(
            AminoAcid::AsparticAcid.formulas()[0].clone(),
            Charge::new::<crate::system::charge::e>(1),
            0,
            0,
            FragmentType::Precursor,
        );
        let loss = a.with_neutral_losses(&[NeutralLoss::Loss(molecular_formula!(H 2 O 1))]);
        dbg!(&a, &loss);
        assert_eq!(a.formula, loss[0].formula);
        assert_eq!(
            a.formula.unwrap(),
            &loss[1].formula.clone().unwrap() + &molecular_formula!(H 2 O 1)
        );
    }

    #[test]
    fn flip_terminal() {
        let n0 = PeptidePosition::n(SequencePosition::Index(0), 2);
        let n1 = PeptidePosition::n(SequencePosition::Index(1), 2);
        let n2 = PeptidePosition::n(SequencePosition::Index(2), 2);
        let c0 = PeptidePosition::c(SequencePosition::Index(0), 2);
        let c1 = PeptidePosition::c(SequencePosition::Index(1), 2);
        let c2 = PeptidePosition::c(SequencePosition::Index(2), 2);
        assert_eq!(n0.flip_terminal(), c0);
        assert_eq!(n1.flip_terminal(), c1);
        assert_eq!(n2.flip_terminal(), c2);
    }
}
