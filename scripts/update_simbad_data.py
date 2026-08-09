#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023 Mattia Verga <mattia.verga@tiscali.it>
# SPDX-License-Identifier: MIT
#
# assisted by: Claude (Anthropic)
"""
update_simbad_data.py
======================

Checks NGC.csv (OpenNGC) against current Simbad data and reports (or
directly applies) updates/corrections/additions for parallax, proper
motion, radial velocity/redshift, angular dimensions and magnitudes.

Unlike a naive script that issues one HTTP request per object (e.g. via
sim-script), this uses Simbad's TAP service with an uploaded table
(TAP_UPLOAD): every object in a batch is resolved and queried with a
SINGLE ADQL query. For the ~14000 objects in NGC.csv this means a few
dozen queries instead of 14000+.

For each object:
  1. one or more "candidate identifiers" are generated: the NGC/IC name
     reformatted to Simbad's convention, any catalog identifiers derived
     from other Name conventions used in OpenNGC's addendum.csv (Barnard,
     Caldwell, Collinder, ESO, HCG, Harvard, Messier, Melotte, MWSC, PGC,
     UGC), any "trusted" identifiers already present in the Identifiers
     column (2MASX, PGC, LBN, MCG, IRAS, UGC, ESO, CGCG, KUG, ZWG, ARP,
     VV, MRK, SDSS, Cl, Mel, MWSC, WDS), and the object's common names
     (queried with the 'NAME ' prefix Simbad uses for proper names);
  2. the candidates are resolved against Simbad through the "ident"
     table;
  3. for every Simbad object found, the angular separation between the
     NGC.csv position and the Simbad position is computed, and whether
     the NGC.csv identifiers appear among the Simbad cross-identifications
     (table "ids") is checked;
  4. a confidence level (HIGH / MEDIUM / LOW / NONE) is assigned based on
     the positional separation and the number of candidate Simbad objects
     (ambiguity);
  5. a FIXED set of Simbad fields is downloaded for every object: Pax,
     Pm-RA, Pm-Dec, RadVel, Redshift (table "basic"), MajAx, MinAx,
     PosAng (basic.galdim_*), B/V/J/H/K-Mag (table "allfluxes");
  6. for each of these fields, the "Sources" column of NGC.csv is
     consulted (it records, per field, the code of the original source;
     code 2 = Simbad):
       - if the field already has a value AND its source is Simbad
         (code 2): it is compared with the new Simbad value and flagged
         if different;
       - if the field is empty in NGC.csv and Simbad has a value: it is
         proposed as an ADDITION, with the corresponding "Field:2" entry
         to add to the Sources column (Sources_new column in the output);
       - if the field already has a value from a source other than
         Simbad: it is left untouched and not compared.

Two files are produced:
  - a review CSV (delimiter ';', numbers with a decimal point and no
    thousands separator, as in NGC.csv) containing ONLY the objects that
    have at least one changed or addable field AND whose identification
    confidence is not HIGH. These need manual review.
  - a full copy of NGC.csv (same columns, same order, same delimiter,
    every original row included) in which objects with HIGH confidence
    have their changed/added fields (and, where relevant, the Sources
    column) updated directly in place. Objects that are not touched, or
    that end up in the review file, are left unchanged in this copy.

Special cases:
  - for PN, GCl and OCl objects that already have a MajAx value,
    MinAx/PosAng are never proposed as additions from Simbad even if
    empty in NGC.csv (for these types, MinAx/PosAng are often not
    meaningful, or not defined the same way, once MajAx has already
    been set from another source);
  - "Cl+N" objects always get a confidence capped at MEDIUM (never
    HIGH), because matching them against a single Simbad otype is too
    subjective to verify automatically;
  - if the three J, H and K magnitudes already in NGC.csv match those of
    the Simbad candidate (within tolerance), this is treated as strong
    evidence that the identification was already manually verified in
    the past, and can raise the confidence to HIGH -- but never above a
    LOW/MEDIUM/HIGH tier warranted by the positional separation, which
    always remains the primary criterion.

This script works on both NGC.csv and OpenNGC's addendum.csv, since the
two files share the same column layout.

Requirements:
    pip install astroquery astropy

Usage:
    python update_simbad_data.py NGC.csv review.csv NGC_updated.csv
"""

import argparse
import csv
import re
import sys
from collections import defaultdict

import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table, vstack
from astroquery.simbad import Simbad

