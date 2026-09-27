# Camera Motion Language release checklist

This checklist covers the experimental CLI candidate described in
[RELEASE_CANDIDATE.md](RELEASE_CANDIDATE.md). It does not certify market demand
or general real-video accuracy. Earlier private SOP scores, brightness-centroid
measurements and unverified install-time promises are not release evidence.

## Candidate checks

- [x] Clear purpose, limits and English/Traditional Chinese onboarding.
- [x] Full decode by default; sampled preview never grants approval.
- [x] JSON version/exit contract and conservative error handling documented.
- [x] Fresh Windows Python environment: documented static demo and 14 tests pass.
- [x] Reproducible positive and negative synthetic cases, including omitted-frame motion.
- [x] Four fixed open-animation excerpts with attribution; all abstentions retained.
- [x] Bug/first-use issue form, metadata suggestions, targeted draft and empty observation table.
- [ ] Bind the final reviewed diff to its publication commit and record it.
- [ ] Publish candidate files, then verify links and commands from the public revision.
- [ ] Publish/run the CI matrix through an authorized workflow write path.

The last CI item remains explicit: this candidate's measured platform is the
Windows/Python combination in its receipt. Do not claim the matrix has run.
The metadata file and launch draft do not automatically update GitHub settings
or send a community message.

## Release observations, separate from the gate above

- Record actual first-use attempts, problems and voluntary repeat use.
- Keep views, clones and stars as separate measurements; clones may be automated.
- Broader accuracy work needs rights-cleared AI video and independently specified
  labels. Do not advertise precision/recall or camera/subject separation meanwhile.
- Revisit the comparison after new evidence; do not delete difficult examples.

The earlier sampled/brightness methods are historical implementations, not the
current contract. Preserve their dated records when comparing versions, and use
current JSON and raw benchmark files for this candidate.
