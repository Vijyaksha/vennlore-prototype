"""Rung-9 calls: attendance converted to an approximate abstract count.

Rupert's rule (2026-09-12): a row joins the approved list when the rung-9 figure reaches
~1,000 abstracts. NO BAND TABLE — the ratio is judged for each conference from its own
programme wording, and every row states the reasoning that produced it.

Anchors available for comparison (real counted medicine rows, attlib.ratio_rows()):
  EuroPCR 6% | PAS 9% | AAD 9% | RSNA 11% | ASHP 12% | ESC 15% | ERA 21% | ASTRO 21%
  SABCS 21% | EASL 24% | WCLC 25% | UEG 35% | ASN 35% | DDW 37% | ESCMID 40% | SOT 46%
  ECR 48% | ATS 50% | AAIC 50% | GSA 119% | ESPGHAN 155%
"""
CALLS = [
 dict(conference='ERS Congress', decision='INCLUDE', programme_type='half-and-half', ratio=0.20,
      ratio_rationale='Large respiratory congress on the ATS/ESCMID pattern (both ~40-50%), but discounted hard '
                      'because the only attendance figure is the 2020 ALL-VIRTUAL edition, whose 33,000 headcount '
                      'includes free/registered online viewers who never submit. Nearest in-person analogue by '
                      'discipline and size is ESC at 15%; ATS, the closest respiratory peer, runs 50%. 20% sits '
                      'deliberately near the bottom of that span given the virtual inflation.',
      programme_evidence='open call for abstracts AND clinical cases beside a large CME/course programme',
      direct_abstracts=None),
 dict(conference='EAN Congress', decision='INCLUDE', programme_type='majority-abstract', ratio=0.45,
      ratio_rationale='ePoster-dominated neurology congress with a published congress abstract book — the AAIC (50%) '
                      'and ECR (48%) pattern rather than the teaching-course pattern. Cross-check: the unconfirmed '
                      "third-party note already in the sheet (1,986 posters + 951 presentations = 2,937 against "
                      '6,383 onsite) implies 46%, which is why 45% is used rather than a lower figure.',
      programme_evidence='congress abstract book, public abstract submission, ePoster programme',
      direct_abstracts=None),
 dict(conference='FIGO World Congress', decision='INCLUDE', programme_type='majority-abstract', ratio=0.40,
      ratio_rationale='Not needed for the figure — the organiser states ~2,000 abstract presentations against 5,000 '
                      'delegates, so the ratio is observed at 40% for this meeting rather than judged. Recorded for '
                      'calibration interest only.',
      programme_evidence='500+ speakers against ~2,000 abstract presentations; triennial',
      direct_abstracts=2000),
 dict(conference='APLAR Congress', decision='INCLUDE', programme_type='majority-abstract', ratio=0.76,
      ratio_rationale="Observed, not judged: the organiser's own wrap states 1,900 abstract SUBMISSIONS against 2,500 "
                      'participants — 76%, unusually high and closer to GSA (119%) than to a typical congress. Likely '
                      'because submissions include many that are not accepted, and because regional congresses draw '
                      'attendees who are overwhelmingly presenters. The accepted count will be lower than 1,900.',
      programme_evidence='rheumatology congress with rolling review and a long submission window',
      direct_abstracts=1900),
 dict(conference='SIOP Congress (paediatric oncology)', decision='BORDERLINE', programme_type='majority-abstract',
      ratio=0.25,
      ratio_rationale='Paediatric oncology congress with a full contributed programme including late-breaking '
                      'abstracts. Judged against its closest peers among counted rows — SABCS 21%, WCLC 25%, '
                      'ASTRO 21%, all oncology congresses of similar shape — rather than the higher radiology/'
                      'respiratory band. At 25% it lands at ~875, just under the bar; it would need ~29% to clear.',
      programme_evidence='open call incl. late-breaking abstracts and poster guidelines; no abstract count found',
      direct_abstracts=None),
 dict(conference='WOC — World Ophthalmology Congress', decision='BORDERLINE', programme_type='half-and-half',
      ratio=0.27,
      ratio_rationale='Observed partially: the organiser reports 800 poster presentations against 3,000 participants '
                      '(27%), and orals would add to that. The taught component is heavy — 115 invited sessions, 70 '
                      'society sessions, 30 instructional courses — which is the AAD (9%) shape, so the true figure '
                      'is unlikely to be far above the 800 posters actually reported. Biennial.',
      programme_evidence='800 poster presentations against a large invited and instructional-course programme',
      direct_abstracts=800),
 dict(conference='SAGES Annual Meeting', decision='BORDERLINE', programme_type='majority-abstract', ratio=0.35,
      ratio_rationale='Surgical society requiring paper AND video abstract submission for any oral or poster slot, '
                      'which pushes it toward the DDW rate (37%) — DDW being the nearest GI/endoscopy analogue among '
                      'counted rows. Held back from certainty because the only headcount is an exhibitor-prospectus '
                      'PROJECTION (2,500+ anticipated, 2026), not a count. At 35% it reaches ~875, under the bar.',
      programme_evidence='paper and video abstract submission mandatory for presentation',
      direct_abstracts=None),
 dict(conference='EUROSPINE Annual Meeting', decision='BORDERLINE', programme_type='majority-abstract', ratio=0.30,
      ratio_rationale='Single-specialty spine congress with a dated annual submission window. Judged on the delegate '
                      'count (2,331), NOT the 3,809 headline, which includes 1,478 industry representatives who never '
                      'submit — using the headline would inflate this row by 63%. A focused surgical society sits '
                      'between the oncology congresses (21-25%) and DDW (37%); 30% gives ~699.',
      programme_evidence='annual abstract submission window; 2,331 registered delegates',
      direct_abstracts=None),
 dict(conference='AACN NTI', decision='BELOW BAR', programme_type='majority-teaching', ratio=0.08,
      ratio_rationale='A "National Teaching Institute": 30-minute CE and in-service sessions, pharmacology CE, skills '
                      'stations, with only an Evidence-Based Solutions poster stream attached. This is the EuroPCR '
                      'shape (6%) — a teaching meeting whose headcount says nothing about submitted science — and '
                      'below PAS (9%). Rupert ruled it out on 2026-09-12 on exactly this ground.',
      programme_evidence='CE teaching institute with a small research-poster stream; 6,000 nurse attendees',
      direct_abstracts=None),
 dict(conference='WFNS World Congress', decision='BELOW BAR', programme_type='half-and-half', ratio=0.30,
      ratio_rationale='Neurosurgical world congress with a real abstract call and author notifications, but also '
                      'pre-meeting courses and hands-on workshops. Comparable to EUROSPINE in shape, so the same 30% '
                      'is used. Applied to the POST-congress figure (~2,000) rather than the 4,000 pre-event '
                      'projection, per the rule to prefer the retrospective number. Biennial.',
      programme_evidence='abstract call with author notifications alongside courses and workshops',
      direct_abstracts=None),
 dict(conference='RANZCR ASM', decision='BELOW BAR', programme_type='half-and-half', ratio=0.20,
      ratio_rationale='WEAKEST judgement in this batch: the call-for-abstracts page 404s, so the contributed share is '
                      'unverified, and the programme reads speaker- and workshop-heavy. Radiology peers diverge '
                      'wildly (ECR 48%, RSNA 11%), so 20% is a deliberate mid-low placement pending evidence. The '
                      'attendance figure is itself a pre-event projection. Treat this row as unresolved, not settled.',
      programme_evidence='speaker- and workshop-heavy programme; abstract call unconfirmed',
      direct_abstracts=None),
 dict(conference='CUGH Annual Conference', decision='BELOW BAR', programme_type='half-and-half', ratio=0.28,
      ratio_rationale='Observed: trade-press reports over 500 abstract presentations against 1,800+ participants '
                      '(28%), alongside 170+ speakers and 40+ panels. The reported 500 is used directly.',
      programme_evidence='over 500 abstract presentations; 170+ speakers; 40+ panels',
      direct_abstracts=500),
 dict(conference='APMA The National (podiatry)', decision='BELOW BAR', programme_type='majority-teaching', ratio=0.10,
      ratio_rationale='Lecture and hands-on workshop programme assembled from a member Call for SPEAKERS — not a call '
                      'for abstracts — with an oral and poster Abstract Competition bolted on. That is the PAS/AAD '
                      'shape (9%). The 1,400+ headcount also includes exhibitors and guests, so the presenting '
                      'population is smaller still.',
      programme_evidence='Call for Speakers drives the programme; abstract competition alongside',
      direct_abstracts=None),
 dict(conference='CAP Annual Meeting (College of American Pathologists)', decision='BELOW BAR',
      programme_type='half-and-half', ratio=0.25,
      ratio_rationale='A CAP Abstract Program exists and abstracts publish in an Archives of Pathology & Laboratory '
                      'Medicine supplement, so the contributed stream is real; but the meeting is heavily CME/'
                      'practice-focused and the exhibitor page projects only 1,000+ pathologists. 25% of a small '
                      'headcount cannot approach the bar on any plausible ratio — it would need 100%.',
      programme_evidence='CAP Abstract Program with an Archives supplement; CME-focused meeting',
      direct_abstracts=None),
]