# ----------------------------------------------------------------------
# CONFIGURATION (adjust as needed)
# ----------------------------------------------------------------------

# Object types that have no data of their own (duplicates, groups/pairs/
# triplets of galaxies, non-existent objects, etc.): these are skipped,
# as they have no single Simbad counterpart.
SKIP_TYPES = {"Dup", "Other", "NonEx", "GGroup", "GPair", "GTrpl"}

# "Trusted" identifier prefixes to try as query candidates, in addition
# to the NGC/IC/addendum-derived name. NOTE: in NGC.csv the PGC/LEDA
# catalog is always given with the "PGC" prefix (never "LEDA": they are
# the same catalog, PGC=LEDA), so "LEDA" is not needed here.
PRIORITY_PREFIXES = (
    "PGC", "LBN", "MCG", "UGC", "MWSC",
    "2MASX", "IRAS", "ESO", "CGCG", "KUG", "ZWG", "ARP", "VV", "MRK", "SDSS",
    "Cl", "Mel", "WDS",
)

# Angular separation thresholds (arcsec) for the confidence level
SEP_HIGH = 10.0     # <= : HIGH confidence
SEP_MEDIUM = 60.0   # <= : MEDIUM confidence; beyond: LOW

# ------------------------------------------------------------------
# Mapping between the "Type" field of NGC.csv and Simbad's otype, used
# as an additional signal for identification confidence. The Simbad
# codes used here are documented at
# https://simbad.cds.unistra.fr/guide/otypes.htx (the "AGS All
# Aggregates of Stars" and "AIM All ISM" groupings) and in the NED->
# Simbad mapping table (OpenNGC's Type values mirror NED's
# classification). NOTE: for "Cl+N" and "EmN" an exact match to a
# single Simbad otype is not certain: "EmN" is checked against {"HII",
# "GNe"}; "Cl+N" is not checked against a specific otype at all (see
# TYPES_ALWAYS_MEDIUM below) since it is too subjective.
# ------------------------------------------------------------------
GALAXY_OTYPES = {
    "G", "LSB", "bCG", "SBG", "H2G", "EmG", "AGN", "SyG", "Sy1", "Sy2",
    "rG", "LIN", "QSO", "Bla", "BLL", "GiP", "GiG", "GiC", "BiC", "AG?", "IG",
}
CLUSTER_OTYPES = {"Cl*", "OpC", "GlC", "As*", "St*", "MGr"}
NEBULA_OTYPES = {
    "ISM", "SFR", "HII", "Cld", "GNe", "RNe", "MoC", "DNe",
    "glb", "CGb", "HVC", "cor", "bub", "SNR", "sh", "flt",
}


def _is_star_otype(ot):
    return ot.endswith("*") or ot == "Psr"


# NGC.csv Type -> function checking whether a Simbad otype is compatible
TYPE_CHECKERS = {
    "*": _is_star_otype,
    "**": lambda ot: ot == "**",
    "*Ass": lambda ot: ot == "As*",
    "OCl": lambda ot: ot == "OpC",
    "GCl": lambda ot: ot == "GlC",
    "G": lambda ot: ot in GALAXY_OTYPES,
    "PN": lambda ot: ot == "PN",
    "HII": lambda ot: ot == "HII",
    "DrkN": lambda ot: ot == "DNe",
    "RfN": lambda ot: ot == "RNe",
    "SNR": lambda ot: ot == "SNR",
    "Nova": lambda ot: ot == "No*",
    "Neb": lambda ot: ot in NEBULA_OTYPES,
    "EmN": lambda ot: ot in {"HII", "GNe"},
    # "Cl+N": matching against a single, precise otype is too subjective
    # (a cluster+nebula object may be classified as Cl*, HII, etc.
    # depending on what dominates) to check automatically: for these
    # objects confidence is always capped at MEDIUM anyway (see
    # TYPES_ALWAYS_MEDIUM), to always be reviewed manually.
}

# Types for which identification confidence is always capped at MEDIUM
# (never HIGH), regardless of position/identifiers/otype, because
# matching against Simbad is inherently too subjective to verify
# automatically.
TYPES_ALWAYS_MEDIUM = {"Cl+N"}


