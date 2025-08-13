//! Handle glycan structures
use std::str::FromStr;
use std::{fmt::Display, hash::Hash};

use itertools::Itertools;
use serde::{Deserialize, Serialize};

use super::{
    glycan_parse_list, BaseSugar, GlycanBranchIndex, GlycanBranchMassIndex, MonoSaccharide,
    PositionedGlycanStructure,
};
use crate::{
    error::{Context, CustomError},
    formula::{Chemical, MolecularFormula},
};

include!("../shared/glycan_structure.rs");

impl FromStr for GlycanStructure {
    type Err = CustomError;
    /// Parse a textual structure representation of a glycan (outside ProForma format)
    /// Example: Hex(Hex(HexNAc)) => Hex-Hex-HexNAc (linear)
    /// Example: Hex(Fuc,Hex(HexNAc,Hex(HexNAc)))
    ///          =>  Hex-Hex-HexNAc
    ///              └Fuc  └Hex-HexNAc
    /// # Errors
    /// Return an Err if the format is not correct
    fn from_str(line: &str) -> Result<Self, CustomError> {
        Self::parse(line, 0..line.len())
    }
}

impl GlycanStructure {
    /// Parse a textual structure representation of a glycan (outside ProForma format)
    /// Example: Hex(Hex(HexNAc)) => Hex-Hex-HexNAc (linear)
    /// Example: Hex(Fuc,Hex(HexNAc,Hex(HexNAc)))
    ///          =>  Hex-Hex-HexNAc
    ///              └Fuc  └Hex-HexNAc
    /// # Errors
    /// Return an Err if the format is not correct
    pub fn parse(line: &str, range: Range<usize>) -> Result<Self, CustomError> {
        Self::parse_internal(line, range).map(|(g, _)| g)
    }

    /// # Errors
    /// Return an Err if the format is not correct
    fn parse_internal(line: &str, range: Range<usize>) -> Result<(Self, usize), CustomError> {
        // Parse at the start the first recognised glycan name
        if let Some(name) = glycan_parse_list()
            .iter()
            .find(|name| line[range.clone()].starts_with(&name.0))
        {
            // If the name is followed by a bracket parse a list of branches
            let index = range.start + name.0.len();
            if line.as_bytes()[index] == b'(' {
                // Find the end of this list
                let end = end_of_enclosure(line, index + 1, b'(', b')').ok_or_else(|| {
                    CustomError::error(
                        "Invalid glycan branch",
                        "No valid closing delimiter",
                        Context::line(None, line, index, 1),
                    )
                })?;
                // Parse the first branch
                let mut index = index + 1;
                let mut branches = Vec::new();
                let (glycan, pos) = Self::parse_internal(line, index..end)?;
                index = pos;
                branches.push(glycan);
                // Keep parsing until the end of this branch level (until the ')' is reached)
                while index < end {
                    if line.as_bytes()[index] != b',' {
                        return Err(CustomError::error(
                            "Invalid glycan structure",
                            "Branches should be separated by commas ','",
                            Context::line(None, line, index, 1),
                        ));
                    }
                    index += 1;
                    let (glycan, pos) = Self::parse_internal(line, index..end)?;
                    branches.push(glycan);
                    index = pos;
                }
                Ok((
                    Self {
                        sugar: name.1.clone(),
                        branches,
                    },
                    end + 1,
                ))
            } else {
                Ok((
                    Self {
                        sugar: name.1.clone(),
                        branches: Vec::new(),
                    },
                    range.start + name.0.len(),
                ))
            }
        } else {
            Err(CustomError::error(
                "Could not parse glycan structure",
                "Could not parse the following part",
                Context::line(None, line, range.start, range.len()),
            ))
        }
    }

    /// Annotate all positions in this tree with all positions
    pub fn determine_positions(self) -> PositionedGlycanStructure {
        self.internal_pos(0, &[]).0
    }

