# Copilot Agents Demo

Use the following 3 files to setup your Copilot Agents demo. 
Paste the ISSUE.md file into a new issue in that repository. 

## What this demo shows
- Assign an issue to Copilot to start an agent task
- Monitor progress in AgentHQ
- Re-steer mid-session with a new requirement
- Review the resulting PR like a teammate’s work

## Demo files
- `ISSUE.md` contains the exact issue text to copy/paste into GitHub
- `STEER.md` contains the mid-session requirement change to paste while the agent is working

## Quick demo steps
1. Create a new GitHub Issue by copying the Title and Body from `ISSUE.md`
2. Assign the issue to Copilot to start the agent task
3. Open AgentHQ to monitor progress
4. Paste `STEER.md` into the agent session to re-steer the work
5. Review the PR diff for clarity, completeness, and constraints.
6. Verify the PR edited the README.md file by adding priority levels plus the steered examples. 

---

## Ticket Triage Policy

### Severity levels
| Severity | Description |
|----------|-------------|
| Low | Minor annoyance with an easy workaround |
| Medium | Meaningful user impact but workarounds exist |
| High | Blocks key workflows or causes data loss |

### Priority levels
| Priority | Meaning |
|----------|---------|
| P0 | Critical — system down, immediate response required |
| P1 | High — major feature broken, fix within 1 business day |
| P2 | Medium — degraded experience, fix within 1 sprint |
| P3 | Low — minor issue or enhancement, backlog |

### Severity → Priority mapping
| Severity | Default Priority |
|----------|-----------------|
| High | P0 or P1 |
| Medium | P2 |
| Low | P3 |

### How to triage in 60 seconds
1. Read the ticket and assign a Severity (Low / Medium / High)
2. Use the mapping above to set the default Priority
3. Adjust Priority up/down based on customer impact or business context
4. Assign an owner and set the due date per the Priority SLA
5. Add relevant labels and close the triage loop