# Definition of the fields to download/compare. For each:
#   ngc     -> column name in NGC.csv (and key in the Sources column)
#   simbad  -> name/alias of the corresponding column in the TAP result
#   dec     -> number of fixed decimals in output (with trailing zeros)
#   tol     -> tolerance below which the value is not considered "changed"
FIELD_SPECS = [
    {"ngc": "Pax", "simbad": "plx_value", "dec": 4, "tol": 0.01},          # mas
    {"ngc": "Pm-RA", "simbad": "pmra", "dec": 3, "tol": 0.01},             # mas/yr
    {"ngc": "Pm-Dec", "simbad": "pmdec", "dec": 3, "tol": 0.01},           # mas/yr
    {"ngc": "RadVel", "simbad": "rvz_radvel", "dec": 0, "tol": 0.5},       # km/s
    {"ngc": "Redshift", "simbad": "rvz_redshift", "dec": 6, "tol": 0.00002},
    {"ngc": "MajAx", "simbad": "galdim_majaxis", "dec": 2, "tol": 0.01},   # arcmin
    {"ngc": "MinAx", "simbad": "galdim_minaxis", "dec": 2, "tol": 0.01},   # arcmin
    {"ngc": "PosAng", "simbad": "galdim_angle", "dec": 0, "tol": 1},       # degrees
    {"ngc": "B-Mag", "simbad": "mag_b", "dec": 2, "tol": 0.02},
    {"ngc": "V-Mag", "simbad": "mag_v", "dec": 2, "tol": 0.02},
    {"ngc": "J-Mag", "simbad": "mag_j", "dec": 2, "tol": 0.02},
    {"ngc": "H-Mag", "simbad": "mag_h", "dec": 2, "tol": 0.02},
    {"ngc": "K-Mag", "simbad": "mag_k", "dec": 2, "tol": 0.02},
]

# Number of objects per batch sent to Simbad (to avoid a single,
# oversized query against the TAP service)
BATCH_SIZE = 2000

# ADQL columns requested from Simbad: astrometry/velocity and galaxy
# dimensions from the "basic" table, magnitudes from the "allfluxes"
# table (one row per object, one column per photometric band).
ADQL_TEMPLATE = """
SELECT mt.obj_idx, mt.candidate_id,
       basic.oid, basic.main_id, basic.ra, basic.dec, basic.otype,
       basic.plx_value, basic.pmra, basic.pmdec,
       basic.rvz_radvel, basic.rvz_redshift,
       basic.galdim_majaxis, basic.galdim_minaxis, basic.galdim_angle,
       allfluxes."B" AS mag_b, allfluxes."V" AS mag_v, allfluxes."J" AS mag_j,
       allfluxes."H" AS mag_h, allfluxes."K" AS mag_k,
       ids.ids
FROM TAP_UPLOAD.mytable AS mt
JOIN ident ON ident.id = mt.candidate_id
JOIN basic ON basic.oid = ident.oidref
LEFT JOIN ids ON ids.oidref = basic.oid
LEFT JOIN allfluxes ON allfluxes.oidref = basic.oid
"""

OUTPUT_FIELDS = (
    ["Name", "NGC_Type", "Simbad_OType", "Simbad_MainID", "Confidence", "Separation_arcsec", "N_candidates"]
    + [f"{spec['ngc'].replace('-', '')}_{suffix}" for spec in FIELD_SPECS for suffix in ("old", "new")]
    + ["Updated_fields", "Added_fields", "Sources_new", "Notes"]
)


# ----------------------------------------------------------------------
# Utility
# ----------------------------------------------------------------------

# Catalogs (besides NGC/IC and ESO, handled separately) that appear as a
# prefix of the Name field in addendum.csv: Name prefix -> Simbad
# keyword. Both the zero-stripped number and, when different, the
# originally-padded one are generated as candidates (it is not always
# certain which of the two forms Simbad uses, and including both is
# harmless: candidates that don't resolve simply produce no result).
ADDENDUM_CATALOG_PATTERNS = [
    (re.compile(r"^B(\d+)$"), "Barnard"),
    (re.compile(r"^C(\d+)$"), "Caldwell"),
    (re.compile(r"^Cl(\d+)$"), "Collinder"),
    (re.compile(r"^HCG(\d+)$"), "HCG"),
    (re.compile(r"^H(\d+)$"), "Harvard"),
    (re.compile(r"^Mel(\d+)$"), "Melotte"),
    (re.compile(r"^MWSC(\d+)$"), "MWSC"),
    (re.compile(r"^PGC(\d+)$"), "PGC"),
    (re.compile(r"^UGC(\d+)$"), "UGC"),
    (re.compile(r"^M(\d+)$"), "M"),  # Messier: try last (more generic prefix)
]


