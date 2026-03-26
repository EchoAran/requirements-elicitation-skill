# intent routing

Use this file to classify newest user input before structural maintenance and slot filling.

## Intent classes

- explicit requirement
- exploratory idea
- scope change or correction
- meta process comment

## Classification signals

### explicit requirement
Common signals:
- should
- must
- need
- required

Action:
- fill corresponding slot with `confirmed` when mapping is clear
- if mapping is broad, split into one confirmed item and one follow up question

### exploratory idea
Common signals:
- maybe
- perhaps
- we might
- should we

Action:
- store as tentative using `supported_inference` or open question
- ask one confirmation question before treating as committed scope

### scope change or correction
Common signals:
- not anymore
- actually we do not
- replace previous decision
- correction

Action:
- treat newest statement as authoritative candidate
- replace old slot value when correction is explicit
- trigger framework maintenance review when scope direction changes

### meta process comment
Common signals:
- this interview is too long
- summarize what we have
- switch strategy

Action:
- do not fill product requirement slots from this line alone
- adjust question strategy or move to interim summary

## Product type routing at start

When phase is `start`, detect product type from initial idea:
- commerce marketplace
- internal enterprise tool
- social content product
- workflow utility product
- unknown

Routing rule:
- if product type is clear, initialize with the corresponding minimum viable topic emphasis
- if unclear, use default topic set and ask one compact disambiguation question
