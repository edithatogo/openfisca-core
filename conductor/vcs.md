# Git VCS Adapter

Adapter version: `conductor.vcs/1`

- Require `git rev-parse --show-toplevel` to equal the selected project root.
- Stage explicit repository-relative paths and refuse unrelated staged changes.
- Use GitHub Flow with pull requests targeting `master`.
- Push, merge, release, publication, and issue or project mutation require
  explicit authorization.
- Structured track ledgers are authoritative; Git notes are disabled here.