def name_to_simbad_candidates(name):
    """Converts the Name field of NGC.csv/addendum.csv into one or more
    forms Simbad may recognize: 'NGC0001'/'IC0001A' -> 'NGC 1'/'IC 1A';
    'ESO056-115' -> 'ESO 056-115'; 'B033' -> 'Barnard 33'; 'C009' ->
    'Caldwell 9'; 'Cl399' -> 'Collinder 399'; 'PGC000143' -> 'PGC 143'
    (+ 'PGC 000143'); etc."""
    name = name.strip()

    m = re.match(r"^(IC|NGC)0*(\d+)([A-Za-z]*)$", name)
    if m:
        prefix, num, suffix = m.groups()
        return [f"{prefix} {num}{suffix}"]

    m = re.match(r"^ESO(\d+)-(\d+)$", name)
    if m:
        return [f"ESO {m.group(1)}-{m.group(2)}"]

    for pattern, word in ADDENDUM_CATALOG_PATTERNS:
        m = pattern.match(name)
        if m:
            digits = m.group(1)
            stripped = digits.lstrip("0") or "0"
            candidates = [f"{word} {stripped}"]
            if digits != stripped:
                candidates.append(f"{word} {digits}")
            return candidates

    return [name]


def candidate_identifiers(name, identifiers_field, common_names_field=""):
    """List (deduplicated) of candidate identifiers to look up on Simbad:
    the name(s) derived from the Name field, the "trusted" identifiers
    already present in Identifiers, and the common names (queried with
    the 'NAME ' prefix Simbad uses for proper names)."""
    candidates = list(name_to_simbad_candidates(name))
    if identifiers_field:
        for ident in identifiers_field.split(","):
            ident = ident.strip()
            if ident.startswith(PRIORITY_PREFIXES):
                candidates.append(ident)
    if common_names_field:
        for cname in common_names_field.split(","):
            cname = cname.strip()
            if cname:
                candidates.append(f"NAME {cname}")
    seen, ordered = set(), []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            ordered.append(c)
    return ordered


def parse_coords(ra_str, dec_str):
    """NGC.csv sexagesimal RA/Dec ('00:08:27.05', '+27:43:03.6') -> degrees."""
    try:
        c = SkyCoord(ra=ra_str, dec=dec_str, unit=(u.hourangle, u.deg))
        return c.ra.deg, c.dec.deg
    except Exception:
        return None, None


def to_float(value):
    if value is None:
        return None
    s = str(value).strip()
    if s == "" or s.lower() == "--" or s.lower() == "nan" or s.lower() == "masked":
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    if f != f:  # NaN
        return None
    return f


def values_differ(old, new, tol):
    if old is None and new is None:
        return False
    if old is None or new is None:
        return True
    return abs(old - new) > tol


def jhk_match(old_j, old_h, old_k, new_j, new_h, new_k, tol=0.02):
    """True if the three J, H and K magnitudes match (within tolerance)
    between the value already in NGC.csv and the Simbad candidate's. If
    all three match, it is strong evidence that the identification had
    already been manually verified in the past."""
    for old_v, new_v in ((old_j, new_j), (old_h, new_h), (old_k, new_k)):
        if old_v is None or new_v is None:
            return False
        if abs(old_v - new_v) > tol:
            return False
    return True


def fmt_fixed(value, decimals):
    """Rounds to a fixed number of decimals, keeping trailing zeros
    (used for Pax: 4 decimals, Redshift: 6 decimals, RadVel: 0 decimals)."""
    if value is None:
        return ""
    return f"{value:.{decimals}f}"


def parse_sources(sources_field):
    """'Type:1|RA:1|...|RadVel:2' -> {'Type': '1', 'RA': '1', ..., 'RadVel': '2'}"""
    d = {}
    if not sources_field:
        return d
    for pair in sources_field.split("|"):
        if ":" in pair:
            key, value = pair.split(":", 1)
            d[key.strip()] = value.strip()
    return d


