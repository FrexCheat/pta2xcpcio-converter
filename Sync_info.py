import json
import time
import requests


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


def get_member_info(PTA_session, JSESSIONID, ProblemSetId):
    result = {}
    members = list()

    session = get_session(PTA_session, JSESSIONID)
    
    url = f"https://pintia.cn/api/problem-sets/{ProblemSetId}/exam-members?page=0&limit=20"
    res = session.get(url)
    res_json = json.loads(res.text)

    sum_count = int(res_json.get("total"))
    if sum_count % 100 == 0:
        page_count = int(sum_count / 100)
    else:
        page_count = int(sum_count / 100) + 1

    for i in range(page_count):
        url = f"https://pintia.cn/api/problem-sets/{ProblemSetId}/exam-members?page={i}&limit=100"
        res = session.get(url)
        res_json = json.loads(res.text)
        members = members + res_json.get("members")
        time.sleep(0.5)

    for member in members:
        if "studentUser" in member:
            mGroup = "official"
            mOrganization = "your_organization_name"
            mName = member.get("studentUser").get("name")
            mId = member.get("studentUser").get("studentNumber")

            # this is a simple example of zzuliers, you can modify the rules according to yours.
            if mId[0:1] not in "54":
                mOrganization = "2024新生赛-校外"
                mGroup = "unofficial"

            result[f"{mId}"] = {
                "team_id": mId,
                "name": mName,
                "organization": mOrganization,
                "members": [mName],
                "coach": "None",
                "location": "None",
                "group": [mGroup],
            }
        else:
            continue

    with open("team.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    get_member_info("PTASession", "JSESSIONID", "ProblemSetId")
