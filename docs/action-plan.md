# PivotMap Action Plan

## Product Thesis

PivotMap is a persistent career proof graph for students.

It is not a generic resume generator. It turns messy student evidence into structured, confidence-scored proof that can be reused across resumes, job applications, and interviews.

The wedge is low-friction evidence capture:

- speak about what you did
- upload existing material
- connect institution context such as modules
- paste a target JD

All of those inputs write into the same proof store. The graph compounds over time, and MiroFlow makes that compounding useful through registered tools, verification, and visible agent orchestration.

## Hackathon MVP

The hackathon product should center on one golden path:

1. Student yaps about a project or experience.
2. MiroFlow extracts concrete claims.
3. Verifier labels each claim as `verified`, `supported`, `user-attested`, `weak`, or `missing`.
4. Evidence nodes are saved into the proof graph.
5. Student pastes a JD.
6. MiroFlow researches the JD context.
7. Proof map shows matched, weak, and missing evidence.
8. Student receives resume bullets and a gap roadmap.

This is the clearest demonstration of product value and MiroFlow-native architecture.

## Rose, Thorns, Buds

### Rose

- The new direction is tighter because the proof graph is the product spine.
- Voice Yap is the strongest demo moment: raw student ramble becomes structured career evidence.
- Honest scoring is differentiated: PivotMap says which claims will survive scrutiny.
- Live agent trace makes MiroFlow visible instead of hiding it behind a spinner.

### Thorns

- The full feature list is too broad for the hackathon.
- Discovery mode, alumni scraping, and market demand scoring are data-heavy and can sink the build.
- "Verified" must be used carefully. Some evidence is only user-attested or weakly supported.
- NUS-specific features need to be framed as first adapters, not the whole product.

### Buds

- Pitch line: "Anyone can generate a resume bullet. PivotMap tells you whether it will survive scrutiny."
- Institution adapters can make the product globally scalable.
- The proof store can become a long-term career memory graph after the hackathon.
- STAR interview generation becomes natural once proof nodes exist.

## Feature Priority

### Must Ship

- Voice Yap or text-yap capture to structured claims.
- STAR bullet generation from captured evidence.
- JD targeting mode with proof map.
- Live agent trace panel.
- Honest confidence labels.
- Lightweight persistent proof graph.

### Should Ship

- Resume upload as cold start.
- NUSMods module adapter as one proof-enrichment plugin.
- Basic graph visualization.

### Nice To Have

- STAR interview generator.
- GitHub or LinkedIn profile import.
- More institution adapters.

### Cut For Hackathon

- Full Discovery Mode.
- Alumni career path scraping.
- SG market demand scoring.
- Club or society recommendation.
- Full multi-semester career memory beyond a simple persisted proof graph.

## Judge Demo Script

1. Open with the command hero: "Modify my resume to fit this LinkedIn post."
2. Paste or type a 30-second yap transcript about a hackathon.
3. Show MiroFlow trace:
   - planner extracts claims
   - research agent finds context
   - verifier labels confidence
   - synthesiser creates STAR bullets
4. Show the proof graph update with new evidence nodes.
5. Paste a JD.
6. Show MiroFlow researching company-specific skill meaning.
7. Show matched, weak, and missing proof.
8. End on a resume bullet plus roadmap action.

## Judging Alignment

### Product Value

Students forget, undersell, or cannot articulate what they have done. PivotMap lowers the friction to capture proof and turns it into reusable career evidence.

### Engineering Execution

The build demonstrates a real agent pipeline, registered tools, confidence labels, trace output, and persistence.

### AI-Native Authenticity

The product would be weaker as a single LLM call. MiroFlow adds planner decomposition, source-aware research, verification, plugin calls, and stateful graph updates.

### Global Scalability

NUSMods is the first institution adapter. The same architecture can support other universities, job markets, and evidence sources.
