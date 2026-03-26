# ================================================================
# 0 FOR THE HUMAN
# ================================================================
#
# Prompting is the broad skill of providing input to AI systems
#   so that they can do useful work.
# 1. Prompt Craft: Tells autonomous agents what to do.
#    Synchronous. Session-based. Individual skill.
#    Knowing how to structure a query.
#    Must have clear instructions.
#    Must provide clear examples and counter-examples.
#    Need to include appropriate guardrails.
#    Need to include an explicit output format.
#    Be very clear about resolving ambiguity and conflict so that
#      the model doesn't have to make it up on the fly.
#    This scope might be maybe 200 tokens.
# 2. Context Engineering: Tells agents what to know.
#    The set of strategies for curating and maintaing the optimal
#      set of tolkens during an LLM task.
#    Providing relevant tokens to the LLM for inference.
#    Shift from crafting a single instruction to curating the
#      entire information environment an agent operates within.
#    All of the system prompts.
#    All of the tool definitions.
#    All of the retrieved documents.
#    All of the message history.
#    All of the memory systems.
#    The MCP connection.
#    This is the discipline that produces claude.md files,
#      agent specifications, rag pipeline design, memory architectures.
#    Ensures a coding agent understands project conventions.
#    Ensures a research agent has access to the right documents.
#    Ensures a customer service agent can retrieve releavant
#      account history.
#    LLMs degrade as you give them more information, so retrieval
#      quality drops as context grows.
#    Better context infrastructure minimizes this liability.
#    This seems like OpenBrain.
#    This scope might be 1 million tokens.
# 3. Intent Engineering: Tells agents what to want.
#    Practice of encoding organizational purpose.
#    Translate organizational goals, values, trade-off heirarchies,
#      decision boundaries into infrastructure that agents can
#      act against.
#    Intent engineering sits above context engineering the way
#      strategy sits above tactics.
# 4. Specification Engineering: tells agent what success looks like.
#    Practice of writing documents across your organization
#      that autonomous agents can execute against
#      over extended time horizons without human intervention.
#    Ensuring organization's entire informational corpus is
#      agent ingestible and fungible.
#    Specifications are complete structured internally consGL NCCCistent
#      descriptions of what an output should be for a given task.
#    Define how quality is measured.
#    Allow you to apply agents across large swaths of your context
#      with the confidence that what the agent reads
#      will be relevant.
#    Specifications provide a pattern such that
#      an initial agent sets up the environment,
#      a progress log documents what's been done,
#      a coding agent then makes incremental progress
#      against a structured plan every session.
#    The specification becomes the scaffolding that lets
#      multiple agents produce coherent output across sessions.
#
# 5. Human workflow
#    Direct the agent to interview me in detail. 
#    Ask about technical implementation,
#      user interace/user experience (UI/UX), edge cases,
#      concerns, and trade-offs.
#    Don't ask obvious questions -- dig into the hard parts.
#    The agent then writes the spec with the human.

