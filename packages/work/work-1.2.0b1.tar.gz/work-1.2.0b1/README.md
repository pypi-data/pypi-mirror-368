# Work time log

`work` allows manual time tracking with an interaction model inspired by `git`:

1. Text files are used for storage. This makes it easy to track the log with `git`.
2. The tool does not run continously and instead only modifies the `work status` on disk.
3. The `work status` is global, meaning any terminal can be used to check or update it.
4. Checksums are used to verify that the log was not modified by another tool.

## Features

- Time tracking
  + Time track while working and (optionally) add a category and message.
  + Retroactively add and modify any entry.
- Analyses
  + Calculate and check the hours worked over arbitrary periods.
  + List tracked entries by date or category with optional filters.
- Overtime and undertime
  + Configure "expected hours" and view the accumulated over-/undertime.
  + (Optionally) store vacations or holidays.
- Export entries as CSV.

## Read More

For more information, including examples and the release history, check the [website](https://vauhoch.zett.cc/work/).
