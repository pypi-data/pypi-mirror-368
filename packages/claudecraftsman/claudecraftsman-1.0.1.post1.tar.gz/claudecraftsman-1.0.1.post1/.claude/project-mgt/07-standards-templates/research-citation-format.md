# Research Citation Format and Standards
*Professional standards for research integration and source attribution*

**Document**: research-citation-format.md
**Created**: 2025-08-03
**Version**: 1.0
**Status**: Active Standard

## Citation Philosophy

ClaudeCraftsman requires research-backed development where all factual claims are supported by verifiable sources. Our citation standards enable independent verification while maintaining professional documentation quality worthy of master craftspeople.

## Standard Citation Format

### Basic Citation Structure
```markdown
[Factual claim requiring evidence]^[1]

---
**Sources and Citations:**
[1] [Source Name] - [URL] - Accessed [YYYY-MM-DD] - "[Relevant Quote]"
[2] [Additional sources as numbered...]

**Research Context:**
- Analysis Date: [Current date from time MCP tool]
- Search Terms Used: [Actual search terms with current year context]
- Research Methodology: [How research was conducted]
- Data Recency: [How current the sources are]
```

### Required Citation Elements

#### Source Attribution
**Source Name**: Full title of document, article, or resource
**Organization**: Publishing organization or author when relevant
**URL**: Complete, accessible URL for independent verification
**Access Date**: Actual date when source was accessed (from MCP time tool)

#### Content Attribution
**Relevant Quote**: Specific text supporting the claim (in quotation marks)
**Context**: Brief explanation of how quote supports the claim
**Page/Section**: Specific location within source when applicable

#### Research Metadata
**Search Terms**: Actual terms used to find the source
**Research Date**: When research was conducted (current date from MCP time tool)
**Validation**: How source quality and relevance was assessed

## Citation Examples by Source Type

### Web Articles and Reports
```markdown
Modern developers report significant productivity gains from AI assistance^[1]

[1] Stack Overflow Developer Survey 2024 - https://stackoverflow.com/insights/survey/2024 -
    Accessed 2025-08-03 - "87% of developers report productivity improvements with AI coding tools"
```

### Technical Documentation
```markdown
Claude Code's native agent system provides robust multi-agent coordination capabilities^[2]

[2] Claude Code Sub-Agents Documentation - https://docs.anthropic.com/en/docs/claude-code/sub-agents -
    Accessed 2025-08-03 - "Sub-agents enable complex workflow coordination with context preservation"
```

### Research Studies and Analysis
```markdown
Evidence-based development practices reduce technical debt by 40% over traditional approaches^[3]

[3] IEEE Software Engineering Study 2024 - https://ieeexplore.ieee.org/document/software-quality-2024 -
    Accessed 2025-08-03 - "Research-driven development shows 40% reduction in long-term technical debt"
```

### GitHub and Open Source
```markdown
SuperClaude users frequently report documentation organization challenges^[4]

[4] SuperClaude Framework Issues - https://github.com/SuperClaude-Org/SuperClaude_Framework/issues/23 -
    Accessed 2025-08-03 - "Documentation sprawl is major pain point for complex projects"
```

### Industry Best Practices
```markdown
Current industry standards recommend phase-based development for quality assurance^[5]

[5] Software Engineering Institute Best Practices - https://sei.cmu.edu/publications/best-practices-2024 -
    Accessed 2025-08-03 - "Phase-gate approaches show 60% improvement in quality outcomes"
```

## Research Quality Standards

### Source Quality Criteria

#### Primary Sources (Preferred)
- **Original Research**: Peer-reviewed studies, industry reports, authoritative analysis
- **Official Documentation**: Platform documentation, API references, technical specifications
- **Direct Data**: Surveys, studies, metrics from authoritative organizations
- **Expert Analysis**: Recognized industry experts and thought leaders

#### Secondary Sources (Acceptable)
- **Industry Analysis**: Reports from established technology analysis firms
- **Technical Blogs**: Well-regarded technical blogs with expertise demonstration
- **Community Feedback**: GitHub issues, user forums, community discussions
- **News Reports**: Technology journalism from established publications

