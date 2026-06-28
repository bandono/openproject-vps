# Task Status Workflow

Menu:

```
Administration > Work packages > Workflow

<BASE URL>/workflows/edit
```
(Edit for `Member` and `Project admin` Type `Task` )

Task next status depends on the previous status, below are the allowed change in current settings which are slight modification from default (only the important ones listed with each status ID)


|              |          |    *Next* →  |                 |              |             |              | |
|:-------------|:--------:|:------------:|:---------------:|:------------:|:-----------:|:------------:|:------------:|
| ***Prev* ↓**  | New (1) | Scheduled (6) | In Progress (7) | Tested (10) | Closed (12) | On Hold (13) | Rejected (14) |
| New (1)         | ◆ | ◆ | ◆ |   | ◆ | ◆ | ◆ |
| Scheduled (6)   | ◆ | ◆ | ◆ |   |   |   |   |
| In Progress (7) | ◆ |   | ◆ | ◆ |   | ◆ | ◆ |
| Tested (10)     |   |   |   | ◆ | ◆ | ◆ |   |
| Closed (12)     | ◆ |   | ◆ |   | ◆ | ◆ | ◆ |
| On Hold (13)    | ◆ |   | ◆ |   | ◆ | ◆ | ◆ |
| Rejected (14)   | ◆ |   | ◆ |   | ◆ | ◆ | ◆ |