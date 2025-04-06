# pta2xcpcio-converter

## Install dependencies

```bash
pip install -r requirements.txt
```

## Change PTA Cookies

```python
# sync_runs.py
get_member_runs("PTASession", "JSESSIONID", "ProblemSetId", isFrozen, frozenTime)
```

## Run Script

```bash
# Usage: python3 sync_runs.py -h
# Usage 1: python3 sync_runs.py -f -t <frozenTime>
# Usage 2: python3 sync_runs.py --frozen --frozenTime <frozenTime>
python3 sync_runs.py -f -t 1800
```

## Run with scheduler

```bash
# The default cycle time is 15s.
# You can change it in .py source file.
python3 sync_scheduler.py
```
