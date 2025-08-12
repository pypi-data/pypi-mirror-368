"""
Budget request ingestion and filtering for Yearn Treasury.

This module fetches budget requests from GitHub, parses them into
BudgetRequest objects, and provides lists of approved and rejected
requests.
"""

import os
from requests import get
from typing import Final, List

from yearn_treasury.budget._request import BudgetRequest


# Optionally use a GitHub personal access token for higher API rate limits.
# TODO move this to envs file and document
_TOKEN: Final = os.environ.get("GITHUB_TOKEN")
_HEADERS: Final = {"Authorization": f"token {_TOKEN}"} if _TOKEN else {}


def fetch_brs() -> List[BudgetRequest]:
    # URL to fetch issues from the repo
    api_url = "https://api.github.com/repos/yearn/budget/issues"
    # Use parameters to fetch issues in all states, up to 100 per page.
    params = {"state": "all", "per_page": 100, "page": 1}

    brs = []
    retries = 0
    while True:
        response = get(api_url, headers=_HEADERS, params=params)  # type: ignore [arg-type]
        if response.status_code != 200:
            if retries < 5:
                retries += 1
                continue
            raise ConnectionError(f"Failed to fetch issues: {response.status_code} {response.text}")

        data: List[dict] = response.json()  # type: ignore [type-arg]
        if not data:  # If the current page is empty, we are done.
            break

        for item in data:
            # GitHub's issues API returns pull requests as well.
            if "pull_request" in item:
                continue

            # TODO labels table in db (also dataclass) with the descriptions included
            # Extract the label names (tags) from the "labels" key.
            label_objs: List[dict] = item.get("labels", [])  # type: ignore [type-arg]
            labels = {label.get("name") for label in label_objs}

            if "budget request" not in labels:
                continue

            br = BudgetRequest(
                id=item.get("id"),  # type: ignore [arg-type]
                number=item.get("number"),  # type: ignore [arg-type]
                title=item.get("title"),  # type: ignore [arg-type]
                state=item.get("state"),  # type: ignore [arg-type]
                url=item.get("html_url"),  # type: ignore [arg-type]
                created_at=item.get("created_at"),  # type: ignore [arg-type]
                updated_at=item.get("updated_at"),  # type: ignore [arg-type]
                closed_at=item.get("closed_at"),  # type: ignore [arg-type]
                body=item.get("body"),  # type: ignore [arg-type]
                labels=labels,  # type: ignore [arg-type]
            )
            brs.append(br)

        # Move on to the next page.
        params["page"] += 1  # type: ignore [operator]

    return brs


requests = fetch_brs()
approved_requests = [r for r in requests if r.is_approved()]
rejected_requests = [r for r in requests if r.is_rejected()]
