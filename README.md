# YourTurn

YourTurn answers the question every shared flat argues about: **"whose turn is it?"** Roommates pick their name (no login) and the app keeps track of two things:

- **Chores**: chores repeat on a schedule (e.g. dishes daily, bathroom weekly). When someone presses "I did it", the app logs it and shows whose turn is next. It also flags overdue chores ("bins not done for 3 days") and shows who did the most chores this month.
- **Shared supplies**: shared items like eggs, coffee pods or toilet paper. When someone presses "I bought it" and enters the price, the app shows whose turn it is to buy next and how much each roommate has spent this month.

This is a single-process monolithic app (Python + Flask + SQLite), built for Individual Assignment 1. The two domains share only the list of roommates, so they can be split into separate services later.

## Status

Project setup. Setup instructions, run command and test coverage command will be added as the app is built.