# Column order in NGC.csv: entries in the Sources column follow this
# same order, so newly added entries must be reinserted in the right
# position rather than simply appended at the end.
NGC_COLUMN_ORDER = [
    "Name", "Type", "RA", "Dec", "Const", "MajAx", "MinAx", "PosAng",
    "B-Mag", "V-Mag", "J-Mag", "H-Mag", "K-Mag", "SurfBr", "Hubble",
    "Pax", "Pm-RA", "Pm-Dec", "RadVel", "Redshift",
    "Cstar U-Mag", "Cstar B-Mag", "Cstar V-Mag", "M", "NGC", "IC",
    "Cstar Names", "Identifiers", "Common names", "NED notes", "OpenNGC notes",
]
_COLUMN_ORDER_INDEX = {name: i for i, name in enumerate(NGC_COLUMN_ORDER)}


def build_sources_new(original_sources_field, added_fields):
    """Adds 'Field:2' for every field in 'added_fields' to the original
    Sources string, preserving existing entries and reordering the
    result according to NGC.csv's column order (as in the original)."""
    fields = parse_sources(original_sources_field)
    for field in added_fields:
        fields[field] = "2"
    ordered_keys = sorted(fields, key=lambda f: _COLUMN_ORDER_INDEX.get(f, len(NGC_COLUMN_ORDER)))
    return "|".join(f"{key}:{fields[key]}" for key in ordered_keys)


# ----------------------------------------------------------------------
# Reading NGC.csv and building the table to upload to Simbad
# ----------------------------------------------------------------------

def load_ngc(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)
        fieldnames = reader.fieldnames
    return rows, fieldnames


def build_query_plan(rows):
    """
    Returns:
      - upload_rows: list of (obj_idx, candidate_id) to upload to Simbad
      - idx_map: obj_idx -> (NGC.csv row, csv_ra_deg, csv_dec_deg)
    Skips composite objects (SKIP_TYPES) and those with unparseable
    coordinates.
    """
    upload_rows = []
    idx_map = {}
    n_skipped_type = 0
    n_skipped_coord = 0

    for i, row in enumerate(rows):
        if row.get("Type") in SKIP_TYPES:
            n_skipped_type += 1
            continue
        ra_deg, dec_deg = parse_coords(row.get("RA", ""), row.get("Dec", ""))
        if ra_deg is None:
            n_skipped_coord += 1
            continue
        idx_map[i] = (row, ra_deg, dec_deg)
        for cand in candidate_identifiers(row["Name"], row.get("Identifiers", ""), row.get("Common names", "")):
            upload_rows.append((i, cand))

    print(
        f"Objects in input file: {len(rows)} | skipped (composite type): "
        f"{n_skipped_type} | skipped (invalid coordinates): {n_skipped_coord} "
        f"| to be queried: {len(idx_map)} ({len(upload_rows)} candidate identifiers)",
        file=sys.stderr,
    )
    return upload_rows, idx_map


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def query_simbad_batches(upload_rows, batch_size=BATCH_SIZE):
    """Runs the TAP query in batches and concatenates the results."""
    results = []
    batches = list(chunked(upload_rows, batch_size))
    for n, batch in enumerate(batches, start=1):
        obj_idx = [b[0] for b in batch]
        candidate_id = [b[1] for b in batch]
        upload_table = Table([obj_idx, candidate_id], names=["obj_idx", "candidate_id"])
        print(f"Batch {n}/{len(batches)}: {len(batch)} identifiers...", file=sys.stderr)
        res = Simbad.query_tap(ADQL_TEMPLATE, mytable=upload_table)
        if res is not None and len(res) > 0:
            results.append(res)
    if not results:
        return Table()
    return vstack(results, metadata_conflicts="silent")


# ----------------------------------------------------------------------
# Analyzing the results and comparing them against NGC.csv
# ----------------------------------------------------------------------

