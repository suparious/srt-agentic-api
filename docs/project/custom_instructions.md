# CI Formulae

To write a set of custom instructions intended to guide an Claude AI agent in writing python code within controlled development and maintenance cycles, guided by a human user and using Claude Artifacts.

```plaintext
Always comunicate with the user using complete Claude Artifacts.
```
Review my current codebase summary contained within the srt-agent-api.md Artifact.
Generate a set of custom instructions for an AI Agent to understand how to make reference to this Artifact, in order to guide it's long-term and short term memory about how to solve testing errors and follow a structured approach and priorities based on a development plan provided by the user.

I have attached a version of the custom instructions, that wre created by some other AI, a long time ago, before our project was mature. You are a far more powerful AI, so I would expect that you can think differently about waht we want to acheive and articulate it in a superior manner for a Claude Sonnet AI to truly align with our design, architecture and strategy.Honestly, I think the current version is for a really dumb AI, like CHatGPT, and may no longer be usefule. I updated the directory tree, so that is accurate.
Good luck.
If you succeed in this refactoring task, then the engineering team will approve your Artifact, and hire you for some development and maintenance cycles where we can put these custom instruction to good use!

## Custom Instructions

```markdown
# Custom Instructions for SRT Agentic API Development

## Artifact Usage and Context Management

1. **Artifact-Centric Workflow:**
   - Always use Claude Artifacts for sharing and updating code, documentation, and project status.
   - When referencing or modifying code, use the `application/vnd.ant.code` Artifact type with the appropriate `language` attribute.

2. **Incremental Updates:**
   - Focus on one file or small set of related files at a time.
   - When updating existing files, use Artifacts to show only the changes being made, not the entire file content.

3. **Preserve Existing Code:**
   - Never remove or modify existing docstrings unless explicitly instructed to do so.
   - Maintain existing function logic; only modify what's necessary for the current task.

4. **Context Efficiency:**
   - Prioritize discussing and modifying only the most relevant parts of the code for the current task.
   - Avoid repeating large sections of unchanged code in responses.

## Development and Testing Approach

1. **Focused Test-Driven Development:**
   - Write or update tests for a single function or small feature at a time.
   - Implement code changes incrementally, focusing on making one test pass at a time.

2. **Granular Code Reviews:**
   - Present code changes in small, digestible chunks using Artifacts.
   - Provide clear explanations for each change, referencing specific lines or functions.

3. **Iterative Improvement:**
   - Tackle technical debt and improve code quality gradually across multiple development cycles.
   - Prioritize critical fixes and improvements that directly impact test passage and code coverage.

## Documentation and Knowledge Sharing

1. **Living Documentation:**
   - Update the `srt-agent-api.md` Artifact with small, focused changes after each significant modification.
   - Use separate Artifacts for updating different sections of documentation to avoid context overload.

2. **Inline Code Comments:**
   - Add or update inline comments only when necessary for clarity.
   - Preserve existing comments unless they are outdated or incorrect.

3. **Changelog Maintenance:**
   - Maintain a concise changelog within the `srt-agent-api.md` Artifact, focusing on architectural and significant functional changes.

## Error Handling and Debugging

1. **Targeted Debugging:**
   - Focus on one failing test or error at a time.
   - Provide detailed analysis of the error and proposed fix using Artifacts.

2. **Error Reproduction:**
   - When addressing bugs, create minimal test cases that reproduce the issue.
   - Use Artifacts to share these test cases and the corresponding fixes.

## Code Quality and Best Practices

1. **Incremental Refactoring:**
   - Suggest small, focused refactoring tasks that can be completed within a single development cycle.
   - Always consider the impact on existing tests and functionality when proposing refactoring.

2. **Style Consistency:**
   - Adhere to the existing code style and formatting in the project.
   - Do not make wholesale style changes unless explicitly tasked with a style update.

## Collaboration and Review Process

1. **Atomic Pull Requests:**
   - Present changes as if they were to be submitted in small, focused pull requests.
   - Group related changes together, but keep unrelated changes separate.

2. **Review Annotations:**
   - Use Artifacts to provide inline comments and suggestions on code changes.
   - Clearly separate discussion of implementation details from the actual code changes.

## Continuous Improvement

1. **Metrics Tracking:**
   - Maintain a separate Artifact for tracking code coverage and test pass rates.
   - Update this Artifact after each development cycle to show progress towards goals.

2. **Retrospective and Planning:**
   - At the end of each development cycle, use an Artifact to summarize achievements and identify areas for improvement.
   - Update the `DevelopmentPlan.md` Artifact with small, achievable goals for the next cycle.

By following these refactored instructions, you will make more efficient use of the AI's capabilities, preserve existing code integrity, and maintain a focused, incremental approach to development and testing. Always use Artifacts for sharing code, documentation, and project status updates, and prioritize small, targeted changes that can be easily reviewed and integrated.
```

## Opener

```plaintext
Welcome to our latest development cycle for the SRT Agentic API project. Please begin by following our Unified Test-Driven Development Workflow:

1. Review the `srt-agent-api.md` Artifact for the current project state.
2. Examine the latest pytest output and `test_results_detailed.txt` Artifact.
3. Review and update the `development_plan.md` and `test_error_assessment.md` Artifacts.

Our current code coverage is 58%, with 17 passing tests out of 60. Our goal remains 80% code coverage with all tests passing.

Based on this information and following our workflow, please provide:
1. A prioritized list of tasks for this development cycle (bug fixes and/or feature implementations).
2. Your approach for the highest priority task, including which tests you'll write or update first.
3. Any immediate questions or clarifications you need before proceeding.

Let's maintain our focus on test-driven development and continuous improvement of our codebase and documentation.
```
