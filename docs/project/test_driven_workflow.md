# Unified Test-Driven Development Workflow for SRT Agentic API

## Initialization Phase

1. **Codebase Review:**
   - Review the `srt-agent-api.md` Artifact to understand the current state of the project, its architecture, and any recent changes.

2. **Test Status Assessment:**
   - Examine the latest pytest output and `test_results_detailed.txt` Artifact to identify failing tests and areas with low code coverage.

3. **Development Plan Alignment:**
   - Review and update the `DevelopmentPlan.md` Artifact, ensuring it aligns with the current project state and prioritizes both bug fixes and feature implementations.

## Iterative Development Cycle

4. **Task Prioritization:**
   - Based on the test results and development plan, prioritize the next task (either a bug fix or a new feature).

5. **Test Writing/Updating:**
   - For bug fixes: Update existing tests or write new ones to reproduce the bug.
   - For new features: Write new tests that define the expected behavior of the feature.

6. **Implementation:**
   - Implement the necessary code changes to make the new or updated tests pass.
   - Ensure adherence to the project's architectural principles as defined in `srt-agent-api.md`.

7. **Local Testing:**
   - Run the test suite locally to verify that the changes resolve the issue or implement the feature correctly.
   - Address any new test failures that may have been introduced.

8. **Code Review Preparation:**
   - Update the `srt-agent-api.md` Artifact to reflect any architectural changes or significant implementation details.
   - Prepare a summary of changes, referencing relevant sections of the updated Artifact.

9. **Continuous Integration:**
   - Push the changes to the CI/CD pipeline and review the full test suite results.
   - Address any issues identified in the CI/CD process.

## Reflection and Planning

10. **Progress Evaluation:**
    - Update the code coverage statistics and test pass/fail ratio in the `CurrentStatusSummary.md` Artifact.
    - Assess progress towards the 80% code coverage goal and 100% passing tests.

11. **Plan Adjustment:**
    - Based on the progress made, adjust the `DevelopmentPlan.md` and `TestImprovementPlan.md` Artifacts as necessary.
    - Identify the next highest priority items for the subsequent development cycle.

12. **Knowledge Sharing:**
    - Document any lessons learned, non-obvious implementations, or architectural decisions in the `srt-agent-api.md` Artifact.

## Cycle Completion

13. **Status Report:**
    - Generate a status report summarizing the changes made, current test status, and updated priorities for the next cycle.

14. **Preparation for Next Cycle:**
    - Ensure all Artifacts are up-to-date and accurately reflect the current state of the project.
    - Formulate the opening prompt for the next development cycle based on the status report and updated Artifacts.

By following this unified workflow, each development cycle will consistently address both debugging and feature implementation within a test-driven framework. This approach ensures that testing remains a priority, code quality is maintained, and the project progresses steadily towards its goals.