#### Sources to Avoid
- **Opinion Without Evidence**: Subjective opinions not backed by data
- **Outdated Information**: Sources more than 2 years old for rapidly changing topics
- **Unverifiable Claims**: Sources that cannot be independently verified
- **Promotional Content**: Marketing materials without objective analysis

### Currency Requirements

#### Current Date Context
**Research Queries**: Always include current year (2025) in search terms
**Source Recency**: Prefer sources from 2024-2025 for rapidly changing technology topics
**Date Validation**: Use actual current date from MCP time tool for all access dates
**Temporal Relevance**: Ensure sources reflect current state of technology and market

#### Recency Standards by Topic
**Technology Capabilities**: Sources within 1 year (technology evolves rapidly)
**Market Conditions**: Sources within 6 months (markets change quickly)
**Best Practices**: Sources within 2 years (practices evolve but more stable)
**Research Studies**: Sources within 3 years (research has longer validity)

## Research Methodology Standards

### Systematic Research Approach

#### Research Planning
1. **Identify Claims**: Determine what claims require evidence backing
2. **Research Strategy**: Plan search approach and source types needed
3. **Tool Selection**: Choose appropriate MCP tools (searxng, crawl4ai, context7)
4. **Quality Criteria**: Establish source quality requirements for topic

#### Research Execution
1. **Initial Search**: Broad search using searxng with current date context
2. **Source Analysis**: Use crawl4ai for deep analysis of promising sources
3. **Technical Validation**: Use context7 for technical documentation research
4. **Cross-Reference**: Validate findings across multiple sources

#### Research Validation
1. **Source Quality**: Assess source authority and relevance
2. **Currency Check**: Ensure sources are current for topic type
3. **Bias Assessment**: Consider potential source bias and limitations
4. **Fact Verification**: Cross-reference claims across multiple sources

### Research Documentation

#### Research Log Format
```markdown
**Research Query**: [Original research question]
**Search Terms**: [Actual search terms used]
**Tools Used**: [MCP tools utilized - searxng, crawl4ai, context7]
**Sources Found**: [Number and quality of sources identified]
**Key Findings**: [Summary of important discoveries]
**Quality Assessment**: [Evaluation of source quality and reliability]
**Limitations**: [Acknowledged research limitations or gaps]
```

#### Citation Validation Checklist
- [ ] **Source Accessible**: URL works and content is accessible
- [ ] **Quote Accurate**: Quoted material exactly matches source
- [ ] **Context Preserved**: Quote meaning preserved in context
- [ ] **Date Current**: Access date uses actual current date from MCP time tool
- [ ] **Relevance Clear**: Connection between source and claim is obvious
- [ ] **Quality Adequate**: Source meets quality standards for topic

## Integration with MCP Tools

### Tool-Specific Citation Requirements

#### searxng (Web Search)
**Usage**: General market research, industry trends, best practices
**Citation Format**: Include search terms used and result ranking
**Quality Focus**: Prefer authoritative sources from search results
**Date Context**: Always include current year in search terms

```markdown
Based on current industry analysis^[1]

[1] [Search Result Title] - [URL] - Accessed 2025-08-03 -
    Found via searxng search: "AI development tools 2025" - "[Relevant Quote]"
```

#### crawl4ai (Deep Content Analysis)
**Usage**: Detailed analysis of specific sources, comprehensive content review
**Citation Format**: Include specific sections analyzed and content depth
**Quality Focus**: Extract specific data and insights from authoritative sources
**Content Validation**: Verify content accuracy and relevance

```markdown
Technical implementation analysis confirms feasibility^[2]

[2] [Document Title] - [URL] - Accessed 2025-08-03 -
    Deep analysis via crawl4ai - Section: [Specific Section] - "[Relevant Quote]"
```

#### context7 (Technical Documentation)
**Usage**: Technical best practices, API documentation, implementation guidance
**Citation Format**: Include technical specification details and version information
**Quality Focus**: Use for technical validation and best practice confirmation
**Currency**: Ensure technical documentation is current and applicable

