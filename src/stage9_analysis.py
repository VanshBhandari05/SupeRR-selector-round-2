"""Stage 9 analysis functions: RR cells, gap ranking, candidate / squad slot evidence. Pure functions of an Engine (one pressure-flag variant)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage9_common import *

MIN_N = C9["min_slot_pressure_balls"]
SLOTS = {"bat": BAT_SLOTS, "bowl": BOWL_SLOTS}
SIDE = {"bat": "batting", "bowl": "bowling"}
# marginal splits requested for bowling (overlap the fine cells; reported, not separately ranked)
BOWL_MARGINALS = {**{f"phase:{p}": [2 * i, 2 * i + 1] for i, p in enumerate(PHASE_NAMES)}, **{f"type:{t}": [j, 2 + j, 4 + j] for j, t in enumerate(TYPE_NAMES)}, "all bowling": list(range(6))}
BAT_MARGINALS = {"all batting": list(range(4))}


def cell_stats(E, role, slots, P):
    """RR vs rest-of-IPL for one slot set and pressure state; returns dict of replicate arrays."""
    rr = E.sums(role, E.mask(role, rr=1, slot=slots, P=P)); rest = E.sums(role, E.mask(role, rr=0, grp=0, slot=slots, P=P))
    rr_mean = rr["S"] / rr["W"]; par = rest["S"] / rest["W"]
    return dict(rr_n=rr["NB"], rr_mean=rr_mean, par=par, gap=rr_mean - par, per_inn=rr["NB"] / E.n_inn,
                prio_v=(rr_mean - par) * rr["NB"] / E.n_inn, prio_wp=(rr["SSW"] - par * rr["SW"]) / E.n_inn, par_n=rest["NB"])


def rr_profile(E):
    """Item 1: every RR cell (fine slots + marginals), pressure and ordinary, with intervals, and the pressure-minus-ordinary shift."""
    recs = []
    for role in ("bat", "bowl"):
        sets = {s: [i] for i, s in enumerate(SLOTS[role])}
        sets.update(BAT_MARGINALS if role == "bat" else BOWL_MARGINALS)
        for name, sl in sets.items():
            cs = {P: cell_stats(E, role, sl, P) for P in (0, 1)}
            fine = name in SLOTS[role]
            for P in (1, 0):
                c = cs[P]; iv = interval(c["gap"])
                recs.append(dict(side=SIDE[role], slot=name, slot_kind="cell" if fine else "marginal (overlaps cells)", state="pressure" if P else "ordinary",
                                 rr_balls=int(round(c["rr_n"][0])), rr_balls_per_innings=c["per_inn"][0], rr_value_per_ball=c["rr_mean"][0], league_par_per_ball=c["par"][0], par_balls=int(round(c["par_n"][0])),
                                 gap_vs_par=iv["est"], gap_p10=iv["p10"], gap_p90=iv["p90"], gap_p025=iv["p025"], gap_p975=iv["p975"], p_gap_below0=iv["p_below0"], call=verdict(iv)))
            sh = interval(cs[1]["gap"] - cs[0]["gap"])
            recs.append(dict(side=SIDE[role], slot=name, slot_kind="cell" if fine else "marginal (overlaps cells)", state="shift (pressure gap - ordinary gap)", rr_balls=int(round(cs[1]["rr_n"][0])),
                             gap_vs_par=sh["est"], gap_p10=sh["p10"], gap_p90=sh["p90"], gap_p025=sh["p025"], gap_p975=sh["p975"], p_gap_below0=sh["p_below0"], call=verdict(sh).replace("par", "zero shift")))
    return pd.DataFrame(recs)


def gap_ranking(E):
    """Item 2: rank the 10 non-overlapping slots (4 batting bands + 6 bowling phase x type cells) by pressure gap x pressure balls per RR innings."""
    recs = []
    for role in ("bat", "bowl"):
        for i, s in enumerate(SLOTS[role]):
            c = cell_stats(E, role, [i], 1)
            recs.append(dict(role=role, side=SIDE[role], slot=s, c=c))
    prio = np.vstack([r["c"]["prio_v"] for r in recs])                         # (10, R+1)
    ranks = prio[:, 1:].argsort(0).argsort(0) + 1                              # 1 = most negative priority in that replicate
    out = []
    for k, r in enumerate(recs):
        c = r["c"]; g = interval(c["gap"]); pv = interval(c["prio_v"]); pw = interval(c["prio_wp"])
        out.append(dict(side=r["side"], slot=r["slot"], rr_pressure_balls=int(round(c["rr_n"][0])), rr_pressure_balls_per_innings=c["per_inn"][0], rr_value_per_ball=c["rr_mean"][0], league_par_per_ball=c["par"][0],
                        gap_vs_par=g["est"], gap_p10=g["p10"], gap_p90=g["p90"], gap_p025=g["p025"], gap_p975=g["p975"], p_gap_below0=g["p_below0"], gap_call=verdict(g),
                        priority_value_per_innings=pv["est"], priority_p10=pv["p10"], priority_p90=pv["p90"],
                        winprob_vs_par_per_innings=pw["est"], winprob_p10=pw["p10"], winprob_p90=pw["p90"],
                        boot_rank_p10=float(np.quantile(ranks[k], 0.1)), boot_rank_p90=float(np.quantile(ranks[k], 0.9)), p_in_boot_top3=float((ranks[k] <= 3).mean())))
    df = pd.DataFrame(out)
    df["distinguishable_below_par_80"] = (df.gap_p90 < 0)
    df["distinguishable_below_par_95"] = (df.gap_p975 < 0)
    # only slots whose point estimate is below par are gaps; they are ranked by pressure-gap x pressure-balls-per-innings (most negative first).
    # Whether each one is distinguishable from par is carried beside the rank, never used to hide or reorder it.
    below = df[df.priority_value_per_innings < 0].sort_values("priority_value_per_innings")
    df["rank_below_par_slots"] = np.nan
    df.loc[below.index, "rank_below_par_slots"] = np.arange(1, len(below) + 1)
    return df.sort_values(["rank_below_par_slots", "priority_value_per_innings"]).reset_index(drop=True)


def target_slots(gr, n=None):
    """Slots handed to the candidate mapping: the top n below-par slots by priority (with their evidence status kept alongside)."""
    n = n or C9["n_gap_slots_for_mapping"]
    t = gr[gr.rank_below_par_slots.notna()].sort_values("rank_below_par_slots").head(n)
    return [(("bat" if r.side == "batting" else "bowl"), r.slot) for r in t.itertuples()]


class PlayerEvidence:
    """Slot-level opposition-adjusted pressure excess for any player: mean over their pressure balls in the slot of (adj v - rest-of-league par for that
    competition group, slot, pressure state). Par excludes the player's own balls. Whole-match bootstrap interval; suppressed below MIN_N balls."""

    def __init__(self, E):
        self.E = E; self.tot = {}
        for role in ("bat", "bowl"):
            for g in (0, 1):
                for s in range(len(SLOTS[role])):
                    self.tot[(role, g, s)] = E.sums(role, E.mask(role, grp=g, slot=s, P=1))

    def eval(self, role, pid, slot_ids):
        E = self.E; own = np.searchsorted(E.d.all_bat if role == "bat" else E.d.all_bowl, pid)
        nr = E.Wm.shape[0]
        num = np.zeros(nr); numw = np.zeros(nr); den = np.zeros(nr); nb = {0: 0.0, 1: 0.0}
        for g in (0, 1):
            for s in slot_ids:
                c = E.sums(role, E.mask(role, own=own, grp=g, slot=s, P=1)); t = self.tot[(role, g, s)]
                with np.errstate(invalid="ignore", divide="ignore"):
                    par = (t["S"] - c["S"]) / (t["W"] - c["W"])
                par = np.nan_to_num(par)
                num += c["S"] - par * c["W"]; numw += c["SSW"] - par * c["SW"]; den += c["W"]; nb[g] += c["NB"][0]
        with np.errstate(invalid="ignore", divide="ignore"):
            ex = num / den; exw = 100 * numw / den
        return dict(n_ipl=int(round(nb[0])), n_t20i=int(round(nb[1])), n=int(round(nb[0] + nb[1])), ex=ex, exw=exw)

    def row(self, role, pid, slot_ids, label):
        r = self.eval(role, pid, slot_ids); n = r["n"]
        rec = dict(slot=label, n_pressure_balls=n, n_ipl=r["n_ipl"], n_t20i=r["n_t20i"])
        rec["slot_record"] = "none" if n == 0 else ("IPL-only" if r["n_t20i"] == 0 else ("T20I-only" if r["n_ipl"] == 0 else "both"))
        if n < MIN_N:
            rec.update(suppressed=True, note=f"suppressed: {n} pressure balls < {MIN_N}")
            for k in ("excess_per_ball", "p10", "p90", "p025", "p975", "p_above0", "excess_winprob_per_100_balls"): rec[k] = np.nan
            rec["supported"] = False
        else:
            iv = interval(r["ex"]); ivw = interval(r["exw"])
            rec.update(suppressed=False, note="", excess_per_ball=iv["est"], p10=iv["p10"], p90=iv["p90"], p025=iv["p025"], p975=iv["p975"], p_above0=1 - iv["p_below0"],
                       excess_winprob_per_100_balls=ivw["est"], supported=bool(iv["p10"] > 0))
        return rec


