# Tasks

Types:

```python
from chunkr_ai.types import Task
```

Methods:

- <code title="get /tasks">client.tasks.<a href="./src/chunkr_ai/resources/tasks/tasks.py">list</a>(\*\*<a href="src/chunkr_ai/types/task_list_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task.py">SyncTasksPage[Task]</a></code>
- <code title="delete /tasks/{task_id}">client.tasks.<a href="./src/chunkr_ai/resources/tasks/tasks.py">delete</a>(task_id) -> None</code>
- <code title="get /tasks/{task_id}/cancel">client.tasks.<a href="./src/chunkr_ai/resources/tasks/tasks.py">cancel</a>(task_id) -> None</code>
- <code title="get /tasks/{task_id}">client.tasks.<a href="./src/chunkr_ai/resources/tasks/tasks.py">get</a>(task_id, \*\*<a href="src/chunkr_ai/types/task_get_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task.py">Task</a></code>

## Parse

Methods:

- <code title="post /tasks/parse">client.tasks.parse.<a href="./src/chunkr_ai/resources/tasks/parse.py">create</a>(\*\*<a href="src/chunkr_ai/types/tasks/parse_create_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task.py">Task</a></code>
- <code title="patch /tasks/parse/{task_id}">client.tasks.parse.<a href="./src/chunkr_ai/resources/tasks/parse.py">update</a>(task_id, \*\*<a href="src/chunkr_ai/types/tasks/parse_update_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task.py">Task</a></code>

# Files

Types:

```python
from chunkr_ai.types import Delete, File, FilesPageResponse, FileURL
```

Methods:

- <code title="post /files">client.files.<a href="./src/chunkr_ai/resources/files.py">create</a>(\*\*<a href="src/chunkr_ai/types/file_create_params.py">params</a>) -> <a href="./src/chunkr_ai/types/file.py">File</a></code>
- <code title="get /files">client.files.<a href="./src/chunkr_ai/resources/files.py">list</a>(\*\*<a href="src/chunkr_ai/types/file_list_params.py">params</a>) -> <a href="./src/chunkr_ai/types/file.py">SyncFilesPage[File]</a></code>
- <code title="delete /files/{file_id}">client.files.<a href="./src/chunkr_ai/resources/files.py">delete</a>(file_id) -> <a href="./src/chunkr_ai/types/delete.py">Delete</a></code>
- <code title="get /files/{file_id}/content">client.files.<a href="./src/chunkr_ai/resources/files.py">content</a>(file_id) -> None</code>
- <code title="get /files/{file_id}">client.files.<a href="./src/chunkr_ai/resources/files.py">get</a>(file_id) -> <a href="./src/chunkr_ai/types/file.py">File</a></code>
- <code title="get /files/{file_id}/url">client.files.<a href="./src/chunkr_ai/resources/files.py">url</a>(file_id, \*\*<a href="src/chunkr_ai/types/file_url_params.py">params</a>) -> <a href="./src/chunkr_ai/types/file_url.py">FileURL</a></code>

# Health

Types:

```python
from chunkr_ai.types import HealthCheckResponse
```

Methods:

- <code title="get /health">client.health.<a href="./src/chunkr_ai/resources/health.py">check</a>() -> str</code>
