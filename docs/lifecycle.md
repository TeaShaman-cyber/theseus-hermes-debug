# Repository lifecycle policy

## Purpose and current state

This repository is a bounded debugging and reproduction workspace for Hermes Agent workflow and harness defects.

**Research status: PARKED / INCOMPLETE.**

**Registry membership: not declared.** Candidate discovery is advisory and must never be treated as membership, acceptance, or promotion.

## Entry / discovery

A new agent or maintainer entering the repository should:

1. read this policy and the root README;
2. inspect the relevant open issue and current Git state;
3. determine whether the local Hermes environment is actually available;
4. run the canonical QA entrypoint before treating repository changes as ready;
5. keep unknown or unavailable checks explicit rather than converting them to PASS.

## Canonical QA

The single repository QA entrypoint is:

```bash
bash tools/dev/check
```

It is deterministic and network-free. CI invokes the same command rather than reimplementing QA policy in workflow YAML.

The gate checks:

- repository lifecycle contract;
- deterministic unit regressions;
- shell syntax for the QA entrypoint;
- Python syntax for tracked Python files;
- whitespace in the committed branch range, index, tracked worktree, ordinary untracked files, and files inside untracked embedded Git directories.

A green result means only that the observed deterministic checks passed for that repository state.

```text
QA PASS != acceptance != merge authority != release authority
```

## Acceptance and integration

Non-trivial changes should use a GitHub Issue and pull request.

Readiness requires:

1. canonical QA PASS on the exact candidate state;
2. exact-head review with blocking findings resolved or explicitly dispositioned;
3. clear unresolved/degraded evidence, if any.

Merge requires explicit authorized acceptance. Green QA or a review comment does not grant merge authority by itself.

After merge, important lifecycle changes require exact remote readback of the accepted state.

## Release policy

**Release policy: none.**

This debug/reproduction repository does not create tags, GitHub Releases, packages, or publication artifacts by default.

Changing release policy is a project-level decision and requires a dedicated Issue, explicit acceptance, and a versioned policy change. Merge is not release.

## External / upstream writes

Opening or updating issues or pull requests in upstream/external repositories is a separate external mutation. Local reproduction evidence does not imply authority to publish externally.

## Safe resumption

Hermes experiments remain parked until:

1. the local Hermes environment is available again;
2. current runtime/model/tool state is re-audited from fresh evidence;
3. the intended experiment is tied to an existing Issue or a new narrow reproduction Issue;
4. resource/usage constraints are bounded before the run;
5. expected evidence and stop conditions are written down before expensive model execution.

Issue #1 may resume only under these conditions. A new defect should get a separate narrow reproduction Issue rather than expanding the bootstrap issue.

## Registry promotion

Repository name, ownership, public visibility, or doctor discovery are insufficient for Theseus registry membership.

Promotion requires an explicit project decision after the research line is reproducible, maintained, and has a clear lifecycle. Until then, candidate discovery is expected advisory output.