def nationality_table():
    mp = pd.read_csv(ROOT / "competition_team_player_mapping.csv"); comps = pd.read_csv(ROOT / "competitions.csv")
    mp = mp.merge(comps[["comp_id", "match_format"]], on="comp_id")
    t20i = mp[mp.match_format == "T20I"]
    nat = t20i.groupby("player_id").team_name.agg(lambda s: sorted(set(s)))
    ateam = mp[mp.comp_id.isin(CFG["competition"]["ateam_comp_ids"])].groupby("player_id").team_name.agg(lambda s: sorted(set(s)))
    out = {}
    for pid in mp.player_id.unique():
        if pid in nat.index:
            teams = nat[pid]
            out[pid] = ("India" if teams == ["India"] else (teams[0] if len(teams) == 1 else "ambiguous: " + "/".join(teams)), "T20I squad listing")
        elif pid in ateam.index and all(x.endswith(" A") for x in ateam[pid]):
            out[pid] = (ateam[pid][0][:-2], "A-team listing only")
        else:
            out[pid] = (None, "")
    return out


def nat_class(n):
    if n is None: return "not in supplied data"
    if n.startswith("ambiguous"): return "not in supplied data"
    return "Indian" if n == "India" else "overseas"


# ---------------------------------------------------------------- candidates and RR squad
def load_candidates():
    """Top 20 batters and bowlers exactly as ranked by Stage 7 (eligible_table_*.csv rank column). No re-ranking."""
    names = pd.read_csv(ROOT / "competition_team_player_mapping.csv").drop_duplicates("player_id").set_index("player_id").player_name
    out = []
    for role, f in (("bat", "eligible_table_batters.csv"), ("bowl", "eligible_table_bowlers.csv")):
        t = pd.read_csv(OUT / f); t = t[t["rank"] <= C9["top_n_candidates"]]
        for r in t.itertuples():
            out.append(dict(role=role, rank=int(r.rank), player_id=int(r.player_id), name=names[r.player_id], pressure_rating=r.pressure_rating, floor_p10=r.floor_p10,
                            pressure_balls_overall=int(r.balls_P if role == "bat" else r.deliveries_P), matches_pressure=int(r.matches_P)))
    return pd.DataFrame(out)