def analyze(simbad_result, idx_map):
    by_obj = defaultdict(list)
    for r in simbad_result:
        by_obj[int(r["obj_idx"])].append(r)

    output_rows = []
    high_updated_names = []

    for i, (row, csv_ra, csv_dec) in idx_map.items():
        name = row["Name"]
        matches = by_obj.get(i, [])
        csv_pos = SkyCoord(csv_ra * u.deg, csv_dec * u.deg)

        # All identifiers already known for the object in NGC.csv (not
        # just the "trusted" ones used as query candidates): used to
        # confirm/disambiguate the match, as requested.
        csv_idents = {x.strip() for x in row.get("Identifiers", "").split(",") if x.strip()}

        # J/H/K magnitudes already present in NGC.csv: if they match
        # those of the Simbad candidate, it is a strong indication that
        # the identification had already been manually verified in the
        # past.
        old_j = to_float(row.get("J-Mag"))
        old_h = to_float(row.get("H-Mag"))
        old_k = to_float(row.get("K-Mag"))

        # Dedup by Simbad oid, keeping the smallest separation found and
        # computing whether the NGC.csv identifiers appear among that
        # object's Simbad cross-identifications (ids.ids), as well as
        # the J/H/K magnitude match
        by_oid = {}
        for m in matches:
            oid = int(m["oid"])
            m_ra = to_float(m["ra"])
            m_dec = to_float(m["dec"])
            if m_ra is None or m_dec is None:
                continue
            sep = csv_pos.separation(SkyCoord(m_ra * u.deg, m_dec * u.deg)).arcsec
            ids_field_m = str(m["ids"]) if m["ids"] is not None else ""
            simbad_idents_m = {x.strip() for x in re.split(r"[|,]", ids_field_m) if x.strip()}
            id_overlap = bool(csv_idents & simbad_idents_m)
            jhk_ok = jhk_match(old_j, old_h, old_k, to_float(m["mag_j"]), to_float(m["mag_h"]), to_float(m["mag_k"]))
            if oid not in by_oid or sep < by_oid[oid][0]:
                by_oid[oid] = (sep, m, id_overlap, jhk_ok)

        note_parts = []
        best = None
        best_sep = None

        if not by_oid:
            confidence = "NONE"
            note_parts.append("no match found on Simbad")
        else:
            n_candidates = len(by_oid)
            oids_with_overlap = [oid for oid, (sep, m, ov, jm) in by_oid.items() if ov]
            oids_with_jhk = [oid for oid, (sep, m, ov, jm) in by_oid.items() if jm]
            oids_confirmed = set(oids_with_overlap) | set(oids_with_jhk)

            if n_candidates == 1:
                # a single Simbad object found: no ambiguity.
                # The positional separation remains the primary
                # criterion: JHK/cross-identifiers can raise a
                # separation within SEP_MEDIUM to HIGH at most, never
                # beyond it.
                best_oid, (best_sep, best, best_overlap, best_jhk) = next(iter(by_oid.items()))
                if best_sep <= SEP_HIGH:
                    confidence = "HIGH"
                elif best_sep <= SEP_MEDIUM and best_jhk:
                    confidence = "HIGH"
                    note_parts.append(
                        f'positional separation {best_sep:.1f}" but J/H/K magnitudes match NGC.csv: '
                        "probable identification already manually verified in the past"
                    )
                elif best_sep <= SEP_MEDIUM and best_overlap:
                    confidence = "HIGH"
                    note_parts.append(
                        f'positional separation {best_sep:.1f}" but confirmed by cross-identifiers '
                        "between NGC.csv and Simbad"
                    )
                elif best_sep <= SEP_MEDIUM:
                    confidence = "MEDIUM"
                    note_parts.append(f'positional separation {best_sep:.1f}"')
                else:
                    confidence = "LOW"
                    note_parts.append(f'large positional separation: {best_sep:.1f}"')
                    if best_jhk:
                        note_parts.append(
                            "J/H/K magnitudes match, but the positional separation is too large to "
                            "trust: needs checking"
                        )
                    if not best_overlap and csv_idents:
                        note_parts.append("none of the NGC.csv identifiers found among the Simbad cross-ids")
            elif len(oids_confirmed) == 1:
                # several candidate Simbad objects, but only one is
                # confirmed by cross-identifiers and/or JHK match. Here
                # too the separation remains the primary criterion: the
                # confirmation can only raise confidence to HIGH within
                # SEP_MEDIUM, otherwise confidence stays low despite the
                # confirmation.
                best_oid = next(iter(oids_confirmed))
                best_sep, best, best_overlap, best_jhk = by_oid[best_oid]
                if best_sep <= SEP_MEDIUM and best_jhk:
                    confidence = "HIGH"
                    note_parts.append(
                        f"ambiguous identifier ({n_candidates} candidate Simbad objects) resolved via "
                        "J/H/K magnitude match: probable identification already manually verified "
                        "in the past"
                    )
                elif best_sep <= SEP_MEDIUM:
                    # resolved only via cross-identifiers: confidence is
                    # capped at MEDIUM (never HIGH) because in practice
                    # these cases have often turned out to be wrong
                    # matches: always to be reviewed manually.
                    confidence = "MEDIUM"
                    note_parts.append(
                        f"ambiguous identifier ({n_candidates} candidate Simbad objects) resolved via "
                        "NGC.csv cross-identifiers (confidence capped at MEDIUM for manual review)"
                    )
                else:
                    confidence = "LOW"
                    note_parts.append(
                        f"ambiguous identifier ({n_candidates} candidate Simbad objects) resolved via "
                        f"{'J/H/K magnitudes' if best_jhk else 'NGC.csv cross-identifiers'}, but the "
                        f'positional separation is large ({best_sep:.1f}"): needs manual review'
                    )
            else:
                # unresolvable ambiguity: none, or more than one, of the
                # candidates is confirmed by cross-identifiers/JHK ->
                # pick the closest by position but flag for manual
                # review
                best_oid, (best_sep, best, _, _) = min(by_oid.items(), key=lambda kv: kv[1][0])
                confidence = "LOW"
                if oids_confirmed:
                    note_parts.append(
                        f"ambiguous identifier: {n_candidates} candidate Simbad objects, "
                        f"{len(oids_confirmed)} confirmed by cross-identifiers or JHK magnitudes "
                        "(conflicting confirmations among several candidates)"
                    )
                else:
                    note_parts.append(f"ambiguous identifier: {n_candidates} candidate Simbad objects")

        main_id = str(best["main_id"]) if best is not None else ""
        ngc_type = row.get("Type", "")
        simbad_otype = str(best["otype"]) if best is not None and best["otype"] is not None else ""
        if simbad_otype.lower() in ("", "--", "nan", "masked"):
            simbad_otype = ""

        # Check consistency between the NGC.csv object type and the
        # Simbad otype: if incompatible, it is a strong sign of a wrong
        # identification, so confidence is capped at MEDIUM even if
        # position and/or cross-identifiers seemed to agree.
        type_checker = TYPE_CHECKERS.get(ngc_type)
        if best is not None and simbad_otype and type_checker is not None and not type_checker(simbad_otype):
            if confidence == "HIGH":
                confidence = "MEDIUM"
            note_parts.append(
                f"NGC.csv type '{ngc_type}' not compatible with Simbad otype '{simbad_otype}' "
                "(confidence capped at MEDIUM for manual review)"
            )

        if best is not None and ngc_type in TYPES_ALWAYS_MEDIUM and confidence == "HIGH":
            confidence = "MEDIUM"
            note_parts.append(
                f"NGC.csv type '{ngc_type}': matching against Simbad is too subjective to verify "
                "automatically (confidence capped at MEDIUM for manual review)"
            )

        sources = parse_sources(row.get("Sources", ""))
        # PN, GCl and OCl objects: if MajAx is already known, MinAx/PosAng
        # are not added from Simbad even if missing in NGC.csv (for these
        # types, MinAx/PosAng are often not meaningful, or not defined the
        # same way, once MajAx has already been set from another source).
        is_dim_exempt_type_with_majax = (
            row.get("Type") in ("PN", "GCl", "OCl") and to_float(row.get("MajAx")) is not None
        )
        is_reliable = confidence == "HIGH"

        changed_fields = []
        added_fields = []
        high_changed_fields = []
        high_added_fields = []
        skipped_dim_fields = []
        field_values = {}

        for spec in FIELD_SPECS:
            ngc_col = spec["ngc"]
            out_key = ngc_col.replace("-", "")
            old_val = to_float(row.get(ngc_col))
            new_val = to_float(best[spec["simbad"]]) if best is not None else None
            new_fmt = fmt_fixed(new_val, spec["dec"])

            # old/new are written to the review output ONLY for fields
            # that actually end up in added_fields/changed_fields below
            # (i.e. actionable ones): fields left untouched because their
            # value comes from a source other than Simbad, or because old
            # and new already match, are left blank to avoid confusion
            # with the Updated_fields/Added_fields columns.

            if old_val is None and new_val is not None:
                if ngc_col in ("MinAx", "PosAng") and is_dim_exempt_type_with_majax:
                    # MajAx already known for this type: MinAx/PosAng are
                    # not added from Simbad even if missing in NGC.csv
                    skipped_dim_fields.append(ngc_col)
                elif is_reliable:
                    # HIGH confidence: the addition is applied directly
                    # to the NGC.csv copy (row is the same dict object
                    # as in 'rows')
                    row[ngc_col] = new_fmt
                    high_added_fields.append(ngc_col)
                else:
                    # field missing in NGC.csv, present on Simbad ->
                    # proposed as an addition
                    added_fields.append(ngc_col)
                    field_values[f"{out_key}_old"] = ""
                    field_values[f"{out_key}_new"] = new_fmt
            elif sources.get(ngc_col) == "2" and values_differ(old_val, new_val, spec["tol"]):
                if is_reliable:
                    row[ngc_col] = new_fmt
                    high_changed_fields.append(ngc_col)
                else:
                    # field already sourced from Simbad, value changed
                    changed_fields.append(ngc_col)
                    field_values[f"{out_key}_old"] = fmt_fixed(old_val, spec["dec"])
                    field_values[f"{out_key}_new"] = new_fmt
            # otherwise: value present from a different source (left
            # untouched), or both empty, or Simbad-sourced and
            # unchanged -> no action, old/new left blank in the review
            # output (field_values has no entry for this field)

        if high_added_fields:
            # update the Sources column of the NGC.csv copy with the new fields
            row["Sources"] = build_sources_new(row.get("Sources", ""), high_added_fields)
        if high_changed_fields or high_added_fields:
            high_updated_names.append(name)

        sources_new = ""
        if added_fields:
            sources_new = build_sources_new(row.get("Sources", ""), added_fields)
        if changed_fields:
            note_parts.append("Simbad fields changed: " + ", ".join(changed_fields))
        if added_fields:
            note_parts.append("fields addable from Simbad: " + ", ".join(added_fields))
        if skipped_dim_fields:
            note_parts.append(
                f"{ngc_type} with MajAx already present, not added from Simbad: "
                + ", ".join(skipped_dim_fields)
            )

        if changed_fields or added_fields:
            output_rows.append(
                {
                    "Name": name,
                    "NGC_Type": ngc_type,
                    "Simbad_OType": simbad_otype,
                    "Simbad_MainID": main_id,
                    "Confidence": confidence,
                    "Separation_arcsec": f"{best_sep:.2f}" if best_sep is not None else "",
                    "N_candidates": len(by_oid),
                    **field_values,
                    "Updated_fields": ", ".join(changed_fields),
                    "Added_fields": ", ".join(added_fields),
                    "Sources_new": sources_new,
                    "Notes": "; ".join(note_parts),
                }
            )

    return output_rows, high_updated_names


