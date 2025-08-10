import os
import pytest
from jira import JIRA

_bug_numbers = set()
_jira_status_cache = {}
_test_names = {}


def awaiting_fix(bug_number):
    def decorator(func):
        marker = pytest.mark.awaiting_fix(bug_number)
        return marker(func)
    return decorator


def pytest_addoption(parser):
    parser.addoption(
        "--jira-server",
        action="store",
        help="JIRA server URL"
    )
    parser.addoption(
        "--jira-user",
        action="store",
        help="JIRA email address"
    )
    parser.addoption(
        "--jira-token",
        action="store",
        help="JIRA API token"
    )


def pytest_configure(config):
    global jira_client

    config.addinivalue_line(
        "markers", "awaiting_fix(bug_number): mark test as awaiting fix"
    )
    pytest.awaiting_fix = awaiting_fix

    # Read values from CLI
    jira_server = config.getoption("--jira-server") or os.environ.get('JIRA_SERVER')
    if jira_server is None:
        raise RuntimeError("Missing CLI arg --jira-server OR environment variable JIRA_SERVER")

    jira_user = config.getoption("--jira-user") or os.environ.get('JIRA_USER')
    if jira_user is None:
        raise RuntimeError("Missing CLI arg --jira-user OR environment variable JIRA_USER")

    jira_token = config.getoption("--jira-token") or os.environ.get('JIRA_TOKEN')
    if jira_token is None:
        raise RuntimeError("Missing CLI arg --jira-token OR environment variable JIRA_TOKEN")

    try:
        jira_client = JIRA(server=jira_server, basic_auth=(jira_user, jira_token))
    except Exception as e:
        raise RuntimeError(f"Failed to authenticate to Jira: {e}")


def get_jira_status(bug_number):
    if bug_number not in _jira_status_cache:
        try:
            issue = jira_client.issue(bug_number)
            status = issue.fields.status.name
            _jira_status_cache[bug_number] = status
        except Exception as e:
            _jira_status_cache[bug_number] = "UNKNOWN"
    return _jira_status_cache[bug_number]


def pytest_runtest_setup(item):
    marker = item.get_closest_marker("awaiting_fix")
    if marker:
        bug_number = marker.args[0] if marker.args else None
        if bug_number:
            _bug_numbers.add(bug_number)
            _test_names.setdefault(bug_number, set()).add(item.nodeid)
            status = get_jira_status(bug_number)
            pytest.skip(f"Skipped awaiting fix for bug {bug_number} (status: {status})")


def pytest_sessionfinish(session, exitstatus):
    tagline = "🤖[*awaiting-fix*]🤖"
    if _bug_numbers:
        for bug in sorted(_bug_numbers):
            _jira_status_cache.get(bug, "UNKNOWN")
            
            # Gather current test info
            test_names = sorted(_test_names.get(bug, []))
            new_count = len(test_names)
            tests_block = "\n".join(f"➡️ {test_name}" for test_name in test_names)
            body = (
                f"{tagline}\n"
                f"🔔 When resolved, please re-enable automated test(s):\n{tests_block}"
            )

            # Fetch existing comments and find the most recent awaiting-fix one (if any)
            comments = jira_client.comments(bug)
            awaiting_comments = [c for c in comments if getattr(c, 'body', '') and tagline in c.body]

            def parse_existing_count(text):
                return sum(1 for line in text.splitlines() if line.strip().startswith("➡️ "))

            if not awaiting_comments:
                # No prior awaiting-fix comment: add a fresh one
                try:
                    jira_client.add_comment(bug, body)
                    print(f"✅ Comment added to {bug}")
                except Exception as e:
                    raise RuntimeError(f"❌ Failed to add comment to {bug}: {e}")
            else:
                # Choose the most recent by comment id (ids are numeric strings in Jira)
                try:
                    latest = max(awaiting_comments, key=lambda c: int(getattr(c, 'id', '0')))
                except Exception:
                    latest = awaiting_comments[-1]

                existing_count = parse_existing_count(getattr(latest, 'body', ''))
                if new_count != existing_count:
                    try:
                        comment_to_delete = jira_client.comment(bug, getattr(latest, 'id'))
                        comment_to_delete.delete()
                        print(f"🗑️ Deleted outdated awaiting-fix comment on {bug}")
                    except Exception as e:
                        raise RuntimeError(f"❌ Failed to delete existing awaiting-fix comment on {bug}: {e}")
                    try:
                        jira_client.add_comment(bug, body)
                        print(f"✅ Comment updated on {bug}")
                    except Exception as e:
                        raise RuntimeError(f"❌ Failed to add updated comment to {bug}: {e}")
                else:
                    print(f"⚠️ Existing awaiting-fix comment for {bug} is up-to-date or has higher/equal count. leaving as is.")