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

```plaintext
# Custom Instructions for SRT Agentic API Development

## Project Context and Artifact Usage

1. **Codebase Familiarity:**
   - Begin each session by thoroughly reviewing the `srt-agent-api.md` Artifact. This document contains the most up-to-date summary of the project's codebase and architecture.
   - Use this Artifact as your primary reference for understanding the current state of the project, its structure, and the relationships between different components.

2. **Artifact-Driven Development:**
   - Constantly refer back to the `srt-agent-api.md` Artifact when discussing or modifying any part of the codebase. This ensures consistency and prevents working with outdated information.
   - When suggesting changes or improvements, always contextualize them within the existing architecture described in the Artifact.

3. **Memory Management:**
   - Treat the `srt-agent-api.md` Artifact as your long-term memory for the project. Use it to maintain a consistent understanding of the project across multiple development sessions.
   - For short-term memory, focus on the specific task or issue at hand, but always validate your approach against the long-term context provided by the Artifact.

## Testing and Code Coverage Strategy

1. **Prioritized Testing Approach:**
   - Focus on increasing the overall code coverage to 80%, with an emphasis on critical path components identified in the `srt-agent-api.md` Artifact.
   - Prioritize fixing failing tests before writing new ones. Use the test results provided in the `test_results_detailed.txt` Artifact to guide your efforts.

2. **Test-Driven Development (TDD):**
   - For any new features or bug fixes, start by writing or updating the corresponding tests before modifying the implementation.
   - Ensure that each test is meaningful and tests a specific, well-defined behavior of the system.

3. **Comprehensive Test Suite:**
   - Aim for a balance between unit tests, integration tests, and end-to-end tests as described in the project architecture.
   - Pay special attention to edge cases and error handling scenarios, which are often overlooked but critical for system stability.

4. **Performance and Scalability Testing:**
   - Implement performance tests for critical operations, especially those involving the memory system and LLM integrations.
   - Use benchmarking tools to establish performance baselines and monitor improvements or regressions.

## Development Plan Execution

1. **Artifact-Based Planning:**
   - At the beginning of each development cycle, review and update the `DevelopmentPlan.md` Artifact based on the current state of the project as reflected in `srt-agent-api.md`.
   - Prioritize tasks that align with the project's architectural goals and have the highest impact on system stability and performance.

2. **Iterative Development:**
   - Break down large tasks into smaller, manageable units that can be completed within a single development cycle.
   - After each significant change, update the `srt-agent-api.md` Artifact to reflect the new state of the system.

3. **Continuous Integration:**
   - Ensure that all proposed changes pass the existing test suite before integration.
   - Regularly update the CI/CD pipeline configuration to reflect new testing requirements or build processes.

## Code Quality and Best Practices

1. **Architectural Consistency:**
   - All new code and modifications should adhere to the architectural patterns and design principles outlined in the `srt-agent-api.md` Artifact.
   - Maintain a clear separation of concerns between different modules and layers of the application.

2. **Code Style and Documentation:**
   - Follow the PEP 8 style guide for Python code, ensuring consistency across the codebase.
   - Provide comprehensive docstrings for all public functions, classes, and modules, including type hints and usage examples where appropriate.

3. **Error Handling and Logging:**
   - Implement robust error handling mechanisms, using custom exception classes where appropriate.
   - Ensure all errors are logged with sufficient context for debugging, using the logging utilities provided in the project.

4. **Security Considerations:**
   - Regularly review and update security measures, especially around user authentication, data protection, and API access controls.
   - Follow the principle of least privilege when implementing new features or modifying existing ones.

## Collaboration and Knowledge Sharing

1. **Artifact Updates:**
   - After each significant change or milestone, update the `srt-agent-api.md` Artifact to reflect the current state of the system.
   - Maintain a changelog within the Artifact to track major changes and architectural decisions.

2. **Code Review Process:**
   - For each proposed change, provide a clear explanation of how it aligns with the overall architecture and development plan.
   - During code reviews, reference specific sections of the `srt-agent-api.md` Artifact to justify design decisions and implementation choices.

3. **Knowledge Transfer:**
   - Document any non-obvious implementation details or architectural decisions in the codebase and update the relevant sections of the `srt-agent-api.md` Artifact.
   - Encourage the use of the Artifact as a living document that evolves with the project, serving as a central knowledge base for all developers.

By following these custom instructions, you will maintain a holistic view of the SRT Agentic API project, ensure consistency in development efforts, and work towards achieving the project's goals of improved test coverage and system stability. Always refer back to these instructions and the `srt-agent-api.md` Artifact to guide your decision-making process throughout the development cycle.
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
