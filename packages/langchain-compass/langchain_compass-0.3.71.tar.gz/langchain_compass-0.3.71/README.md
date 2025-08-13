# langchain-compass

This package contains the LangChain integration with LangchainCompass

## Installation

```bash
pip install -U langchain-compass
```

And you should configure credentials by setting the following environment variables:

Import this toolkit by
```python
from langchain_compass.toolkits import LangchainCompassToolkit
```

Compass requires an API key for some features. You can set the key as an environment variable
```bash
OPENAI_API_KEY="<Your-Compass-API-KEY>"
```