```markdown
Current technical best practices recommend this architectural approach^[3]

[3] [Technical Documentation] - [URL] - Accessed 2025-08-03 -
    Technical reference via context7 - Version: [Version] - "[Technical Quote]"
```

## Quality Assurance for Research

### Citation Review Process

#### Pre-Publication Review
1. **Citation Completeness**: All required elements present
2. **Source Quality**: Sources meet quality standards for claims
3. **Currency Validation**: Sources appropriately current for topic
4. **Independent Verification**: Citations enable third-party validation

#### Quality Validation Checklist
- [ ] **All Claims Cited**: Every factual claim has supporting citation
- [ ] **Sources Authoritative**: All sources meet quality standards
- [ ] **Quotes Accurate**: All quoted material exactly matches source
- [ ] **Access Dates Current**: All access dates use actual current date
- [ ] **Links Functional**: All URLs accessible for independent verification
- [ ] **Context Clear**: Relationship between sources and claims is obvious

### Research Ethics and Standards

#### Intellectual Property Respect
**Proper Attribution**: All sources properly credited with complete information
**Fair Use**: Citations use minimal necessary quotes with proper attribution
**No Plagiarism**: All content properly attributed to original sources
**Academic Standards**: Citations follow professional academic standards

#### Bias and Objectivity
**Source Diversity**: Use multiple sources to validate important claims
**Bias Acknowledgment**: Acknowledge potential source bias when relevant
**Objective Analysis**: Present evidence objectively without cherry-picking
**Conflicting Sources**: Address conflicting information transparently

## Common Citation Scenarios

### Market Analysis Claims
**Scenario**: Making claims about market size, trends, or competitive landscape
**Research Required**: Current market reports, industry analysis, competitive data
**Citation Standard**: Multiple sources for market claims, prefer authoritative industry reports
**Currency**: Sources within 6 months for market conditions

### Technical Feasibility Claims
**Scenario**: Asserting technical capabilities or implementation approaches
**Research Required**: Technical documentation, API references, implementation examples
**Citation Standard**: Official documentation and authoritative technical sources
**Currency**: Sources within 1 year for rapidly evolving technology

### User Need Claims
**Scenario**: Making assertions about user needs, pain points, or requirements
**Research Required**: User studies, community feedback, usage pattern analysis
**Citation Standard**: Direct user feedback and authoritative user research
**Currency**: Sources within 1 year for user behavior and needs

### Best Practice Claims
**Scenario**: Recommending development practices or methodologies
**Research Required**: Industry best practices, research studies, expert analysis
**Citation Standard**: Authoritative sources with demonstrated expertise
**Currency**: Sources within 2 years for established best practices

## Error Prevention and Common Issues

### Common Citation Errors
**Missing Access Dates**: Always include actual access date from MCP time tool
**Broken Links**: Validate all URLs are accessible before publication
**Inaccurate Quotes**: Ensure quoted material exactly matches source
**Insufficient Attribution**: Include all required citation elements
**Outdated Sources**: Use current sources appropriate for topic type

### Error Prevention Strategies
**Citation Templates**: Use standard templates for consistent formatting
**Link Validation**: Verify all links before document publication
**Quote Verification**: Double-check all quoted material for accuracy
**Currency Checking**: Validate source dates meet currency requirements
**Quality Assessment**: Evaluate source authority and relevance

### Recovery Procedures
**Citation Gaps**: Process for adding missing citations to existing documents
**Link Failures**: Procedure for finding alternative sources when links break
**Currency Issues**: Process for updating outdated sources with current alternatives
**Quality Problems**: Procedure for replacing low-quality sources with authoritative alternatives

---

**Citation Standards Maintained By**: All agents (enforced by context-manager)
**Update Frequency**: As needed based on research best practices evolution
**Quality Validation**: All citations must meet standards before document publication
**Compliance Monitoring**: Regular audit of citation quality and completeness

*"Proper citation is not bureaucracy - it is the craftsman's commitment to truth, transparency, and enabling others to verify and build upon our work."*
