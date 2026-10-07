# socket_demo

A small Python project used to demonstrate a layered security pipeline in GitHub Actions: supply chain checks with Socket.dev, static analysis (SAST) with Bandit, and secret scanning with Gitleaks.

The application itself is deliberately tiny. The pipeline is the point.

## What the pipeline checks

| Layer | Tool | When it runs | What it looks at | What makes it fail |
|---|---|---|---|---|
| Pull request review | Socket GitHub app | On every PR | Changes to `requirements.txt` | Reports risky dependency changes |
| Dependency policy gate | Socket CLI (`socket ci`) | PRs and pushes to `main` | The whole dependency manifest | Any alert set to Block in the security policy |
| Install-time protection | Socket Firewall (`sfw`) | PRs and pushes to `main` | Each package as it downloads | A package identified as malicious |
| Static analysis (SAST) | Bandit | PRs and pushes to `main` | The Python source code | Any security issue found in the code |
| Secret scanning | Gitleaks | PRs and pushes to `main` | The full git history | Any committed credential |

The first three layers check code written by other people (dependencies). The last two check code written in this repository.

## How it is enforced

A branch ruleset on `main` requires a pull request and requires these four checks to pass before merging:

- Socket dependency scan
- Install through Socket Firewall
- Bandit SAST
- Gitleaks secret scan

Without the ruleset the checks only advise. With it, a failing check blocks the merge.

## See it catch something

Pull request #4, "Demo: intentionally vulnerable code (do not merge)", adds a file with three planted flaws. It is left open on purpose.

| Planted flaw | Risk | Caught by |
|---|---|---|
| Hardcoded AWS-style key (fake) | Anyone who can read the repo has the credential | Gitleaks |
| `subprocess.run(..., shell=True)` with user input | Command injection (Bandit B602, CWE-78) | Bandit |
| `requests.get(..., verify=False)` | Certificate checking disabled (Bandit B501, CWE-295) | Bandit |

On that PR the two Socket jobs pass, because no dependency changed, while Bandit and Gitleaks fail. Each tool watches a different part of the project.

## Dependencies

Two packages were chosen directly (`requests` and `pydantic`). `requirements.txt` lists ten, because the other eight are transitive dependencies. Every version is pinned with `==` so that the versions scanned are the versions installed.

## Security policy

Socket's default policy blocks only known malware.

[WRITE THIS YOURSELF: say which alert types you changed to Block, if any, and why you chose those and left the rest as warnings.]

## How to reproduce

1. Fork or clone the repository.
2. Install the Socket Security GitHub app on the repository.
3. Create a Socket API token with the scopes `full-scans:create`, `full-scans:list` and `security-policy:read`.
4. Save it as a repository secret named `SOCKET_CLI_API_TOKEN`.
5. Open a pull request. The workflow in `.github/workflows/security.yml` runs automatically.

To run the checks locally:

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
pip install bandit==1.9.4
bandit -r . -x ./.venv
socket scan create --report
```

## What went wrong while building this

[WRITE THIS YOURSELF, in your own words. Suggested points:]

- [The virtual environment failed to build the first time. What caused it and how you fixed it.]
- [The Bandit job failed on its first run in CI. What the log showed and what the fix was.]
- [The free Socket plan limited the number of API tokens. What you did about it.]

## Known limitations

- **One shared API token.** The free Socket plan allows a single token, so the same one is used locally and in CI. In a production setup each environment would have its own token so it can be revoked independently.
- **Actions pinned to version tags.** The workflow uses tags such as `actions/checkout@v4`. Third-party actions are part of the supply chain too, so a hardened setup would pin them to full commit SHAs.
- **Socket Basics not used.** Socket's own SAST and secret scanning add-on is a separately purchased product, so Bandit and Gitleaks are used as open-source equivalents.
- **No runtime or infrastructure checks.** This pipeline covers dependencies, source code and secrets. It does not include DAST, container scanning or infrastructure-as-code scanning.

## What I would add next

[WRITE THIS YOURSELF: two or three next steps, for example DAST against a running app, pinning actions to SHAs, or a scheduled weekly scan so newly disclosed vulnerabilities are caught even when no code changes.]