    /// Given the inner depth determine the correct positions and branch ordering
    /// Return the positioned tree and the outer depth.
    /// # Panics
    /// When any of the masses in this glycan cannot be compared see [`f64::partial_cmp`].
    fn internal_pos(
        self,
        inner_depth: usize,
        branch: &[(GlycanBranchIndex, GlycanBranchMassIndex)],
    ) -> (PositionedGlycanStructure, usize) {
        // Sort the branches on decreasing molecular weight
        let branches = self
            .branches
            .into_iter()
            .enumerate()
            .sorted_unstable_by(|(_, a), (_, b)| {
                b.formula()
                    .monoisotopic_mass()
                    .partial_cmp(&a.formula().monoisotopic_mass())
                    .unwrap()
            })
            .collect_vec();

        // Get the correct branch indices adding a new layer of indices when needed
        let branches: Vec<(PositionedGlycanStructure, usize)> = if branches.len() == 1 {
            branches
                .into_iter()
                .map(|(_, b)| b.internal_pos(inner_depth + 1, branch))
                .collect()
        } else {
            branches
                .into_iter()
                .enumerate()
                .map(|(mass_index, (index, b))| {
                    let mut new_branch = branch.to_vec();
                    new_branch.push((index, mass_index));
                    b.internal_pos(inner_depth + 1, &new_branch)
                })
                .collect()
        };

        let outer_depth = branches.iter().map(|b| b.1).max().unwrap_or(0);
        (
            PositionedGlycanStructure {
                sugar: self.sugar,
                branches: branches.into_iter().map(|b| b.0).collect(),
                branch: branch.to_vec(),
                inner_depth,
                outer_depth,
            },
            outer_depth + 1,
        )
    }

    /// Get the composition of a `GlycanStructure`. The result is normalised (sorted and deduplicated).
    /// # Panics
    /// If one monosaccharide species has occurrence outside the range of [`isize::MIN`] to [`isize::MAX`].
    pub fn composition(&self) -> Vec<(MonoSaccharide, isize)> {
        let composition = self.composition_inner();
        MonoSaccharide::simplify_composition(composition)
            .expect("One monosaccharide species has a number outside of the range of isize")
    }

    /// Get the composition in monosaccharides of this glycan
    fn composition_inner(&self) -> Vec<(MonoSaccharide, isize)> {
        let mut output = vec![(self.sugar.clone(), 1)];
        output.extend(self.branches.iter().flat_map(Self::composition_inner));
        output
    }
}

#[cfg(test)]
#[expect(clippy::missing_panics_doc)]
mod test {
    use super::*;

