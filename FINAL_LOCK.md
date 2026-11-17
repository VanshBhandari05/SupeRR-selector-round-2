# FINAL LOCK

Locked on 2026-11-14 after a full `python run_all.py` from an empty `outputs/` folder.

SHA-256 of the files that define the submission:

| File | SHA-256 |
|---|---|
| config.yaml | `27709eea817d9e411d4f2bfe87eb2d25b4ab853b8865b7def888248d30f47ded` |
| outputs/top10_batters.csv | `c3182235b809d758c96219c90fe76459a988e4e0a6768bdbf2aaa15a89023234` |
| outputs/top10_bowlers.csv | `31c82073156f75c597d9e0be37dfc5e3963f49c5a9497588193528ce45dc7949` |

To verify: `python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <file>` and compare. Any change to config.yaml or either list changes a hash.

Names with two player ids (check the Unstop dropdown by team): Rashid Khan (list uses 4722; other: 20172 (Nepal)).