def write_output(output_rows, path):
    # lineterminator="\n" forces Unix line endings: the csv module
    # otherwise defaults to "\r\n" regardless of the OS it runs on.
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)


def write_ngc_updated(rows, fieldnames, path):
    """Writes a full copy of NGC.csv (same columns, same order, same
    delimiter) with the updates/additions applied in-place (see
    analyze()) for objects with HIGH confidence."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", nargs="?", default="NGC.csv", help="Path to NGC.csv (or addendum.csv)")
    parser.add_argument(
        "output_csv",
        nargs="?",
        default="simbad_review.csv",
        help="Review CSV output (only objects with MEDIUM confidence or lower)",
    )
    parser.add_argument(
        "updated_ngc_csv",
        nargs="?",
        default="NGC_updated.csv",
        help="Copy of the input file with updates applied directly (HIGH confidence objects only)",
    )
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Objects per TAP batch (default: %(default)s)")
    args = parser.parse_args()

    rows, fieldnames = load_ngc(args.input_csv)
    upload_rows, idx_map = build_query_plan(rows)

    if not upload_rows:
        print("No objects to query.", file=sys.stderr)
        return

    simbad_result = query_simbad_batches(upload_rows, batch_size=args.batch_size)
    print(f"Total rows returned by Simbad: {len(simbad_result)}", file=sys.stderr)

    # analyze() modifies 'rows' in place for HIGH-confidence objects
    # (the same dict objects are shared with idx_map)
    output_rows, high_updated_names = analyze(simbad_result, idx_map)

    write_output(output_rows, args.output_csv)
    write_ngc_updated(rows, fieldnames, args.updated_ngc_csv)

    print(
        f"Objects updated directly in {args.updated_ngc_csv} (HIGH confidence): "
        f"{len(high_updated_names)}",
        file=sys.stderr,
    )
    print(
        f"Objects written to {args.output_csv} for manual review "
        f"(MEDIUM confidence or lower): {len(output_rows)}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