    #[test]
    fn parse_glycan_structure_01() {
        assert_eq!(
            GlycanStructure::from_str("hep(hex)").unwrap(),
            GlycanStructure {
                sugar: MonoSaccharide::new(BaseSugar::Heptose(None), &[]).with_name("Hep"),
                branches: vec![GlycanStructure {
                    sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[]).with_name("Hex"),
                    branches: Vec::new()
                }],
            }
        );
    }

    #[test]
    fn parse_glycan_structure_02() {
        assert_eq!(
            GlycanStructure::from_str("hex(hex,hep)").unwrap(),
            GlycanStructure {
                sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[]).with_name("Hex"),
                branches: vec![
                    GlycanStructure {
                        sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[]).with_name("Hex"),
                        branches: Vec::new()
                    },
                    GlycanStructure {
                        sugar: MonoSaccharide::new(BaseSugar::Heptose(None), &[]).with_name("Hep"),
                        branches: Vec::new()
                    }
                ],
            }
        );
    }

    #[test]
    fn parse_glycan_structure_03() {
        assert_eq!(
            GlycanStructure::from_str("hex(hex(hex),hep)").unwrap(),
            GlycanStructure {
                sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[]).with_name("Hex"),
                branches: vec![
                    GlycanStructure {
                        sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[]).with_name("Hex"),
                        branches: vec![GlycanStructure {
                            sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[])
                                .with_name("Hex"),
                            branches: Vec::new()
                        }]
                    },
                    GlycanStructure {
                        sugar: MonoSaccharide::new(BaseSugar::Heptose(None), &[]).with_name("Hep"),
                        branches: Vec::new()
                    }
                ],
            }
        );
    }

    #[test]
    fn parse_glycan_structure_04() {
        assert_eq!(
            GlycanStructure::from_str("hep(hex(hex(hex(hep),hex)))").unwrap(),
            GlycanStructure {
                sugar: MonoSaccharide::new(BaseSugar::Heptose(None), &[]).with_name("Hep"),
                branches: vec![GlycanStructure {
                    sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[]).with_name("Hex"),
                    branches: vec![GlycanStructure {
                        sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[]).with_name("Hex"),
                        branches: vec![
                            GlycanStructure {
                                sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[])
                                    .with_name("Hex"),
                                branches: vec![GlycanStructure {
                                    sugar: MonoSaccharide::new(BaseSugar::Heptose(None), &[])
                                        .with_name("Hep"),
                                    branches: Vec::new(),
                                }],
                            },
                            GlycanStructure {
                                sugar: MonoSaccharide::new(BaseSugar::Hexose(None), &[])
                                    .with_name("Hex"),
                                branches: Vec::new(),
                            },
                        ],
                    }],
                }],
            }
        );
    }

    #[test]
    fn correct_masses() {
        let (sugar, _) = MonoSaccharide::from_short_iupac("Neu5Ac", 0, 0).unwrap();
        dbg!(&sugar);

        assert_eq!(sugar.formula(), molecular_formula!(C 11 H 17 N 1 O 8));
    }

    #[test]
    fn correct_structure_g43728nl() {
        // Furanoses added for error detection
        let structure = GlycanStructure::from_short_iupac(
            "Neu5Ac(?2-?)Galf(?1-?)GlcNAc(?1-?)Man(?1-?)[Galf(?1-?)GlcNAc(?1-?)Man(?1-?)]Man(?1-?)GlcNAc(?1-?)GlcNAc", 
            0..101,
            0
        )
        .unwrap();

        assert_eq!(
            structure.to_string(),
            "HexNAc(HexNAc(Hex(Hex(HexNAc(Hexf(NonNAAc))),Hex(HexNAc(Hexf)))))"
        );
    }

    #[test]
    fn correct_structure_g36564am() {
        let structure = GlycanStructure::from_short_iupac(
            "Gal(?1-?)GlcNAc(?1-?)Man(?1-?)[GlcNAc(?1-?)Man(?1-?)][GlcNAc(?1-?)]Man(?1-?)GlcNAc",
            0..82,
            0,
        )
        .unwrap();

        assert_eq!(
            structure.to_string(),
            "HexNAc(Hex(Hex(HexNAc(Hex)),Hex(HexNAc),HexNAc))"
        );
    }
    #[test]
    fn correct_structure_g04605kt() {
        let structure = GlycanStructure::from_short_iupac(
            "L-GlcNAc(b1-2)L-Man(a1-3)[GlcNAc(b1-4)][L-Gal(b1-4)GlcNAc(b1-2)L-Man(a1-6)]Man(b1-4)L-GlcNAc(b1-4)GlcNAc(b1-",
            0..108,
            0,
        )
        .unwrap();

        assert_eq!(
            structure.to_string(),
            "HexNAc(HexNAc(Hex(Hex(HexNAc),HexNAc,Hex(HexNAc(Hex)))))"
        );
    }

    #[test]
    fn correct_structure_g67881ee() {
        // Fully specified version of g36564am
        // Furanoses added for error detection
        let structure = GlycanStructure::from_short_iupac(
            "GlcNAc(b1-2)Man(a1-3)[GlcNAc(b1-4)][Galf(b1-4)GlcNAc(b1-2)Man(a1-6)]Man(b1-4)GlcNAc(b1-",
            0..87,
            0,
        )
        .unwrap();

        assert_eq!(
            structure.to_string(),
            "HexNAc(Hex(Hex(HexNAc),HexNAc,Hex(HexNAc(Hexf))))"
        );
    }

    #[test]
    fn correct_structure_g11771hd() {
        let structure = GlycanStructure::from_short_iupac(
            "GlcNAc(?1-?)[GlcNAc(?1-?)]Man(?1-?)[Man(?1-?)Man(?1-?)]Man(?1-?)GlcNAc(?1-?)GlcNAc(?1-",
            0..86,
            0,
        )
        .unwrap();

        assert_eq!(
            structure.to_string(),
            "HexNAc(HexNAc(Hex(Hex(HexNAc,HexNAc),Hex(Hex))))"
        );
    }
}
