# Step 3: five reports (no rule, ranking or list changed)

## (a) Top-10 overlap: floor ranking on baseline only vs the main ranking

Baseline bootstrap = bootstrap pressure rating minus bootstrap shift. Floor = 10th percentile. Main ranking = the listed top 10 (floor of pressure rating, same pool).

| role    | pool                                               |   overlap_of_10 | baseline_only_top10_not_in_main   | main_top10_not_in_baseline_only   |
|:--------|:---------------------------------------------------|----------------:|:----------------------------------|:----------------------------------|
| batters | same pool as main (negative-shift players removed) |               9 | Jos Buttler                       | Shubman Gill                      |
| batters | eligible + active, nothing removed                 |               9 | Jos Buttler                       | Shubman Gill                      |
| bowlers | same pool as main (negative-shift players removed) |              10 |                                   |                                   |
| bowlers | eligible + active, nothing removed                 |              10 |                                   |                                   |

## (b) Players removed for a reliably negative pressure shift (90th percentile of the bootstrap shift below zero)

Baseline rank = rank by baseline rating among eligible + active players (53 batters, 55 bowlers). Floor rank = rank by floor of pressure rating in the same pool before removal.

### batters removed: 6 of 53

| name             |   player_id |   baseline_rank |   floor_rank_if_kept |   baseline |   shift |   shift_p90 |   pressure_rating |   floor_p10 |
|:-----------------|------------:|----------------:|---------------------:|-----------:|--------:|------------:|------------------:|------------:|
| Shivam Dube      |        4755 |              17 |                   17 |     0.1090 | -0.0075 |     -0.0007 |            0.1014 |      0.0568 |
| Marcus Stoinis   |        2639 |              31 |                   33 |     0.0748 | -0.0103 |     -0.0017 |            0.0645 |      0.0037 |
| Babar Azam       |        2485 |              37 |                   35 |     0.0540 | -0.0085 |     -0.0007 |            0.0455 |     -0.0060 |
| Tanzid Hasan     |        7900 |              42 |                   48 |     0.0341 | -0.0119 |     -0.0054 |            0.0222 |     -0.0514 |
| Ayush Badoni     |        6460 |              46 |                   46 |     0.0206 | -0.0099 |     -0.0030 |            0.0107 |     -0.0462 |
| Charith Asalanka |        4895 |              50 |                   52 |     0.0070 | -0.0126 |     -0.0046 |           -0.0056 |     -0.0793 |

### bowlers removed: 7 of 55

| name               |   player_id |   baseline_rank |   floor_rank_if_kept |   baseline |   shift |   shift_p90 |   pressure_rating |   floor_p10 |
|:-------------------|------------:|----------------:|---------------------:|-----------:|--------:|------------:|------------------:|------------:|
| Rahul Chahar       |        6161 |              30 |                   38 |     0.0457 | -0.0078 |     -0.0001 |            0.0378 |     -0.0360 |
| Mohammed Siraj     |        5944 |              38 |                   36 |     0.0216 | -0.0111 |     -0.0003 |            0.0105 |     -0.0319 |
| Andre Russell      |        1318 |              41 |                   46 |     0.0004 | -0.0110 |     -0.0013 |           -0.0106 |     -0.0735 |
| Tushar Deshpande   |        6806 |              45 |                   45 |    -0.0043 | -0.0139 |     -0.0061 |           -0.0183 |     -0.0660 |
| Azmatullah Omarzai |        6676 |              47 |                   48 |    -0.0083 | -0.0148 |     -0.0046 |           -0.0232 |     -0.0742 |
| Hardik Pandya      |        3330 |              48 |                   47 |    -0.0173 | -0.0117 |     -0.0016 |           -0.0290 |     -0.0741 |
| Vaibhav Arora      |        8746 |              49 |                   50 |    -0.0226 | -0.0086 |     -0.0004 |           -0.0312 |     -0.0837 |

## (c) Recalibration logit(WP*) = a + c x logit(WP)

|   innings |       a |   c (slope) |
|----------:|--------:|------------:|
|    1.0000 | -0.0468 |      0.7332 |
|    2.0000 |  0.1526 |      0.8042 |

Fitted on out-of-fold raw win probabilities from leave-one-season-out fits (all four competition groups, ties excluded). c < 1 means the exact model was over-confident, as the blueprint expected.

## (d) Spinner share of pressure balls bowled vs all live balls (rating sample)

| subset              |   balls |   spin_share |
|:--------------------|--------:|-------------:|
| all live balls      |  156062 |       0.3722 |
| pressure balls      |   31263 |       0.3496 |
| ordinary live balls |  124799 |       0.3779 |
| innings 1: all live |   90549 |       0.3606 |
| innings 1: pressure |      78 |       0.1282 |
| innings 2: all live |   65513 |       0.3883 |
| innings 2: pressure |   31185 |       0.3501 |

Ratio of spinner share on pressure balls to spinner share on all live balls: 0.939.

Spinners among the bowlers (a bowler is a spinner if more than half of his live balls are spin):

| group                         |   spinners |   of |
|:------------------------------|-----------:|-----:|
| listed top 10 bowlers         |          8 |   10 |
| eligible + active bowler pool |         20 |   55 |

Listed top-10 bowlers who are spinners: Sunil Narine, Kuldeep Yadav, Rashid Khan, Varun Chakravarthy, Wanindu Hasaranga, Axar Patel, Noor Ahmad, Krunal Pandya.

## (e) Recency variant (two-season half-life), batters only

Top-10 overlap with the main top 10 (floor proxy, the sensitivity-grid definition): **8 of 10**. Overlap with the final listed batters: 8 of 10. Kendall tau vs main over the pool: 0.803.

In the final list but not in the recency top 10: Nicholas Pooran, Shubman Gill.
In the recency top 10 but not in the final list: Ishan Kishan, Virat Kohli.

Recency top 14 with ranks under each definition:

| name                 |   player_id |   main_rank_proxy |   recency_rank |
|:---------------------|------------:|------------------:|---------------:|
| Abhishek Sharma      |        6281 |                 4 |              1 |
| Heinrich Klaasen     |        4260 |                 1 |              2 |
| Tim David            |        6396 |                 3 |              3 |
| Shreyas Iyer         |        3647 |                 6 |              4 |
| Suryakumar Yadav     |        1699 |                 2 |              5 |
| Phil Salt            |        5553 |                 5 |              6 |
| Ishan Kishan         |        4117 |                15 |              7 |
| Virat Kohli          |          47 |                12 |              8 |
| Namboori Tilak Varma |        7897 |                 7 |              9 |
| Sai Sudharsan        |       23450 |                 8 |             10 |
| Jos Buttler          |         813 |                 9 |             11 |
| Shubman Gill         |        6288 |                11 |             12 |
| Lokesh Rahul         |         953 |                14 |             13 |
| Mitchell Marsh       |         818 |                13 |             14 |
