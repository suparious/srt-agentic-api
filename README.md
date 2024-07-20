# SolidRusT Agentic API

SolidRusT Agentic API is a powerful and flexible API for creating, managing, and interacting with AI agents. It provides a robust framework for agent-based AI operations, including memory management, function execution, and message processing.

## Key Features

- Agent creation and management
- Short-term (Redis) and long-term (ChromaDB) memory systems
- Function calling capabilities
- Flexible LLM provider integration
- Scalable architecture

## Project Structure

```plaintext
srt-agentic-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── endpoints/
│   │   └── models/
│   ├── core/
│   └── utils/
├── logs/
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/SolidRusT/srt-agentic-api.git
   cd srt-agentic-api
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the `.env.example` file to `.env` and update the values:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file with your specific configuration values.

5. Set up the database:
   - Ensure Redis is running for short-term memory operations.
   - Set up ChromaDB for long-term memory operations.

## Running the Application

To run the application locally:

```
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

## Development

### Running Tests

To run the test suite:

```
pytest
```

### Adding New Endpoints

1. Create a new file in `app/api/endpoints/` for your endpoint.
2. Define the necessary models in `app/api/models/`.
3. Implement the core logic in `app/core/` if needed.
4. Update `app/main.py` to include your new endpoint router.

### Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and write tests if applicable.
4. Run the test suite to ensure all tests pass.
5. Submit a pull request with a clear description of your changes.

## Docker

To build and run the Docker container:

```
docker build -t srt-agentic-api .
docker run -p 8000:8000 srt-agentic-api
```
