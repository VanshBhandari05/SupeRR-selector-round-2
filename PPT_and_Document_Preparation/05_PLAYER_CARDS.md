# 05 PLAYER CARDS: one evidence card per listed player (20)

Source: `outputs/evidence_cards.md` (parsed), `outputs/top10_*.csv`, `outputs/eligible_table_*.csv`. Cards follow the blueprint's evidence-card blocks: sample, rating, cricket numbers on pressure vs ordinary balls, consistency, single highest-value pressure match (date, opponent; value = win probability added over the player's pressure balls in that match, `dWP0` summed). The 'why' sentence is generated from the numbers only. `player_cards.csv` has the same fields in one row per player.

**Surprise names** (marked SURPRISE): for each role, the three listed players with the lowest probability of finishing in the top 10 across the 300 resamples (the website's stated rule, `website/data/omissions.json`; replicated here and equal). **Notable omissions** (marked OMISSION in the table at the end): for each role, the four eligible players outside the top 10 with the highest baseline rating (this includes players removed for a reliably negative shift). Both are rules, not my taste.

## Batters

### Batter #1: Heinrich Klaasen (id 4260; Sunrisers Hyderabad / South Africa)


- Sample: 200 pressure balls in 19 matches (IPL 160, T20I 40)
- Rating: pressure rating 0.245, floor (10th pct) 0.197, 90th pct 0.292; baseline 0.232, pressure shift 0.0125
- Cricket numbers: strike rate 187.5 pressure vs 164.5 ordinary; runs index 128; dismissal ratio 0.74
- Consistency: delivery rate 0.89 (9 matches with 6+ pressure balls); P(top 10) 0.99, P(top 20) 1.00, 80% rank interval 1-6; in the top 10 under 13 of 14 sensitivity variants (stable)
- Best pressure match: 2026-04-29 vs Mumbai Indians (+0.55 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Heinrich Klaasen ranks 1st on a floor of 0.197 (rating 0.245 = baseline 0.232 +0.013 shift) from 200 pressure balls in 19 matches; his strike rate is 187.5 on pressure balls against 164.5 on ordinary balls (runs index 128, dismissal ratio 0.74).

### Batter #2: Suryakumar Yadav (id 1699; Mumbai Indians / India)


- Sample: 433 pressure balls in 33 matches (IPL 265, T20I 168)
- Rating: pressure rating 0.248, floor (10th pct) 0.194, 90th pct 0.302; baseline 0.237, pressure shift 0.0104
- Cricket numbers: strike rate 172.3 pressure vs 163.0 ordinary; runs index 121; dismissal ratio 0.77
- Consistency: delivery rate 0.74 (23 matches with 6+ pressure balls); P(top 10) 0.99, P(top 20) 1.00, 80% rank interval 1-6; in the top 10 under 14 of 14 sensitivity variants (stable)
- Best pressure match: 2023-05-03 vs Punjab Kings (+0.41 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Suryakumar Yadav ranks 2nd on a floor of 0.194 (rating 0.248 = baseline 0.237 +0.010 shift) from 433 pressure balls in 33 matches; his strike rate is 172.3 on pressure balls against 163.0 on ordinary balls (runs index 121, dismissal ratio 0.77); his rating is higher than Heinrich Klaasen's (0.248 vs 0.245) but his floor is lower (0.194 vs 0.197), so he ranks below.

### Batter #3: Tim David (id 6396; Mumbai Indians / Australia)


- Sample: 270 pressure balls in 29 matches (IPL 147, T20I 123)
- Rating: pressure rating 0.226, floor (10th pct) 0.165, 90th pct 0.303; baseline 0.229, pressure shift -0.0034
- Cricket numbers: strike rate 183.7 pressure vs 172.9 ordinary; runs index 127; dismissal ratio 0.98
- Consistency: delivery rate 0.58 (19 matches with 6+ pressure balls); P(top 10) 0.91, P(top 20) 0.97, 80% rank interval 1-10; in the top 10 under 13 of 14 sensitivity variants (stable)
- Best pressure match: 2024-02-21 vs New Zealand (+0.72 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Tim David ranks 3rd on a floor of 0.165 (rating 0.226 = baseline 0.229 -0.003 shift) from 270 pressure balls in 29 matches; his strike rate is 183.7 on pressure balls against 172.9 on ordinary balls (runs index 127, dismissal ratio 0.98).

### Batter #4: Abhishek Sharma (id 6281; Sunrisers Hyderabad / India)


- Sample: 385 pressure balls in 33 matches (IPL 288, T20I 97)
- Rating: pressure rating 0.209, floor (10th pct) 0.143, 90th pct 0.271; baseline 0.209, pressure shift 0.0008
- Cricket numbers: strike rate 188.1 pressure vs 184.5 ordinary; runs index 125; dismissal ratio 1.11
- Consistency: delivery rate 0.68 (22 matches with 6+ pressure balls); P(top 10) 0.85, P(top 20) 0.98, 80% rank interval 2-14; in the top 10 under 13 of 14 sensitivity variants (stable)
- Best pressure match: 2025-04-12 vs Punjab Kings (+0.49 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Abhishek Sharma ranks 4th on a floor of 0.143 (rating 0.209 = baseline 0.209 +0.001 shift) from 385 pressure balls in 33 matches; his strike rate is 188.1 on pressure balls against 184.5 on ordinary balls (runs index 125, dismissal ratio 1.11).

### Batter #5: Phil Salt (id 5553; Royal Challengers Bengaluru / England)


- Sample: 231 pressure balls in 19 matches (IPL 74, T20I 157)
- Rating: pressure rating 0.194, floor (10th pct) 0.129, 90th pct 0.254; baseline 0.182, pressure shift 0.0114
- Cricket numbers: strike rate 188.3 pressure vs 167.0 ordinary; runs index 127; dismissal ratio 0.59
- Consistency: delivery rate 0.73 (15 matches with 6+ pressure balls); P(top 10) 0.76, P(top 20) 0.96, 80% rank interval 2-16; in the top 10 under 13 of 14 sensitivity variants (stable)
- Best pressure match: 2023-12-16 vs West Indies (+0.50 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Phil Salt ranks 5th on a floor of 0.129 (rating 0.194 = baseline 0.182 +0.011 shift) from 231 pressure balls in 19 matches; his strike rate is 188.3 on pressure balls against 167.0 on ordinary balls (runs index 127, dismissal ratio 0.59).

### Batter #6: Shreyas Iyer (id 3647; Punjab Kings / India)


- Sample: 298 pressure balls in 20 matches (IPL 255, T20I 43)
- Rating: pressure rating 0.188, floor (10th pct) 0.126, 90th pct 0.245; baseline 0.165, pressure shift 0.0222
- Cricket numbers: strike rate 172.8 pressure vs 148.2 ordinary; runs index 124; dismissal ratio 0.52
- Consistency: delivery rate 0.75 (16 matches with 6+ pressure balls); P(top 10) 0.74, P(top 20) 0.94, 80% rank interval 3-17; in the top 10 under 13 of 14 sensitivity variants (stable)
- Best pressure match: 2025-06-01 vs Mumbai Indians (+0.80 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Shreyas Iyer ranks 6th on a floor of 0.126 (rating 0.188 = baseline 0.165 +0.022 shift) from 298 pressure balls in 20 matches; his strike rate is 172.8 on pressure balls against 148.2 on ordinary balls (runs index 124, dismissal ratio 0.52).

### Batter #7: Namboori Tilak Varma (id 7897; Mumbai Indians / India)


- Sample: 497 pressure balls in 33 matches (IPL 252, T20I 246)
- Rating: pressure rating 0.164, floor (10th pct) 0.121, 90th pct 0.211; baseline 0.158, pressure shift 0.0060
- Cricket numbers: strike rate 146.3 pressure vs 144.4 ordinary; runs index 107; dismissal ratio 0.55
- Consistency: delivery rate 0.62 (26 matches with 6+ pressure balls); P(top 10) 0.59, P(top 20) 0.93, 80% rank interval 4-18; in the top 10 under 14 of 14 sensitivity variants (stable)
- Best pressure match: 2025-01-25 vs England (+0.83 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Namboori Tilak Varma ranks 7th on a floor of 0.121 (rating 0.164 = baseline 0.158 +0.006 shift) from 497 pressure balls in 33 matches; his strike rate is 146.3 on pressure balls against 144.4 on ordinary balls (runs index 107, dismissal ratio 0.55).

### Batter #8: Sai Sudharsan (id 23450; Gujarat Titans) (SURPRISE)


- Sample: 312 pressure balls in 24 matches (IPL 312, T20I 0)
- Rating: pressure rating 0.142, floor (10th pct) 0.102, 90th pct 0.175; baseline 0.143, pressure shift -0.0011
- Cricket numbers: strike rate 152.6 pressure vs 144.9 ordinary; runs index 96; dismissal ratio 0.73
- Consistency: delivery rate 0.56 (16 matches with 6+ pressure balls); P(top 10) 0.28, P(top 20) 0.81, 80% rank interval 8-23; in the top 10 under 12 of 14 sensitivity variants (stable)
- Best pressure match: 2026-05-03 vs Punjab Kings (+0.15 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Sai Sudharsan ranks 8th on a floor of 0.102 (rating 0.142 = baseline 0.143 -0.001 shift) from 312 pressure balls in 24 matches; his strike rate is 152.6 on pressure balls against 144.9 on ordinary balls (runs index 96, dismissal ratio 0.73); he finishes in the top 10 in only 28% of resamples (P(top 20) 0.81); all his pressure balls are in the IPL, so he is rated on one competition only.

### Batter #9: Nicholas Pooran (id 3125; Lucknow Super Giants / West Indies) (SURPRISE)


- Sample: 368 pressure balls in 33 matches (IPL 204, T20I 164)
- Rating: pressure rating 0.159, floor (10th pct) 0.099, 90th pct 0.225; baseline 0.150, pressure shift 0.0090
- Cricket numbers: strike rate 164.9 pressure vs 156.1 ordinary; runs index 119; dismissal ratio 0.83
- Consistency: delivery rate 0.62 (24 matches with 6+ pressure balls); P(top 10) 0.56, P(top 20) 0.86, 80% rank interval 4-23; in the top 10 under 11 of 14 sensitivity variants (stable)
- Best pressure match: 2023-04-10 vs Royal Challengers Bengaluru (+0.67 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Nicholas Pooran ranks 9th on a floor of 0.099 (rating 0.159 = baseline 0.150 +0.009 shift) from 368 pressure balls in 33 matches; his strike rate is 164.9 on pressure balls against 156.1 on ordinary balls (runs index 119, dismissal ratio 0.83); his rating is higher than Sai Sudharsan's (0.159 vs 0.142) but his floor is lower (0.099 vs 0.102), so he ranks below.

### Batter #10: Shubman Gill (id 6288; Gujarat Titans / India) (SURPRISE)


- Sample: 469 pressure balls in 36 matches (IPL 387, T20I 83)
- Rating: pressure rating 0.136, floor (10th pct) 0.094, 90th pct 0.172; baseline 0.132, pressure shift 0.0041
- Cricket numbers: strike rate 164.4 pressure vs 147.5 ordinary; runs index 108; dismissal ratio 0.87
- Consistency: delivery rate 0.57 (23 matches with 6+ pressure balls); P(top 10) 0.25, P(top 20) 0.76, 80% rank interval 8-26; in the top 10 under 7 of 14 sensitivity variants (stable)
- Best pressure match: 2023-05-21 vs Royal Challengers Bengaluru (+0.56 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Shubman Gill ranks 10th on a floor of 0.094 (rating 0.136 = baseline 0.132 +0.004 shift) from 469 pressure balls in 36 matches; his strike rate is 164.4 on pressure balls against 147.5 on ordinary balls (runs index 108, dismissal ratio 0.87); he finishes in the top 10 in only 25% of resamples (P(top 20) 0.76).

## Bowlers

### Bowler #1: Sunil Narine (id 781; Kolkata Knight Riders)


- Sample: 300 pressure balls in 23 matches (IPL 300, T20I 0)
- Rating: pressure rating 0.198, floor (10th pct) 0.153, 90th pct 0.245; baseline 0.193, pressure shift 0.0053
- Cricket numbers: economy 7.28 pressure vs 6.56 ordinary; economy index 121; wicket ratio 1.23
- Consistency: delivery rate 0.59 (22 matches with 6+ pressure balls); P(top 10) 0.98, P(top 20) 1.00, 80% rank interval 1-7; in the top 10 under 13 of 14 sensitivity variants (stable)
- Best pressure match: 2025-04-29 vs Delhi Capitals (+0.40 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Sunil Narine ranks 1st on a floor of 0.153 (rating 0.198 = baseline 0.193 +0.005 shift) from 300 pressure balls in 23 matches; his economy is 7.28 on pressure balls against 6.56 on ordinary balls (economy index 121, wicket ratio 1.23); all his pressure balls are in the IPL, so he is rated on one competition only.

### Bowler #2: Kuldeep Yadav (id 3644; Delhi Capitals / India)


- Sample: 299 pressure balls in 20 matches (IPL 233, T20I 66)
- Rating: pressure rating 0.165, floor (10th pct) 0.123, 90th pct 0.211; baseline 0.159, pressure shift 0.0062
- Cricket numbers: economy 8.10 pressure vs 7.77 ordinary; economy index 117; wicket ratio 1.13
- Consistency: delivery rate 0.74 (19 matches with 6+ pressure balls); P(top 10) 0.85, P(top 20) 0.99, 80% rank interval 2-12; in the top 10 under 14 of 14 sensitivity variants (stable)
- Best pressure match: 2026-05-24 vs Kolkata Knight Riders (+0.39 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Kuldeep Yadav ranks 2nd on a floor of 0.123 (rating 0.165 = baseline 0.159 +0.006 shift) from 299 pressure balls in 20 matches; his economy is 8.1 on pressure balls against 7.77 on ordinary balls (economy index 117, wicket ratio 1.13).

### Bowler #3: Rashid Khan (id 4722; Gujarat Titans / Afghanistan)


- Sample: 439 pressure balls in 33 matches (IPL 235, T20I 204)
- Rating: pressure rating 0.170, floor (10th pct) 0.119, 90th pct 0.217; baseline 0.163, pressure shift 0.0067
- Cricket numbers: economy 6.67 pressure vs 7.44 ordinary; economy index 128; wicket ratio 1.10
- Consistency: delivery rate 0.73 (30 matches with 6+ pressure balls); P(top 10) 0.84, P(top 20) 0.98, 80% rank interval 1-12; in the top 10 under 14 of 14 sensitivity variants (stable)
- Best pressure match: 2026-04-08 vs Delhi Capitals (+0.55 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Rashid Khan ranks 3rd on a floor of 0.119 (rating 0.170 = baseline 0.163 +0.007 shift) from 439 pressure balls in 33 matches; his economy is 6.67 on pressure balls against 7.44 on ordinary balls (economy index 128, wicket ratio 1.1); his rating is higher than Kuldeep Yadav's (0.170 vs 0.165) but his floor is lower (0.119 vs 0.123), so he ranks below.

### Bowler #4: Varun Chakravarthy (id 6256; Kolkata Knight Riders / India)


- Sample: 373 pressure balls in 31 matches (IPL 249, T20I 124)
- Rating: pressure rating 0.171, floor (10th pct) 0.116, 90th pct 0.220; baseline 0.175, pressure shift -0.0048
- Cricket numbers: economy 8.77 pressure vs 7.93 ordinary; economy index 100; wicket ratio 1.34
- Consistency: delivery rate 0.58 (26 matches with 6+ pressure balls); P(top 10) 0.80, P(top 20) 0.98, 80% rank interval 1-13; in the top 10 under 14 of 14 sensitivity variants (stable)
- Best pressure match: 2023-05-04 vs Sunrisers Hyderabad (+0.87 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Varun Chakravarthy ranks 4th on a floor of 0.116 (rating 0.171 = baseline 0.175 -0.005 shift) from 373 pressure balls in 31 matches; his economy is 8.77 on pressure balls against 7.93 on ordinary balls (economy index 100, wicket ratio 1.34); his rating is higher than Rashid Khan's (0.171 vs 0.170) but his floor is lower (0.116 vs 0.119), so he ranks below.

### Bowler #5: Josh Hazlewood (id 830; Royal Challengers Bengaluru / Australia)


- Sample: 352 pressure balls in 25 matches (IPL 236, T20I 116)
- Rating: pressure rating 0.169, floor (10th pct) 0.106, 90th pct 0.226; baseline 0.162, pressure shift 0.0066
- Cricket numbers: economy 8.36 pressure vs 8.03 ordinary; economy index 111; wicket ratio 1.55
- Consistency: delivery rate 0.59 (22 matches with 6+ pressure balls); P(top 10) 0.78, P(top 20) 0.97, 80% rank interval 1-15; in the top 10 under 14 of 14 sensitivity variants (stable)
- Best pressure match: 2025-04-24 vs Rajasthan Royals (+0.78 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Josh Hazlewood ranks 5th on a floor of 0.106 (rating 0.169 = baseline 0.162 +0.007 shift) from 352 pressure balls in 25 matches; his economy is 8.36 on pressure balls against 8.03 on ordinary balls (economy index 111, wicket ratio 1.55).

### Bowler #6: Wanindu Hasaranga (id 4900; Royal Challengers Bengaluru / Sri Lanka)


- Sample: 364 pressure balls in 26 matches (IPL 208, T20I 156)
- Rating: pressure rating 0.143, floor (10th pct) 0.099, 90th pct 0.197; baseline 0.155, pressure shift -0.0116
- Cricket numbers: economy 8.89 pressure vs 7.44 ordinary; economy index 95; wicket ratio 1.34
- Consistency: delivery rate 0.50 (20 matches with 6+ pressure balls); P(top 10) 0.68, P(top 20) 0.96, 80% rank interval 3-17; in the top 10 under 14 of 14 sensitivity variants (stable)
- Best pressure match: 2025-03-30 vs Chennai Super Kings (+0.42 win prob. added)

- Companion: fails the strict economy-only sign rule; passes the amended rule; amended sign check passes: True.
- **Why he ranks here:** Wanindu Hasaranga ranks 6th on a floor of 0.099 (rating 0.143 = baseline 0.155 -0.012 shift) from 364 pressure balls in 26 matches; his economy is 8.89 on pressure balls against 7.44 on ordinary balls (economy index 95, wicket ratio 1.34); his economy index is below 100 but his wicket ratio is above 1, which is why the bowler sign check was amended.

### Bowler #7: Jasprit Bumrah (id 2933; Mumbai Indians / India)


- Sample: 318 pressure balls in 27 matches (IPL 239, T20I 79)
- Rating: pressure rating 0.149, floor (10th pct) 0.095, 90th pct 0.195; baseline 0.157, pressure shift -0.0082
- Cricket numbers: economy 7.84 pressure vs 6.97 ordinary; economy index 117; wicket ratio 0.59
- Consistency: delivery rate 0.41 (22 matches with 6+ pressure balls); P(top 10) 0.67, P(top 20) 0.95, 80% rank interval 3-17; in the top 10 under 13 of 14 sensitivity variants (stable)
- Best pressure match: 2026-05-10 vs Royal Challengers Bengaluru (+0.32 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Jasprit Bumrah ranks 7th on a floor of 0.095 (rating 0.149 = baseline 0.157 -0.008 shift) from 318 pressure balls in 27 matches; his economy is 7.84 on pressure balls against 6.97 on ordinary balls (economy index 117, wicket ratio 0.59); his rating is higher than Wanindu Hasaranga's (0.149 vs 0.143) but his floor is lower (0.095 vs 0.099), so he ranks below; his wicket ratio is below 1 so his rating rests on economy.

### Bowler #8: Axar Patel (id 2876; Delhi Capitals / India) (SURPRISE)


- Sample: 386 pressure balls in 35 matches (IPL 173, T20I 213)
- Rating: pressure rating 0.123, floor (10th pct) 0.082, 90th pct 0.169; baseline 0.111, pressure shift 0.0115
- Cricket numbers: economy 8.36 pressure vs 7.71 ordinary; economy index 107; wicket ratio 1.19
- Consistency: delivery rate 0.61 (28 matches with 6+ pressure balls); P(top 10) 0.39, P(top 20) 0.90, 80% rank interval 5-20; in the top 10 under 10 of 14 sensitivity variants (stable)
- Best pressure match: 2023-12-01 vs Australia (+0.48 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Axar Patel ranks 8th on a floor of 0.082 (rating 0.123 = baseline 0.111 +0.011 shift) from 386 pressure balls in 35 matches; his economy is 8.36 on pressure balls against 7.71 on ordinary balls (economy index 107, wicket ratio 1.19); he finishes in the top 10 in only 39% of resamples (P(top 20) 0.90).

### Bowler #9: Noor Ahmad (id 7967; Chennai Super Kings / Afghanistan) (SURPRISE)


- Sample: 207 pressure balls in 16 matches (IPL 139, T20I 68)
- Rating: pressure rating 0.144, floor (10th pct) 0.074, 90th pct 0.204; baseline 0.150, pressure shift -0.0060
- Cricket numbers: economy 9.66 pressure vs 7.74 ordinary; economy index 92; wicket ratio 1.39
- Consistency: delivery rate 0.31 (13 matches with 6+ pressure balls); P(top 10) 0.54, P(top 20) 0.87, 80% rank interval 2-23; in the top 10 under 12 of 14 sensitivity variants (stable)
- Best pressure match: 2022-06-14 vs Zimbabwe (+0.51 win prob. added)

- Companion: fails the strict economy-only sign rule; passes the amended rule; amended sign check passes: True.
- **Why he ranks here:** Noor Ahmad ranks 9th on a floor of 0.074 (rating 0.144 = baseline 0.150 -0.006 shift) from 207 pressure balls in 16 matches; his economy is 9.66 on pressure balls against 7.74 on ordinary balls (economy index 92, wicket ratio 1.39); his rating is higher than Axar Patel's (0.144 vs 0.123) but his floor is lower (0.074 vs 0.082), so he ranks below; his economy index is below 100 but his wicket ratio is above 1, which is why the bowler sign check was amended.

### Bowler #10: Krunal Pandya (id 4219; Lucknow Super Giants) (SURPRISE)


- Sample: 247 pressure balls in 18 matches (IPL 247, T20I 0)
- Rating: pressure rating 0.137, floor (10th pct) 0.072, 90th pct 0.196; baseline 0.121, pressure shift 0.0160
- Cricket numbers: economy 6.60 pressure vs 8.01 ordinary; economy index 131; wicket ratio 1.52
- Consistency: delivery rate 0.76 (17 matches with 6+ pressure balls); P(top 10) 0.54, P(top 20) 0.87, 80% rank interval 3-22; in the top 10 under 10 of 14 sensitivity variants (stable)
- Best pressure match: 2025-06-03 vs Punjab Kings (+0.37 win prob. added)

- Companion: sign check (strict economy-only rule) passes; amended sign check passes: True.
- **Why he ranks here:** Krunal Pandya ranks 10th on a floor of 0.072 (rating 0.137 = baseline 0.121 +0.016 shift) from 247 pressure balls in 18 matches; his economy is 6.6 on pressure balls against 8.01 on ordinary balls (economy index 131, wicket ratio 1.52); all his pressure balls are in the IPL, so he is rated on one competition only.

## Notable omissions (rule: highest baseline among eligible players outside the top 10)

| role   |   player_id | name              |   baseline |   baseline_rank_among_eligible | status                |   floor_p10 |   floor_of_10th_listed |   p_top10 |   shift |   shift_p90 |   gap_floor_to_10th |
|:-------|------------:|:------------------|-----------:|-------------------------------:|:----------------------|------------:|-----------------------:|----------:|--------:|------------:|--------------------:|
| batter |         818 | Mitchell Marsh    |     0.1489 |                              9 | ranked 14 in the pool |      0.0666 |                 0.0941 |    0.2567 | -0.0120 |      0.0007 |             -0.0275 |
| batter |         813 | Jos Buttler       |     0.1389 |                             11 | ranked 11 in the pool |      0.0937 |                 0.0941 |    0.2700 |  0.0030 |      0.0148 |             -0.0004 |
| batter |        4736 | Josh Inglis       |     0.1296 |                             13 | ranked 20 in the pool |      0.0457 |                 0.0941 |    0.3233 |  0.0048 |      0.0126 |             -0.0484 |
| batter |         953 | Lokesh Rahul      |     0.1187 |                             14 | ranked 13 in the pool |      0.0743 |                 0.0941 |    0.1400 |  0.0008 |      0.0120 |             -0.0197 |
| bowler |        6450 | Mujeeb Ur Rahman  |     0.1210 |                              9 | ranked 11 in the pool |      0.0556 |                 0.0725 |    0.3767 | -0.0010 |      0.0075 |             -0.0169 |
| bowler |        2490 | Mohammad Nawaz    |     0.1117 |                             11 | ranked 15 in the pool |      0.0382 |                 0.0725 |    0.3767 |  0.0055 |      0.0146 |             -0.0342 |
| bowler |         360 | Bhuvneshwar Kumar |     0.1028 |                             13 | ranked 12 in the pool |      0.0539 |                 0.0725 |    0.3100 |  0.0070 |      0.0214 |             -0.0186 |
| bowler |        7364 | Haris Rauf        |     0.1009 |                             14 | ranked 19 in the pool |      0.0270 |                 0.0725 |    0.2233 | -0.0078 |      0.0015 |             -0.0455 |

Reading: each omission is excluded because his FLOOR is below the 10th listed player's floor (or, if marked removed, because his bootstrap shift is reliably negative). Jos Buttler is the closest: 11th, floor 0.0937 vs Gill's 0.0941 (a gap of 0.0004).
