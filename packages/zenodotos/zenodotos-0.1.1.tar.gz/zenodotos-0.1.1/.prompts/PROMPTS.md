# Quill Project: Chronological List of Prompts by Development Milestone

> **Note:** This file is for reference only and should not be committed to version control.

---

## 1. Project Initialization & Structure
- **Prompt:** "Create a well-organized project structure for a Google Drive CLI tool."
- **Prompt:** "Generate a `README.md` with project description and usage instructions."
- **Prompt:** "Add a `LICENSE` file."
- **Prompt:** "Set up a `pyproject.toml` with dependencies for Google Drive API integration."
- **Prompt:** "Create a testing framework using pytest."
- **Prompt:** "Add documentation directories and files."

## 2. Configuration & Tooling
- **Prompt:** "Add and refine `.gitignore` for Python and coverage files."
- **Prompt:** "Add and enforce project-specific rules for dependency management (using `uv`), testing, linting, and pre-commit hooks."
- **Prompt:** "Review and update `.cursor-rules` for pytest, pre-commit, and dependency management."
- **Prompt:** "Ensure all configuration and dependency changes are tracked and protected."

## 3. Version Control & Commit Workflow
- **Prompt:** "Stage all changes and prepare a conventional commit message."
- **Prompt:** "Review and edit commit messages in Cursor before committing."
- **Prompt:** "Check `git status` and `git diff --staged` before committing."
- **Prompt:** "Commit changes using a prepared message file."

## 4. Google Drive Integration
- **Prompt:** "Review and enhance the `DriveClient` implementation for listing files, pagination, filtering, and error handling."
- **Prompt:** "Review and update the `DriveFile` data model."
- **Prompt:** "Plan and implement file upload and download features."
- **Prompt:** "Pause implementation for review and planning."

## 5. Testing
- **Prompt:** "Create unit tests for the `DriveFile` model and `DriveClient` class."
- **Prompt:** "Create and later discard integration tests for Google Drive."
- **Prompt:** "Run all tests and check for coverage."
- **Prompt:** "Fix test failures related to mocking and error handling."
- **Prompt:** "Skip or suppress problematic tests and document them as tech debt."
- **Prompt:** "Improve test coverage for CLI and formatter modules."
- **Prompt:** "Run and interpret test, lint, and type-checking commands."

## 6. CLI & User Experience
- **Prompt:** "Implement the `list-files` subcommand in the CLI."
- **Prompt:** "Run the CLI and subcommands, and troubleshoot issues with credentials and imports."
- **Prompt:** "Provide instructions for setting up Google API credentials."

## 7. Quality Assurance
- **Prompt:** "Run `pytest` with coverage, `ruff check .`, and `ty check .` as part of the QA process."
- **Prompt:** "Format code using `ruff format .`."

## 8. Documentation & Roadmap
- **Prompt:** "Update the `ROADMAP.md` with known issues and rename the section to 'Accumulated Tech Debt.'"
- **Prompt:** "Document skipped or problematic tests in the roadmap."

## 9. Miscellaneous
- **Prompt:** "Check the current working directory and shell environment."
- **Prompt:** "Review deleted files and their impact on the project."

# Development Prompts

## Authentication Flow and Environment Variable Support

### Task: Implement GOOGLE_DRIVE_CREDENTIALS environment variable support

1. Feature Request:
```
I would like to modify the Quill application to allow the use of Google Drive API without needing a credentials file in a specific location. I propose to use the environment variable GOOGLE_DRIVE_CREDENTIALS.
```

2. Authentication Flow Review:
```
I'm a bit confused about the authentication and configuration interaction for Google Drive. Could you clarify the roles of the credentials file and token file?
```

3. Authentication Refactoring:
```
Let's refactor the authentication flow to handle both credentials and token files properly, ensuring a clear separation of concerns and better error handling.
```

4. Test Implementation:
```
Let's adjust tests for the authentication flow to ensure we have proper coverage for both the default credentials path and the environment variable option.
```

5. Test Verification:
```
Do the tests run correctly? I'm concerned about the mock_credentials being called directly in the mock_flow fixture.
```

6. Documentation Update:
```
Update the README.md to detail this feature
```

7. Roadmap Update:
```
Do we have the Google Drive API's throttling limitations implementation as part of our roadmap? If not, let's include this there.
```

8. Commit Message Review:
```
The commit message is incomplete. The documentation and roadmap is only part of what we just did. The main task was to use an environment variable to specify the credentials file. To do this, we refactored the authentication flow, then added the implementation, created new tests to cover for this change, verified all the checks and then added the documentation. Change the commit message to make all this clear
```

9. Commit Changes:
```
Now we can stage and commit this
```

10. Prompt Documentation:
```
Add the prompts for this task to the PROMPTS.md
``` 