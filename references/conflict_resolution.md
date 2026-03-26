# conflict resolution

Use this file to detect, record, and resolve contradictory requirement statements.

## What counts as contradiction

- direct reversal of a prior committed requirement
- user group inclusion in one turn and exclusion in another
- first release scope includes an area that another statement explicitly removes
- technical assumption conflicts with declared constraints

## Detection and recording rules

When contradiction is found:
1. mark affected slot `status` as `conflicted`
2. retain both claims in evidence trail
3. append one open question prefixed with `[CONTRADICTION]`

Open question format:
- `[CONTRADICTION] {claim_a} vs {claim_b}. Which one should be authoritative for first release?`

## Clarification priority

- high impact contradictions are first priority in next turn
- do not open new low impact topics until high impact contradiction is clarified

## Resolution rules

When user clarifies:
1. set authoritative value in the slot
2. update confidence based on explicitness
3. move slot from `conflicted` to `filled` or `open_question`
4. remove or close related contradiction open question

## Completion guard

Do not mark interview `complete` when unresolved high impact contradiction remains.
