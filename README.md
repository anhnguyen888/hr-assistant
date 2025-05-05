# HR Assistant with PostgreSQL Vector Database

This project implements an HR Assistant using PostgreSQL with the pgvector extension as a vector database for storing and retrieving document embeddings.

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- All Python dependencies listed in `requirements.txt`

## Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd hr-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Linux/Mac
   # OR
   .\venv\Scripts\activate   # On Windows
   ```

3. Install Docker and Docker Compose
   
   Follow the official Docker installation guide for your platform:
   - [Docker Engine](https://docs.docker.com/engine/install/)
   - [Docker Compose](https://docs.docker.com/compose/install/)
   
   Verify the installations by running:
   ```bash
   # Verify Docker installation
   docker --version
   # Expected output: Docker version XX.XX.XX, ...
   
   # Verify Docker is running
   docker info
   # Should display system-wide information
   
   # Verify Docker Compose installation
   docker-compose --version
   # Expected output: Docker Compose version vX.XX.X
   ```

4. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

5. Start PostgreSQL with pgvector in Docker:
   ```bash
   docker-compose up -d
   ```

   The `docker-compose.yml` file contains the configuration for PostgreSQL with pgvector extension.

6. Setup PostgreSQL database and pgvector extension (first run only):
   ```bash
   python3 src/setup_postgres.py
   ```

## Configuration

1. Update the `.env` file with your PostgreSQL credentials (default values are configured for Docker setup):
   ```
   POSTGRES_USER=anhnguyen
   POSTGRES_PASSWORD=password
   POSTGRES_DBNAME=hr_assistant
   POSTGRES_CONNECTION_STRING=postgresql://anhnguyen:password@localhost:5433/hr_assistant
   ```

   Note: These credentials should match those in the `docker-compose.yml` file.

## Usage

Make sure you are in the project directory and have the virtual environment activated before running any commands:

```bash
cd hr-assistant
source venv/bin/activate  # On Linux/Mac
# OR
.\venv\Scripts\activate  # On Windows
```

1. Ingest documents:
   ```bash
   python3 src/ingest.py
   ```

   Options:
   - `--collection`: Collection name (default: hr_documents)
   - `--recreate`: Recreate collection if it exists

2. Run the assistant:
   ```bash
   streamlit run src/app.py
   ```

## Implementation Details

### Components

1. **db_utils.py**: Utility functions for working with PostgreSQL and pgvector
2. **setup_postgres.py**: Script to set up PostgreSQL with pgvector extension
3. **ingest.py**: Modified to use PostgreSQL instead of ChromaDB
4. **main.py**: Updated to use pgvector for vector storage and retrieval

### Vector Database Implementation

This implementation uses:
- **pgvector**: PostgreSQL extension for vector similarity search
- **langchain_pgvector**: LangChain integration with pgvector
- **HuggingFaceEmbeddings**: For generating document embeddings

Benefits of using PostgreSQL as a vector database:
- Scalability: PostgreSQL can handle large datasets efficiently
- Persistence: Data is stored in a robust, production-ready database
- SQL integration: Complex queries combining vector search with SQL
- ACID compliance: Ensures data reliability and consistency
