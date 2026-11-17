# Audit: Stage 7 (final ranking)

Rule: eligible + active, drop reliably negative shift, sort by bootstrap floor (10th percentile of pressure rating), ties by delivery rate then pressure balls.

| role    |   listed |   top20_prob_below_0_6 |   sign_check_fails |   strict_sign_check_fails |   fragile |   duplicate_names |   id_ok |
|:--------|---------:|-----------------------:|-------------------:|--------------------------:|----------:|------------------:|--------:|
| batters |       10 |                      0 |                  0 |                         0 |         0 |                 0 |       1 |
| bowlers |       10 |                      0 |                  0 |                         2 |         0 |                 1 |       1 |

## Top 10 batters

|   rank | name                 |   player_id | teams                                 |   pressure_rating |   floor_p10 |   p90 |   baseline |   shift |   p_top10 |   p_top20 |   delivery_rate | fragile   | sign_check   |
|-------:|:---------------------|------------:|:--------------------------------------|------------------:|------------:|------:|-----------:|--------:|----------:|----------:|----------------:|:----------|:-------------|
|      1 | Heinrich Klaasen     |        4260 | Sunrisers Hyderabad / South Africa    |             0.245 |       0.197 | 0.292 |      0.232 |   0.013 |     0.993 |     1.000 |           0.889 | False     | True         |
|      2 | Suryakumar Yadav     |        1699 | Mumbai Indians / India                |             0.248 |       0.194 | 0.302 |      0.237 |   0.010 |     0.990 |     1.000 |           0.739 | False     | True         |
|      3 | Tim David            |        6396 | Mumbai Indians / Australia            |             0.226 |       0.165 | 0.303 |      0.229 |  -0.003 |     0.907 |     0.967 |           0.579 | False     | True         |
|      4 | Abhishek Sharma      |        6281 | Sunrisers Hyderabad / India           |             0.209 |       0.143 | 0.271 |      0.209 |   0.001 |     0.850 |     0.977 |           0.682 | False     | True         |
|      5 | Phil Salt            |        5553 | Royal Challengers Bengaluru / England |             0.194 |       0.129 | 0.254 |      0.182 |   0.011 |     0.763 |     0.957 |           0.733 | False     | True         |
|      6 | Shreyas Iyer         |        3647 | Punjab Kings / India                  |             0.188 |       0.126 | 0.245 |      0.165 |   0.022 |     0.743 |     0.940 |           0.750 | False     | True         |
|      7 | Namboori Tilak Varma |        7897 | Mumbai Indians / India                |             0.164 |       0.121 | 0.211 |      0.158 |   0.006 |     0.587 |     0.930 |           0.615 | False     | True         |
|      8 | Sai Sudharsan        |       23450 | Gujarat Titans                        |             0.142 |       0.102 | 0.175 |      0.143 |  -0.001 |     0.283 |     0.813 |           0.562 | False     | True         |
|      9 | Nicholas Pooran      |        3125 | Lucknow Super Giants / West Indies    |             0.159 |       0.099 | 0.225 |      0.150 |   0.009 |     0.563 |     0.860 |           0.625 | False     | True         |
|     10 | Shubman Gill         |        6288 | Gujarat Titans / India                |             0.136 |       0.094 | 0.172 |      0.132 |   0.004 |     0.247 |     0.760 |           0.565 | False     | True         |

Removed for a reliably negative shift: 6. Candidates (eligible and active): 53; ranked pool after removal: 47.

Ranks 11 to 20 (for face validity):

|   rank | name             |   pressure_rating |   floor_p10 |   p_top10 |
|-------:|:-----------------|------------------:|------------:|----------:|
|     11 | Jos Buttler      |             0.142 |       0.094 |     0.270 |
|     12 | Virat Kohli      |             0.127 |       0.087 |     0.190 |
|     13 | Lokesh Rahul     |             0.119 |       0.074 |     0.140 |
|     14 | Mitchell Marsh   |             0.137 |       0.067 |     0.257 |
|     15 | Ishan Kishan     |             0.116 |       0.065 |     0.153 |
|     16 | Yashasvi Jaiswal |             0.119 |       0.060 |     0.177 |
|     17 | Cameron Green    |             0.119 |       0.051 |     0.227 |
|     18 | Riyan Parag      |             0.097 |       0.050 |     0.127 |
|     19 | Rovman Powell    |             0.103 |       0.049 |     0.097 |
|     20 | Josh Inglis      |             0.134 |       0.046 |     0.323 |

