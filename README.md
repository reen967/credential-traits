# Credential Trait Explorer

This project explores a simple but layered question: what might we infer from someone's path through education?

The Credential Trait Explorer is a tool designed for anyone who wants to explore how we might think differently about education data. Using IPEDS (Integrated Postsecondary Education Data System) as its backbone, this tool allows users to explore colleges based on traits that may be inferred from institutional-level data e.g. resilience, adaptability, self-direction, or communication.

The interface lets you:

- Choose which traits matter to you

- Assign different weights to each trait

- Filter by state

- View results in an interactive table (with options to reveal scores, notes, and state)

There’s also an accompanying reflective essay that dives deeper into the ideas behind the tool; why these traits were selected, the limits of inference, and what this means for how we evaluate candidates.

### Why this exists
We tend to default to prestige, GPA, or school name when evaluating someone’s background. But what if we could use available data more creatively? What if we looked not just at where someone went, but what it might have taken to get through? This tool  offers a starting point for shifting how we think about credentials and the people behind them.

### How the Traits Are Inferred
All trait scores reflect the estimated percentage of graduates from that institution likely to have demonstrated that trait based on the environment they navigated. Here’s how each is calculated (simplified):

**Conscientiousness:** Based on structured graduation timelines. Includes Pell and non-Pell completion rates across 4, 6, and 8 years.

**Resilience/Grit:** Highlights students who likely faced more barriers. Looks at delayed completion (especially for Pell students), transfer-in rates, older students, and GI Bill usage—students who persisted despite a nontraditional path.

**Adaptability:** Captures students navigating multiple formats and transitions. Includes hybrid and online learning, older students, GI Bill, and transfer enrollment.

**Self-Direction:** Indicates agency in navigating one’s education. Combines longer time to completion, part-time/older enrollment, and intentional hybrid participation.

**Growth Mindset:** Reflects improvement and evolution over time. Measures growth across multi-year completion windows and includes hybrid learners.

**Cognitive Readiness:** Based on standardized test scores adjusted for Pell enrollment—acknowledging that raw scores can reflect opportunity more than ability.

**Communication:** Includes English test scores, on-time graduation, and the presence of international students (as a proxy for navigating diverse communication demands).

**Quantitative Reasoning:** Based on math test scores, adjusted by Pell enrollment.

All calculations are available in the code and documented in plain English formulas.

## Data Source + Thanks
All institutional data is drawn from the Integrated Postsecondary Education Data System (IPEDS), a publicly available dataset maintained by the National Center for Education Statistics (NCES). We're grateful for their work in making educational data transparent and accessible.

Also thanks to ChatGPT for helping me think through this, including fixing formulas, writing the bulk of the code, and pointing out improvements in the accompanying essay.

## A Note
This is not a ranking system. It’s a way of looking differently, and hopefully more generously, at what credentials might tell us, and what they often don’t.

Thanks for exploring. If you’re curious about how this was built or want to contribute ideas, I'd love to chat. You can reach me here: arina.berezovsky@gmail.com :)
