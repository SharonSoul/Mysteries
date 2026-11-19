---
name: historical-fact-checking
description: Rigorous fact-checking, source verification, and evidence categorization for historical and archaeological mystery documentaries. Use when researching historical topics, verifying claims, checking archaeological provenance, identifying pseudoarchaeology or misattributed quotations, and classifying claims into the 6-tier epistemic truth framework.
license: MIT
metadata: {"scope": "research-library", "epistemic_levels": 6}
---

# Historical Fact-Checking & Source Verification

This skill enforces strict historical rigor, source credibility evaluation, and claim taxonomy for the **Mysteries and Unexplained History Documentary Studio**.

## The 6-Tier Epistemic Truth Framework

Every factual claim in a documentary script or research dossier MUST be explicitly classified into one of the following six categories:

1. **Established Historical Fact**: Direct physical, archaeological, epigraphic, or unanimous documentary evidence accepted by the scholarly consensus (e.g., the Antikythera mechanism was recovered from a shipwreck dated to ~60 BC).
2. **Strongly Supported Interpretation**: High-probability hypothesis backed by substantial peer-reviewed evidence and methodology, though direct documentation is missing (e.g., the mechanism was used as an astronomical analogue computer).
3. **Disputed Historical Claim**: Multiple competing, credible academic hypotheses exist with conflicting interpretations of the evidence (e.g., whether the Minoan civilization collapsed primarily due to the Thera eruption or subsequent Mycenaean invasion).
4. **Popular Theory / Folk Tradition**: Widespread cultural, traditional, or speculative beliefs documented historically, but lacking rigorous archaeological or material corroboration (e.g., stories connecting the Oak Island mystery to the Knights Templar).
5. **Speculation / Fringe Hypothesis**: Assertions with minimal, cherry-picked, or debunked evidence (e.g., ancient advanced acoustic levitation of megaliths, extraterrestrial intervention). *Rule: May be presented only as a cultural phenomenon or debunked concept, never as historical reality.*
6. **Genuinely Unexplained Question**: An acknowledged historical or archaeological mystery where empirical data is currently insufficient for definitive conclusions (e.g., the undeciphered Linear A script, the exact destination of the Lost Colony of Roanoke).

## Non-Negotiable Research Standards

- **Zero Invention**: Never hallucinate or invent archaeological discoveries, dates, radiocarbon readings, artifact dimensions, historical figures, or quotes.
- **Traceable Attribution**: Every primary assertion must have a verifiable source (institution, author, year, publication).
- **Primary vs. Secondary Distinctions**: Always differentiate between an ancient primary source (e.g., Herodotus writing 400 years after an event) and modern archaeological/forensic confirmation.
- **Dating Methodology**: Clearly state dating methods (e.g., stratigraphic excavation, radiocarbon dating with standard deviation, dendrochronology, thermoluminescence) when dates are pivotal to the mystery.

## Source Credibility Hierarchy

| Tier | Source Category | Examples | Usage |
|---|---|---|---|
| **Tier 1** | Primary Scholarly / Institutional | *Nature*, *Science*, *Antiquity*, *Journal of Archaeological Science*, The British Museum, Smithsonian, Louvre, INAH, peer-reviewed excavation reports | Definitive source of record |
| **Tier 2** | Academic Books & Monographs | Oxford University Press, Cambridge UP, Routledge, university department publications | Reliable context and synthesis |
| **Tier 3** | Reputable Educational & Historical Media | National Geographic, Archaeology Magazine, BBC History, Smithsonian Magazine | General narrative context; verify claims against Tier 1/2 |
| **Tier 4** | Primary Historical Chronicles & Folklore | Icelandic Sagas, ancient papyri, medieval chronicles, folklore anthologies | Treat as historical literature/perspectives, not uncritical empirical facts |
| **Tier 5** | Unvetted Web Content / Fringe Literature | Commercial mystery blogs, sensationalist conspiracy books, viral social posts | Inadmissible as factual citations; examine only as examples of public myth |

## Red Flags & Pseudoarchaeology Traps

When conducting research, actively test against common historical pitfalls:
- **Anachronistic Technology**: Claims attributing modern engineering capabilities to ancient builders without evidence of intermediate tools.
- **Hyperdiffusionism**: Assuming similar geometric shapes (pyramids, mounds, spirals) across separate continents require a single lost mother civilization.
- **Misattributed or Fabricated Quotations**: Frequently attributed to figures like Einstein, Napoleon, or ancient philosophers. Always check primary texts.
- **Ignored Stratigraphy**: Treating an artifact found in an upper soil layer as belonging to an ancient lower stratum.

## Deliverable: The Fact-Check Ledger

Save all verification dossiers into `research-library/<project-name>/fact_check_ledger.md` using this table format:

```markdown
# Fact-Check Ledger: [Documentary Title]

| ID | Script Line / Scene | Claim Extracted | Epistemic Tier (1-6) | Primary Source / Academic Reference | Status / Notes |
|---|---|---|---|---|---|
| C01 | Scene 1 (00:15) | Discovered in 1901 off the coast of Antikythera | Tier 1 (Fact) | Price, D. de Solla (1974); Hellenic Ministry of Culture | Verified |
| C02 | Scene 3 (02:40) | The gearing calculated the Saros eclipse cycle | Tier 2 (Supported) | Freeth et al., Nature (2006) 444, 587–591 | Verified |
| C03 | Scene 5 (06:10) | Built directly by Archimedes | Tier 3 (Disputed) | Cicero, De Re Publica (literary); disputed timeline | Script must phrase as "Cicero attributed similar devices to Archimedes, but the exact builder remains unknown" |
```
