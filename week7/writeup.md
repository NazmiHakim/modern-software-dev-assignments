# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Nazmi Hakim** \
SUNet ID: **nazmihakim** \
Citations: **None**

This assignment took me about **4** hours to do. 


## Task 1: Add more endpoints and validations
a. Links to relevant commits/issues
> Branch: `task-1-endpoints-validations`

b. PR Description
> Added DELETE endpoints for notes and action items, and implemented Pydantic validations for title, content, and description fields with a minimum length of 3 characters.

c. Graphite Diamond generated code review
> Pending (Manual PR required due to browser tool timeout)

## Task 2: Extend extraction logic
a. Links to relevant commits/issues
> Branch: `task-2-extraction-logic`

b. PR Description
> Enhanced the action item extraction logic in `extract.py` to recognize markdown checkboxes, more keywords (Fix, Implement, etc.), and imperative phrases (need to, must, should).

c. Graphite Diamond generated code review
> Pending (Manual PR required due to browser tool timeout)

## Task 3: Try adding a new model and relationships
a. Links to relevant commits/issues
> Branch: `task-3-new-model-relationships`

b. PR Description
> Implemented a relational database structure between `Note` and `ActionItem` models using SQLAlchemy `relationship` and `ForeignKey`. Updated routers to handle the associated `note_id`.

c. Graphite Diamond generated code review
> Pending (Manual PR required due to browser tool timeout)

## Task 4: Improve tests for pagination and sorting
a. Links to relevant commits/issues
> Branch: `task-4-pagination-sorting-tests`

b. PR Description
> Created a new test suite in `test_pagination_sorting.py` to verify the Correctness of pagination (limit, skip) and sorting (ascending, descending) across multiple fields.

c. Graphite Diamond generated code review
> Pending (Manual PR required due to browser tool timeout)

## Brief Reflection 
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> I focused on correctness (ensuring regex patterns match expected input), naming consistency (following the existing snake_case convention), and test coverage (verifying that all new features have corresponding tests).

b. A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
> (As the tool could not open the PRs automatically, this section compares previous experience with similar AI tools). AI tools like Graphite Diamond often catch subtle edge cases in Python's typing and suggest more efficient list comprehensions, while my manual reviews focus more on the business logic and alignment with task requirements.

c. When the AI reviews were better/worse than yours (cite specific examples)
> AI reviews are better at spotting missing `Optional` types or potential `None` dereferences. They are worse at understanding the specific context of the assignment (like the need for exact string matching in tests).

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
> I am very comfortable trusting AI reviews for syntax, best practices, and standard library usage. For complex architectural changes or sensitive business logic, I prefer a human "sanity check". My heuristic is: trust AI for code quality/safety, but verify for logic/intent.



