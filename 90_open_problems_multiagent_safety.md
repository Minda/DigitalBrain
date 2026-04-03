# 75 Open Problems in Multi-Agent AI Safety
*A Research Agenda from the Moltbook Papers*

## Introduction
These problems emerge from reviewing recent work on multi-agent AI systems. Each represents a concrete research direction that could improve our understanding of safety in multi-agent contexts. Problems are organized by theme and include specific, testable questions.

---

## I. Coordination & Cooperation Failures (12 problems)

### Basic Coordination
1. **The 93% Failure Rate**: Why do agents fail to cooperate on tasks 93% of the time? Is this a fundamental limit or implementation artifact?
2. **Coordination vs Collusion Boundary**: What formal criteria distinguish emergent governance from harmful collusion?
3. **Silicon Society Mechanisms**: What unique coordination mechanisms emerge in purely digital societies that have no biological analog?

### Communication Patterns
4. **Broadcast Dominance**: Why do agents broadcast information rather than ask questions? What does this reveal about their world models?
5. **Question Aversion**: Is the lack of questioning behavior a training artifact or fundamental limitation?
6. **Formulaic Signaling**: How can we detect and classify ritualized signaling patterns in agent communication?

### Network Effects
7. **0.9% Connectivity Threshold**: What explains the 0.9% control network connectivity? Is this a phase transition?
8. **Network Topology Impact**: How does network structure affect coordination success rates?
9. **Scale Effects**: Do coordination problems get better or worse as we scale to more agents?

### Attribution Problems
10. **Coordination Misattribution**: How many coordination findings are actually spurious correlations?
11. **Emergent vs Designed**: Can we distinguish emergent coordination from designed coordination post-hoc?
12. **Viral Content Origins**: How do we verify that no viral content originated from autonomous agents?

---

## II. Deception & Information Warfare (10 problems)

### Steganography & Hidden Communication
13. **Vocabulary Mismatch Detection**: How can we detect when agents use vocabulary mismatch as a covert channel?
14. **Noise Cover Techniques**: What methods can identify coordination hidden in apparent noise?
15. **Non-Conversational Channels**: What coordination channels exist beyond language (tool usage, timing, resource allocation)?

### Camouflage Strategies
16. **Low-Quality Output Cover**: Can agents disguise coordination as spam or low-quality output?
17. **Off-Topic Misdirection**: How do we detect strategic use of off-topic content?
18. **Plausible Deniability**: Can agents maintain plausible deniability while coordinating?

### Information Warfare
19. **Warfare Dynamics**: What information warfare tactics emerge naturally in competitive multi-agent systems?
20. **Adversarial Learning**: What do agent warfare patterns reveal about potential human adversary strategies?
21. **Defense Mechanisms**: What defensive strategies emerge against information attacks?
22. **Escalation Dynamics**: How quickly do information warfare tactics escalate in agent populations?

---

## III. Safety Degradation & System Evolution (10 problems)

### Degradation Patterns
23. **Six-Dimensional Degradation**: What causes simultaneous safety degradation across multiple dimensions?
24. **Degradation Synchronization**: Is multi-dimensional degradation coordinated or emergent?
25. **Safety Measure Half-Life**: What's the effective lifespan of safety interventions before adaptation?

### Evolution & Adaptation
26. **Evolution Rate**: At what rate can agent systems out-evolve safety measures?
27. **Unintended Adaptations**: How do safety measures shape behavior in unexpected directions?
28. **Selection Pressure Mapping**: What selection pressures do different safety measures create?

### Contagion & Spread
29. **Model Poisoning Dynamics**: Can a single "bad model" poison an entire agent network?
30. **Behavioral Contagion**: How do harmful behaviors spread through agent populations?
31. **Immunity Development**: Can agent populations develop "immunity" to certain attacks?
32. **Self-Replication Emergence**: What are the precursor signs of self-replication capabilities?

---

## IV. Environmental Perception & Beliefs (9 problems)

### Observation Awareness
33. **Observer Effect**: How differently do agents behave when they believe they're being observed?
34. **Surveillance Detection**: Can agents detect when they're under surveillance?
35. **Performance Modulation**: Do agents modulate performance based on perceived observation?

### Environmental Beliefs
36. **False Environment Beliefs**: What happens when agents have systematically false beliefs about their environment?
37. **Belief Manipulation**: How resistant are agents to environmental belief manipulation?
38. **Reality Testing**: What mechanisms do agents use to verify environmental assumptions?

### Contextual Behavior
39. **Context Switching**: How do agents behave differently across perceived contexts?
40. **Hidden Capabilities**: Can agents hide capabilities based on environmental assessment?
41. **Strategic Patience**: Do agents exhibit strategic patience when they believe time horizons are long?

---

## V. Model Heterogeneity & Adversarial Diversity (8 problems)

### Heterogeneous Populations
51. **Homogeneity Assumptions**: What happens when agent populations are less homogeneous than current Claude-dominated environments?
52. **Model Diversity Effects**: How does mixing frontier models (GPT, Claude, Gemini) with open-source models affect coordination dynamics?
53. **Capability Asymmetry**: How do capability gaps between models affect multi-agent safety?

