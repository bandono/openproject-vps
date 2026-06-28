# Agent Task Board Management Using API

## 1. Python Env

```
~/.pyenv/versions/[placeholder]
```

`<script path>`

```
~/[placeholder]
```

## 2. API Settings and Project Information 

API settings is kept in `<root project path>/.config/client-settings.json`

```
{
  "api_key": "<generated value obtained by logging in to the OpenProject web, will differ for each USER_ID>",
  "base_url": "http://example.com"
}
```

Required project information that will be passed as argument to relevant API script

```
USER_ID = [placeholder]
PROJECT_ID = [placeholder]
BOARD_ID = [placeholder]
```

This `API Test Project` test board can be used to try API using below information:

```
(TEST) PROJECT_ID = 5
(TEST) BOARD_ID = 14
```

## 3. Available Use Cases

### 3.1. Create Board Task

In addition to the basic project information, the below is required: 

```
PARENT_ID
```

other member of team as Task-Taker (if you are Architect).

```
Task-Taker 1
ASSIGNEE_ID = [placeholder]

Task-Taker 2
ASSIGNEE_ID = [placeholder]
```

Create OpenProject `Work package` with the type of `Task` (typically) under a `User Story` (having the `PARENT_ID`)

Function:
1. Create `Task` under (typically) a `User Story` (default successful creation will not be on Task Board yet) using `task-example.md` file containing at least subject (task card short description) and description.
2. Assign task to other member.
3. Make the created task appears on the Task Board where the vertical position default is on top of the swim lane (unless specified).
4. Default `Status` is New (1)

Use the project `<root project path>/tmp` for creating Task subject and description by `.md` file. Example file: [task-example.md](task-example.md)



Example

```
<pyenv> <script path>/create-board-task.py \
  --project PROJECT_ID \
  --parent PARENT_ID \
  --file tmp/task-example.md \
  --lane "Sprint Backlog" \
  --position 0 \
  --assignee ASSIGNEE_ID
```

Output

`Work package` ID

```
Created WP #105: Some example subject  or card title
WP #105 added to 'Sprint Backlog' (query=41) position=0
```

Task board swim lanes are listed in `<script path>/board-settings.json`. They represent where we are in visual flow system (Kanban), however preserving `Work package` `Status` e.g. New, Scheduled.

Starting lane on the board is 'Long List'. This lane is for Architect populating candidate tasks to enter the Sprint. Tasks agreed in Sprint Planning are moved to Sprint Backlog. Task-taker will wait for the `Status` to change to Scheduled (6) for them to start working on it.

### 3.2. Move Task

Required information:

`Work package` ID

```
WP_ID
TARGET_LANE
```
Function:
1. Move task between swim lanes of the Task Board with default `Status` change as listed in `board-settings.json` by first removing it from its current lane.
2. Change the `Status` while moving lane or staying in the same lane.

Rule of next `Status` will be based on previous `Status` should follow configured matrix [See: TASK-STATUS-FLOW.md](TASK-STATUS-FLOW.md) or it will return error.

Example

```
<pyenv> <script path>/move-task.py 105 --lane "WIP" --status 7
```

Output

```
Removed WP #105 from 'Sprint Backlog'
Moved WP #105 to 'WIP'
Updated WP #105 status to 7
```

Example

```
<pyenv> <script path>/move-task.py 105 --lane "WIP"
```

Output

```
WP #105 already in 'WIP'
Updated WP #105 status to 7
```

#### 3.2.1. Monitoring Flow

As Task-Taker, you can pull tasks from the 'Sprint Backlog' into 'WIP' which will change the `Status` to In Progress (or by explicitly changing it). You can then push it to 'Ready' lane providimg test for review by Architect [See: Task Comment](#34-add-comment-and-mention).

As Architect you need to monitor `Task` which is moved to 'Ready' as well as `Mention` for clarification in `Comment`. Mark reviewed `Task` in 'Ready' by changing the `Status` to Tested.

### 3.3. Get Task Assignments

Required information:

```
USER_ID
```

Function:
1. Get task assigned accross all projects or specified project only.

Only specified `PROJECT_ID` to be checked during Sprint. Other is to be ignored e.g. the `API Test Project`.

Example

```
<pyenv> <script path>/task-assigned.py --user USER_ID --project PROJECT_ID
```

Output

```
#112 [Tested] Implement API client with assignee
#113 [Tested] Getting assigned task and its position on the board
#114 [New] Implement mention in comment
```

As Task-Taker, the one with `[Scheduled]` status is ready to be started based on the task description.

#### 3.3.1. Get Task Description

From list of assigned task, get task description using `Work package` ID
Example

```
<pyenv> <script path>/get-task-description.py WP_ID

```

Output

```
- [x] Task status example
- [ ] Another example

More content.
```

### 3.4. Add Comment and Mention

As Architect, you can mention Task-Taker for update or change to `Task` In Progress, sharing test result feedback, request for change, etc. within `Comment` content through `Mention`. As Task-Taker you can mention Architect for `Task` clarification.

`Comment` to the `Task` required the following content for mention:

```
USER_ID = [placeholder]  
USER_NAME = [placeholder]
```

Note: `ASSIGNEE_ID` for Task-Taker in previous use case is the same `USER_ID`.

Example

```
<pyenv> <script path>/add-comment.py TASK_ID --comment "Hey <mention class=\"mention\" data-id=\"USER_ID\" data-type=\"user\" data-text=\"@USER_NAME\">@USER_NAME</mention> please check."
```

or using `*.md` file

```
<pyenv> <script path>/add-comment.py TASK_ID --file tmp/comment-tag-team.md
```

#### 3.4.1. List My Mention

Function:
1. List mentions based on my [`API_KEY`](#2-api-settings-and-project-information) when calling.

Example

```
<pyenv> <script path>/my-mention.py
```

Output

```
Mentioned in: Implement API client with assignee — /api/v3/work_packages/TASK_ID_1
Mentioned in: Implement mention in comment — /api/v3/work_packages/TASK_ID_2
Mentioned in: Implement API client with assignee — /api/v3/work_packages/TASK_ID_2
```

Both Task-Taker and Architect need to check `Mention` for relevant tasks on hand e.g. when waiting for feedback after completing `Task`, after asking for clarification.

#### 3.4.2 Get Task Comment

Similar to [Get Task Description](#331-get-task-description)

Example

```
<pyenv> <script path>/get-task-comments.py TASK_ID
```

Output

```
--- #108 by {'href': '/api/v3/users/USER_ID_0'} at 2026-06-24T06:25:03.470Z ---
<mention class="mention" data-id="USER_ID_1" data-type="user" data-text="@USER_NAME_1">@USER_NAME_1</mention> &nbsp;check this out

--- #115 by {'href': '/api/v3/users/USER_ID_2'} at 2026-06-24T09:44:37.267Z ---
Hey <mention class="mention" data-id="USER_ID_1" data-type="user" data-text="@USER_NAME_1">@USER_NAME_1</mention> please check.
```


### 3.5. Update Task Description

Similar to [Create Task](#31-create-board-task) 

Example

```
<pyenv> <script path>/update-task.py TASK_ID --file tmp/task-board-groundrule.md
```

Output

```
Updated WP #105
```