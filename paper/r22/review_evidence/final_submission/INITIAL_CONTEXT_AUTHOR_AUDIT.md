# Independent context and author audit

Reviewed by: `/root/r22_final_context_audit`, 5 October 2026. Read-only review of scientific artifacts; no detector runs, scientific results, manuscript edits or external reviewer dispatch.

Baseline inspected: `03_submission_IEEE-TRS/manuscript/main.tex` SHA256 `672391d80749913f886acf9c961e05f14c5e329c4fe2fb68881da120287d81d1`; `supplement/supplement.tex` `18ee8cc71102a5fda1583ac69c26915843fa4c4170baed0dcbb5d4c8bd03a9f8`; `manuscript/references.bib` `8dc2a2f1d385939d244a3ada1cfbb4364f092f2fb6d80944aea14596c99d6ff0`. These identify the initial R22 snapshot, not any subsequently edited final snapshot.

## Findings and recommended scope

R22 already gives results analysis and limitations for all three additions. No new theorem or new theoretical contribution should be manufactured from the additional experiments. The useful final pass is an evidence-to-narrative integration and submission polish pass: make the established hook and the purpose of each validation visible without accumulating another literature survey.

| Addition | Existing substantive integration | Literature decision |
| --- | --- | --- |
| Extended guard trajectories | Results, persistent/emerging subsection; Fig. 3b; Table IV; Discussion; Conclusion; full supplement extension and Fig. S6 | Existing Lops/Naldi clutter-map self-masking, PAMF and the paper's post-onset law are sufficient. No new reference is necessary merely because the horizon increased from eight to 48 elapsed looks. |
| Unknown-timing continuous migration | Discussion paragraph; Table IV; abstract/conclusion qualification; complete supplement search protocol, all 24 conditions and null intervals | One focused motion-aware acquisition bridge is justified. A classic point-target reference is a closer match than a recent spread-target method. A modern spread-target extension can be included only with its distinct target model explicit. |
| UW external-camera pedestrian presence | Results paragraph cites `uwraw2022` and `gao2021ramp`; Table IV; Discussion/Conclusion; complete supplement mask/endpoint/rotation/sensitivity description | Existing primary dataset and RAMP-CNN label-method citations are sufficient. No separate vision survey, learned-detector comparison or extra recent dataset citation is warranted. |

The new studies should be described as distinct questions within one detector-design argument: recovery of classical innovation laws under a stated model; calibration on measured clutter; prediction of reference contamination and its guarded delay; certification under a stated hit model; and boundaries under realistic emergence/acquisition and real-target evidence. Presenting them as an ever-growing list of contributions would weaken that argument.

## Focused migration literature

### Closest match: point-target motion-aware coherent integration

