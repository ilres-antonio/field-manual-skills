# Triage labels

The five canonical states `/triage` uses to move issues through the
backlog state machine, mapped to the literal label strings configured on
this repo&#39;s GitHub Issues.

For this repo we use the canonical defaults &mdash; each role&#39;s string equals
its name. No mapping needed.

| Role | Label string | Color | When applied |
| --- | --- | --- | --- |
| Needs evaluation       | `needs-triage`     | `#FBCA04` (yellow) | New issue just landed; a maintainer hasn&#39;t looked yet. |
| Waiting on reporter    | `needs-info`       | `#F9D0C4` (peach)  | Maintainer asked for clarification; ball is in reporter&#39;s court. |
| Ready for an AFK agent | `ready-for-agent`  | `#0E8A16` (green)  | Fully specified, contained, an autonomous loop can pick it up. |
| Ready for human        | `ready-for-human`  | `#1D76DB` (blue)   | Needs a human decision or implementation step. |
| Won&#39;t fix              | `wontfix`          | `#CFD3D7` (grey)   | Declined, duplicate, out of scope. Closed without action. |

## State machine

```
              ┌──────────────────────────────┐
              ▼                              │
  (new) ── needs-triage ─┬─► needs-info ─────┘
                         │
                         ├─► ready-for-agent ─► (closed by Ralph loop)
                         │
                         ├─► ready-for-human ─► (closed by human commit)
                         │
                         └─► wontfix ─► (closed without action)
```

- An issue should have **exactly one** triage-state label at any time.
- Transitions update the label by removing the old one and adding the new
  one in the same call: `gh issue edit N --remove-label needs-triage
  --add-label ready-for-agent`.
- `/triage` will refuse to apply a label that doesn&#39;t exist on the repo.
  If you rename a label later, update this file *and* re-run
  `gh label create` for the new name.

## How to recreate the labels (if accidentally deleted)

```sh
gh label create needs-triage    --color FBCA04 --description "Needs maintainer evaluation"
gh label create needs-info      --color F9D0C4 --description "Waiting on reporter for more info"
gh label create ready-for-agent --color 0E8A16 --description "Fully specified — AFK agent can pick up"
gh label create ready-for-human --color 1D76DB --description "Needs human decision or implementation"
gh label create wontfix         --color CFD3D7 --description "Will not be actioned"
```
