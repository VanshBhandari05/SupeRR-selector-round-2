# Audit: Stage 9 (RR pressure gaps, additive)

Run order: `python run_stage9.py` (stage9a gates + variant refits ~12 min, 9b main, 9c sensitivity, 9d cross-check). Parameters in `config_stage9.yaml`;
`config.yaml`, `outputs/top10_*.csv` and every earlier output are untouched (sha256 of config.yaml and both top-10 files match FINAL_LOCK.md).

## Gates (all PASS; none loosened)
- stage9a: position resolved for all 150,307 batter rows; top-20% flag rebuilt from LI equals the pipeline flag on all 306,369 rows;
  replayed bootstrap weights reproduce Stage 5 replicates (max difference 1.4e-8, float32 storage); RR matches (75 of 77; 2 cleaned out) and 61 RR players agree across matches.csv, playing_eleven.csv and ball rows.
- stage9d: independent pandas recomputation of all 10 RR pressure slots equals the engine (max diff 1.4e-16, identical ball counts); dWP0 centred in every Stage-4 bin; slots exhaustive; each RR match has one batting and one bowling innings.
- A first-draft check ("mean adjusted value near 0") failed because it was a wrong assumption; it was replaced by the correct bin-centring check and the reason is recorded in stage9d_crosscheck.py.

## Method as run
- Adjusted value per row: batter row `v + W_j + P*K_j` (bowler's published terms), bowler row `v + B_i + P*C_i` (batter's), using the SAME bootstrap replicate's terms for each resample (opposition uncertainty is inside the intervals). Point estimate uses the published ratings.
- Par: RR cells vs all other IPL teams, same slot and pressure state. Candidate/squad par: all other players of the same competition group (IPL / T20I), same slot, pressure state, own balls removed. Slot excess = mean over the player's balls of (adjusted v - par).
- Slots: batting position bands 1-2, 3-4, 5-6, 7+ (pipeline's batting_position, clipped at 11); bowling phase (overs 1-6, 7-15, 16-20) x pace/spin (supplied field). Ranking uses the 4 + 6 non-overlapping cells; phase and pace/spin marginals are reported in rr_01 but not separately ranked.
- Priority = gap x RR pressure balls per RR innings (a count, not a chosen weight), shown decomposed (gap, balls per innings, product) and also in win-probability points (sum of (adj v - par) x swing per innings).
- Bootstrap: 300 whole-match resamples, same seed and draw order as Stage 5. Variants refit both ridge fits per replicate (penalties fixed) with the flag changed.
- "Supported" candidate cell: >= 40 pressure balls in the slot AND 10th percentile of slot excess above 0 (the rating's own floor convention). Cells under 40 balls are blank.
- Coverage of a gap: a 2026-listed RR player who clears the Stage-5 eligibility flags in that role, has >= 40 slot balls and a supported slot excess.

## Files (outputs/rr_fit/)
rr_00_identification, rr_00_rr_matches_excluded, rr_01_batting_profile, rr_01_bowling_profile, rr_02_gap_ranking, rr_02b_rr_squad_slot_evidence, rr_02c_rr_2026_squad_nationality,
rr_03_candidate_slot_evidence, rr_03_candidate_gap_map, rr_03_candidate_summary, rr_04_sensitivity_* (gap_ranks, gap_summary, names, new_names, names_own_targets, summary),
rr_printed_tables.txt, RR_FINDINGS_NOTE.txt, RR_ABSTENTIONS.txt, terms_*.npz (cached refits), stage9*_log.txt.
