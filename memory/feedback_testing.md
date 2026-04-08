---
name: Write tests instead of interactive approvals
description: User prefers a runnable test suite over interactive bash approvals for verification tasks
type: feedback
---

Write automated tests (pytest) that can be run with a single command rather than asking the user to approve multiple interactive bash commands for verification.

**Why:** Repeated approval prompts for bash commands are annoying when the goal is just confirming things work.

**How to apply:** When verifying that code or an environment works correctly, write a test file and add a `pixi run test` task (or equivalent), then run that once for approval rather than running multiple ad-hoc bash commands.
