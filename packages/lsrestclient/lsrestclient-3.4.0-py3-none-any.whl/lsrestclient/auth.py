from lsrestclient import LsRestClient, DownStreamError


def auth_am_login(**kwargs) -> str:
    am = LsRestClient.from_env("AM_API_URL", "am", True)
    r = am.post("/auth/login", body=kwargs)
    if r.status_code == 200:
        return r.json().get("access_token")
    else:
        raise DownStreamError("/auth/login", r.status_code, r.content)


def auth_am_login_apikey(org_id: str, api_key: str) -> str:
    return auth_am_login(ORG_ID=org_id, API_KEY=api_key)