## Top 10 bowlers

|   rank | name               |   player_id | teams                                   |   pressure_rating |   floor_p10 |   p90 |   baseline |   shift |   p_top10 |   p_top20 |   delivery_rate | fragile   | sign_check   |
|-------:|:-------------------|------------:|:----------------------------------------|------------------:|------------:|------:|-----------:|--------:|----------:|----------:|----------------:|:----------|:-------------|
|      1 | Sunil Narine       |         781 | Kolkata Knight Riders                   |             0.198 |       0.153 | 0.245 |      0.193 |   0.005 |     0.983 |     1.000 |           0.591 | False     | True         |
|      2 | Kuldeep Yadav      |        3644 | Delhi Capitals / India                  |             0.165 |       0.123 | 0.211 |      0.159 |   0.006 |     0.847 |     0.993 |           0.737 | False     | True         |
|      3 | Rashid Khan        |        4722 | Gujarat Titans / Afghanistan            |             0.170 |       0.119 | 0.217 |      0.163 |   0.007 |     0.840 |     0.980 |           0.733 | False     | True         |
|      4 | Varun Chakravarthy |        6256 | Kolkata Knight Riders / India           |             0.171 |       0.116 | 0.220 |      0.175 |  -0.005 |     0.800 |     0.983 |           0.577 | False     | True         |
|      5 | Josh Hazlewood     |         830 | Royal Challengers Bengaluru / Australia |             0.169 |       0.106 | 0.226 |      0.162 |   0.007 |     0.780 |     0.970 |           0.591 | False     | True         |
|      6 | Wanindu Hasaranga  |        4900 | Royal Challengers Bengaluru / Sri Lanka |             0.143 |       0.099 | 0.197 |      0.155 |  -0.012 |     0.683 |     0.963 |           0.500 | False     | True         |
|      7 | Jasprit Bumrah     |        2933 | Mumbai Indians / India                  |             0.149 |       0.095 | 0.195 |      0.157 |  -0.008 |     0.670 |     0.953 |           0.409 | False     | True         |
|      8 | Axar Patel         |        2876 | Delhi Capitals / India                  |             0.123 |       0.082 | 0.169 |      0.111 |   0.011 |     0.390 |     0.903 |           0.607 | False     | True         |
|      9 | Noor Ahmad         |        7967 | Chennai Super Kings / Afghanistan       |             0.144 |       0.074 | 0.204 |      0.150 |  -0.006 |     0.540 |     0.867 |           0.308 | False     | True         |
|     10 | Krunal Pandya      |        4219 | Lucknow Super Giants                    |             0.137 |       0.072 | 0.196 |      0.121 |   0.016 |     0.537 |     0.867 |           0.765 | False     | True         |

Removed for a reliably negative shift: 7. Candidates (eligible and active): 55; ranked pool after removal: 48.

Ranks 11 to 20 (for face validity):

|   rank | name              |   pressure_rating |   floor_p10 |   p_top10 |
|-------:|:------------------|------------------:|------------:|----------:|
|     11 | Mujeeb Ur Rahman  |             0.120 |       0.056 |     0.377 |
|     12 | Bhuvneshwar Kumar |             0.110 |       0.054 |     0.310 |
|     13 | Mitchell Santner  |             0.106 |       0.046 |     0.260 |
|     14 | Ravindra Jadeja   |             0.107 |       0.043 |     0.253 |
|     15 | Mohammad Nawaz    |             0.117 |       0.038 |     0.377 |
|     16 | Trent Boult       |             0.074 |       0.032 |     0.087 |
|     17 | Kagiso Rabada     |             0.079 |       0.030 |     0.063 |
|     18 | Arshdeep Singh    |             0.064 |       0.029 |     0.020 |
|     19 | Haris Rauf        |             0.093 |       0.027 |     0.223 |
|     20 | Mustafizur Rahman |             0.073 |       0.027 |     0.080 |