def rr_membership():
    mp = pd.read_csv(ROOT / "competition_team_player_mapping.csv")
    teams = pd.read_csv(ROOT / "teams.csv"); rr_id = int(teams[teams.team_name == C9["rr"]["team_name"]].team_id.unique().item())
    sq26 = set(mp[(mp.team_id == rr_id) & (mp.comp_id == C9["rr"]["squad_comp_id"])].player_id)
    anyrr = set(mp[(mp.team_id == rr_id) & mp.comp_id.isin(CFG["competition"]["ipl_comp_ids"])].player_id)
    return rr_id, sq26, anyrr


def evidence_long(E, PE, people):
    """people: DataFrame with player_id (and optional list_role). One row per (person, slot_role, slot) plus a slot-mix-adjusted overall row per slot_role.
    Evaluated in BOTH roles (a bowler's batting slots and a batter's bowling slots count); a person absent from a role's rating rows gets no rows there."""
    recs = []
    ids = {"bat": set(E.d.all_bat), "bowl": set(E.d.all_bowl)}
    for p in people.itertuples():
        for role in ("bat", "bowl"):
            if p.player_id not in ids[role]: continue
            slots = SLOTS[role]
            for i, s in enumerate(slots):
                r = PE.row(role, p.player_id, [i], s); r.update(slot_role=role, player_id=p.player_id); recs.append(r)
            r = PE.row(role, p.player_id, list(range(len(slots))), "ALL pressure balls (slot-mix adjusted)"); r.update(slot_role=role, player_id=p.player_id); recs.append(r)
    return pd.DataFrame(recs)


