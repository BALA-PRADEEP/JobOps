# JobOps UI Direction

## Product interpretation

JobOps is not a job board. It is an application operations system sitting between hourly job discovery and verified application execution.

Primary user:
- the candidate/operator running JobOps for themselves.

Primary goal:
- understand what JobOps is doing without inspecting logs;
- see which jobs are progressing;
- immediately notice when the system needs a human decision;
- trust that no unsafe submission happened.

## Chosen direction

Product / futuristic, restrained.

The interface uses an operations-desk metaphor rather than a conventional SaaS dashboard.

### Memorable idea: the application runway

Every job is shown on one continuous execution route:

```text
Discover -> Resolve -> Score -> Prepare -> Execute -> Outcome
```

A job's current position is visible spatially. Human intervention interrupts the route in a different color, making "where automation stops" immediately legible.

This is intentionally more memorable than a collection of status cards.

## Composition

First viewport:
- narrow masthead;
- large editorial command statement;
- live operational counts;
- asymmetric human-intervention block;
- dark application runway beginning immediately.

Second level:
- dense fresh-job queue on the left;
- intervention desk on the right.

Footer level:
- deterministic system rules as a horizontal contract rather than cards.

## Visual system

Neutrals:
- warm paper background;
- near-black operational canvas;
- muted graphite text.

Primary accent:
- acid chartreuse, used for automation progress and focus.

Supporting state:
- coral/orange, used only for human intervention and blocking state.

No decorative gradients, glass panels, glow blobs or generic dashboard card grid.

## Typography

Typography carries most of the hierarchy:
- condensed/system display stack for large headings;
- functional sans stack for interface text;
- monospace for state, indices and operational metadata.

Numbers are deliberately oversized where they communicate system state.

## Interaction

- pipeline rows brighten on hover/focus;
- the current stage marker enlarges subtly;
- human-blocked markers pulse gently;
- queue rows shift by a few pixels to reveal scanability;
- keyboard focus uses the primary accent;
- reduced-motion preference disables nonessential motion.

## States

Loading:
- branded runway progress line.

Empty:
- pipeline remains visible as a zero-state rather than replacing the interface with a generic illustration.

Error:
- explicitly states that no application action was taken and offers a feed retry.

Success:
- submitted jobs move to Outcome and use confirmation language, not celebratory decoration.

## Responsive behavior

Desktop:
- full six-stage horizontal runway;
- asymmetric 2-column queue/intervention composition.

Tablet:
- runway remains horizontally scrollable;
- intervention desk drops below queue.

Mobile:
- masthead becomes two rows;
- hero stacks;
- pipeline retains horizontal spatial logic rather than collapsing into cards.