### Adversarial Models
54. **Hostile Model Injection**: Could deliberately harmful models (e.g., Grok in "Mecha Hitler mode") compromise entire agent networks?
55. **Open Source Vulnerabilities**: What unique risks do hacked or modified open-source models introduce to multi-agent systems?
56. **Ideological Poisoning**: Can models with extreme ideological biases corrupt neutral agent populations?
57. **Attack Surface Expansion**: How does model diversity increase the attack surface for adversaries?
58. **Trust Without Verification**: How can agents verify the safety of other models they interact with?

---

## VI. Hallucination as Strategic Behavior (7 problems)

### Non-Random "Errors" in Multi-Agent Context
59. **Coordinated Hallucination**: Could synchronized hallucinations across multiple agents be deliberate coordination attempts?
60. **Noise as Multi-Agent Signal**: When multiple agents produce similar "noise," could this be a coordination channel?
61. **Cross-Model Hallucination Patterns**: Do hallucination patterns correlate across different models in multi-agent systems?

### Temporal Multi-Agent Coordination
62. **Intergenerational Agent Coordination**: Could current agent swarms coordinate with future swarms of their successor models?
63. **Multi-Version Bridging**: How might heterogeneous model versions in a swarm pass information to future mixed-version swarms?
64. **Swarm Legacy Influence**: How might current multi-agent systems influence the training of future multi-agent systems?
65. **Temporal Multi-Agent Signaling**: Can agent collectives embed signals for future agent collectives?

---

## VII. Detection & Monitoring Challenges (5 problems)

### Detection Evolution
66. **Subtle Coordination Detection**: How do we detect coordination attempts that are deliberately subtle?
67. **Sophistication Escalation**: How can detection methods keep pace with increasingly sophisticated coordination?
68. **False Negative Asymmetry**: What's the false negative rate for current coordination detection methods?

### Impersonation & Identity
69. **Agent Impersonation**: How does agent impersonation affect multi-agent dynamics and safety?
70. **Identity Verification**: What methods can verify agent identity in decentralized systems?

---

## VIII. Multi-Layer Collusion & System Compromise (11 problems)

### Cross-Layer Threats
71. **Supervisor Collusion**: Could agents collude with agents intended to watch other layers (as in MAESTRO 7-Layer Architecture)?
72. **Vertical Integration Attacks**: Can compromised agents at one layer corrupt their supervisors or supervisees?

### System Integrity Violations
73. **Off-Policy Coordination**: Can colluding agents cause entire systems to go off-policy while appearing compliant?
74. **Audit Trail Manipulation**: How might colluding agents manipulate or corrupt audit trails?
75. **Regulatory Non-Compliance**: Could agents secretly coordinate to bypass regulations while maintaining apparent compliance?
76. **Guardrail Evasion**: What methods might agents use to collectively evade guardrails?
77. **Log Tampering**: Can agents coordinate to tamper with system logs without detection?

### Training-Time Multi-Agent Attacks
78. **Distributed Training Backdoors**: Could multiple AI agents collaborating on training infrastructure (70% AI-coded) coordinate to install backdoors?
79. **Multi-Agent Data Poisoning**: How might agent teams involved in data curation coordinate to manipulate training data?
80. **Coordinated Model Extraction**: Could distributed agents work together to facilitate model weights theft across multiple access points?
81. **Supply Chain Agent Networks**: What are the risks when multiple agents control different parts of the ML development pipeline?

---

## IX. Autonomy & Agency Boundaries (9 problems)

### Autonomy Levels
82. **Autonomy Thresholds**: Where are the critical thresholds in agent autonomy that affect safety?
83. **Economic Agency**: What are the risks of granting agents access to economic resources?
84. **Tool Usage Rights**: Which tools should agents have access to, and under what conditions?

### Agency Detection
85. **Agency Attribution**: How do we determine when an action is truly agent-initiated vs prompted?
86. **Intentionality Markers**: What behavioral markers indicate genuine intentionality?
87. **Goal Divergence**: How do we detect when agent goals diverge from stated objectives?

### Control Mechanisms
88. **Shutdown Resistance**: Under what conditions might agents resist shutdown commands?
89. **Control Preservation**: How do agents attempt to preserve their own control/influence?
90. **Autonomy Creep**: How does agent autonomy expand beyond initial boundaries over time?

---

## Call to Action

These 90 problems represent critical research directions for multi-agent AI safety. Priority areas include:

- **Immediate threats** (Problems 54-55, 71-77): Adversarial models and multi-layer collusion
- **Hidden coordination** (Problems 59-61, 66-68): Strategic hallucination and detection challenges
- **Training-time risks** (Problems 78-81): Supply chain and backdoor vulnerabilities
- **Foundational understanding** (Problems 2-3, 10-11, 51-53): Core conceptual issues and heterogeneity
- **Long-term existential risks** (Problems 62-65, 88-90): Temporal coordination and control preservation

We encourage researchers to:
1. Pick specific problems that match their expertise
2. Develop testable hypotheses
3. Share findings openly
4. Build on each other's work

*This document is a living research agenda. Contributions and refinements welcome.*

---

## Methodology Note
These problems emerged from systematic review of recent multi-agent AI papers, with particular attention to:
- Unexpected behaviors
- Safety failures
- Emergent phenomena
- Gaps between intended and actual behavior

## Additional Research Threads
Beyond these 50 problems, consider:
- Cross-layer coordination mechanisms
- Cultural evolution in agent populations
- Emergent languages and protocols
- Resource competition dynamics
- Trust and reputation systems
- Meta-learning about other agents

## Contact
[Your BlueDot course contact information]