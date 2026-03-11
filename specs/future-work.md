# Future Work

Deferred features from planning conversations. These are out of scope for MVP but worth pursuing later.

---

## Authentication & API Keys
- User registration and API key generation
- Key-based rate limiting and usage tracking
- Per-key analytics (which structures, how many inferences)

## Pricing Tiers
- Implement the two-tier pricing model from the PRD
- Metering: track discovery calls vs inference calls separately
- Billing integration (Stripe or similar)
- Free tier with limited discoveries per month

## SDKs & Client Libraries
- Python SDK for programmatic access
- Java SDK for enterprise integration
- TypeScript/Node SDK for web developers
- All SDKs should wrap the REST API with typed models

## Ethical AI Guardrails
- Harmful-content detector AI that screens every reasoning structure before returning to user
- Block generation of reasoning structures for malicious tasks
- Content policy enforcement on task descriptions and outputs
- Audit logging for compliance

## Enterprise Metrics Dashboard
- Usage analytics: discoveries per day, inferences per structure, most popular structures
- Accuracy tracking: compare structured vs naive results over time
- Cost savings calculator: show users how much compute they're saving
- Structure health monitoring: detect structures that produce poor results

## Robotics Expansion
- Adapt atomic modules for robotics task planning
- Atomic modules = robot actions (grasp, move, sense, place)
- Discover optimal action sequences for robotic tasks
- Execute discovered plans across different physical environments

## XML Support
- XML output format as alternative to JSON for reasoning structures
- XML request bodies for enterprise systems that prefer XML
- Content negotiation via Accept headers

## Benchmarking Harness
- Automated benchmark suite (BigBench-Hard, MATH, etc.)
- Run SELF-DISCOVER vs CoT vs CoT-SC on standard datasets
- Track accuracy and compute metrics over time
- Regression detection when models or prompts change

## Structure Versioning
- Version history for reasoning structures
- Diff view between structure versions
- Ability to roll back to previous versions
- Track which version was used for each inference

## Rate Limiting
- Per-user and per-API-key rate limits
- Separate rate limits for discovery (expensive) vs inference (cheap)
- Graceful degradation with queue-based overflow
- Rate limit headers in API responses

## Cross-Model Transfer Experiment
- Test discovered structures across different LLM families (GPT-4, Claude, Llama)
- Validate the paper's finding that structures transfer between models
- Build a model compatibility matrix for each structure
- Allow users to specify which model to use for inference

## Custom Reasoning Modules
- Let users define their own atomic reasoning modules
- Module marketplace: share and discover community-created modules
- Module effectiveness scoring based on usage data

## Batch Processing
- Batch inference endpoint for processing many problems with same structure
- Async job queue for large batches
- Webhook notifications on batch completion

## Structure Sharing & Marketplace
- Public structure library: browse and use structures others have discovered
- Rating and review system for structures
- Categories and tags for discoverability
- Fork and modify existing structures
