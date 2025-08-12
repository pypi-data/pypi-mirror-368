# Chat

Types:

```python
from relaxai_test.types import (
    ChatCompletionMessage,
    ContentFilterResults,
    FunctionCall,
    FunctionDefinition,
    StreamOptions,
    Usage,
    ChatCreateCompletionResponse,
)
```

Methods:

- <code title="post /v1/chat/completions">client.chat.<a href="./src/relaxai_test/resources/chat.py">create_completion</a>(\*\*<a href="src/relaxai_test/types/chat_create_completion_params.py">params</a>) -> <a href="./src/relaxai_test/types/chat_create_completion_response.py">ChatCreateCompletionResponse</a></code>

# Completions

Types:

```python
from relaxai_test.types import CompletionCreateResponse
```

Methods:

- <code title="post /v1/completions">client.completions.<a href="./src/relaxai_test/resources/completions.py">create</a>(\*\*<a href="src/relaxai_test/types/completion_create_params.py">params</a>) -> <a href="./src/relaxai_test/types/completion_create_response.py">CompletionCreateResponse</a></code>

# Embeddings

Types:

```python
from relaxai_test.types import EmbeddingCreateResponse
```

Methods:

- <code title="post /v1/embeddings">client.embeddings.<a href="./src/relaxai_test/resources/embeddings.py">create</a>(\*\*<a href="src/relaxai_test/types/embedding_create_params.py">params</a>) -> <a href="./src/relaxai_test/types/embedding_create_response.py">EmbeddingCreateResponse</a></code>

# Health

Types:

```python
from relaxai_test.types import HealthCheckResponse
```

Methods:

- <code title="get /v1/health">client.health.<a href="./src/relaxai_test/resources/health.py">check</a>() -> str</code>

# Models

Types:

```python
from relaxai_test.types import Model, ModelListResponse
```

Methods:

- <code title="get /v1/models/{model}">client.models.<a href="./src/relaxai_test/resources/models.py">retrieve</a>(model) -> <a href="./src/relaxai_test/types/model.py">Model</a></code>
- <code title="get /v1/models">client.models.<a href="./src/relaxai_test/resources/models.py">list</a>() -> <a href="./src/relaxai_test/types/model_list_response.py">ModelListResponse</a></code>
