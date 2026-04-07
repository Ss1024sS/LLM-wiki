# Security Policy

## Scope

LLM-wiki generates scripts that run on users' machines (bootstrap, validation, provenance checks). Security issues in these scripts are in scope.

The generated wiki content itself (markdown files) is not executable and generally not a security concern.

## Reporting a Vulnerability

If you find a security issue, please **do not open a public issue**.

Email: [open a private GitHub security advisory](https://github.com/Ss1024sS/LLM-wiki/security/advisories/new)

Or DM on GitHub: [@Ss1024sS](https://github.com/Ss1024sS)

I will respond within 72 hours and work with you on a fix before public disclosure.

## What Counts

- Path traversal in bootstrap script (writing files outside target directory)
- Code injection via project name or raw root name arguments
- Manifest parsing that could execute arbitrary content
- Provenance check that could be tricked into reading sensitive files

## What Doesn't Count

- The bootstrap overwrites files when `--force` is used (that's by design)
- Wiki content can contain anything (it's user-generated markdown)