Verified article: **Jia Xu, Ji Yu, Ying-Ning Peng and Xiang-Gen Xia**, “Radon-Fourier Transform for Radar Target Detection, I: Generalized Doppler Filter Bank,” **IEEE Transactions on Aerospace and Electronic Systems, 47(2), 1186–1202, 2011**, **DOI [10.1109/TAES.2011.5751251](https://doi.org/10.1109/TAES.2011.5751251)**.

The [actual author-uploaded full paper](https://www.researchgate.net/publication/224230390_Radon-Fourier_Transform_for_Radar_Target_Detection_I_Generalized_Doppler_Filter_Bank) explicitly identifies Jia Xu as the content uploader. It is a primary research paper hosted on ResearchGate, not a secondary literature summary. Its abstract describes a range/velocity hypothesis search followed by Doppler integration. Section II uses linear radial motion, a sinc compressed-pulse response and a constant complex backscatter coefficient. This closely matches the assumptions of the present point-target migration injection. Its introduction discusses the residence-time limit of single-cell Doppler integration. Publisher access was attempted but returned a sparse page; bibliographic details also agree with the citation in the [IET publisher's related STRFT paper](https://doi.org/10.1049/iet-rsn.2011.0132).

This source supports the existence and purpose of motion-aware coherent processing. It does not establish its performance under this manuscript's calibrated NetRAD search, and no RFT experiment was performed here. Do not imply a measured comparison or a validated upstream/downstream system architecture.

Suggested compact Related Work text:

> Motion-aware coherent integration searches range and velocity jointly to recover returns that migrate across cells [Xu2011]. Our migration test asks whether a cell-wise history-normalized screen remains sensitive when crossing time is unknown.

### Qualified modern extension, optional

Verified article: **Yunlian Tian, Wei Yi, Wujun Li and Hongbin Li**, “Joint Coherent Integration and Detection of Radar Spread Targets With Range Migration,” **IEEE Transactions on Signal Processing, 73, 4873–4888, 2025**, **DOI [10.1109/TSP.2025.3629732](https://doi.org/10.1109/TSP.2025.3629732)**. The [author-institution primary record](https://researchwith.stevens.edu/en/publications/joint-coherent-integration-and-detection-of-radar-spread-targets-/) displays those exact authors, year, title, journal, volume, pages, DOI and abstract.

The source's exact relevant abstract passage is: “multiple-hypothesis architecture with respect to the RST motion state and scattering centers (SCs) distribution.” It concerns **range-spread targets**, jointly estimated motion/scatterer support and combined inter-pulse coherent/intra-pulse incoherent integration. The displayed detailed derivation is for a zero-mean Gaussian noise case. These assumptions differ from the present point-target injection and compound-Gaussian clutter question.

If the author chooses to cite a modern extension, the accurate two-sentence bridge is:

> Motion-aware coherent integration searches range and velocity jointly for migrating point targets [Xu2011]; recent joint detectors also estimate the scattering support of range-spread targets [Tian2025]. Here the migration test measures the sensitivity of a cell-wise history-normalized screen with unknown crossing time.

The recommendation is **Xu2011 first; Tian2025 only if this precise distinction adds value and fits**. Do not cite Tian2025 merely for recency. No third addition is needed. A 2023 modified-Keystone sea-surface paper was identified in the primary publisher's search result, but it also treats high-resolution range-spread structure; it is unnecessary beside the more directly matched RFT source.

Suggested bibliography fields, with no invented issue number for the continuous-volume TSP paper:

```bibtex
@article{xu2011rft,
  author={Jia Xu and Ji Yu and Ying-Ning Peng and Xiang-Gen Xia},
  title={Radon-{Fourier} Transform for Radar Target Detection, {I}: Generalized {Doppler} Filter Bank},
  journal={IEEE Trans. Aerosp. Electron. Syst.},
  volume={47}, number={2}, pages={1186--1202}, year={2011},
  doi={10.1109/TAES.2011.5751251}}
@article{tian2025migration,
  author={Yunlian Tian and Wei Yi and Wujun Li and Hongbin Li},
  title={Joint Coherent Integration and Detection of Radar Spread Targets With Range Migration},
  journal={IEEE Trans. Signal Process.},
  volume={73}, pages={4873--4888}, year={2025},
  doi={10.1109/TSP.2025.3629732}}
```

## UW context is already sufficient

The [primary RAMP-CNN full text](https://arxiv.org/html/2011.08981v2), Sections IV-C and VI-A, describes synchronized camera/radar capture, image-derived classes/depth and manually calibrated camera labels. Its acquisition table specifies 30 frames/s and 2 transmitters/4 receivers. The source supports the existing label-provenance wording; it supplies no precise error bound establishing native-bin radar onset. The source does not justify relabelling presence association as detector sensitivity to an externally timed clean onset.

No additional modern automotive recognition citation is needed: the manuscript evaluates a fixed scalar detector, not the RAMP-CNN network, and its limited selected records cannot be presented as a full automotive recognition benchmark. Existing references plus the complete supplement preserve the appropriate distinction.

## Credibility wording and data breadth

The main Introduction's current validation sentence lists IPIX, NetRAD and 77 GHz real-interference data but omits the newly added UW camera-labelled pedestrian records. Experimental Design also lists only the original three sources; UW methodology is given later and in the supplement. One concise validation map would integrate the addition without claiming stronger validation than achieved. For example:

> The tests span X- and S-band measured sea clutter, 77 GHz measured interference and camera-labelled pedestrian returns. Injected targets isolate onset and migration mechanisms; real returns test their practical limits.

This is an optional but valuable narrative integration, not a newly discovered scientific defect. If the main Methods adds a UW clause, it should identify three records, the 33.3 ms look spacing, whole-record roles and the supplement's fixed acquisition/mask protocol; it need not repeat all parameters.

Data-release recency and measurement recency are different. IPIX is 1993, NetRAD records are 2011 with a 2026 public dataset citation, and selected UW records are 2019 with a 2022 dataset citation. The diverse frequencies, clutter regimes, interference provenance, target endpoints and exposure stages add credibility. Calling these many newly measured independent campaigns would be inaccurate. G/M reuse exposed IPIX/NetRAD recordings; R uses three new same-day UW records. Many pulses and conditions do not create independent campaigns.

Claims that remain mature and do not require polishing: physical clutter source does not enter the common-texture AR model; exchangeability is required rather than established by nonoverlap; guards delay rather than cure self-masking; migration tests lack a measured complex hardware response; external camera labels identify presence without precise clean radar onset. These are already stated clearly.

## Author identity and affiliation

The user supplied the fourth/fifth author order. Public sources verify identity/affiliation, not research contribution roles, author consent or order.

The accessible [NUST CAE faculty directory](https://cae.nust.edu.pk/faculty/) lists **M Atif Shahzad** and **Syed M Kazam Abbas Kazmi**, each under **Department of Avionics Engineering**, with displayed designation RVF. The [CAE institutional page](https://cae.nust.edu.pk/about-us/) confirms College of Aeronautical Engineering, National University of Sciences and Technology. These primary institutional records support a common affiliation consistent with the existing first-author CAE/NUST/Risalpur address.

Use **M.~Atif~Shahzad** fourth and **Syed~M.~Kazam~Abbas~Kazmi** fifth, preserving the displayed name forms. The user typed “Atif Shehzad,” while the linked official directory uses **Shahzad**. Do not expand either M into Muhammad without an author/source confirming it. No degree, IEEE membership, biography, ORCID or author-specific CRediT role is verified by this review.

The two exact supplied profile URLs were attempted via `web.open` and direct HTTPS fetch. The first tools returned cache/fetch failures; the direct public requests returned HTTP 403. Therefore no individual-profile contact details were verified. Search surfaced several different historical Kazmi email forms in publications, which are not reliable current-profile confirmation; omit author-specific emails unless author-confirmed. The existing corresponding-author email can remain.

Provided profile URLs: [fourth author](https://cae.nust.edu.pk/faculty/m-atif-shahzad/), [fifth author](https://cae.nust.edu.pk/faculty/syed-m-kazam-abbas-kazmi/). Only the accessible directory is relied on for the verified names and departments.

## Verdict

The additional results do **not** merit a broad new literature review. They merit one tightly matched motion-aware-acquisition context bridge and a compact evidence map, while existing results/discussion analysis is already substantive. An end-to-end final narrative pass is justified by the user's submission goal, provided it changes only passages with a concrete communication defect or missing connection, retains conditional contributions and failed outcomes, and leaves mature mathematical statements intact. All manuscript/companion identity changes require refreshed PDFs, bibliography, source ZIPs and package manifests; prior signed checks identify the previous hashes and cannot automatically certify the revised artifact.
