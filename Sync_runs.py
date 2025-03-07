import sys
import json
import time
import getopt
import requests
from datetime import datetime


def time_difference(time1: str, time2: str) -> int:
    dt1 = datetime.strptime(time1, "%Y-%m-%dT%H:%M:%SZ")
    dt2 = datetime.strptime(time2, "%Y-%m-%dT%H:%M:%SZ")
    return int((dt1 - dt2).total_seconds())


def transComplierToLanguage(compiler):
    if compiler == "GXX" or compiler == "CLANGXX":
        return "C++"
    elif compiler == "GCC" or compiler == "CLANG" or compiler == "MODERN_GCC":
        return "C"
    elif compiler == "PYPY3" or compiler == "PYTHON3" or compiler == "PYTHON2":
        return "Python"
    elif compiler == "JAVAC":
        return "Java"
    else:
        return "Other Language"


def get_session(PTASession, JSESSIONID):
    session = requests.Session()
    cookies = {"PTASession": PTASession, "JSESSIONID": JSESSIONID}
    headers = {
        "Accept-Language": "zh-CN",
        "Accept": "application/json;charset=UTF-8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
    }
    session.cookies.update(cookies)
    session.headers.update(headers)
    return session


def get_member_runs(PTASession, JSESSIONID, PTASetid, isFrozen, frozenTime):
    count = 0
    runs = []
    submissions = []
    runtime_errors = ["NON_ZERO_EXIT_CODE", "SEGMENTATION_FAULT", "FLOAT_POINT_EXCEPTION"]

    session = get_session(PTASession, JSESSIONID)

    info_url = f"https://pintia.cn/api/problem-sets/{PTASetid}"
    info_res = session.get(info_url)
    info_json = json.loads(info_res.text)

    startTime_utc = info_json["problemSet"]["startAt"]
    endTime_utc = info_json["problemSet"]["endAt"]

    while True:
        sub_url = ""
        if count == 0:
            sub_url = f"https://pintia.cn/api/problem-sets/{PTASetid}/submissions?limit=200&filter=%7B%7D"
        else:
            sub_url = f"https://pintia.cn/api/problem-sets/{PTASetid}/submissions?before={submissions[-1]['id']}&limit=200&filter=%7B%7D"

        sub_res = session.get(sub_url)
        sub_json = json.loads(sub_res.text)
        if not sub_json["submissions"]:
            break

        submissions = sub_json["submissions"]
        for submission in submissions:
            submitStamp = time_difference(submission["submitAt"], startTime_utc)
            submitDiffStamp = time_difference(endTime_utc, submission["submitAt"])
            submitLanguage = transComplierToLanguage(submission["compiler"])

            if submission["status"] == "COMPILE_ERROR":
                submission["status"] = "COMPILATION_ERROR"

            if submission["status"] in runtime_errors:
                submission["status"] = "RUNTIME_ERROR"

            if isFrozen and submitDiffStamp <= int(frozenTime):
                submission["status"] = "FROZEN"

            runs.insert(
                0,
                {
                    "language": submitLanguage,
                    "problem_id": sub_json["problemSetProblemById"][submission["problemSetProblemId"]]["problemPoolIndex"] - 1,
                    "status": submission["status"],
                    "submission_id": submission["id"],
                    "team_id": sub_json["examMemberByUserId"][submission["userId"]]["studentUser"]["studentNumber"],
                    "timestamp": submitStamp,
                },
            )
        count += 1
        time.sleep(0.5)

    with open("run.json", "w", encoding="utf-8") as f:
        json.dump(runs, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    isFrozen = False
    frozenTime = 1800
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hft:", ["help", "frozen", "frozenTime="])
    except getopt.GetoptError:
        print("Usage 1: python3 Sync_runs.py -f -t <frozenTime>")
        print("Usage 2: python3 Sync_runs.py --frozen --frozenTime <frozenTime>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Usage 1: python3 Sync_runs.py -f -t <frozenTime>")
            print("Usage 2: python3 Sync_runs.py --frozen --frozenTime <frozenTime>")
            sys.exit()
        elif opt in ("-f", "--frozen"):
            isFrozen = True
        elif opt in ("-t", "--frozenTime"):
            frozenTime = arg

    get_member_runs("PTASession", "JSESSIONID", "ProblemSetId", isFrozen, frozenTime)