# ---------------------------------------------------------------- shared context + items 2-3 as functions (used by main and by the sensitivity run)
class Ctx:
    def __init__(self, D):
        self.D = D
        mp = pd.read_csv(ROOT / "competition_team_player_mapping.csv")
        self.names = mp.drop_duplicates("player_id").set_index("player_id").player_name
        self.nat = nationality_table()
        self.rr_id, self.sq26, self.anyrr = rr_membership()
        self.cands = load_candidates().rename(columns={"role": "list_role", "rank": "list_rank"})
        self.ppl_c = self.cands[["player_id"]].drop_duplicates()
        self.ppl_s = pd.DataFrame({"player_id": sorted(self.sq26)})

    def decorate(self, ev):
        ev = ev.copy()
        ev["name"] = ev.player_id.map(self.names)
        ev["nationality"] = ev.player_id.map(lambda p: self.nat.get(p, (None, ""))[0] or "not in supplied data")
        ev["nationality_class"] = ev.player_id.map(lambda p: nat_class(self.nat.get(p, (None, ""))[0]))
        for role in ("bat", "bowl"):
            r = self.D.ratings[role].set_index("player_id"); m = ev.slot_role == role
            ev.loc[m, "clears_gates_in_slot_role"] = ev[m].player_id.map(lambda p: bool(r.eligible.get(p, False) and r.active.get(p, False)))
        ev["rr_2026_squad"] = ev.player_id.isin(self.sq26); ev["rr_any_ipl_2022_26"] = ev.player_id.isin(self.anyrr)
        return ev


def coverage(gr, sq_ev):
    cov = []
    fmt = lambda t: "; ".join(f"{a.name} (n={a.n_pressure_balls}, excess {a.excess_per_ball:+.3f}, p10 {a.p10:+.3f})" for a in t.itertuples()) or "none"
    for r in gr.itertuples():
        role = "bat" if r.side == "batting" else "bowl"
        s = sq_ev[(sq_ev.slot_role == role) & (sq_ev.slot == r.slot)]; enough = s[~s.suppressed]
        gate_ok = enough[enough.clears_gates_in_slot_role == True]; sup = gate_ok[gate_ok.supported]
        status = ("COVERED" if len(sup) else ("OPEN: squad gate-clearer has slot sample but is not shown above par" if len(gate_ok) else "OPEN: no gate-clearing squad player with a slot sample"))
        cov.append(dict(coverage_status=status, squad_gate_clearers_with_slot_sample=fmt(gate_ok), squad_with_slot_sample_not_clearing_gates=fmt(enough[enough.clears_gates_in_slot_role != True])))
    return pd.concat([gr.reset_index(drop=True), pd.DataFrame(cov)], axis=1)


def gap_map(gr, ev, tg):
    gm_ = {(("bat" if r.side == "batting" else "bowl"), r.slot): r for r in gr.itertuples()}
    rows = []
    for role, slot in tg:
        g = gm_[(role, slot)]
        s = ev[(ev.slot_role == role) & (ev.slot == slot)].copy()
        s["target_slot"] = f"{g.side}:{slot}"; s["rr_gap_rank"] = g.rank_below_par_slots; s["rr_gap_distinguishable_80"] = bool(g.distinguishable_below_par_80)
        s["rr_gap_p_below0"] = g.p_gap_below0; s["rr_gap_vs_par"] = g.gap_vs_par
        s["rank_in_class_among_supported"] = np.nan
        for cl, sub in s[s.supported].groupby("nationality_class"):
            s.loc[sub.sort_values("p10", ascending=False).index, "rank_in_class_among_supported"] = np.arange(1, len(sub) + 1)
        rows.append(s)
    return pd.concat(rows) if rows else pd.DataFrame()


def analyse(D, ctx, Wm, terms, P_bat, P_bowl, with_profile=True):
    E = Engine(D, P_bat, P_bowl, terms, Wm); PE = PlayerEvidence(E)
    gr = gap_ranking(E)
    tg = target_slots(gr)
    sq_ev = ctx.decorate(evidence_long(E, PE, ctx.ppl_s))
    gr = coverage(gr, sq_ev)
    ev = ctx.decorate(evidence_long(E, PE, ctx.ppl_c)).merge(ctx.cands[["player_id", "list_role", "list_rank", "pressure_rating", "floor_p10", "pressure_balls_overall", "matches_pressure"]], on="player_id")
    gm = gap_map(gr, ev, tg)
    return dict(E=E, PE=PE, gr=gr, tg=tg, sq_ev=sq_ev, ev=ev, gm=gm, prof=rr_profile(E) if with_profile else None)
