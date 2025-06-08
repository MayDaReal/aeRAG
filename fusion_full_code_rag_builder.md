
Fichier: rag_builder\aeRAG.md
Contenu:
**aeRAG: A Scalable Modular Knowledge System**

# 1. Introduction

## 1.1 Context and Project Origin
Archethic is a **transaction chain** that introduces a number of innovations beyond what most traditional blockchains (e.g., Ethereum, Bitcoin, Cosmos) provide. Despite its unique capabilities—such as enhanced security models, improved transaction handling, and a more scalable architecture—**the complexity of its underlying technology** can make it difficult to explain, learn, and adopt.

To tackle this issue, we aim to develop a **Retrieval-Augmented Generation (RAG)** system that unifies Archethic’s data (source code, commits, issues, pull requests, developer documentation, community discussions, etc.) into a single, easily accessible knowledge base. By bridging natural language queries with relevant, curated project data, we hope to improve:
- **Technical clarity** for developers looking to build decentralized applications (DApps) on Archethic.  
- **Transparency** for potential investors who need quick, accurate insights into the technology’s fundamentals and roadmap.  
- **Efficiency** for members of the Archethic Foundation who want to query existing data, code, and documents rapidly.  
- **Community engagement** by enabling content creators and ecosystem advocates to generate reliable articles, FAQs, and promotional materials.  
- **Scalability** by ensuring that as the ecosystem grows, the system can integrate new data sources and retrieval methods efficiently.

## 1.2 Main Objective
The overarching goal is to provide a comprehensive, AI-powered solution that can accurately answer a wide range of questions—from deep technical queries about node configurations or smart contract development, to higher-level inquiries about Archethic’s value proposition and economic model.

Furthermore, the system is designed with **replicability and extensibility** in mind: the same architecture and codebase can be **reused for other projects** by simply **adjusting configuration files** and data-collection endpoints to suit each new context. By abstracting data collection, storage, and retrieval processes, aeRAG can be adapted for different blockchain ecosystems or even non-blockchain domains.

## 1.3 Scope of This Document
This document details:
- **High-Level Architecture** of the RAG pipeline: from data collection in GitHub repositories, to chunking and embedding content, to producing final answers through a Large Language Model (LLM).
- **Implementation Details** of the current system: how MongoDB is used to store, query, and index data; how chunking strategies differ between code and text; and how metadata such as summaries and keywords are generated.
- **Future Extensions** including advanced retrieval logic, integration with vector databases (e.g., Faiss, LlamaIndex, or Milvus), query optimization techniques (SQL-based retrieval, dynamic reasoning, multi-step planning), and support for multiple LLM backends (Mistral, DeepSeek, OpenAI, etc.).
- **Deployment Considerations** for local or cloud-based environments.  
- **Testing and Maintenance** approaches that ensure the system remains robust, accurate, and easy to evolve over time.  
- **User Interface and Accessibility** by discussing how aeRAG can be integrated into **chatbots, API endpoints, and other interactive platforms** to make knowledge retrieval as seamless as possible.

By offering a **modular, well-structured** RAG solution, this project aims to **accelerate Archethic’s adoption** and empower its community with a reliable, user-friendly tool for exploring, understanding, and leveraging the technology’s full potential. Additionally, it serves as a blueprint for any ecosystem looking to integrate RAG-based AI-driven knowledge retrieval.

---

# 2. Requirements and Use Cases

## 2.1 Functional Requirements

### 2.1.1 Data Collection
- **GitHub Integration**:  
  The system must be able to fetch code, commits, pull requests, issues, and release notes from Archethic’s (or any other project's) GitHub repositories. This includes handling authentication (e.g., OAuth tokens), pagination, and rate limits.
- **Extended Data Sources**:  
  While GitHub is the primary data source initially, the architecture should support plugging in additional data feeds (e.g., forum posts, technical blogs, governance records). Configuration files or environment variables should make it simple to add or remove these sources.

### 2.1.2 Data Organization and Indexing
- **Structured Storage in MongoDB**:  
  Each type of data (e.g., commits, issues, code files) is stored in dedicated MongoDB collections. The system must maintain references between these collections (e.g., issues linked to related pull requests).
- **Metadata Generation**:  
  The system must generate extended metadata for each file or record, including:
  - **Text chunking** (custom size, overlap, or code syntax-aware).  
  - **Embeddings** (e.g., with SentenceTransformers).  
  - **Summaries** (T5 Summarizer or equivalent).  
  - **Keywords** (Yake or any other configured extractor).
- **Vector Index Support**:  
  Even though MongoDB houses the core data, the system should be designed to integrate with a vector database (e.g., Faiss, LlamaIndex, Milvus) for rapid similarity searches on embeddings.

### 2.1.3 Retrieval-Augmented Queries
- **Similarity Search**:  
  For any incoming natural language query, the system must locate the most relevant chunks (via embeddings) and produce a concise context for the LLM.
- **LLM Interaction**:  
  The pipeline should support hooking up multiple LLMs (Mistral, DeepSeek, OpenAI, etc.). Internally, the system organizes the context, merges it with user queries, and delegates the final text generation to the chosen model.

### 2.1.4 Chatbot / API Interface
- **User Interaction**:  
  The solution should provide at least a chatbot-like interface, whether through a CLI, a web-based UI, or both.
- **API Access** *(Planned)*:  
  An HTTP endpoint (e.g., REST or GraphQL) may be exposed so external applications can query the system programmatically.

### 2.1.5 Logging and Monitoring
- **Request Logs**:  
  Each query, along with the relevant chunks retrieved and LLM response, should be optionally logged for future analysis (with attention to privacy/security concerns).
- **System Health**:  
  Basic metrics (e.g., memory usage, response times, indexing completion stats) are necessary for debugging and optimization.

### 2.1.6 Testing (Unit and Non-Regression)
- **Unit Tests**:  
  Each module (collectors, chunkers, embeddings, metadata management) should include tests to confirm expected behavior.
- **Integration & Non-Regression Tests**:  
  The system should run scenario-based tests (e.g., retrieving commits for a specific repo, chunking and vectorizing them, ensuring results remain consistent over time).

---

## 2.2 Non-Functional Requirements

### 2.2.1 Performance and Scalability
- **Low Latency Retrieval**:  
  The system must return relevant chunks quickly, especially in conversational use cases. This requirement often drives the need for an **ANN (Approximate Nearest Neighbor) index** in a vector database.
- **Horizontal Scalability**:  
  As more data sources are added, the system should handle increased storage and indexing loads via horizontal scaling. For instance, separate microservices could handle chunking, vector indexing, and LLM calls.

### 2.2.2 Reliability and Fault Tolerance
- **Robust Error Handling**:  
  If a collector encounters an error (e.g., a GitHub rate limit), it should retry gracefully or log the issue without halting the entire pipeline.
- **Retry and Rollback**:  
  Large-scale indexing processes might fail mid-way; the system should be able to resume or roll back partial updates.

### 2.2.3 Maintainability and Clean Code
- **Modular Architecture**:  
  Each functionality (data collection, chunking, embeddings, etc.) is self-contained with clear interfaces. This fosters easier upgrades and refactoring.
- **Adherence to Clean Code Principles**:  
  Following Robert C. Martin’s guidelines (SOLID, DRY, etc.) ensures the code remains approachable for new contributors.
- **Documentation**:  
  Clear in-code docstrings and external documentation for each module so that maintainers can easily extend or modify the system.

### 2.2.4 Security and Access Control
- **Token Management**:  
  Credentials for GitHub or other data sources must be stored securely, e.g., in environment variables or a secrets manager.
- **User Data Privacy**:  
  If personal or sensitive data is ever ingested, the system must comply with relevant privacy regulations and best practices.  
- **Network Restrictions**:  
  For enterprise or closed-source usage, there may be a requirement to restrict external LLM calls or manage them via secure proxies.

### 2.2.5 Portability
- **Local vs. Cloud Deployments**:  
  The system should support easy installation on a local machine (e.g., on-premise server) or container-based deployment in the cloud.
- **Minimal External Dependencies**:  
  While vector databases or advanced LLMs might be optional add-ons, the core pipeline should remain functional and not break if certain optional dependencies are missing or swapped.

---

## 2.3 Use Cases

### 2.3.1 Developer Building DApps on Archethic
1. **Scenario**: A developer wants to understand Archethic’s smart contract framework and needs to see examples of code usage.  
2. **Steps**:  
   - Developer types a question, e.g., *“How do I deploy a multi-sig contract on Archethic?”*  
   - aeRAG fetches relevant code snippets, docs, and commits that reference `multi-sig`, compiles context, and feeds it to the LLM.  
   - LLM responds with a step-by-step guide or references to official docs.  
3. **Benefit**: Rapid, contextual knowledge retrieval shortens the learning curve and speeds up development.

### 2.3.2 Potential Investor or Partner
1. **Scenario**: A venture capital firm or an individual investor wants to understand Archethic’s roadmap and unique selling points.  
2. **Steps**:  
   - They query, *“What makes Archethic more scalable than typical proof-of-stake networks?”*  
   - aeRAG surfaces relevant discussions from the repository, official documentation, and whitepapers.  
   - The LLM generates a concise overview of the scalability features (e.g., the transaction chain’s design).  
3. **Benefit**: Clear, investor-friendly explanations build trust and expedite decision-making.

### 2.3.3 Archethic Foundation Member
1. **Scenario**: A foundation developer needs to quickly find the commit history related to a specific protocol upgrade that might have introduced a bug.  
2. **Steps**:  
   - The query, *“Show me all commits related to ‘protocol_upgrade_X’ since version 2.0”*.  
   - aeRAG compiles the relevant commits, issues, and possibly pull requests to highlight changes.  
   - The developer identifies potential regressions faster without manually browsing through logs.  
3. **Benefit**: Faster internal processes and improved incident resolution.

### 2.3.4 Community Content Creator
1. **Scenario**: A community ambassador wants to write a blog post about Archethic’s approach to governance.  
2. **Steps**:  
   - They ask, *“What governance proposals have shaped Archethic’s roadmap in 2023?”*  
   - aeRAG retrieves data from the main GitHub governance repo or related discussion boards, plus any official announcements.  
   - The LLM provides an ordered list or summary of major proposals with key points.  
3. **Benefit**: Accurate, centralized knowledge supports consistent community messaging.

---

# 3. High-Level Architecture

This chapter provides a **bird’s-eye view** of the aeRAG system—how data travels from raw sources (like GitHub) through chunking, embedding, and indexing, and ultimately how it’s fed to a Large Language Model (LLM) to answer user queries. The architecture is designed around **modularity** and **extensibility**, ensuring new data sources, vector databases, or LLM backends can be added with minimal friction.

---

## 3.1 Overview of the RAG Pipeline

1. **Data Collection**  
   - The system periodically or on-demand fetches information from configured sources (primarily GitHub).  
   - Each repository’s commits, issues, pull requests, and files are retrieved and stored.

2. **Data Storage**  
   - Retrieved data is structured and saved in MongoDB (or any chosen database).  
   - Collections such as `commits`, `issues`, `pull_requests`, `main_files`, etc., store relevant metadata and references.

3. **Document Chunking**  
   - Each stored file or piece of text is **split** into manageable chunks for fine-grained retrieval.  
   - aeRAG uses **overlapping text-based** or **language-specific code** chunking strategies to preserve context.

4. **Vectorization**  
   - Each chunk is embedded into a vector space using a chosen embedding model (e.g., SentenceTransformers).  
   - The resulting vectors are stored, either directly in MongoDB or in a vector database (planned feature).

5. **Vector Database Indexing (Planned)**  
   - For faster similarity searches, embeddings may be indexed in a specialized vector DB (Faiss, LlamaIndex, or Milvus).  
   - The system can fall back to MongoDB-based indexing if a vector DB is unavailable or optional for smaller deployments.

6. **Retrieval & RAG Engine**  
   - Upon user query, the engine searches for top-k similar chunks based on semantic similarity.  
   - The system compiles relevant chunks into a context package.

7. **LLM Integration**  
   - The context package and user query are passed to the selected LLM (Mistral, DeepSeek, OpenAI, etc.).  
   - The LLM returns an answer that is more accurate and context-aware, thanks to the RAG pipeline.

8. **User Interaction**  
   - Interactions can occur via a CLI chatbot, web UI, or an API endpoint.  
   - Query logs or results can be monitored for debugging and continuous improvement.

---

## 3.2 Key Components and Their Roles

### 3.2.1 Collectors
**Primary Purpose**: Gather data from external sources, especially GitHub, and insert or update that data in MongoDB.

1. **GitHubCollector**  
   - Coordinates the retrieval of **commits, pull requests, issues, and file trees**.  
   - Uses submodules to handle specific data (e.g., `github_commits.py`, `github_issues.py`).  
   - Manages API rate limits, token authentication, and error handling.

2. **Collector Extensibility**  
   - Additional collectors can be created for other data sources (forums, curated docs, or even other Git platforms).  
   - Each collector follows a similar pattern: fetch data → standardize format → store in the database.

### 3.2.2 Core Database & File Storage
**Primary Purpose**: Serve as the unified data backbone, storing both raw text/code and structured metadata.

1. **DatabaseManager**  
   - Handles **MongoDB connections** and collection creation.  
   - Defines indexes for improved query performance (e.g., on `repo`, `date`, or `updated_at` fields).

2. **FileStorageManager**  
   - Manages large file content, either locally (via a simple HTTP server) or through a remote storage service.  
   - Ensures raw files remain accessible for post-processing or direct viewing.

### 3.2.3 Chunking Strategies
**Primary Purpose**: Break down large documents (code files, markdown docs, etc.) into **smaller chunks** that can be indexed and retrieved more precisely.

1. **TextChunkingStrategy**  
   - Splits text into segments based on a chosen size (e.g., 500 tokens) and overlap (e.g., 50 tokens).  
   - Useful for documentation, discussion threads, or any natural-language content.

2. **CodeChunkingStrategy**  
   - Analyzes code structure (functions, classes, imports) to split at logical boundaries.  
   - Different sub-routines exist for languages like Python, JavaScript/TypeScript, etc.

3. **ChunkingStrategyFactory**  
   - Dynamically decides which strategy to use based on file type or extension.  
   - Extendable for new formats (HTML, JSON config, etc.).

### 3.2.4 Embeddings and Metadata
**Primary Purpose**: Add **semantic layers** to the data so the RAG engine can find relevant chunks via similarity search.

1. **Embedding Models**  
   - Typically uses a `SentenceTransformerEmbeddingModel` for general semantic embeddings.  
   - Could integrate other encoders if needed (e.g., OpenAI embeddings, BERT variants).

2. **Summarizers & Keyword Extractors**  
   - Summarizers (e.g., T5) can generate short abstracts of each chunk, aiding high-level indexing.  
   - Keyword extractors (e.g., Yake) allow quick tagging and filtering.

3. **MetadataManager**  
   - Coordinates the creation of chunked documents, embeddings, summaries, and keywords.  
   - Updates or re-generates metadata if a file changes in GitHub or a new version is released.

### 3.2.5 Vector Database (Future Integration)
**Primary Purpose**: **Accelerate similarity searches** on embedded data, crucial as the dataset grows.

1. **Supported Options**  
   - **Faiss**: A library for efficient similarity search in high-dimensional spaces.  
   - **LlamaIndex or Milvus**: Alternative solutions offering advanced features (like partitioning or distributed indexes).

2. **Index Management**  
   - The system defines how embeddings are uploaded, updated, or deleted.  
   - Queries the index to retrieve the top-k results for a user’s query embedding.

### 3.2.6 RAG Engine
**Primary Purpose**: Orchestrate the retrieval and packaging of relevant context for the LLM.

1. **Similarity Search**  
   - Takes the user’s question, embeds it, and searches the vector index or fallback (MongoDB).  
   - Ranks chunks by relevance score.

2. **Context Assembly**  
   - Collects top-k chunks into a consolidated context, possibly combining multiple documents.  
   - May apply summarization or additional filtering (e.g., removing duplicates).

3. **Query Routing** (Future Feature)  
   - In more advanced modes, decides if the LLM even needs retrieval from the knowledge base (fallback to base LLM if the question is generic).  
   - Could also orchestrate multi-step plans, e.g., generating a structured query for the DB.

### 3.2.7 LLMs and Response Generation
**Primary Purpose**: **Generate answers** in natural language using the retrieved context.

1. **LLM Manager**  
   - Abstracts the interface to different LLMs (Mistral, DeepSeek, OpenAI, etc.).  
   - Passes the user query plus retrieved context to the chosen model.

2. **Prompt Engineering**  
   - Shapes how the context and user question are combined (system prompts, user prompts, or few-shot examples).  
   - Minimizes hallucination by emphasizing or injecting retrieved facts.

3. **Response Handling**  
   - Returns the LLM’s final text to the user (via CLI, web UI, or API).  
   - Optionally logs the query and final response for analysis or debugging.

### 3.2.8 Server and CLI
**Primary Purpose**: Provide **entry points** for interactive usage and automation.

1. **LocalStorageServer**  
   - A minimal HTTP server that serves raw files (such as code or logs) for convenience.  
   - Can be extended to offer a small web UI or endpoints if needed.

2. **`main.py` CLI**  
   - Interactive menu for listing repos, updating data, starting the local server, and performing metadata updates.  
   - Allows testing or demonstration of the system’s core functions in a terminal environment.

3. **Future API**  
   - A planned extension for external apps: REST or GraphQL endpoints that handle user queries.

---

## 3.3 Data Flow Diagram (Conceptual)
Below is a conceptual outline of how data moves through aeRAG. *(A text-based description is provided—feel free to create a visual diagram if desired.)*

1. **Collector** calls the GitHub API → receives commits, issues, PRs.  
2. **Collector** stores results in **MongoDB** (collections: `commits`, `issues`, etc.).  
3. **MetadataManager** reads a file or record → uses **ChunkingStrategy** to split → uses **EmbeddingModel** to produce vectors.  
4. **MetadataManager** saves chunk metadata (embedding, summary, keywords) in **MongoDB** or a **Vector DB**.  
5. At **query time**, the RAG engine:  
   - Embeds the user query → searches top-k similar chunks.  
   - Gathers context from the relevant chunk documents.  
   - Sends the context and user query to the **LLM**.  
   - LLM produces a final answer, which is returned to the user.

---

## 3.4 Architectural Rationale

1. **Separation of Concerns**  
   - Each step (collecting, chunking, embedding, retrieving, LLM generation) is modular. This allows partial upgrades (e.g., swapping out the chunking strategy or embedding model) without rewriting the entire pipeline.

2. **Incremental Adoption**  
   - The system works with just MongoDB for smaller data sets. As the data volume increases, a specialized vector DB can be integrated for speed and scalability.

3. **Scalability and Flexibility**  
   - By supporting multiple LLMs and data sources, the architecture remains future-proof.  
   - The system can scale horizontally, with separate microservices for chunking, embeddings, and search if needed.

4. **Maintainability**  
   - Clean Code patterns keep each module self-contained and testable.  
   - Clear data flows ensure developers can trace how a chunk moves from raw file to LLM prompt.

---

## 3.5 Summary
The aeRAG architecture combines **a robust ingestion pipeline** with **modular chunking, embedding, and retrieval strategies**. It leverages MongoDB for flexible document storage and aims to integrate specialized vector databases for high-speed similarity search. A dedicated RAG engine then collates context for the LLM, ultimately **enabling domain-specific, context-rich responses** for end-users.

In the **next chapter**, we will **delve deeper into the existing implementation**, showing how these architectural components map to actual modules and functions in the codebase. This includes details on how the GitHub collectors are structured, how metadata is generated and stored, and the current approach to chunking and embedding.

---

# 4. Current Implementation Details

Building on the **High-Level Architecture** described in Chapter 3, this chapter focuses on **how the system is implemented today (02/03/2025)**, including the structure of collectors, metadata generation, and data handling in MongoDB. **Future releases will add or modify features documented here, and a dedicated changelog will track major changes over time.**

---

## 4.1 Data Collection

### 4.1.1 GitHubCollector
- **Primary Module**: `github_collector.py`  
- **Role**: Orchestrates fetching and updating information from GitHub, including:
  - **Repository Info**: Basic metadata (description, language, URL, last commit date).  
  - **Commits**: Detailed commit logs, including author, date, changed files, and diffs.  
  - **Pull Requests**: PR titles, states, commit references, and attached comments.  
  - **Issues**: Titles, bodies, state (open/closed), labels, and discussion threads.

#### 4.1.1.1 Workflow
1. **Fetch Repository List**: A call to GitHub’s `/orgs/<org>/repos` endpoint retrieves all repos for the organization.  
2. **Update Selected Repos**: For each repo, the system fetches new commits, pull requests, and issues since the last recorded date.  
3. **Store in MongoDB**:  
   - Data gets normalized into collections like `repositories`, `commits`, `pull_requests`, `issues`, etc.  
   - Any large file content is saved separately via the `file_storage_manager.py`.

#### 4.1.1.2 Error & Rate-Limit Handling
- The collector checks GitHub’s response headers (e.g., `X-RateLimit-Remaining`) and **waits** if the rate limit is reached.  
- If requests fail, the system logs the error and **continues** processing for other repos or data types.

### 4.1.2 Additional Collector Files
- **`github_commits.py`**: Fetches commit details and changed files.  
- **`github_issues.py`**: Retrieves issues and related comments, storing them in `issues` and `issues_comments` collections.  
- **`github_pull_requests.py`**: Manages pull request data (state, associated commits, comments).  
- **`github_files.py`**: Fetches files from the main branch or the latest release tag, storing them into `main_files` or `last_release_files`.

---

## 4.2 Data Storage in MongoDB

### 4.2.1 DatabaseManager
- **File**: `database_manager.py`  
- **Responsibilities**:
  - Open a connection to the MongoDB instance.  
  - Create indices for each collection (e.g., on `repo`, `date`, `state`, or custom fields).  
  - Provide a simple `db` property to access raw PyMongo operations.

#### 4.2.1.1 Collections Overview
1. **`repositories`**:  
   - Holds basic info: `_id` (e.g., `org/repo`), description, language, URL.  
2. **`commits`**:  
   - Each commit includes metadata such as message, date, author, files changed.  
   - Linked to files in `files` or `main_files` via commit SHA references.  
3. **`pull_requests`** and **`issues`**:  
   - Each record captures title, body, creation date, labels, comments, etc.  
   - Comments are stored separately in `pull_requests_comments` and `issues_comments` to keep the main documents smaller.  
4. **`files`, `main_files`, and `last_release_files`**:  
   - Store file metadata (filename, commit ID, and external URLs to the raw content).  
5. **`metadata`**:  
   - Contains references to text chunks, embeddings, summaries, and file hashes.  
   - The `_id` often encodes the source collection and document ID (e.g., `meta_repo_commits_sha`).  
6. **`chunks`**:  
   - Stores chunk-level data (e.g., `chunk_src`, `embedding`, `metadata_id`).  
   - Links back to the `metadata` collection, enabling fine-grained retrieval.

### 4.2.2 FileStorageManager
- **File**: `file_storage_manager.py`  
- **Purpose**:
  - Writes large or raw file content to a local storage path.  
  - Generates a public (or internal) URL, which is saved into MongoDB for future retrieval or analysis.  
  - Also handles retrieving existing content if needed for re-processing.

#### 4.2.2.1 Usage Flow
1. **Store File**: On retrieving a new file from GitHub, the collector calls `store_file_content()` with `(content, repo, reference_id, filename)`.  
2. **Generate URL**: The manager returns a path like `http://localhost:8000/<repo>/<reference_id>/<filename>`.  
3. **MongoDB Reference**: This URL gets stored in a relevant collection (e.g., `main_files`).  
4. **Subsequent Access**: If a chunking process or user needs the raw file, it can fetch via this URL.

---

## 4.3 Chunking and Metadata Generation

### 4.3.1 Chunking Strategies
- **TextChunkingStrategy (`text_chunking_strategy.py`)**:  
  - Splits documents into overlapping text chunks. Typical defaults: chunk size of ~500–1000 characters and overlap of 50–200 characters.  
  - Useful for **markdown docs**, **issues** bodies, or any plain text.

- **CodeChunkingStrategy (`code_chunking_strategy.py`)**:  
  - Splits code based on classes, function definitions, imports, etc.  
  - Supports multiple languages (Python, JavaScript, Dart, Go, C/C++, Ruby, etc.) by using language-specific regex patterns.

- **ChunkingStrategyFactory (`chunking_strategy_factory.py`)**:  
  - Determines whether to treat a file as `code` or `text` based on file extensions or other metadata.  
  - **Fallback**: If the file type is unknown, it uses the text strategy.

### 4.3.2 MetadataManager
- **File**: `metadata_manager.py`  
- **Core Logic**: 
  1. **Detect File Type**: For each record (commit, file, etc.), check extension or stored metadata.  
  2. **Retrieve Content**: Fetch text from `external_url` if available, or from the `patch` field for commits.  
  3. **Chunk the Content**: Call the appropriate chunking strategy.  
  4. **Generate Embeddings**: Pass each chunk to an embedding model.  
  5. **Create Summaries & Keywords**: Use T5-based summarizers or Yake-based keyword extractors.  
  6. **Save to `metadata`** and `chunks`**: Each chunk is stored with an `_id` referencing the metadata record.

#### 4.3.2.1 Example Flow for a New File
1. A new file in `main_files` is detected with `_id: <repo>_main_<filepath>`.  
2. **`MetadataManager`** extracts text from `file_storage_manager`’s URL.  
3. Chooses `CodeChunkingStrategy` if extension is `.py`; else `TextChunkingStrategy`.  
4. The resulting chunk texts are embedded using a `SentenceTransformerEmbeddingModel` from **`embeddings.py`**.  
5. Summaries and keywords might be generated, stored in the `metadata` collection.  
6. Each chunk’s embedding and text is saved to `chunks`.

---

## 4.4 Embeddings and Summaries

### 4.4.1 Embedding Models
- **File**: `embeddings.py`  
- **Implemented Class**: `SentenceTransformerEmbeddingModel` (commonly with the `"all-MiniLM-L6-v2"` or user-specified model).  
- **Usage**:
  - `encode(text)` returns a vector (list of floats).  
  - For chunked text, this is called in a loop. The resulting vectors are inserted into the `chunks` collection along with references to the parent metadata ID.

### 4.4.2 Summarizers
- **File**: `summarizers.py`  
- **Current Approach**: A T5-based summarizer, which can compress chunked text into shorter paragraphs.  
- **Optional Step**: Summaries are not always generated for large volumes of data, as it can be time-consuming. Instead, it may be triggered on demand or for specific file types.

### 4.4.3 Keyword Extraction
- **File**: `keywords_extractors.py`  
- **Extractor Used**: Yake (`YakeKeywordExtractor`) by default.  
- **Purpose**: Assign up to 10 keywords for each content extracted to facilitate topic tagging and quick searching.

---

## 4.5 RAG Engine and Retrieval

### 4.5.1 Current Retrieval Mechanism
- **MongoDB**:  
  - Currently, the system relies on MongoDB queries combined with embedded vectors.  
  - The approach is simpler but less optimal for high-scale similarity searches.  
  - A fallback to “metadata-based” queries also exists (e.g., matching chunk labels, file names, or keywords).

**Note**: A skeleton `rag_engine.py` file exists (or is planned) to unify retrieval logic. In future iterations, it will orchestrate how queries are parsed, how chunk searches are performed, and how fallback logic is managed.

### 4.5.2 Planned Vector Index
- **Faiss / LlamaIndex**:  
  - The codebase contains placeholders or “TODO” comments for hooking into a vector database.  
  - Once integrated, each chunk embedding is pushed to the index, enabling top-k similarity searches.

### 4.5.3 LLM Integration
- **Connection Points**:
  - The pipeline can feed top-k chunks to an LLM. 
  - Chat-based usage is prototyped in `main.py`, but a more robust “RAG engine” that orchestrates chunk retrieval is under development.
- **Configurable Model**:
  - The user can specify **Mistral, DeepSeek, OpenAI GPT-4,** etc. The code is structured so that each model implements a standardized interface (see `llm_manager.py` or `llm_interface.py` in the `LLMs` folder).

---

## 4.6 Local Server and CLI

### 4.6.1 Local Storage Server
- **File**: `local_storage_server.py`  
- **Role**: Serves locally stored files (e.g., raw code from GitHub) through a simple HTTP interface.  
- **Usage**:
  - Runs typically at `localhost:8000`, so any external file references become accessible via standard HTTP requests.
- **Extension**:  
  - Could be expanded into a minimal REST API for retrieving chunk data or for chatbot integration.

### 4.6.2 `main.py` CLI
- **Interactive Menu**: Provides the user with commands such as:
  - **Listing GitHub repositories** and updating them.  
  - **Fetching and storing** new commits/issues/PR data.  
  - **Updating metadata** for selected collections (files, commits, issues, etc.).  
  - **Starting/Stopping** the local storage server.  
  - Basic logs viewing (to see if the server or collector is running smoothly).

- **Roadmap**:
  - Possibly a “Chat” option (still partially implemented) to let the user query the system from the CLI.

---

## 4.7 Example Data Flow

Consider a scenario: **New commit** made to `archethic-foundation/core-engine` with a patch for improving transaction logic.

1. **GitHubCollector** → detects new commits since last fetch.  
2. Commit details stored in `commits` collection, associated files in `main_files`.  
3. `MetadataManager` → sees an unprocessed commit or file.  
4. **Chunk** the file if it’s new or changed.  
5. **Embed** the chunk text, store vectors in `chunks`.  
6. On user query, e.g., “How does Archethic handle transaction throughput?”  
7. The system (currently) searches `chunks` by textual keywords or naive embedding similarity in MongoDB. (Advanced: hits Faiss index in future).  
8. Assembles the top relevant chunks, merges them, and sends them to an LLM for an answer.

---

## 4.8 Limitations in the Current Implementation

1. **No Dedicated Vector DB**  
   - Reliance on MongoDB’s basic queries or naive embedding search can be slow at scale.  
   - The upcoming integration of Faiss or LlamaIndex is expected to **greatly improve** retrieval performance.

2. **Minimal RAG Engine**  
   - There is no sophisticated fallback logic (e.g., deciding whether to query the knowledge base at all).  
   - Multi-step reasoning (like generating SQL or advanced queries) is not implemented yet.

3. **Limited UI/UX**  
   - The user interacts via CLI or a very basic local HTTP server.  
   - A modern, **user-friendly** solution could be:
     1. **A minimal web-based chatbot** (e.g., built with React, Vue, or Svelte) that calls the RAG API, displaying results in real time.  
     2. **Plugin-based integration** with popular chat platforms (e.g., Slack, Discord) for collaborative usage.
   - Either approach would prioritize ease of access, a clean interface, and real-time feedback for end users.

4. **Automatic Summarization**  
   - Summaries can be expensive. Currently, summary generation is triggered manually for large volumes of data.  
   - **Two possible enhancements**:  
     1. **Batch Summarization**: Summaries are generated in bulk after certain thresholds (e.g., once daily or weekly).  
     2. **More Efficient Model**: A GPU-accelerated or lighter summarization model could handle large-scale data without blocking processes.

---

## 4.9 Summary

The current state of **aeRAG** already provides:
- **End-to-end GitHub data collection** and structured storage in MongoDB.  
- **Document chunking** with strategies for both textual and code-based content.  
- **Embedding-based** metadata generation (via SentenceTransformers), plus optional summaries and keywords.  
- A **CLI-driven workflow** to fetch data, chunk, embed, and prepare it for retrieval.

Upcoming expansions—like vector database integration, an enhanced RAG engine, and more sophisticated LLM prompts—will **transform** this from a **basic aggregator** into a **fully featured** retrieval and conversation system.

**This chapter reflects the codebase as of 02/03/2025; subsequent updates will be tracked in a dedicated changelog for easier versioning.**

Below is a **restructured Chapter 5**, renamed **“Technical Proposals for Next Steps.”** We have **removed** the explicit roadmap and milestones content (previously Section 5.8 and part of 5.9) so that it can be placed in **Chapter 6** (“Roadmap and Priorities”), as per your original plan. This version focuses on **technical proposals** and feature expansions, but leaves the detailed timeline and prioritization for the next chapter.

---

# 5. Technical Proposals for Next Steps

Even though **aeRAG** already handles core ingestion, chunking, and basic retrieval, several key **technical developments** are needed for the system to reach robust, production-grade status. This chapter outlines **future proposals** that will enhance aeRAG’s performance, user experience, and feature set—particularly focusing on a **minimal-yet-performant RAG engine**, **testing strategy**, **summarization improvements**, **user interface enhancements**, and **the idea of a GPT-like agent** enriched by RAG.

---

## 5.1 Minimal Yet Performant RAG Engine

### 5.1.1 Motivation
- **Immediate Testing & Validation**: To ensure reliability and gather baseline metrics, aeRAG needs a RAG engine that’s **straightforward** yet leverages a vector database for quick, similarity-based retrieval.
- **Scalable Foundation**: A “lightweight” design means simpler debugging, clearer performance data, and a stable foundation for subsequent feature expansions.

### 5.1.2 Proposed Approach
1. **Faiss Integration**  
   - **Core Step**: Store new or updated chunk embeddings in a Faiss index instead of relying solely on MongoDB for similarity searches.  
   - **Implementation**:  
     - Develop a service (e.g., `faiss_index_manager.py`) to push vectors from the `chunks` collection into Faiss.  
     - Adapt the retrieval pipeline to query Faiss for top-k results, then map back to chunk data.
2. **Light RAG Engine**  
   - **Focus**: Keep logic minimal—query embeddings, fetch top-k chunks, assemble context, and invoke the chosen LLM.  
   - **Benefit**: Clear testable steps, easier to measure latency, resource usage, and accuracy.

### 5.1.3 Advantages
- **Reduced Complexity**: Eliminates advanced multi-step logic until we have proven performance.  
- **Better Data for Tests**: With Faiss or a similar vector index, we can run systematic performance checks on speed and recall quality.

---

## 5.2 Testing Strategy: Unit, Non-Regression, and Performance

### 5.2.1 Current Gap
- **No Existing Tests**: There are no automated tests for either the collectors, chunkers, or the RAG pipeline.

### 5.2.2 Planned Testing Layers
1. **Unit Tests**  
   - **Scope**: Each module (collectors, chunking, embedding, LLM connectors) gets dedicated tests.  
   - **Example**: Verifying `GitHubCollector` properly handles pagination; confirming the chunk factory returns `CodeChunkingStrategy` for `.py`.
2. **Non-Regression Tests**  
   - **Goal**: Protect against breakage of previously functioning features as new code is introduced.  
   - **Method**: Maintain a canonical test dataset (sample code commits, issues, etc.). Each code update triggers a pipeline run, ensuring outputs remain consistent.
3. **Performance Tests**  
   - **Usage**: Evaluate retrieval speed, memory usage, and scaling.  
   - **Implementation**: Query the minimal Faiss-based engine with realistic data volume to see if it meets targeted latencies.

### 5.2.3 Release Confidence
- Once all three test layers pass, changes can be tagged as a “stable” or “release” build, ensuring production readiness.

---

## 5.3 Summarization Revisited

### 5.3.1 Observations from T5 and Mistral-7B
- **T5**: While easy to integrate, it has proven suboptimal for Archethic’s specialized content. The process is also relatively slow for large batches.  
- **Mistral-7B Instruct**: Delivers more relevant summaries but is even more GPU-heavy, raising cost and infrastructure needs.

### 5.3.2 Potential Strategies
1. **Optimized or Smaller Models**  
   - Investigate quantization, model distillation, or specialized short-input summarizers that reduce load.  
2. **Selective Summaries**  
   - Summaries are generated only for top-accessed or frequently queried chunks, conserving resources.

### 5.3.3 Benefits
- **Optional but Valuable**: Enhanced summarizations still have potential for improving retrieval context, especially if done selectively.  
- **User-Focused**: Detailed, relevant summaries help developers, investors, or community members grasp key points without parsing entire chunks.

---

## 5.4 User Interface Enhancements

### 5.4.1 Telegram or Discord Chat Integration
- **Rationale**: Users often prefer a familiar messaging platform.  
- **Telegram Bot**: Commands (e.g., `/rag "search query"`) forward to aeRAG, and the bot replies with top chunks or an LLM-generated answer.  
- **Discord Bot**: Similarly, the bot listens in specified channels, responding with context from the RAG engine.

### 5.4.2 Modern Web UI
- **Approach**:  
  - Build a minimal **React** or **Vue** single-page app that communicates with an HTTP/REST (or GraphQL) endpoint.  
  - Provide a sleek chat window, plus references for chunk sources.  
- **Benefit**: A more general interface accessible to those not using Telegram/Discord or the CLI.

---

## 5.5 GPT-Like Agent Enriched by RAG

### 5.5.1 Concept
- **Hybrid Approach**: Combine aeRAG’s domain knowledge with advanced OpenAI ChatGPT+ models.  
- **User Experience**: End users “talk to” a GPT instance that’s automatically augmented with fresh, context-specific data from Archethic repos.

### 5.5.2 Possible Implementations
1. **ChatGPT Plugin**  
   - The plugin calls aeRAG for relevant chunks whenever the user asks a domain-specific question.  
   - Must follow OpenAI’s plugin guidelines.
2. **Proxy API**  
   - A server intercepts user queries, retrieves context from aeRAG, and injects it into ChatGPT’s system prompts.  
   - Manages session and token usage carefully.

### 5.5.3 Anticipated Gains
- **Real-Time Augmentation**: Even advanced GPT models lack up-to-date or project-specific knowledge; RAG bridging solves that.  
- **Easy Adoption**: People already using ChatGPT+ can retain their workflow while gaining specialized insights on Archethic.

---

## 5.6 Additional Data Sources

### 5.6.1 Other Git Platforms
- **Adaptation**: Minimal changes for GitLab or Bitbucket collectors, reusing the GitHubCollector’s structure.

### 5.6.2 Community & Governance
- **On-Chain Proposals, Forum Threads**:  
  - Each post/proposal can be chunked and embedded, letting the user query historical or current decisions easily.

### 5.6.3 Index Refreshes
- **Scheduled Jobs**: Nightly or weekly re-checking of large sources, ensuring the knowledge base remains updated.

---

## 5.7 Logging, Analytics, and Monitoring

### 5.7.1 Structured Logging
- **Objective**: Collect queries, chunk retrieval data, and LLM latency in JSON logs.  
- **Benefit**: Facilitates debugging, usage tracking, and compliance with security or privacy standards.

### 5.7.2 Usage Analytics
- **Focus**: Identify the most common search queries or bottlenecks.  
- **Outcome**: Informs future data collection priorities, helps refine chunking or summarization.

### 5.7.3 Resource Monitoring
- **GPU/CPU Tracking**: Summarization or large LLM inferences can spike resource usage.  
- **Alerts**: DevOps can set thresholds that trigger notifications if usage is excessive or if a collector fails.

---

## 5.8 Conclusion

Implementing **Faiss-based retrieval** for a minimal RAG engine, establishing **unit/non-regression/performance tests**, optimizing **summaries**, and **enhancing user interfaces** (Telegram/Discord or a web UI) all represent critical next steps. Furthermore, the notion of a **GPT-like system**—where ChatGPT+ is seamlessly augmented by aeRAG’s specialized data—captures the long-term vision of delivering advanced, domain-aware conversations.

In **Chapter 6**, we will detail the **Roadmap and Priorities**, mapping these technical proposals onto specific milestones, timelines, and resource planning. This ensures every enhancement—whether for performance, user experience, or LLM integration—fits into a coherent path forward for aeRAG’s evolution.

---

# 6. Roadmap and Priorities

This chapter provides a **structured plan** for implementing the enhancements described throughout the document. By dividing the roadmap into short-, medium-, and long-term milestones, we ensure aeRAG evolves **incrementally** yet remains **focused** on delivering tangible improvements at each phase.

---

## 6.1 Overview of Roadmap Structure

1. **Short-Term (1–3 Months)**  
   - Activities that are essential for establishing **baseline stability**, **performance**, and **basic user-facing features**.
2. **Medium-Term (3–6 Months)**  
   - More advanced capabilities, such as specialized summarizations and broader UI support, once the core RAG engine is stable.
3. **Long-Term (6+ Months)**  
   - Scaling to large datasets, advanced retrieval logic, deeper LLM integrations, and potential plugin-based GPT augmentation.

Each section below lists **priority tasks** (P1, P2, etc.) to help guide resource allocation and sprint planning.

---

## 6.2 Short-Term Milestones (1–3 Months)

### 6.2.1 Integrate Faiss-Based Minimal RAG Engine
- **P1**: **Implement Faiss Index Manager**  
  - Write a service (e.g., `faiss_index_manager.py`) to store and query chunk embeddings.  
  - Incorporate periodic synchronization between the `chunks` collection and the Faiss index.
- **P1**: **Refactor Retrieval Flow**  
  - Update the RAG engine logic (minimal version) to embed user queries, retrieve the top-k similar chunks from Faiss, and pass them to the chosen LLM.
- **P2**: **Basic Performance Benchmarks**  
  - Use a small test dataset to measure average retrieval latency, memory usage, and throughput under typical load.

### 6.2.2 Establish Testing Foundations
- **P1**: **Unit Tests**  
  - Create a skeleton test suite in `tests/` to cover each module: collectors, chunkers, embeddings, LLM connectors.  
  - Examples: verifying GitHub pagination, ensuring `ChunkingStrategyFactory` picks the correct strategy.
- **P1**: **Non-Regression & Performance Tests**  
  - Define a canonical test dataset of code, commits, and issues.  
  - Automate the pipeline in CI, checking that retrieval and indexing produce consistent results and meet basic time thresholds.
- **P2**: **First Stable Release Tag**  
  - Once tests reliably pass and Faiss integration is validated, tag a stable release (e.g., `v0.1`) for internal or public usage.

### 6.2.3 Initial User Interface Enhancements
- **P2**: **Telegram Bot** (Prototype)  
  - Provide a minimal chat-based interface for querying the new RAG engine.  
  - Deploy in a test environment to gather feedback on usability.
- **P3**: **CLI Improvements**  
  - Expand `main.py` with a simple “chat” command that demonstrates end-to-end retrieval using Faiss.

**Goal**: Emerge from the short-term phase with a **solid, test-backed RAG foundation** and **Faiss-accelerated retrieval** ready to handle typical user queries.

---

## 6.3 Medium-Term Milestones (3–6 Months)

### 6.3.1 Summarization Optimization
- **P1**: **Selective Summarization**  
  - Summaries are generated only for frequently accessed or newly updated chunks, balancing resource costs.  
  - Evaluate model performance (T5, Mistral-7B, or alternatives) via smaller-scale deployments.
- **P2**: **Batch Summaries**  
  - Schedule a nightly or weekly job to summarize new chunks en masse, possibly offloading to a GPU server if required.

### 6.3.2 UI & Chat Integrations
- **P1**: **Enhanced Telegram (or Discord) Bot**  
  - Add more advanced features: conversation state, partial multi-step retrieval.  
  - Possibly store user messages and RAG responses for analytics (with privacy considerations).
- **P2**: **Prototype Web UI**  
  - Develop a minimal React or Vue front-end with a chat window, chunk references in the response, and optional user authentication.  
  - Gather user feedback to refine the design and plan a full MVP launch.

### 6.3.3 Extended Data Sources
- **P2**: **Additional Git Platforms**  
  - Adapt existing collectors for GitLab or Bitbucket if needed by the Archethic ecosystem or external adopters.
- **P3**: **Community & Governance**  
  - Index forum discussions, on-chain governance proposals, or relevant archives for a richer knowledge base.

### 6.3.4 Testing Maturity
- **P1**: **Expanded Non-Regression Coverage**  
  - Add more scenarios (larger repos, code merges, governance data) to ensure robust pipeline performance.  
- **P2**: **Performance Stress Tests**  
  - Evaluate system behavior under higher concurrency or data volumes.  
  - Identify bottlenecks (in chunking, embeddings, or Faiss indexing) and optimize accordingly.

---

## 6.4 Long-Term Milestones (6+ Months)

### 6.4.1 GPT-Like Agent Enriched by RAG
- **P1**: **Plugin or Proxy Approach**  
  - Create a ChatGPT plugin or a proxy server that injects aeRAG chunks into GPT prompts.  
  - Overcome constraints related to prompt size, session management, and plugin policy guidelines.
- **P2**: **Continuous Context Updates**  
  - Automate retrieval of the latest Archethic data, ensuring near real-time augmentation for GPT-based queries.  
  - Integrate usage analytics to measure query frequency, chunk relevance, and user satisfaction.

### 6.4.2 Advanced RAG Retrieval Logic
- **P2**: **Multi-Step Reasoning**  
  - The RAG engine orchestrates iterative queries. For complex questions, the system re-retrieves or refines its context.  
  - Could utilize an LLM-based “planner” that decides which chunks or data sources to target next.
- **P3**: **SQL-Based or GraphQL-Based RAG**  
  - Let the LLM generate structured queries for more refined data fetching (e.g., selecting commits by date range, labeling issues by state).

### 6.4.3 Scalability and Architecture Refinements
- **P1**: **Distributed Faiss or Milvus**  
  - Move from a single-node vector index to a multi-node cluster for high availability in enterprise-scale usage.  
- **P2**: **Microservices**  
  - Split chunking, embeddings, and retrieval tasks into separate services if usage patterns or data volumes justify it.

---

## 6.5 Priorities in Context

| Priority | Task                                         | Timeframe   |
|----------|----------------------------------------------|-------------|
| **P1**   | Faiss integration, minimal RAG engine        | Short-Term  |
| **P1**   | Core test suite (unit, non-regression)       | Short-Term  |
| **P2**   | Basic Telegram bot                           | Short-Term  |
| **P1**   | Summarization optimization (selective/batch) | Medium-Term |
| **P1**   | Enhanced Telegram/Discord or Web UI          | Medium-Term |
| **P2**   | GPT-like augmentation or plugin approach      | Long-Term   |
| **P2**   | Multi-step RAG reasoning                     | Long-Term   |
| **P3**   | Additional data collectors (GitLab, forums)   | Medium-Term |

**Note**: This table is a simplified summary. Actual priority may shift based on resource availability, user feedback, and emerging business needs.

---

## 6.6 Conclusion

The short-, medium-, and long-term milestones outlined above aim to transform aeRAG from a **basic aggregator** of Archethic data into a **powerful, user-friendly** RAG solution. By **prioritizing Faiss-based minimal retrieval**, **rigorous testing**, and **UI enhancements** in the near term, we lay the foundation for more ambitious goals—like **GPT augmentation** and **advanced multi-step retrieval**—in subsequent phases.

Through these incremental steps, aeRAG will become **increasingly stable, flexible, and valuable** to Archethic’s developers, investors, and community members, while remaining adaptable enough to serve other ecosystems or projects that require reliable retrieval-augmented AI.

---

# 7. Conclusion

## 7.1 Recap of aeRAG’s Purpose
Archethic is a powerful transaction chain offering advanced capabilities that surpass many traditional blockchains. However, **complex technology** can be an adoption barrier—both for developers seeking to build DApps and for potential investors or community members seeking clear, reliable information.

In response, **aeRAG** (ArchEthic RAG) was conceived as a **Retrieval-Augmented Generation** system to:
- **Collect**, **index**, and **enrich** Archethic’s growing dataset (commits, issues, pull requests, documentation, discussions, etc.).  
- Enable **natural language** access to that knowledge via state-of-the-art **LLMs**.  
- **Scale** seamlessly to new data sources, new retrieval engines, and advanced user interfaces.

## 7.2 Key Insights from This Document
1. **Clean Data Pipeline**  
   - Chapter 3 and 4 demonstrated how GitHub data is **collected**, **stored** in MongoDB, and **chunked**. This pipeline ensures a steady flow of up-to-date information for later retrieval.
2. **Metadata and Chunking**  
   - Adopting code-specific or text-specific chunking strategies (Chapter 4) yields more **targeted** embeddings, enabling relevant, high-quality matches when a user queries the system.
3. **Embedding and Summarization**  
   - SentenceTransformers embeddings provide a **semantic layer**, while optional summarization can boost clarity (albeit at higher compute cost).
4. **Performance Needs**  
   - The shift to a **Faiss-based RAG engine** (Chapter 5 and 6) lays the groundwork for **fast** nearest neighbor lookups, crucial as data scales.
5. **Testing and Roadmap**  
   - Thorough testing—unit, non-regression, and performance—underpins **release confidence** (Chapters 5 and 6).  
   - The **roadmap** (Chapter 6) delineates short-, medium-, and long-term priorities, ensuring a progressive yet organized evolution.

## 7.3 Anticipated Impact
By merging **domain-specific** knowledge with **modern LLMs**, aeRAG can drastically:
- **Reduce onboarding friction** for new developers on Archethic.  
- **Provide transparency** for investors or partners by surfacing relevant commits, proposals, and metrics.  
- **Streamline** the collaborative workflow, letting the Archethic Foundation and community easily retrieve and cross-reference historical context (e.g., searching commits that introduced certain protocol changes).

## 7.4 Reusability Beyond Archethic
An important design criterion for aeRAG is **replicability**. Although the immediate focus is on Archethic data, the same **core architecture**—GitHub collectors, chunk-based embeddings, Faiss integration, etc.—can be extended to:
- Other blockchain ecosystems (e.g., for verifying or explaining code, proposals, and community discussions).  
- Non-blockchain domains that need a robust RAG pipeline (documentation portals, corporate wikis, specialized research archives, etc.).

## 7.5 Next Steps
From the perspective of **ongoing development**:
1. **Implement the Minimal Faiss RAG Engine**  
   - This addresses immediate performance bottlenecks and sets the stage for advanced queries.  
2. **Establish Comprehensive Testing**  
   - Ensure unit and performance tests run in CI to catch regressions and validate readiness for stable releases.  
3. **Enhance UI and Accessibility**  
   - Whether through a Telegram/Discord bot or a minimal web app, user-friendliness is key to encouraging adoption.  
4. **Plan GPT-Augmentation**  
   - Investigate an official ChatGPT plugin or a proxy approach to seamlessly integrate aeRAG context into GPT-4 or other advanced LLMs.

## 7.6 Final Remarks
**aeRAG** stands as a **scalable, modular** RAG system poised to demystify Archethic for a wide audience—developers, investors, and community members alike. By adhering to **Clean Code principles** and robust design patterns, the project remains maintainable and extensible, ready to incorporate upcoming innovations in both the Archethic chain and the broader AI landscape.

In the spirit of open collaboration, the next releases of aeRAG will continue to **iterate** on performance, testing, and user experience. Contributions from the community—be they in chunking optimizations, new LLM connectors, or advanced retrieval techniques—will only deepen the value that aeRAG offers to Archethic and beyond.

With a **well-defined roadmap**, a capable pipeline for data, and a strong vision for future expansions, aeRAG is prepared to **grow alongside** Archethic, becoming an indispensable resource for knowledge retrieval and user engagement in the months and years ahead.

Below is a **Chapter 8** that can serve as **Appendices and Resources**, providing **additional references**, **implementation details**, **clean code best practices**, and **technical pointers** for further exploration. This chapter consolidates various supporting materials that might not fit neatly into earlier chapters but still enrich the understanding and future development of **aeRAG**.

---

# 8. Appendices and Resources

This chapter gathers **supporting information** and **technical references** that complement the core sections of this document. It serves as a handy reference for developers extending or maintaining aeRAG, as well as newcomers seeking deeper insights into the technologies and design principles behind it.

---

## 8.1 References and Documentation

### 8.1.1 MongoDB
- **Official Docs**: [https://docs.mongodb.com](https://docs.mongodb.com)  
  - Comprehensive guides on queries, indexing strategies, and replication.  
  - Useful for optimizing queries, especially with large collections like `commits`, `issues`, `chunks`.

### 8.1.2 GitHub API
- **GitHub REST API Documentation**: [https://docs.github.com/en/rest](https://docs.github.com/en/rest)  
  - Endpoints for repositories, commits, issues, pull requests, etc.  
  - Rate limit details and examples of pagination logic.

### 8.1.3 Vector Databases
- **Faiss**: [https://github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss)  
  - High-performance nearest neighbor search, recommended for the **Minimal RAG** approach.  
  - Includes CPU- and GPU-based indexing strategies, memory management tips.
- **LlamaIndex**: [https://github.com/jerryjliu/llama_index](https://github.com/jerryjliu/llama_index)  
  - Alternative indexing library with a more Pythonic interface, though it may require additional overhead to integrate seamlessly.
- **Milvus**: [https://milvus.io/](https://milvus.io/)  
  - A distributed, cloud-native vector database, scalable for enterprise-level usage.

### 8.1.4 Embeddings and Summarization
- **SentenceTransformers**: [https://www.sbert.net/](https://www.sbert.net/)  
  - Offers a range of models (e.g., `all-MiniLM-L6-v2`) and fine-tuning examples.  
- **T5 Summarizer**: [https://github.com/google-research/text-to-text-transfer-transformer](https://github.com/google-research/text-to-text-transfer-transformer)  
  - Official repo for T5. Summarization is one application, though domain specialization may require advanced fine-tuning.  
- **Mistral-7B**: Official release details vary; keep an eye on repositories like [https://huggingface.co](https://huggingface.co) for the latest model versions and usage tips.

### 8.1.5 OpenAI GPT and ChatGPT Plugins
- **OpenAI Documentation**: [https://platform.openai.com/docs/introduction](https://platform.openai.com/docs/introduction)  
  - Provides API references for GPT-3.5, GPT-4, and plugin development guidelines.  
  - Key for building or integrating a GPT-like agent enriched by aeRAG context.

---

## 8.2 Code Samples and Templates

### 8.2.1 Minimal Faiss Integration Snippet

```python
# faiss_index_manager.py (example)
import faiss
import numpy as np

class FaissIndexManager:
    def __init__(self, dim, index_path=None):
        self.dim = dim
        # Example: Using a simple IndexFlatL2
        self.index = faiss.IndexFlatL2(dim)
        
        if index_path:
            self.load_index(index_path)

    def add_vectors(self, vectors: np.ndarray):
        # vectors shape: (num_vectors, dim)
        self.index.add(vectors)

    def search(self, query_vector: np.ndarray, top_k: int = 5):
        # query_vector shape: (1, dim)
        distances, indices = self.index.search(query_vector, top_k)
        return distances, indices

    def save_index(self, path):
        faiss.write_index(self.index, path)

    def load_index(self, path):
        self.index = faiss.read_index(path)
```

**Notes**:
- This snippet demonstrates the bare minimum for storing vectors and retrieving top-k neighbors.  
- Real-world usage: You’d likely map each vector to a `chunk_id` for referencing back to `chunks` in MongoDB.

### 8.2.2 Summarization Trigger Example

```python
def maybe_summarize_chunk(chunk_text, usage_count, summarizer):
    """ Summarize a chunk if it's heavily accessed or passes a specific threshold. """
    threshold = 10  # example usage threshold
    if usage_count > threshold:
        summary = summarizer.summarize(chunk_text)
        return summary
    return None
```

**Notes**:
- Integrates domain logic (e.g., usage_count from logs or metadata) to decide if summarization is warranted.  
- Minimizes unnecessary compute for rarely accessed chunks.

---

## 8.3 Clean Code Best Practices

aeRAG embraces **Robert C. Martin’s** “Clean Code” principles to ensure **maintainability** and **readability**:

1. **Meaningful Names**  
   - Use descriptive function/class/variable names (`fetch_commits()`, `MetadataManager`), avoiding abbreviations that obscure meaning.
2. **Single Responsibility Principle (SRP)**  
   - Keep modules like `github_collector.py` focused on one main concern—fetching GitHub data—rather than mixing in chunking or storage logic.
3. **DRY (Don’t Repeat Yourself)**  
   - Factor out repeated code into utility functions or base classes, e.g., `github_request.py` for common GitHub API calls.
4. **Small Functions**  
   - Limit function size to a single screenful or less, ensuring clarity. Larger logic can be subdivided into helper methods.
5. **Commenting and Docstrings**  
   - Provide docstrings at the start of each class or method clarifying purpose, parameters, and return values.  
   - Use inline comments sparingly—only when the rationale or approach is non-trivial.

---

## 8.4 Additional Design Patterns and Architectural Tips

1. **Factory Pattern**  
   - Used in `chunking_strategy_factory.py` to pick the correct strategy (text vs. code).  
   - Encourages future extensions (e.g., specialized chunkers for JSON configs, logs, or plain text with fewer lines).
2. **Adapter / Wrapper Classes**  
   - Could be introduced for bridging external APIs or libraries (like Faiss or a Slack/Telegram API).  
   - Keeps your core logic independent of specific library details.
3. **Microservice Architecture** *(Long-Term)*  
   - If data or user requests grow significantly, splitting the chunking pipeline, vector indexing, and LLM requests into separate services can improve concurrency and maintainability.

---

## 8.5 Potential Pitfalls & Troubleshooting

1. **GitHub Rate Limits**  
   - Use environment variables (e.g., `GITHUB_TOKEN`) and implement exponential backoff to avoid frequent “403 Forbidden” errors.
2. **Memory Management with Faiss**  
   - Large embeddings (millions of vectors) can exceed RAM. Investigate GPU-based indexes or sharding across multiple machines.
3. **LLM Token Limits**  
   - When merging multiple chunks for a large query, you can exceed an LLM’s context window (e.g., 8k or 32k tokens). Implement chunk pruning or summarization to fit within constraints.
4. **Summarization Quality**  
   - Domain-specific or newly introduced models (Mistral) may require custom fine-tuning for best results.  
   - Ensure your hardware (GPU VRAM) can handle the chosen model at acceptable speeds.

---

## 8.6 Glossary of Terms

- **RAG (Retrieval-Augmented Generation)**:  
  AI approach that fetches relevant documents/chunks before or during generating a response.  
- **Chunk**:  
  A smaller segment of a larger document (e.g., code file, markdown docs).  
- **Embedding**:  
  A numeric vector representing text in a semantic space, enabling similarity-based searches.  
- **Faiss**:  
  A C++ library from Facebook (Meta) for efficient similarity search of dense vectors.  
- **Mistral-7B**:  
  A 7-billion-parameter LLM known for good instruction-following, albeit with higher resource demands.  
- **ChatGPT Plugin**:  
  An add-on that extends ChatGPT with domain-specific capabilities, bridging external data sources.

---

## 8.7 Future Reading and Exploration

1. **LangChain**: [https://github.com/hwchase17/langchain](https://github.com/hwchase17/langchain)  
   - A popular library for building LLM “chains,” relevant for multi-step reasoning in advanced RAG engines.
2. **RLHF (Reinforcement Learning from Human Feedback)**  
   - Potential method to refine LLM behavior using user feedback from aeRAG queries.
3. **Cloud-Native Vector DB Services**  
   - Vendors like AWS OpenSearch, Azure Cognitive Search, or managed Milvus services if you prefer not to self-host a vector index at scale.

---

## 8.8 Conclusion

This appendix—covering **references, code snippets, best practices**, design insights, and a glossary—aims to **empower developers** and stakeholders with the **context** and **resources** needed to extend aeRAG confidently. Whether you plan to integrate a new summarizer, adopt additional Git platforms, or scale up Faiss to multi-machine setups, these tips and references provide a **starting point**.

As aeRAG grows—alongside the Archethic ecosystem—so too will the supporting tools, patterns, and advanced features. By adhering to **clean code principles**, leveraging well-documented libraries, and staying mindful of potential pitfalls, you ensure aeRAG remains adaptable, performant, and **developer-friendly** for the long haul.


Fichier: rag_builder\main.py
Contenu:
"""
main.py
An interactive script that prompts the user to choose actions dynamically.
"""

import os
from dotenv import load_dotenv
import sys

# Import managers and classes
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from collectors.github_collector import GitHubCollector
from metadata.metadata_manager import MetadataManager

import multiprocessing
from server.local_storage_server import LocalStorageServer

# from models.llm_manager import LLMManager
# from models.llm_interface import ILLM

# Global variable to track server process
server_process = None

def interactive_menu():
    """
    Displays a menu and returns user's choice as an integer.
    """
    print("\n=== Archethic RAG Interactive Menu ===")
    print("1) Configure/Change LLM Model (not implemented yet)")
    print("2) List GitHub repositories (Test OK)")
    print("3) Update all data for an organization (Don't use and test while validation on the first repo is not completed)")
    print("4) Update all data for selected repositories (Test OK)")
    print("5) Update specific data for multiple repositories (Test OK)")
    print("6) List collections in the database (Test OK)")
    print("7) Start local storage server (Test OK)")
    print("8) Stop local storage server (Test OK)")
    print("9) Show last 10 lines of local server log (Test OK)")
    print("10) Generate/Update metadata for selected repositories and selected collections (TODO test)")
    print("11) Run unit tests (not implemented yet)")
    print("12) Start chat with the LLM (not implemented yet)")
    print("0) Exit (Test OK)")
    choice = input("Enter your choice: ")
    return choice.strip()

def load_configuration():
    """
    Loads environment variables and ensures required ones are set.
    """
    load_dotenv()
    
    required_vars = ["MONGO_URI", "DB_NAME", "LOCAL_STORAGE_PATH", "BASE_URL", "PORT"]
    
    for var in required_vars:
        if not os.getenv(var):
            print(f"⚠️ Warning: Environment variable {var} is not set!")

    print("✅ Environment variables loaded successfully.")

def run_main_loop():
    """
    Main interactive loop handling user choices dynamically.
    """
    # Load environment variables
    load_configuration()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "archethic_rag")

    # Initialize FileStorageManager once
    local_storage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv("LOCAL_STORAGE_PATH", "local_storage"))
    base_url = os.getenv("BASE_URL", f"http://localhost:{os.getenv('PORT', 8000)}")
    storage_manager = FileStorageManager(base_storage_path=local_storage_path, base_url=base_url)

    try:
        while True:
            choice = interactive_menu()

            if choice == "1":
                # cmd_configure_llm()
                pass
            elif choice == "2":
                cmd_list_github_repos(mongo_uri, db_name, storage_manager)
            elif choice == "3":
                cmd_update_org_data(mongo_uri, db_name, storage_manager)
            elif choice == "4":
                cmd_update_repos_data(mongo_uri, db_name, storage_manager)
            elif choice == "5":
                cmd_update_multiple_repos_specific_data(mongo_uri, db_name, storage_manager)
            elif choice == "6":
                cmd_list_collections(mongo_uri, db_name)
            elif choice == "7":
                cmd_start_local_server()
            elif choice == "8":
                cmd_stop_local_server()
            elif choice == "9":
                cmd_view_local_server_logs()
            elif choice == "10":
                cmd_update_metadata_multiple_repos_specific_data(mongo_uri, db_name, storage_manager)
            elif choice == "11":
                cmd_run_tests()
            elif choice == "12":
                cmd_start_chat()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("[!] Invalid choice.")
    except KeyboardInterrupt:
        print("\n🛑 KeyboardInterrupt detected. Stopping all processes...")
    finally:
        cmd_stop_local_server()  # Ensure the server stops before exit

# def cmd_configure_llm(current_llm: ILLM) -> ILLM:
#     """
#     Configures the LLM model, using environment variables if available.
#     """
#     print("\nChoose a model backend:")
#     print("1) Local LLM (dummy or local model)")
#     print("2) OpenAI GPT-3.5 or GPT-4 (API)")

#     choice = os.getenv("LLM_MODEL_CHOICE", input("Model choice: ").strip())

#     if choice == "1":
#         model_path = os.getenv("LLM_LOCAL_PATH", input("Enter local model path (dummy for now): ").strip())
#         new_llm = LLMManager.load_llm("local", {"model_path": model_path})
#         print("[LLM] Switched to local model.")
#         return new_llm
#     elif choice == "2":
#         api_key = os.getenv("OPENAI_API_KEY", input("Enter OpenAI API Key: ").strip())
#         model_name = os.getenv("OPENAI_MODEL_NAME", input("Enter model name (e.g. gpt-3.5-turbo): ").strip())
#         new_llm = LLMManager.load_llm("openai", {"api_key": api_key, "model_name": model_name})
#         print("[LLM] Switched to OpenAI model.")
#         return new_llm
#     else:
#         print("Invalid choice, keeping current LLM.")
#         return current_llm


def cmd_list_github_repos(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Lists GitHub repositories, using the token from `.env` if available.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()

    db_manager = DatabaseManager(mongo_uri, db_name)
    collector = GitHubCollector(db_manager, token, org, storage_manager)

    repos = collector.fetch_repositories()

    if repos:
        print(f"\n✅ Retrieved {len(repos)} repositories for '{org}':")
        for r in repos:
            print(" -", r)
    else:
        print(f"\n⚠️ No repositories found for '{org}' or an error occurred.")


def cmd_update_org_data(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Updates all repositories of a given GitHub organization.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()

    db_manager = DatabaseManager(mongo_uri, db_name)
    collector = GitHubCollector(db_manager, token, org, storage_manager)

    print(f"🔄 Updating all repositories in {org}...")
    collector.update_all_repos()
    print("✅ Organization data update complete.")

def cmd_update_repos_data(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Updates all selected repositories from a given GitHub organization.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()

    repos_input = os.getenv("GITHUB_REPOS")
    if not repos_input:
        repos_input = input("Enter repositories (space-separated): ").strip()
    repos = repos_input.split()

    db_manager = DatabaseManager(mongo_uri, db_name)
    collector = GitHubCollector(db_manager, token, org, storage_manager)

    print(f"🔄 Updating selected repositories: {repos}")
    collector.update_selected_repos(repos)
    print("✅ Repository data update complete.")

def cmd_update_multiple_repos_specific_data(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Updates selected data types for multiple repositories.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()
        
    repos_input = os.getenv("GITHUB_REPOS")
    if not repos_input:
        repos_input = input("Enter repositories (space-separated): ").strip()
    repos = repos_input.split()

    options = {
        "1": "repository info",
        "2": "commits",
        "3": "pull requests",
        "4": "issues"
    }

    print("\nSelect the data to update:")
    for key, value in options.items():
        print(f"{key}) {value}")

    choices = input("Enter numbers separated by spaces (e.g., '1 3'): ").split()
    selected_data = [options[choice] for choice in choices if choice in options]

    db_manager = DatabaseManager(mongo_uri, db_name)
    collector = GitHubCollector(db_manager, token, org, storage_manager)

    print(f"🔄 Updating {selected_data} for repositories: {repos}")
    collector.update_multiple_repos_specific_data(repos, selected_data)
    print("✅ Data update complete.")

def cmd_update_metadata_multiple_repos_specific_data(mongo_uri: str, db_name: str, storage_manager: FileStorageManager):
    """
    Updates metadata for a specified repository and collections.
    Uses `.env` variables when available.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        token = input("Enter your GitHub personal access token: ").strip()

    org = os.getenv("GITHUB_ORG")
    if not org:
        org = input("Enter GitHub owner/org: ").strip()
        
    repos_input = os.getenv("GITHUB_REPOS")
    if not repos_input:
        repos_input = input("Enter repositories (space-separated): ").strip()
    repos = repos_input.split()

    options = {
        "1": "files",
        "2": "main_files",
        "3": "last_release_files",
        "4": "commits",
        "5": "pull_requests",
        "6": "issues"
    }

    print("\nSelect the data to update:")
    for key, value in options.items():
        print(f"{key}) {value}")

    choices = input("Enter numbers separated by spaces (e.g., '1 3'): ").split()
    selected_data = [options[choice] for choice in choices if choice in options]

    db_manager = DatabaseManager(mongo_uri, db_name)
    metadata_manager = MetadataManager(db_manager, storage_manager)
    metadata_manager.update_metadata_multiple_repos_specific_data(repos, selected_data)

def cmd_list_collections(mongo_uri: str, db_name: str):
    """
    Lists all collections in the database.
    """
    db_manager = DatabaseManager(mongo_uri, db_name, create_indexes=False)
    cols = db_manager.list_collections()

    print("\nCollections in the DB:")
    for c in cols:
        print(" -", c)

def cmd_start_local_server():
    """
    Starts the local storage server in a separate process so it doesn't block the main script.
    Uses `.env` values when available.
    """
    global server_process

    if server_process and server_process.is_alive():
        print("⚠️ Local storage server is already running.")
        return
    
    # Retrieve port from .env, ensuring it is a valid integer
    port_env = os.getenv("PORT")
    port = None

    if port_env and port_env.isdigit():
        port = int(port_env)
    
    # Ask user only if PORT was not found in .env or is invalid
    if port is None:
        port_input = input("Port to serve on (default: 8000): ").strip()
        if not port_input or not port_input.isdigit(): 
            port = 8000
            print("⚠️ Invalid port. So default port 8000 applied.")

    storage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.getenv("LOCAL_STORAGE_PATH", "local_storage"))

    print(f"\n🚀 Starting local storage server on port {port}, serving '{storage_path}' ...")
    print("📜 Server logs are being saved to 'local_server.log'. You can check logs anytime.")

    # Start server process without passing the log file
    server_process = multiprocessing.Process(target=start_server_process, args=(port, storage_path))
    server_process.start()
    
    print("[✅] Local storage server started in the background.")

def start_server_process(port, storage_directory):
    """
    Function to start the local storage server in a separate process and redirect logs.
    """
    log_file_path = "local_server.log"
    with open(log_file_path, "a", buffering=1) as log_file:
        sys.stdout = log_file  # Redirect standard output
        sys.stderr = log_file  # Redirect error output

        print(f"[LocalStorageServer] Starting server on port {port}, serving '{storage_directory}'")

        server = LocalStorageServer(port=port, storage_directory=storage_directory)
        server.start_server()

def cmd_stop_local_server():
    """
    Stops the local storage server if it is running.
    """
    global server_process

    if server_process and server_process.is_alive():
        print("🛑 Stopping local storage server...")
        server_process.terminate()
        server_process.join()
        server_process = None
        print("[✅] Local storage server stopped.")
    else:
        print("⚠️ No active local storage server to stop.")

def cmd_view_local_server_logs():
    """
    Displays the last few lines of the local storage server log file.
    """
    log_file_path = "local_server.log"

    if not os.path.exists(log_file_path):
        print("⚠️ No log file found. The server may not have been started yet.")
        return

    print("\n📜 Last 10 lines of 'local_server.log':\n")
    
    with open(log_file_path, "r") as log_file:
        lines = log_file.readlines()
        for line in lines[-10:]:  # Show last 10 lines
            print(line.strip())

    print("\n(Use 'tail -f local_server.log' in a terminal to follow logs in real-time.)")

def cmd_run_tests():
    """
    Runs unit tests.
    """
    print("\nRunning unit tests...")
    os.system("pytest archethic_rag/tests")

# def cmd_start_chat(llm: ILLM):
def cmd_start_chat(llm):
    """
    Starts a simple chat with the chosen LLM. 
    (We store interactions in logs if desired).
    """
    print("\n[Chat] Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            print("Exiting chat.")
            break

        # Optionally we could pass context from RAG retrieval, etc.
        answer = llm.chat(user_input, context=None)
        print("Bot:", answer)

# def cmd_analyze_logs(llm: ILLM):
def cmd_analyze_logs(llm):
    """
    Example usage of the LLM to analyze logs and propose improvements.
    """
    # For the demo, let's just ask the user for some logs:
    logs = []
    print("\nEnter lines of logs (type 'done' to finish):")
    while True:
        line = input("> ")
        if line.strip().lower() == "done":
            break
        logs.append(line)
    
    if not logs:
        print("No logs provided.")
        return

    analysis = llm.analyze_logs(logs)
    print("\n[Analysis Result]\n", analysis)

def main():
    print("Welcome to the Archethic RAG Interactive System.")
    run_main_loop()

if __name__ == "__main__":
    main()


Fichier: rag_builder\chunks\abstract_chunking_strategy.py
Contenu:
from abc import ABC, abstractmethod
from typing import List

class AbstractChunkingStrategy(ABC):
    """Interface for chunking strategy."""
    
    @abstractmethod
    def chunk(self, content: str) -> List[str]:
        pass
    

Fichier: rag_builder\chunks\chunking_strategy_factory.py
Contenu:
from .abstract_chunking_strategy import AbstractChunkingStrategy
from .text_chunking_strategy import TextChunkingStrategy
from .code_chunking_strategy import CodeChunkingStrategy

from typing import Dict, Any

class ChunkingStrategyFactory:
    """Returns appropriate strategy based on file type."""

    @staticmethod
    def get_strategy(file_type: str = "", settings: Dict[str, Any] = {}) -> AbstractChunkingStrategy:
        if file_type == "code":
            return CodeChunkingStrategy(settings)
        else:
            return TextChunkingStrategy(settings)  # default
        
        # TODO manage log and doc (in near future try to manage sepcific doc, config, image, video)
        # TODO manage mistral to summarize
        # TODO implement minimaliste rag_engine and try to chat with them
        # TODO on website repo
        # TODO on medium data

Fichier: rag_builder\chunks\code_chunking_strategy.py
Contenu:
from .abstract_chunking_strategy import AbstractChunkingStrategy
from typing import List, Dict, Any
import re

class CodeChunkingStrategy(AbstractChunkingStrategy):
    """Chooses the best chunking strategy based on the detected programming language."""
    def __init__(self, extension: str = ""
                , language: str = ""
                , min_chunk_size: int = 300
                , chunk_size: int = 1000
                , overlap: int = 200):
        
        self.extension = extension
        self.language = language
        self.min_chunk_size = min_chunk_size
        self.chunk_size = chunk_size
        self.overlap = overlap

    def __init__(self, settings: Dict[str, Any]):
        self.extension = settings.get("extension", "")
        self.language = settings.get("language", "")
        self.min_chunk_size = settings.get("min_chunk_size", 300)
        self.chunk_size = settings.get("chunk_size", 1000)
        self.overlap= settings.get("overlap", 200)
        
    def chunk(self, content: str) -> List[str]:
        """Chooses the best chunking strategy based on the detected programming language."""
        chunking_functions = {
            "python": self.chunk_python,
            "typescript": self.chunk_javascript,
            "javascript": self.chunk_javascript,
            "nodejs": self.chunk_javascript,
            "dart": self.chunk_dart,
            "elixir": self.chunk_elixir,
            "html": self.chunk_html_css,
            "css": self.chunk_html_css,
            "go": self.chunk_go,
            "c": self.chunk_c_cpp,
            "cpp": self.chunk_c_cpp,
            "ruby": self.chunk_ruby
        }
        
        if self.language in chunking_functions:
            return chunking_functions[self.language](content, self.min_chunk_size)
        
        # no programming langage managed, use default chunk_text
        return self.chunk_text(content, self.chunk_size, self.overlap)

    def chunk_text(self, text, chunk_size=1000, overlap=200):
        """Splits text into overlapping chunks for optimal retrieval."""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def chunk_python(self, content, min_chunk_size=300):
        """Chunks Python code by function, class, and imports while keeping context."""
        lines = content.split("\n")
        chunks, chunk = [], []
        imports = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith(("import ", "from ")):
                imports.append(line)
                continue

            if re.match(r"^(class |def )", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and imports:
            chunks[0] = "\n".join(imports) + "\n" + chunks[0]

        return chunks

    def chunk_javascript(self, content, min_chunk_size=300):
        """Chunks JavaScript, TypeScript, and Node.js while keeping imports at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        imports = []

        for line in lines:
            stripped = line.strip()

            if re.match(r"^(import |export |require\()", stripped):
                imports.append(line)
                continue

            if re.match(r"^(export\s+)?(function|class)\s", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and imports:
            chunks[0] = "\n".join(imports) + "\n" + chunks[0]

        return chunks

    def chunk_dart(self, content, min_chunk_size=300):
        """Chunks Dart code while keeping import statements at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        imports = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("import "):
                imports.append(line)
                continue

            if stripped.startswith("@override") or re.match(r"^(class |void |final |Future<)", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and imports:
            chunks[0] = "\n".join(imports) + "\n" + chunks[0]

        return chunks

    def chunk_elixir(self, content, min_chunk_size=300):
        """Chunks Elixir code by modules and functions."""
        lines = content.split("\n")
        chunks, chunk = [], []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith(("defmodule ", "def ", "defp ")):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        return chunks

    def chunk_html_css(self, content, min_chunk_size=300):
        """Chunks HTML and CSS files by sections and selectors."""
        lines = content.split("\n")
        chunks, chunk = [], []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("<") or stripped.startswith("{"):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        return chunks

    def chunk_go(self, content, min_chunk_size=300):
        """Chunks Go code while keeping package and import statements at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        imports = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("package "):
                imports.append(line)
                continue

            if stripped.startswith("import "):
                imports.append(line)
                continue

            if stripped.startswith("func "):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and imports:
            chunks[0] = "\n".join(imports) + "\n" + chunks[0]

        return chunks

    def chunk_c_cpp(self, content, min_chunk_size=300):
        """Chunks C/C++ code while keeping #include statements at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        includes = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("#include"):
                includes.append(line)
                continue

            if re.match(r"^(void |int |char |float |double )", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and includes:
            chunks[0] = "\n".join(includes) + "\n" + chunks[0]

        return chunks

    def chunk_ruby(self, content, min_chunk_size=300):
        """Chunks Ruby code while keeping require statements at the top."""
        lines = content.split("\n")
        chunks, chunk = [], []
        requires = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("require "):
                requires.append(line)
                continue

            if re.match(r"^(class |module |def )", stripped):
                if chunk and len("\n".join(chunk)) > min_chunk_size:
                    chunks.append("\n".join(chunk))
                    chunk = []

            chunk.append(line)

        if chunk:
            chunks.append("\n".join(chunk))

        if chunks and requires:
            chunks[0] = "\n".join(requires) + "\n" + chunks[0]

        return chunks

Fichier: rag_builder\chunks\text_chunking_strategy.py
Contenu:
from .abstract_chunking_strategy import AbstractChunkingStrategy
from typing import List, Dict, Any

class TextChunkingStrategy(AbstractChunkingStrategy):
    """Splits text into overlapping chunks of a certain size."""
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def __init__(self, settings: Dict[str, Any] = {}):
        self.chunk_size = settings.get("chunkz_size", 500)
        self.overlap = settings.get("overlap", 50)

    def chunk(self, content: str) -> List[str]:
        chunks = []
        step = self.chunk_size - self.overlap
        for i in range(0, len(content), step):
            chunks.append(content[i:i + self.chunk_size])
        return chunks


Fichier: rag_builder\chunks\__init__.py
Contenu:


Fichier: rag_builder\collectors\github_collector copy.py
Contenu:
"""
github_collector.py
Central controller for GitHub data collection.
This module delegates specific tasks to specialized submodules:
- github_commits.py (commits and contributors)
- github_pull_requests.py (pull requests)
- github_issues.py (issues)
- github_files.py (file management: branches & releases)
"""

import os
import requests
from dotenv import load_dotenv
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from collectors.github_commits import fetch_commits, update_contributors
from collectors.github_pull_requests import fetch_pull_requests
from collectors.github_issues import fetch_issues
from collectors.github_files import fetch_files_from_branch, fetch_latest_release_files


class GitHubCollector:
    """
    Main GitHub data collector that orchestrates interactions with GitHub APIs.
    It delegates specific operations to specialized modules.
    """

    github_token = None

    @staticmethod
    def github_request(url: str, params: Optional[Dict[str, Any]] = None, return_json: bool = True):
        """
        Makes a GitHub API request with rate limit handling.

        Args:
            url (str): The API endpoint URL.
            params (dict, optional): Additional query parameters.
            return_json (bool): Whether to return the response as JSON.

        Returns:
            dict or requests.Response: JSON response from GitHub API or full response object if return_json=False.
        """
        if not GitHubCollector.github_token:
            raise ValueError("GitHub token is not set. Initialize GitHubCollector with a valid token.")

        headers = {"Authorization": f"token {GitHubCollector.github_token}"}

        while True:
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)

                # Manage rate limit
                if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
                    reset_time = int(response.headers["X-RateLimit-Reset"])
                    wait_time = max(0, reset_time - int(time.time())) + 1
                    print(f"⚠️ GitHub rate limit reached. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue 

                # Manage HTTP errors
                if response.status_code != 200:
                    print(f"❌ GitHub API Error ({response.status_code}): {response.text}")
                    return None

                return response.json() if return_json else response

            except requests.RequestException as e:
                print(f"⚠️ Network error while fetching {url}: {e}")
                return None

    def __init__(self, database_manager: DatabaseManager, github_token: str, github_org: str, storage_manager: FileStorageManager):
        """
        Initializes the GitHubCollector with required dependencies.

        Args:
            database_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
            github_token (str): GitHub API token for authentication.
            github_org (str): GitHub organization or user whose data will be collected.
            storage_manager (FileStorageManager): Instance for handling file storage operations.
        """
        self.db_manager = database_manager
        GitHubCollector.github_token = github_token
        self.github_org = github_org
        self.storage_manager = storage_manager

    def collect_all_data(self):
        """
        Collects all relevant GitHub data for the organization/user.

        This method:
        - Retrieves repositories
        - Fetches commits, issues, pull requests, and files
        - Updates contributor information
        """
        print("🔍 Fetching repositories...")
        repositories = self.fetch_repositories()

        for repo in repositories:
            print(f"\n📡 Processing repository: {repo}")

            print("📥 Fetching commits...")
            fetch_commits(self.db_manager, repo)

            print("📥 Fetching issues...")
            fetch_issues(self.db_manager, repo)

            print("📥 Fetching pull requests...")
            fetch_pull_requests(self.db_manager, repo, self.storage_manager)

            print("📥 Fetching files from main branch...")
            fetch_files_from_branch(self.db_manager, repo, self.storage_manager)

            print("📥 Fetching latest release files...")
            fetch_latest_release_files(self.db_manager, repo, self.storage_manager)

        print("\n🔄 Updating contributor data...")
        update_contributors(self.db_manager)

        print("✅ GitHub data collection completed!")

    def fetch_repositories(self):
        """
        Retrieves a list of repositories for the GitHub organization/user.

        Returns:
            list: List of repository names (e.g., ['archethic-foundation/archethic-node']).
        """
        url = f"https://api.github.com/orgs/{self.github_org}/repos?per_page=100"
        repos = []
        page = 1

        while True:
            data = GitHubCollector.github_request(url + f"&page={page}")

            if not data:
                break  # Stop if an error occurs or no more repositories

            repos.extend([repo["full_name"] for repo in data])
            page += 1

        print(f"✅ Retrieved {len(repos)} repositories.")
        return repos
    
    def fetch_repository_info(self, repo: str) -> None:
        """
        Fetches repository metadata and README content.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
        """
        repo_url = f"https://api.github.com/repos/{repo}"
        readme_url = f"https://api.github.com/repos/{repo}/readme"

        repo_data = GitHubCollector.github_request(repo_url)
        if not repo_data or "message" in repo_data and repo_data["message"] == "Not Found":
            print(f"❌ Repository not found: {repo}")
            return

        readme_data = GitHubCollector.github_request(readme_url)
        readme_content = GitHubCollector.github_request(readme_data["download_url"], None) if "download_url" in readme_data else None

        repo_entry = {
            "_id": repo,
            "description": repo_data.get("description", ""),
            "language": repo_data.get("language", ""),
            "url": repo_data.get("html_url", ""),
            "last_commit_date": repo_data.get("updated_at", ""),
            "readme": readme_content
        }

        self.db_manager.db.repositories.update_one({"_id": repo}, {"$set": repo_entry}, upsert=True)
        print(f"✅ Repository {repo} added/updated.")

"""
github_collector.py
Handles interactions with the GitHub API to fetch repository data, commits, issues,
pull requests, and files for integration into MongoDB.
"""

import requests
import time
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from core.database_manager import DatabaseManager  # Import DatabaseManager
from core.file_storage_manager import FileStorageManager  # Import FileStorageManager


class GitHubCollector:
    """
    Collects data from GitHub repositories and stores them in MongoDB.
    """

    def __init__(self, database_manager : DatabaseManager, mongo_uri: str, db_name: str, github_token: str, github_org: str, storage_manager: FileStorageManager):
        """
        Initializes the GitHubCollector with MongoDB and GitHub API credentials.

        Args:
            database_manager (DatabaseManager): Instance of the DatabaseManager class (already initialized).
            github_token (str): GitHub API token for authentication.
            github_org (str): Organization or user to monitor.
            storage_manager (FileStorageManager): Instance for file storage.
        """
        self.db_manager = database_manager
        self.github_token = github_token
        self.github_org = github_org
        self.headers = {"Authorization": f"token {self.github_token}"}
        self.storage_manager = storage_manager

    def github_request(self, url: str, params: dict = None, return_json : bool = True) -> dict:
        """
        Makes a GitHub API request with rate limit handling.

        Args:
            url (str): The API endpoint URL.
            params (dict, optional): Additional query parameters.

        Returns:
            dict: JSON response from GitHub API.
        """
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
                reset_time = int(response.headers["X-RateLimit-Reset"])
                wait_time = max(0, reset_time - int(time.time())) + 1
                print(f"⚠️ GitHub rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            
            if response.status_code != 200:
                print(f"❌ GitHub API Error: {response.status_code} - {response.text}")
                return None
            
            return response.json() if return_json else response

    def fetch_repositories(self) -> list:
        """
        Fetches all repositories for the given GitHub organization.

        Returns:
            list: List of repository full names.
        """
        repos = []
        page = 1
        while True:
            url = f"https://api.github.com/orgs/{self.github_org}/repos?per_page=100&page={page}"
            data = self.github_request(url)
            if not data:
                break
            repos.extend([repo["full_name"] for repo in data])
            page += 1
        return repos

    

    def fetch_commits(self, repo: str) -> None:
        """
        Fetches commits from a repository and stores them in MongoDB.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
        """
        last_commit = self.db_manager.db.commits.find_one({"repo": repo}, sort=[("date", -1)])
        last_commit_date = last_commit["date"] if last_commit else None
        page = 1

        while True:
            url = f"https://api.github.com/repos/{repo}/commits?per_page=100&page={page}"
            data = self.github_request(url)
            if not data:
                break

            commits = []
            for commit in data:
                commit_sha = commit["sha"]
                commit_date = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")

                if last_commit_date and commit_date <= last_commit_date:
                    return

                if self.db_manager.db.commits.find_one({"_id": commit_sha}):
                    continue

                # Fetch file details
                files_changed = self.fetch_commit_files(repo, commit_sha)
                if not files_changed:
                    continue

                commit_entry = {
                    "_id": commit_sha,
                    "repo": repo,
                    "message": commit["commit"]["message"],
                    "author": commit["commit"]["author"]["name"] if commit["commit"]["author"] else None,
                    "author_email": commit["commit"]["author"]["email"] if commit["commit"]["author"] else None,
                    "committer": commit["commit"]["committer"]["name"] if commit["commit"]["committer"] else None,
                    "committer_email": commit["commit"]["committer"]["email"] if commit["commit"]["committer"] else None,
                    "date": commit_date,
                    "files_changed": files_changed
                }
                commits.append(commit_entry)

            if commits:
                self.db_manager.db.commits.insert_many(commits)
                print(f"✅ {len(commits)} new commits added for {repo}")
            page += 1

    def fetch_commit_files(self, repo: str, commit_sha: str) -> list:
        """
        Fetches details (files changed) for a commit.

        Args:
            repo (str): The GitHub repository.
            commit_sha (str): The commit SHA.

        Returns:
            list: List of file paths changed in the commit.
        """
        url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
        data = self.github_request(url)
        if not data or "files" not in data:
            return []

        files_info = []
        files_to_insert = []

        for file in data["files"]:
            file_id = f"{commit_sha}_{file['filename']}"
            if self.db_manager.db.files.find_one({"_id": file_id}):
                files_info.append(file_id)
                continue

            file_obj = {
                "_id": file_id,
                "commit_id": commit_sha,
                "repo": repo,
                "filename": file["filename"],
                "status": file["status"],
                "patch": file.get("patch", ""),
                "metadata_id": None,
                "lfs_pointer_id": None,
                "external_url": None
            }

            if file["status"] == "added":
                raw_url = file.get("raw_url")
                if raw_url:
                    file_content = self.fetch_large_file(raw_url)
                    if isinstance(file_content, dict):  # Git LFS pointer case
                        lfs_pointer_id = f"{commit_sha}_{file['filename']}_lfs"
                        lfs_pointer = {
                            "_id": lfs_pointer_id,
                            "file_id": file_id,
                            "oid": file_content["oid"],
                            "size": file_content["size"],
                            "storage_url": raw_url
                        }
                        self.db_manager.db.lfs_pointers.update_one({"_id": lfs_pointer_id}, {"$set": lfs_pointer}, upsert=True)
                        file_obj["lfs_pointer_id"] = lfs_pointer_id
                    elif file_content:
                        external_url = self.storage_manager.store_file_content(file_content, repo, commit_sha, file["filename"])
                        file_obj["external_url"] = external_url

            files_info.append(file_id)
            files_to_insert.append(file_obj)

        if files_to_insert:
            self.db_manager.db.files.insert_many(files_to_insert)

        return files_info

    def fetch_large_file(self, raw_url: str):
        """
        Fetches file content from its raw URL.
        If it's a Git LFS pointer file, parse and return pointer metadata.
        Otherwise, return the full file content.

        Args:
            raw_url (str): The direct URL to fetch the file content.

        Returns:
            dict or str: If it's a Git LFS pointer file, returns a dictionary with metadata.
                        Otherwise, returns the raw content of the file as a string.
        """
        try:
            response = requests.get(raw_url, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Failed to fetch file: {raw_url} (HTTP {response.status_code})")
                return None

            content = response.text

            # Check if it's a Git LFS pointer file
            if content.startswith("version https://git-lfs.github.com/spec/v1"):
                pointer_info = {}
                for line in content.splitlines():
                    if line.startswith("version"):
                        pointer_info["version"] = line.split(" ", 1)[1].strip()
                    elif line.startswith("oid"):
                        parts = line.split(" ", 1)[1].strip().split(":", 1)
                        if len(parts) == 2:
                            pointer_info["oid_type"] = parts[0]
                            pointer_info["oid"] = parts[1]
                    elif line.startswith("size"):
                        pointer_info["size"] = line.split(" ", 1)[1].strip()

                return pointer_info  # Return structured metadata for Git LFS pointer files

            return content  # Otherwise, return full file content

        except requests.RequestException as e:
            print(f"⚠️ Error fetching file from {raw_url}: {e}")
            return None

    def fetch_issues(self, repo: str) -> None:
        """
        Fetches GitHub issues for a repository and stores them in MongoDB.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
        """
        page = 1
        while True:
            url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100&page={page}"
            data = self.github_request(url)
            if not data:
                break

            issues = []
            bulk_operations = []
            inserted_issue_ids = set()

            for issue in data:
                if 'pull_request' in issue:
                    continue  # Ignore PRs (only store actual issues)

                issue_id = f"{repo}#{issue['number']}"
                existing_issue = self.db_manager.db.issues.find_one({'_id': issue_id})

                issue_data = {
                    '_id': issue_id,
                    'repo': repo,
                    'number': issue['number'],
                    'title': issue['title'],
                    'body': issue.get('body', ''),  # Stocke le contenu de l'issue
                    'state': issue['state'],
                    'labels': [label['name'] for label in issue.get('labels', [])],
                    'comments': issue['comments'],
                    'created_at': issue['created_at'],
                    'updated_at': issue['updated_at'],
                    'url': issue['html_url']
                }

                if not existing_issue and issue_id not in inserted_issue_ids:
                    # Insert new issue
                    issues.append(issue_data)
                    inserted_issue_ids[issue_id] = issue_data
                elif (existing_issue and existing_issue['updated_at'] != issue['updated_at']):
                    bulk_operations.append(({'_id': issue_data['_id']}, {'$set': issue_data}))
                elif(issue_id in inserted_issue_ids):
                    bulk_operations.append(({'_id': issue_data['_id']}, {'$set': issue_data}))

            # Bulk insert for new issues
            if issues:
                self.db_manager.db.issues.insert_many(issues)

            # Bulk update existing issues
            if bulk_operations:
                self.db_manager.db.issues.bulk_write(
                    [pymongo.UpdateOne(q, u) for q, u in bulk_operations]
                )

            print(f"✅ Issues fetched and stored for {repo} (Page {page})")
            page += 1

    def fetch_pull_requests(self, repo: str) -> None:
        """
        Retrieves Pull Requests (PRs) from a repository and stores them in MongoDB.
        Large data (bodies) are stored locally with a reference in MongoDB.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
        """
        page = 1
        while True:
            url = f"https://api.github.com/repos/{repo}/pulls?state=all&per_page=100&page={page}"
            prs = self.github_request(url)
            if not prs:
                break

            prs_to_insert = []
            bulk_operations = []
            inserted_pr_ids = set()

            for pr in prs:
                pr_id = f"{repo}#{pr['number']}"
                existing_pr = self.db_manager.db.pull_requests.find_one({'_id': pr_id})

                # Store PR body content locally
                body_url, body_summary = None, None
                if pr.get("body"):
                    body_url = self.storage_manager.store_file_content(
                        pr["body"], repo, f"pr_{pr['number']}", "_body.txt"
                    )
                    body_summary = pr["body"][:500]  # Keep a short summary

                pr_data = {
                    '_id': pr_id,
                    'repo': repo,
                    'number': pr['number'],
                    'title': pr['title'],
                    'state': pr['state'],
                    'created_at': pr['created_at'],
                    'updated_at': pr['updated_at'],
                    'merged_at': pr.get('merged_at'),
                    'author': pr['user']['login'],
                    'commits': self.fetch_pr_commits(repo, pr['number']),
                    'metadata_id': None,
                    'body_url': body_url,
                    'body_summary': body_summary,
                    'body_metadata': None,
                    'labels': [label['name'] for label in pr.get('labels', [])],
                    'url': pr['html_url']
                }

                if not existing_pr and pr_id not in inserted_pr_ids:
                    prs_to_insert.append(pr_data)
                    inserted_pr_ids.add(pr_id)
                elif existing_pr and existing_pr['updated_at'] != pr['updated_at']:
                    bulk_operations.append(({'_id': pr_data['_id']}, {'$set': pr_data}))

            # Bulk insert for new PRs
            if prs_to_insert:
                self.db_manager.db.pull_requests.insert_many(prs_to_insert)

            # Bulk update existing PRs
            if bulk_operations:
                self.db_manager.db.pull_requests.bulk_write(
                    [pymongo.UpdateOne(q, u) for q, u in bulk_operations]
                )

            print(f"✅ Pull Requests fetched and stored for {repo} (Page {page})")
            page += 1

    def fetch_pr_commits(self, repo: str, pr_number: int) -> List[str]:
        """
        Retrieves commits linked to a Pull Request (PR) by checking only those present in the `commits` collection.
        If a commit is not in the database, it is assumed not to be part of the `main` branch.

        Args:
            repo (str): The GitHub repository (e.g., 'org/repo').
            pr_number (int): The pull request number.

        Returns:
            List[str]: A list of commit SHAs associated with the PR.
        """
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits?per_page=100"
        pr_commits = self.github_request(url)

        if not pr_commits:
            return []

        commit_shas = [commit["sha"] for commit in pr_commits]

        existing_commits = set(
            doc["_id"] for doc in self.db_manager.db.commits.find({"_id": {"$in": commit_shas}}, {"_id": 1})
        )

        valid_commit_ids = [sha for sha in commit_shas if sha in existing_commits]

        return valid_commit_ids

    def update_contributors(self) -> None:
        """
        Aggregates commit data to update the `contributors` collection.
        Each contributor's total commits and last 10 commit references are stored.
        """
        contributors_map = {}

        for commit in self.db_manager.db.commits.find({}, {"author": 1, "author_email": 1, "repo": 1, "_id": 1}):
            author_email = commit.get("author_email")
            if not author_email:
                continue

            if author_email not in contributors_map:
                contributors_map[author_email] = {
                    "name": commit["author"],
                    "email": author_email,
                    "repos": set(),
                    "commits": [],
                    "total_commits": 0
                }

            contributors_map[author_email]["repos"].add(commit["repo"])
            contributors_map[author_email]["commits"].append(commit["_id"])
            contributors_map[author_email]["total_commits"] += 1

        for email, data in contributors_map.items():
            self.db_manager.db.contributors.update_one(
                {"_id": email},
                {
                    "$set": {
                        "name": data["name"],
                        "email": data["email"],
                        "repos": list(data["repos"]),
                        "total_commits": data["total_commits"],
                        "commits": data["commits"][-10:]
                    }
                },
                upsert=True
            )

        print("✅ Update contributors done!")



Fichier: rag_builder\collectors\github_collector.py
Contenu:
"""
github_collector.py
Handles high-level orchestration of GitHub data collection.
This module delegates specific tasks to specialized submodules:
- github_commits.py (commits and contributors)
- github_pull_requests.py (pull requests)
- github_issues.py (issues)
- github_files.py (file management: branches & releases)
"""

from typing import List, Dict
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from collectors.github_commits import fetch_commits, update_contributors
from collectors.github_pull_requests import fetch_pull_requests
from collectors.github_issues import fetch_issues
from collectors.github_files import fetch_files_from_branch, fetch_latest_release_files
from collectors.github_request import github_request


class GitHubCollector:
    """
    Main orchestrator for GitHub data collection.
    """

    def __init__(self, db_manager: DatabaseManager, github_token: str, github_org: str, storage_manager: FileStorageManager):
        """
        Initializes the GitHubCollector with required dependencies.

        Args:
            db_manager (DatabaseManager): MongoDB manager instance.
            github_token (str): GitHub API token.
            github_org (str): GitHub organization to fetch data from.
            storage_manager (FileStorageManager): Storage manager for large files.
        """
        self.db_manager = db_manager
        self.github_token = github_token
        self.github_org = github_org
        self.storage_manager = storage_manager

    def update_all_repos(self):
        """
        Updates all repositories within the GitHub organization.
        """
        repos = self.fetch_repositories()
        self.update_selected_repos(repos)

    def update_selected_repos(self, repos: List[str]):
        """
        Updates all data for a selected list of repositories.

        Args:
            repos (List[str]): List of repositories to update.
        """
        for repo in repos:
            print(f"🔄 Updating all data for {repo}...")
            self.update_specific_data(repo, ["repository info", "commits", "pull requests", "issues"])
        print("✅ Repository updates completed.")

    def update_specific_data(self, repo: str, selected_data: List[str]):
        """
        Updates only selected parts of a repository's data.

        Args:
            repo (str): GitHub repository to update.
            selected_data (List[str]): List of data types to update.
        """
        if "repository info" in selected_data:
            self.fetch_repository_info(repo)
        if "commits" in selected_data:
            fetch_commits(self.db_manager, repo)
            update_contributors(self.db_manager)
        if "pull requests" in selected_data:
            fetch_pull_requests(self.db_manager, repo, self.storage_manager)
        if "issues" in selected_data:
            fetch_issues(self.db_manager, repo)
        # TODO manage main_files and last_release_files !!!

    def update_multiple_repos_specific_data(self, repos: List[str], selected_data: List[str]):
        """
        Updates selected data types for multiple repositories.

        Args:
            repos (List[str]): List of repositories to update.
            selected_data (List[str]): Data types to update.
        """
        for repo in repos:
            print(f"🔄 Updating {selected_data} for {repo}...")
            self.update_specific_data(repo, selected_data)
        
        print("✅ Multi-repo updates completed.")

    def fetch_repositories(self) -> List[str]:
        """
        Retrieves a list of repositories for the GitHub organization.

        Returns:
            List[str]: List of repository names.
        """
        url = f"https://api.github.com/orgs/{self.github_org}/repos?per_page=100"
        data = github_request(url)

        if not data:
            print(f"❌ Failed to fetch repositories for {self.github_org}")
            return []

        return [repo["full_name"] for repo in data]

    def fetch_repository_info(self, repo: str):
        """
        Fetches repository metadata.

        Args:
            repo (str): GitHub repository to fetch metadata for.
        """
        url = f"https://api.github.com/repos/{repo}"
        data = github_request(url)

        if not data:
            print(f"❌ Failed to fetch repository info for {repo}")
            return

        repo_entry = {
            "_id": repo,
            "description": data.get("description", ""),
            "language": data.get("language", ""),
            "url": data.get("html_url", ""),
            "last_commit_date": data.get("updated_at", ""),
        }

        self.db_manager.db.repositories.update_one({"_id": repo}, {"$set": repo_entry}, upsert=True)
        print(f"✅ Repository info updated for {repo}.")


Fichier: rag_builder\collectors\github_commits.py
Contenu:
"""
github_commits.py
Handles fetching and storing GitHub commits, file changes, and contributor updates.
"""

import pymongo
from datetime import datetime
from typing import List
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from collectors.github_request import github_request


def fetch_commits(db_manager: DatabaseManager, repo: str) -> None:
    """
    Fetches commits from a repository and stores them in MongoDB.

    Args:
        db_manager (DatabaseManager): Instance to interact with MongoDB.
        repo (str): The GitHub repository (e.g., 'org/repo').
        github_token (str): GitHub API token.
    """
    last_commit = db_manager.db.commits.find_one({"repo": repo}, sort=[("date", -1)])
    last_commit_date = last_commit["date"] if last_commit else None
    page = 1

    while True:
        url = f"https://api.github.com/repos/{repo}/commits?per_page=100&page={page}"
        data = github_request(url)

        if not data:
            break

        commits = []
        for commit in data:
            commit_sha = commit["sha"]
            commit_date = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")

            if last_commit_date and commit_date <= last_commit_date:
                return  # Stop fetching if commits are already stored

            if db_manager.db.commits.find_one({"_id": commit_sha}):
                continue  # Skip existing commits

            # Retrieve file details for each commit
            files_changed = fetch_commit_files(db_manager, repo, commit_sha)
            if not files_changed:
                continue

            commit_entry = {
                "_id": commit_sha,
                "repo": repo,
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"] if commit["commit"]["author"] else None,
                "author_email": commit["commit"]["author"]["email"] if commit["commit"]["author"] else None,
                "committer": commit["commit"]["committer"]["name"] if commit["commit"]["committer"] else None,
                "committer_email": commit["commit"]["committer"]["email"] if commit["commit"]["committer"] else None,
                "date": commit_date,
                'metadata_id': None,
                "files_changed": files_changed
            }
            commits.append(commit_entry)

        if commits:
            db_manager.db.commits.insert_many(commits)
            print(f"✅ {len(commits)} new commits added for {repo}")

        page += 1

def fetch_commit_files(db_manager: DatabaseManager, repo: str, commit_sha: str) -> List[str]:
    """
    Fetches details (files changed) for a commit.

    Args:
        db_manager (DatabaseManager): Instance to interact with MongoDB.
        repo (str): The GitHub repository.
        commit_sha (str): The commit SHA.
        github_token (str): GitHub API token.

    Returns:
        List[str]: List of file paths changed in the commit.
    """
    url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
    data = github_request(url)

    if not data or "files" not in data:
        return []

    files_info = []
    files_to_insert = []

    for file in data["files"]:
        file_id = f"{commit_sha}_{file['filename']}"
        if db_manager.db.files.find_one({"_id": file_id}):
            files_info.append(file_id)
            continue

        file_obj = {
            "_id": file_id,
            "commit_id": commit_sha,
            "repo": repo,
            "filename": file["filename"],
            "status": file["status"],
            "patch": file.get("patch", ""),
            "metadata_id": None,
            "lfs_pointer_id": None,
            "external_url": None
        }

        # Handle added files (download or detect LFS)
        if file["status"] == "added":
            raw_url = file.get("raw_url")
            if raw_url:
                file_content = fetch_large_file(raw_url)
                if isinstance(file_content, dict):  # Git LFS pointer case
                    lfs_pointer_id = f"{commit_sha}_{file['filename']}_lfs"
                    lfs_pointer = {
                        "_id": lfs_pointer_id,
                        "file_id": file_id,
                        "oid": file_content["oid"],
                        "size": file_content["size"],
                        "external_url": raw_url
                    }
                    db_manager.db.lfs_pointers.update_one({"_id": lfs_pointer_id}, {"$set": lfs_pointer}, upsert=True)
                    file_obj["lfs_pointer_id"] = lfs_pointer_id
                elif file_content:
                    external_url = FileStorageManager("local_storage", "http://localhost:8000").store_file_content(
                        file_content, repo, commit_sha, file["filename"]
                    )
                    file_obj["external_url"] = external_url

        files_info.append(file_id)
        files_to_insert.append(file_obj)

    if files_to_insert:
        db_manager.db.files.insert_many(files_to_insert)

    return files_info

def fetch_large_file(raw_url: str):
    """
    Fetches file content from its raw URL.
    If it's a Git LFS pointer file, parse and return pointer metadata.
    Otherwise, return the full file content.

    Args:
        raw_url (str): The direct URL to fetch the file content.

    Returns:
        dict or str: If it's a Git LFS pointer file, returns a dictionary with metadata.
                     Otherwise, returns the raw content of the file as a string.
    """
    response = github_request(raw_url, return_json=False)
    if not response:
        return None

    content = response.text

    # Check if it's a Git LFS pointer file
    if content.startswith("version https://git-lfs.github.com/spec/v1"):
        pointer_info = {}
        for line in content.splitlines():
            if line.startswith("version"):
                pointer_info["version"] = line.split(" ", 1)[1].strip()
            elif line.startswith("oid"):
                parts = line.split(" ", 1)[1].strip().split(":", 1)
                if len(parts) == 2:
                    pointer_info["oid_type"] = parts[0]
                    pointer_info["oid"] = parts[1]
            elif line.startswith("size"):
                pointer_info["size"] = line.split(" ", 1)[1].strip()

        return pointer_info  # Return structured metadata for Git LFS pointer files

    return content  # Otherwise, return full file content

def update_contributors(db_manager: DatabaseManager) -> None:
    """
    Aggregates commit data to update the `contributors` collection.

    Args:
        db_manager (DatabaseManager): Instance to interact with MongoDB.
    """
    contributors_map = {}

    # Fetch all commits and extract contributor information
    for commit in db_manager.db.commits.find({}, {"author": 1, "author_email": 1, "repo": 1, "_id": 1}):
        author_email = commit.get("author_email")
        author_name = commit.get("author")

        if not author_email:
            continue  # Ignore commits with no valid author email

        # Initialize contributor entry if not already in the map
        if author_email not in contributors_map:
            contributors_map[author_email] = {
                "name": author_name,
                "email": author_email,
                "repos": set(),
                "commits": [],
                "total_commits": 0
            }

        # Add repository and commit information
        contributors_map[author_email]["repos"].add(commit["repo"])
        contributors_map[author_email]["commits"].append(commit["_id"])
        contributors_map[author_email]["total_commits"] += 1

    # Bulk update contributors collection
    bulk_operations = []
    for email, data in contributors_map.items():
        bulk_operations.append(
            pymongo.UpdateOne(
                {"_id": email},
                {"$set": {
                    "name": data["name"],
                    "email": data["email"],
                    "repos": list(data["repos"]),
                    "total_commits": data["total_commits"],
                    "commits": data["commits"][-10:]  # Store only the last 10 commits for efficiency
                }},
                upsert=True  # Insert new contributor if not exists
            )
        )

    if bulk_operations:
        db_manager.db.contributors.bulk_write(bulk_operations)
        print(f"✅ Contributors updated successfully. {len(bulk_operations)} contributors modified.")
    else:
        print("ℹ️ No new contributors to update.")


Fichier: rag_builder\collectors\github_files.py
Contenu:
"""
github_files.py
Handles fetching and storing GitHub files from branches and releases into MongoDB.
"""

from typing import Optional
from collectors.github_request import github_request
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager


def fetch_files_from_branch(db_manager: DatabaseManager, repo: str, storage_manager: FileStorageManager) -> None:
    """
    Retrieves all files from the main branch and updates the `main_files` collection.

    Args:
        db_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
        repo (str): The GitHub repository (e.g., 'org/repo').
        storage_manager (FileStorageManager): Manages the storage of large files.
    """
    branch = get_default_branch(repo)
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    data = github_request(url)

    if not data or "tree" not in data:
        print(f"❌ Failed to fetch files from branch {branch} in {repo}")
        return

    current_files = {doc["filename"]: doc for doc in db_manager.db.main_files.find({"repo": repo})}
    files_to_insert = []
    files_to_delete = set(current_files.keys())

    for item in data["tree"]:
        if item["type"] != "blob":
            continue

        file_id = f"{repo}_main_{item['path']}"
        existing_file = db_manager.db.main_files.find_one({"_id": file_id})

        file_entry = {
            "_id": file_id,
            "repo": repo,
            "filename": item["path"],
            "commit_id": item["sha"],
            "metadata_id": None,
            "external_url": None
        }

        if existing_file:
            if existing_file["commit_id"] == file_entry["commit_id"]:
                files_to_delete.discard(item["path"])
                continue
            db_manager.db.main_files.update_one({"_id": file_id}, {"$set": file_entry})
            files_to_delete.discard(item["path"])
        else:
            raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{item['path']}"
            file_content = get_content(raw_url)

            if file_content:
                external_url = storage_manager.store_file_content(file_content, repo, branch, item["path"])
                file_entry["external_url"] = external_url

            files_to_insert.append(file_entry)

    if files_to_insert:
        db_manager.db.main_files.insert_many(files_to_insert)
        print(f"✅ {len(files_to_insert)} new files added to `main_files` for {repo}")

    if files_to_delete:
        db_manager.db.main_files.delete_many({"filename": {"$in": list(files_to_delete)}})
        print(f"🗑 {len(files_to_delete)} outdated files removed from `main_files` for {repo}")


def fetch_latest_release_files(db_manager: DatabaseManager, repo: str, storage_manager: FileStorageManager) -> None:
    """
    Retrieves all files from the latest release tag and updates the `last_release_files` collection.

    Args:
        db_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
        repo (str): The GitHub repository (e.g., 'org/repo').
        storage_manager (FileStorageManager): Manages the storage of large files.
    """
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    release_data = github_request(url)

    if not release_data or "tag_name" not in release_data:
        print(f"❌ No release found for {repo}")
        return

    latest_tag = release_data["tag_name"]
    print(f"🔖 Latest release for {repo}: {latest_tag}")

    url = f"https://api.github.com/repos/{repo}/git/trees/{latest_tag}?recursive=1"
    data = github_request(url)

    if not data or "tree" not in data:
        print(f"❌ Failed to fetch files from release {latest_tag} in {repo}")
        return

    current_files = {doc["filename"]: doc for doc in db_manager.db.last_release_files.find({"repo": repo})}
    files_to_insert = []
    files_to_delete = set(current_files.keys())

    for item in data["tree"]:
        if item["type"] != "blob":
            continue

        file_id = f"{repo}_last_release_{item['path']}"
        existing_file = db_manager.db.last_release_files.find_one({"_id": file_id})

        file_entry = {
            "_id": file_id,
            "repo": repo,
            "filename": item["path"],
            "commit_id": item["sha"],
            "metadata_id": None,
            "external_url": None
        }

        if existing_file:
            if existing_file["commit_id"] == file_entry["commit_id"]:
                files_to_delete.discard(item["path"])
                continue
            db_manager.db.last_release_files.update_one({"_id": file_id}, {"$set": file_entry})
            files_to_delete.discard(item["path"])
        else:
            raw_url = f"https://raw.githubusercontent.com/{repo}/{latest_tag}/{item['path']}"
            file_content = get_content(raw_url)

            if file_content:
                external_url = storage_manager.store_file_content(file_content, repo, latest_tag, item["path"])
                file_entry["external_url"] = external_url

            files_to_insert.append(file_entry)

    if files_to_insert:
        db_manager.db.last_release_files.insert_many(files_to_insert)
        print(f"✅ {len(files_to_insert)} new files added to `last_release_files` for {repo}")

    if files_to_delete:
        db_manager.db.last_release_files.delete_many({"filename": {"$in": list(files_to_delete)}})
        print(f"🗑 {len(files_to_delete)} outdated files removed from `last_release_files` for {repo}")


def get_default_branch(repo: str) -> str:
    """
    Retrieves the default branch of a GitHub repository.

    Args:
        repo (str): The GitHub repository.

    Returns:
        str: The default branch name (default: 'main').
    """
    url = f"https://api.github.com/repos/{repo}"
    data = github_request(url)

    if not data or "default_branch" not in data:
        print(f"⚠️ Could not determine default branch for {repo}, defaulting to 'main'")
        return "main"

    return data["default_branch"]


def get_content(raw_url: str) -> Optional[str]:
    """
    Fetches the content of a file from its raw GitHub URL.

    Args:
        raw_url (str): The direct URL to fetch the file content.

    Returns:
        Optional[str]: The file content if successfully retrieved.
    """
    response = github_request(raw_url, return_json=False)
    if not response:
        return None

    return response.text


Fichier: rag_builder\collectors\github_issues.py
Contenu:
"""
github_issues.py
Handles fetching and storing GitHub issues into MongoDB.
"""

import pymongo
from collectors.github_request import github_request
from core.database_manager import DatabaseManager


def fetch_issues(db_manager: DatabaseManager, repo: str) -> None:
    """
    Fetches GitHub issues for a repository and stores them in MongoDB.

    Args:
        db_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
        repo (str): The GitHub repository (e.g., 'org/repo').
    """
    page = 1

    while True:
        url = f"https://api.github.com/repos/{repo}/issues?state=all&per_page=100&page={page}"
        data = github_request(url)

        if not data:
            break  # Stop if an error occurs or there are no more issues

        issues = []
        bulk_operations = []
        inserted_issue_ids = set()

        for issue in data:
            if 'pull_request' in issue:
                continue  # Ignore PRs, we only want actual issues

            issue_id = f"{repo}_{issue['number']}"
            existing_issue = db_manager.db.issues.find_one({'_id': issue_id})

            issue_data = {
                '_id': issue_id,
                'repo': repo,
                'number': issue['number'],
                'metadata_id': None,
                'title': issue['title'],
                'body': issue.get('body', ''),
                'state': issue['state'],
                'labels': [label['name'] for label in issue.get('labels', [])],
                'comments': issue['comments'],
                'created_at': issue['created_at'],
                'updated_at': issue['updated_at'],
                'url': issue['html_url']
            }

            if not existing_issue and issue_id not in inserted_issue_ids:
                # Insert new issue
                issues.append(issue_data)
                inserted_issue_ids[issue_id] = issue_data
            elif (existing_issue and existing_issue['updated_at'] != issue['updated_at']):
                bulk_operations.append(({'_id': issue_data['_id']}, {'$set': issue_data}))
            elif(issue_id in inserted_issue_ids):
                bulk_operations.append(({'_id': issue_data['_id']}, {'$set': issue_data}))

        if issue.get("comments", 0) > 0:  # Only fetch comments if they exist
            fetch_issue_comments(db_manager, repo, issue["number"])

        # Bulk insert for new issues
        if issues:
            db_manager.db.issues.insert_many(issues)

        # Bulk update existing issues
        if bulk_operations:
            db_manager.db.issues.bulk_write(
                [pymongo.UpdateOne(q, u) for q, u in bulk_operations]
            )

        print(f"✅ Issues fetched and stored for {repo} (Page {page})")
        page += 1

def fetch_issue_comments(db_manager, repo: str, issue_number: int):
    """
    Fetches all comments for a given issue and stores them in MongoDB.

    Args:
        db_manager (DatabaseManager): MongoDB database manager.
        repo (str): Repository name.
        issue_number (int): Issue number.
        github_token (str): GitHub API token.
    """
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    comments_data = github_request(url)

    if not comments_data:
        print(f"⚠️ No comments found or failed request for PR {repo}_{issue_number}.")
        return

    comments_to_insert = []
    for comment in comments_data:
        comment_id = comment["id"]

        # Check if comment already exists in the database
        existing_comment = db_manager.db.issues_comments.find_one({"_id": comment_id})

        # If comment exists, check if an update is needed
        if existing_comment:
            if existing_comment["comment_body"] != comment["body"]:
                db_manager.db.issues_comments.update_one(
                    {"_id": f"{repo}_{issue_number}_{comment_id}"},
                    {"$set": {"comment_body": comment["body"], "updated_at": comment["updated_at"]}}
                )
                print(f"🔄 Updated comment {comment_id} for PR {repo}#{issue_number}.")
        else:
            # If comment does not exist, prepare for insertion
            comment_obj = {
                "_id": f"{repo}_{issue_number}_{comment_id}",
                "repo": repo,
                "issue_id": f"{issue_number}",
                "comment_body": comment["body"],
                "author": comment["user"]["login"],
                "created_at": comment["created_at"],
                "updated_at": comment.get("updated_at", comment["created_at"])  # Use created_at if updated_at is missing
            }
            comments_to_insert.append(comment_obj)

    # Bulk insert new comments
    if comments_to_insert:
        db_manager.db.issues_comments.insert_many(comments_to_insert)
        print(f"✅ Stored {len(comments_to_insert)} new comments for PR {repo}#{issue_number}.")


Fichier: rag_builder\collectors\github_pull_requests.py
Contenu:
"""
github_pull_requests.py
Handles fetching and storing GitHub Pull Requests into MongoDB.
"""

from typing import List
import pymongo
from collectors.github_request import github_request
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager


def fetch_pull_requests(db_manager: DatabaseManager, repo: str, storage_manager: FileStorageManager) -> None:
    """
    Fetches GitHub Pull Requests for a repository and stores them in MongoDB.

    Args:
        db_manager (DatabaseManager): Instance of DatabaseManager for MongoDB access.
        repo (str): The GitHub repository (e.g., 'org/repo').
        storage_manager (FileStorageManager): Manages the storage of large PR bodies.
    """
    page = 1

    while True:
        url = f"https://api.github.com/repos/{repo}/pulls?state=all&per_page=100&page={page}"
        data = github_request(url)

        if not data:
            break  # Stop if an error occurs or there are no more PRs

        prs = []
        bulk_operations = []
        inserted_pr_ids = set()

        for pr in data:
            pr_id = f"{repo}_{pr['number']}"
            existing_pr = db_manager.db.pull_requests.find_one({'_id': pr_id})

            # Stocke le corps du PR en local (évite de surcharger MongoDB)
            body_url = None
            if pr.get("body"):
                body_url = storage_manager.store_file_content(
                    pr["body"], repo, f"pr_{pr['number']}", "_body.txt"
                )

            pr_data = {
                '_id': pr_id,
                'repo': repo,
                'number': pr['number'],
                'title': pr['title'],
                'state': pr['state'],
                'created_at': pr['created_at'],
                'updated_at': pr['updated_at'],
                'merged_at': pr.get('merged_at'),
                'author': pr['user']['login'],
                'commits': fetch_pr_commits(db_manager, repo, pr['number']),
                'metadata_id': None,
                'body_url': body_url,
                'labels': [label['name'] for label in pr.get('labels', [])],
                'url': pr['html_url']
            }

            if pr.get("comments", 0) > 0:  # Only fetch comments if they exist
                fetch_pull_request_comments(db_manager, repo, pr["number"])

            if not existing_pr and pr_id not in inserted_pr_ids:
                prs.append(pr_data)
                inserted_pr_ids.add(pr_id)
            elif existing_pr and existing_pr['updated_at'] != pr['updated_at']:
                bulk_operations.append(({'_id': pr_data['_id']}, {'$set': pr_data}))

        # Bulk insert for new PRs
        if prs:
            db_manager.db.pull_requests.insert_many(prs)

        # Bulk update existing PRs
        if bulk_operations:
            db_manager.db.pull_requests.bulk_write(
                [pymongo.UpdateOne(q, u) for q, u in bulk_operations]
            )

        print(f"✅ Pull Requests fetched and stored for {repo} (Page {page})")
        page += 1


def fetch_pr_commits(db_manager: DatabaseManager, repo: str, pr_number: int) -> List[str]:
    """
    Retrieves commits linked to a Pull Request (PR) by checking only those present in the `commits` collection.
    If a commit is not in the database, it is assumed not to be part of the `main` branch.

    Args:
        db_manager (DatabaseManager): Instance to interact with MongoDB.
        repo (str): The GitHub repository (e.g., 'org/repo').
        pr_number (int): The pull request number.

    Returns:
        List[str]: A list of commit SHAs associated with the PR.
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits?per_page=100"
    pr_commits = github_request(url)

    if not pr_commits:
        return []

    commit_shas = [commit["sha"] for commit in pr_commits]

    existing_commits = set(
        doc["_id"] for doc in db_manager.db.commits.find({"_id": {"$in": commit_shas}}, {"_id": 1})
    )

    valid_commit_ids = [sha for sha in commit_shas if sha in existing_commits]

    return valid_commit_ids

def fetch_pull_request_comments(db_manager, repo: str, pr_number: int):
    """
    Fetches all comments for a given pull request and stores or updates them in MongoDB.

    Args:
        db_manager (DatabaseManager): MongoDB database manager.
        repo (str): Repository name.
        pr_number (int): Pull request number.
        github_token (str): GitHub API token.
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"
    comments_data = github_request(url)

    if not comments_data:
        print(f"⚠️ No comments found or failed request for PR {repo}#{pr_number}.")
        return

    comments_to_insert = []
    for comment in comments_data:
        comment_id = comment["id"]

        # Check if comment already exists in the database
        existing_comment = db_manager.db.pull_requests_comments.find_one({"_id": comment_id})

        # If comment exists, check if an update is needed
        if existing_comment:
            if existing_comment["comment_body"] != comment["body"]:
                db_manager.db.pull_requests_comments.update_one(
                    {"_id": f"{repo}_{pr_number}_{comment_id}"},
                    {"$set": {"comment_body": comment["body"], "updated_at": comment["updated_at"]}}
                )
                print(f"🔄 Updated comment {comment_id} for PR {repo}#{pr_number}.")
        else:
            # If comment does not exist, prepare for insertion
            comment_obj = {
                "_id": f"{repo}_{pr_number}_{comment_id}",
                "repo": repo,
                "pr_id": f"{pr_number}",
                "comment_body": comment["body"],
                "author": comment["user"]["login"],
                "created_at": comment["created_at"],
                "updated_at": comment.get("updated_at", comment["created_at"])  # Use created_at if updated_at is missing
            }
            comments_to_insert.append(comment_obj)

    # Bulk insert new comments
    if comments_to_insert:
        db_manager.db.pull_requests_comments.insert_many(comments_to_insert)
        print(f"✅ Stored {len(comments_to_insert)} new comments for PR {repo}#{pr_number}.")




Fichier: rag_builder\collectors\github_request.py
Contenu:
import os
import requests
import time
from typing import Dict, Optional, Any

def github_request(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, return_json: bool = True):
    """
    Makes a GitHub API request with rate limit handling.

    Args:
        url (str): The API endpoint URL.
        params (dict, optional): Additional query parameters.
        return_json (bool): Whether to return the response as JSON.

    Returns:
        dict or requests.Response: JSON response from GitHub API or full response object if return_json=False.
    """

    # If headers are not provided, use the GitHub token from the environment
    if headers is None:
        github_token = os.getenv("GITHUB_TOKEN")  # Read from .env only when needed
        if not github_token:
            raise ValueError("GitHub token is not set. Ensure GITHUB_TOKEN is defined in .env or provided explicitly.")
        headers = {"Authorization": f"token {github_token}"}

    while True:
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)

            # Manage rate limit
            if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
                reset_time = int(response.headers["X-RateLimit-Reset"])
                wait_time = max(0, reset_time - int(time.time())) + 1
                print(f"⚠️ GitHub rate limit reached. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue 

            # Manage HTTP errors
            if response.status_code != 200:
                print(f"❌ GitHub API Error ({response.status_code}): {response.text}")
                return None

            return response.json() if return_json else response

        except requests.RequestException as e:
            print(f"⚠️ Network error while fetching {url}: {e}")
            return None

Fichier: rag_builder\collectors\__init__.py
Contenu:


Fichier: rag_builder\core\database_manager.py
Contenu:
"""
database_manager.py
Manages MongoDB connection and allows direct access to the db object.
Indexes can be created here if needed.
"""

import pymongo
from typing import List

class DatabaseManager:
    """Provides direct access to MongoDB database and optionally creates indexes."""

    def __init__(self, mongo_uri: str, db_name: str, create_indexes: bool = True):
        """
        Initializes the MongoDB client and optionally creates indexes.
        
        Args:
            mongo_uri (str): MongoDB connection URI.
            db_name (str): Name of the database to use.
            create_indexes (bool): If True, call self._create_indexes() at init.
        """
        self._client = pymongo.MongoClient(mongo_uri)
        self._db = self._client[db_name]

        if create_indexes:
            self._create_indexes()

    @property
    def db(self):
        """
        Returns the pymongo Database instance so other code can perform 
        any operations they need (insert, update, etc.)
        """
        return self._db

    def _create_indexes(self) -> None:
        """
        Define indexes for all collections and create them only if they do not already exist.
        Optimized for query performance and data retrieval.
        """
        indexes = {
            "commits": [
                ("repo", pymongo.ASCENDING),
                ("date", pymongo.DESCENDING)
            ],
            "repositories": [
                ("_id", pymongo.ASCENDING)  # Unique repository identifier
            ],
            "contributors": [
                ("email", pymongo.ASCENDING, {"unique": True})
            ],
            "files": [
                ("commit_id", pymongo.ASCENDING),
                ("repo", pymongo.ASCENDING)
            ],
            "metadata": [
                ("file_id", pymongo.ASCENDING),
                ("file_source", pymongo.ASCENDING)
            ],
            "metadata_chunks": [
                (("metadata_id", pymongo.ASCENDING), {}),
                (("file_id", pymongo.ASCENDING), {}),
                (("chunk_index", pymongo.ASCENDING), {}),
                (("embedding", pymongo.ASCENDING), {"sparse": True})
            ],
            "lfs_pointers": [
                ("file_id", pymongo.ASCENDING)
            ],
            "issues": [
                (("repo", pymongo.ASCENDING), {}),
                (("updated_at", pymongo.DESCENDING), {}),
                (("state", pymongo.ASCENDING), {}),  # Optimized filtering by state
                (("labels", pymongo.ASCENDING), {}),  # Allows searching by labels
                (("repo", pymongo.ASCENDING), ("state", pymongo.ASCENDING)),  # Optimisation pour filtrage rapide
            ],
            "pull_requests": [
                (("repo", pymongo.ASCENDING), {}),
                (("updated_at", pymongo.DESCENDING), {}),
                (("state", pymongo.ASCENDING), {}),  # Optimized filtering by state
                (("labels", pymongo.ASCENDING), {}),  # Allows searching by labels
                (("repo", pymongo.ASCENDING), ("state", pymongo.ASCENDING)),  # Index composite pour filtrer PRs ouvertes/fermées
            ],
            "main_files": [
                (("repo", pymongo.ASCENDING), {}),
                (("filename", pymongo.ASCENDING), {}),
                (("commit_id", pymongo.DESCENDING), {}),  # Track the latest version
                (("metadata_id", pymongo.ASCENDING), {}),  # Link to metadata
            ],
            "last_release_files": [
                (("repo", pymongo.ASCENDING), {}),
                (("filename", pymongo.ASCENDING), {}),
                (("commit_id", pymongo.DESCENDING), {}),  # Track the latest release version
                (("metadata_id", pymongo.ASCENDING), {}),  # Link to metadata
            ],
            "issues_comments": [
            ("repo", pymongo.ASCENDING),
            ("issue_id", pymongo.ASCENDING)
            ],
            "pull_requests_comments": [
                ("repo", pymongo.ASCENDING),
                ("pr_id", pymongo.ASCENDING)
            ]
            # TODO In near futur, add new collection to manage user feedback and logs of the RAG engine
        }

        for collection, index_list in indexes.items():
            for index in index_list:
                keys = index[:-1] if isinstance(index[-1], dict) else index
                keys = [keys] if isinstance(keys[0], str) else keys  # Ensure it's a list of tuples
                options = index[-1] if isinstance(index[-1], dict) else {}
                self.db[collection].create_index(keys, **options)

    def list_collections(self) -> List[str]:
        """
        Lists all collections in the database.
        
        Returns:
            List[str]: A list of collection names.
        """
        return self.db.list_collection_names()

    def close_connection(self) -> None:
        """Close the MongoDB client connection."""
        self._client.close()


Fichier: rag_builder\core\file_storage_manager.py
Contenu:
"""
file_storage_manager.py
Handles local file storage operations (or could be extended to other storages).
"""

import os
import requests
from typing import Optional

class FileStorageManager:
    """Handles local file storage operations and retrieval of file content."""

    def __init__(self, base_storage_path: str, base_url: str):
        """
        Initializes the FileStorageManager.

        Args:
            base_storage_path (str): The root directory where files are stored locally.
            base_url (str): The base URL for serving files over HTTP.
        """
        self.base_storage_path = os.path.abspath(base_storage_path)
        self.base_url = base_url

        # Ensure the base storage directory exists
        os.makedirs(self.base_storage_path, exist_ok=True)

    def store_file_content(self, content: str, repo: str, reference_id: str, filename: str) -> str:
        """
        Stores file content locally and returns an accessible URL.

        Args:
            content (str): The raw text content to store.
            repo (str): The repository name or identifier.
            reference_id (str): Typically a commit SHA, branch name, or unique ID.
            filename (str): The name of the file.

        Returns:
            str: The external URL where the file can be accessed.
        """
        sanitized_repo = self._sanitize_repo_name(repo)
        sanitized_filename = self._sanitize_filename(filename)

        # Construct the local file path
        local_file_path = os.path.join(self.base_storage_path, sanitized_repo, reference_id, sanitized_filename)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Write the content to the file
        with open(local_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Generate the accessible URL
        relative_path = os.path.join(sanitized_repo, reference_id, sanitized_filename).replace(os.sep, "/")
        external_url = f"{self.base_url}/{relative_path}"

        return external_url

    def fetch_file_content(self, file_path: str) -> Optional[str]:
        """
        Fetches file content from a local path or URL.

        Args:
            file_path (str): The local file path or external URL.

        Returns:
            Optional[str]: The file content if successful, otherwise None.
        """
        if file_path.startswith("http"):
            return self._fetch_remote_file(file_path)
        return self._fetch_local_file(file_path)

    def _fetch_remote_file(self, url: str) -> Optional[str]:
        """
        Fetches file content from a remote URL.

        Args:
            url (str): The URL of the file.

        Returns:
            Optional[str]: The content of the file if successful, otherwise None.
        """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"[FileStorageManager] Error fetching file from {url}: {e}")
        return None

    def _fetch_local_file(self, file_path: str) -> Optional[str]:
        """
        Reads file content from a local path.

        Args:
            file_path (str): The absolute path of the file.

        Returns:
            Optional[str]: The file content if successful, otherwise None.
        """
        try:
            if not file_path.startswith(self.base_storage_path):
                print(f"[Security Warning] Attempt to access unauthorized path: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[FileStorageManager] Error reading file {file_path}: {e}")
        return None

    def delete_file(self, repo: str, reference_id: str, filename: str) -> bool:
        """
        Deletes a file from local storage.

        Args:
            repo (str): The repository name or identifier.
            reference_id (str): Typically a commit SHA, branch name, or unique ID.
            filename (str): The name of the file to delete.

        Returns:
            bool: True if the file was successfully deleted, False otherwise.
        """
        sanitized_repo = self._sanitize_repo_name(repo)
        sanitized_filename = self._sanitize_filename(filename)

        local_file_path = os.path.join(self.base_storage_path, sanitized_repo, reference_id, sanitized_filename)

        try:
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                return True
        except Exception as e:
            print(f"[FileStorageManager] Error deleting file {local_file_path}: {e}")
        return False

    def get_file_url(self, repo: str, reference_id: str, filename: str) -> str:
        """
        Returns the accessible URL of a stored file.

        Args:
            repo (str): The repository name or identifier.
            reference_id (str): Typically a commit SHA, branch name, or unique ID.
            filename (str): The name of the file.

        Returns:
            str: The constructed URL where the file can be accessed.
        """
        sanitized_repo = self._sanitize_repo_name(repo)
        sanitized_filename = self._sanitize_filename(filename)

        relative_path = os.path.join(sanitized_repo, reference_id, sanitized_filename).replace(os.sep, "/")
        return f"{self.base_url}/{relative_path}"

    def _sanitize_repo_name(self, repo: str) -> str:
        """
        Replace forward slashes in repo names with underscores
        so that we have a flat folder structure.
        """
        return repo.replace("/", "_")

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes the filename to avoid directory traversal, etc.
        """
        # Minimal example: remove any '..', etc.
        return os.path.basename(filename)


Fichier: rag_builder\core\rag_engine.py
Contenu:
"""
rag_engine.py
Provides a simple RAG Engine for retrieving context from DB and generating answers.
"""

import numpy as np

class RAGEngine:
    """
    A retrieval-augmented generation engine to handle user queries, 
    retrieve chunks, and generate answers.
    """

    def __init__(self, db_manager, embedding_model, generative_model, vector_index):
        """
        Args:
            db_manager (DatabaseManager): The database manager instance.
            embedding_model: A model that can encode text into vectors.
            generative_model: A model that can generate text from a prompt.
            vector_index: A FAISS or other vector index for semantic search.
        """
        self.db_manager = db_manager
        self.embedding_model = embedding_model
        self.generative_model = generative_model
        self.vector_index = vector_index

    def answer_query(self, query: str, top_k: int = 3) -> str:
        """
        Encodes the query, retrieves top_k relevant chunks, 
        and uses the generative model to produce an answer.
        """
        query_vector = self.embedding_model.encode(query)
        # Suppose we have a FAISS index, do similarity search
        # This is just a placeholder
        D, I = self.vector_index.search(
            np.array([query_vector], dtype=np.float32), top_k
        )

        # TODO using FAISS, mongoDB and manage discussion as it is in openAI

        # Retrieve the text from DB or from an in-memory structure
        # Build a prompt, feed to generative_model
        # For simplicity:
        retrieved_context = "Context from top-k chunks..."
        final_answer = self.generative_model.generate(f"Question: {query}\nContext: {retrieved_context}\nAnswer:")
        return final_answer


Fichier: rag_builder\core\__init__.py
Contenu:


Fichier: rag_builder\embeddings\embeddings.py
Contenu:
from abc import ABC, abstractmethod
from typing import List

class AbstractEmbeddingModel(ABC):
    @abstractmethod
    def encode(self, text: str) -> List[float]:
        """Encodes text into an embedding vector."""
        pass

from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbeddingModel(AbstractEmbeddingModel):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

Fichier: rag_builder\embeddings\__init__.py
Contenu:


Fichier: rag_builder\keywords_extractors\keywords_extractors.py
Contenu:
from typing import List
from abc import ABC, abstractmethod

class AbstractKeywordExtractor(ABC):
    @abstractmethod
    def extract(self, text: str, num_keywords: int = 10) -> List[str]:
        """Extract a list of keywords from the text provided."""
        pass

import yake

class YakeKeywordExtractor(AbstractKeywordExtractor):
    def __init__(self, language: str = "en"):
        self.extractor = yake.KeywordExtractor(lan=language)

    def extract(self, text: str, num_keywords: int = 10) -> List[str]:
        keywords = self.extractor.extract_keywords(text)
        return [kw[0] for kw in keywords][:num_keywords]

Fichier: rag_builder\keywords_extractors\__init__.py
Contenu:


Fichier: rag_builder\LLMs\L5-small_llm.py
Contenu:


Fichier: rag_builder\LLMs\llm_interface.py
Contenu:
"""
llm_interface.py
Defines a unified interface for different LLM implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

class ILLM(ABC):
    """
    A unified interface for various LLM backends: local, API-based, etc.
    """

    @abstractmethod
    def chat(self, user_input: str, context: Optional[str] = None) -> str:
        """
        Returns a response to the user's input in a chat-like format.
        Optionally uses the provided context for better answers.
        """
        pass

    @abstractmethod
    def summarize(self, text: str) -> str:
        """
        Generates a summary of the given text.
        """
        pass

    @abstractmethod
    def run_agent(self, instructions: str) -> str:
        """
        Runs an AI "agent" that can perform multi-step reasoning or actions.
        The implementation depends on the model's capabilities.
        """
        pass

    @abstractmethod
    def analyze_logs(self, logs: List[str]) -> str:
        """
        Analyzes a list of log strings and proposes improvements or insights.
        """
        pass


Fichier: rag_builder\LLMs\llm_manager.py
Contenu:
"""
llm_manager.py
A factory/manager that returns LLM instances based on user config.
"""

from typing import Optional, Dict
from .llm_interface import ILLM
from .mistral_llm import MistralLLM
# Import other future classes here (MistralLLM, DeepSeekLLM, etc.)

class LLMManager:
    """
    A manager to create or retrieve an LLM object for a given "model_type".
    The interface remains consistent (ILLM).
    """

    @staticmethod
    def load_llm(model_type: str, config: Dict[str, str]) -> ILLM:
        """
        Creates and returns an instance of an LLM given a model_type and config.
        
        Args:
            model_type (str): Name of the model type (e.g. 'mistral-7B', 'L5-small', "deepseek-R1" etc.)
            config (Dict[str, str]): Model-specific configuration or credentials.
        
        Returns:
            ILLM: An instance that implements the ILLM interface.
        """
        if model_type == "mistral-7B":
            return MistralLLM(model_path=config.get("model_path", ""))
        # elif model_type == "mistral":
        #     return MistralLLM(...)
        # elif model_type == "deepseek":
        #     return DeepSeekLLM(...)
        else:
            raise ValueError(f"Unknown model_type: {model_type}")


Fichier: rag_builder\LLMs\mistral_llm.py
Contenu:
"""
mistral_llm.py
Example LLM that runs mistrall llm locally (placeholder).
"""

from typing import Optional, List
from .llm_interface import ILLM

class MistralLLM(ILLM):
    """
    A Mistral LLM interface to a local model like.
    Here, just a placeholder that returns static responses.
    """

    def __init__(self, model_path: str):
        self.model_path = model_path
        # Here you'd load the model from disk, e.g. with llama.cpp or GPT4All

    def chat(self, user_input: str, context: Optional[str] = None) -> str:
        return f"[LocalLLM] You said: {user_input}, context: {context}"

    def summarize(self, text: str) -> str:
        return f"[LocalLLM] Summary of text: {text[:100]}..."

    def run_agent(self, instructions: str) -> str:
        return f"[LocalLLM Agent Output] For instructions: {instructions}"

    def analyze_logs(self, logs: List[str]) -> str:
        return f"[LocalLLM] Analyzing {len(logs)} logs. Potential improvements..."


Fichier: rag_builder\LLMs\__init__.py
Contenu:


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\00e849f9b29e20459a20181f255595065195ca1e\apps\uniris_p2p\README.md
Contenu:
# UnirisP2p

**TODO: Add description**

## Installation

If [available in Hex](https://hex.pm/docs/publish), the package can be installed
by adding `uniris_p2p` to your list of dependencies in `mix.exs`:

```elixir
def deps do
  [
    {:uniris_p2p, "~> 0.1.0"}
  ]
end
```

Documentation can be generated with [ExDoc](https://github.com/elixir-lang/ex_doc)
and published on [HexDocs](https://hexdocs.pm). Once published, the docs can
be found at [https://hexdocs.pm/uniris_p2p](https://hexdocs.pm/uniris_p2p).



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\0b7c30046e118177154b22378538406acd747c43\CODE_OF_CONDUCT.md
Contenu:
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the
  overall community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or
  advances of any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email
  address, without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community include using an official e-mail address,
posting via an official social media account, or acting as an appointed
representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
ethic@archethic.net.
All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact**: A violation through a single incident or series
of actions.

**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved, including unsolicited interaction with
those enforcing the Code of Conduct, for a specified period of time. This
includes avoiding interactions in community spaces as well as external channels
like social media. Violating these terms may lead to a temporary or
permanent ban.

### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including
sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior,  harassment of an
individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within
the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.0, available at
https://www.contributor-covenant.org/version/2/0/code_of_conduct.html.

Community Impact Guidelines were inspired by [Mozilla's code of conduct
enforcement ladder](https://github.com/mozilla/diversity).

[homepage]: https://www.contributor-covenant.org

For answers to common questions about this code of conduct, see the FAQ at
https://www.contributor-covenant.org/faq. Translations are available at
https://www.contributor-covenant.org/translations.


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\21a9085080cc766abc778d94cbc7c9d03fdb233d\contributing.md
Contenu:
# Contributing

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to ARCHEthic node which is hosted in the [ARCHEthic Foundation](https://github.com/archethic-foundation) on GitHub. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[I don't want to read this whole thing, I just have a question!!!](#i-dont-want-to-read-this-whole-thing-i-just-have-a-question)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)
     * [Git Commit Messages](#git-commit-messages)


## Code of Conduct

This project and everyone participating in it is governed by the [ARCHEthic code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## I don't want to read this whole thing I just have a question!!!

> **Note:** Please don't file an issue to ask a question.

We have an official message board with a detailed FAQ and where the community chimes in with helpful advice if you have questions.

* [Github Discussions](https://github.com/archethic-foundation/archethic-node/discussions)
* [ARCHEthic Website](https://archethic.net)

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for ARCHEthic node. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report). Fill out [the required template](https://github.com/archethic-foundation/.github/blob/master/.github/ISSUE_TEMPLATE/bug_report.yml), the information it asks for helps us resolve issues faster.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

#### Before Submitting A Bug Report

* **Check the [discussions](https://github.com/archethic-foundation/archethic-node/discussions)** for a list of common questions and problems.
* **Check the [issue list](https://github.com/archethic-foundation/archethic-node/issues)** if it has been already opened.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/) and create an issue on that repository and provide the following information by filling in [the template](https://github.com/archethic-foundation/.github/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml).

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible. When listing steps, **don't just say what you did, but explain how you did it**.
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples. If you're providing snippets in the issue, use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **If you're reporting a crash**, include a crash report with a stack trace. nclude the crash report in the issue in a [code block](https://help.github.com/articles/markdown-basics/#multiple-lines), a [file attachment](https://help.github.com/articles/file-attachments-on-issues-and-pull-requests/), or put it in a [gist](https://gist.github.com/) and provide link to that gist.
* **If the problem is related to performance or memory**, include a screenshot of the `observer`
* **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened and share more information using the guidelines below.

Provide more context by answering these questions:

* **Did the problem start happening recently** (e.g. after updating to a new version) or was this always a problem?
* If the problem started happening recently, **can you reproduce the problem in an older version of the node?** What's the most recent version in which the problem doesn't happen?
* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for ARCHEThic node, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.

Before creating enhancement suggestions, please check [this list](#before-submitting-an-enhancement-suggestion) as you might find out that you don't need to create one. When you are creating an enhancement suggestion, please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion). Fill in [the template](https://github.com/archethic-foundation/.github/blob/master/.github/ISSUE_TEMPLATE/feature_request.yml), including the steps that you imagine you would take if the feature you're requesting existed.

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/) and create an issue on that repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a detailed description of the suggested enhancement** in as many details as possible.
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Explain why this enhancement would be useful** .

### Your First Code Contribution

Unsure where to begin contributing to Atom? You can start by looking through these `beginner` and `help-wanted` issues:

* [Beginner issues][beginner] - issues which should only require a few lines of code, and a test or two.
* [Help wanted issues][help-wanted] - issues which should be a bit more involved than `beginner` issues.

Both issue lists are sorted by total number of comments. While not perfect, number of comments is a reasonable proxy for impact a given change will have.

### Pull Requests

The process described here has several goals:

- Maintain ARCHEthic node's quality
- Fix problems that are important
- Enable a sustainable system for ARCHEthic's maintainers to review contributions

#### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :non-potable_water: `:non-potable_water:` when plugging memory leaks
    * :memo: `:memo:` when writing docs
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\320d947c8d276279687304aab870e09021541059\priv\static\docs\development\testnet\local.md
Contenu:
# Local Testnet

To test and build on top of ArchEthic network, we encourage people to test with a local instance.

## Installation

- Clone the repository: 
```
git clone https://github.com/archethic-foundation/archethic-node.git
```

- Setup the dev environment:

  - [Install Elixir](https://elixir-lang.org/install.html)
  - [Install NodeJS](https://nodejs.org/en/download/)
  - [Install GMP](https://gmplib.org)
  - [Install ScyllaDB](https://www.scylladb.com/download/#server)
  
- Fetch the dependencies
```
mix deps.get
```

- Build web assets
```
cd assets ; npm install; cd -
``` 

- Start instance
```
iex -S mix
```

## Funding addresses

To be able to fund some addresses you can specify in the configuration which will be the addresses and the amount as genesis pool during the network initialization

- Ensure a fresh start
```
make clean
```

- Restart the node with some configuration
```
ARCHETHIC_TESTNET_GENESIS_ADDRESS=YOUR_ADDRESS_IN_HEXADECIMAL ARCHETHIC_TESTNET_GENESIS_AMOUNT=AMOUNT_TO_ALLOCATE iex -S mix
```

- Check the balance

Go to http://localhost:4000/explorer/transaction/{TYPE_YOUR_ADDRESS_IN_HEXADECIMAL}

It should displays some unspent outputs (in the "Ledger inputs" section) 


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\478030c8038287264284465a69661601cb1de7c3\README.md
Contenu:
# uniris-node
Uniris Node


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7c684216305941c70a21aa1c52ae121d25d1bd17\apps\uniris_sync\README.md
Contenu:
# UnirisSync



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\README.md
Contenu:
# Welcome <!-- {docsify-ignore-all} -->
 
ArchEthic is a next generation of Blockchain which provide a truly decentralized limitless network, using `TransactionChain` and a new consensus named ARCH (Atomic Rotating Commitment Heuristic), <br/>  to be the most secure and scalable decentralized network.

---

Our network is built to face most of the issues of other blockchain solutions:
- Support of billions of transactions
- Linear scalability
- Low-energy consumption
- Mass adoption
- Low transaction fees 

This document aims to provide information and resources about the technology
and the usage to build new decentralized applications on top of ArchEthic.


---

## Motivations

Given the universal constraints both material and physical, billions of transactions cannot be integrated into a single branch of chained blocks. <br />
Similarly, regardless of the consensus method, it is not possible to ensure universal consensus on billions of transactions by polling all nodes of the network. <br />
Finally, the functioning of current distributed networks (P2P) is such that it is not possible to guarantee the freshness (consistency) of data on an asynchronous network, <br />
unless the network is slowed down excessively by the calculation of the nonce of the block (PoW), as is the case with other blockchain networks.

ArchEthic Blockchain solved this issues in the following way:
- TransactionChains: 
> Instead of chained blocks of transactions, each block is reduced to its atomic form. <br />
Therefore each block contains only one transaction and each transaction will be chained in its own chain.

## Innovations

- Real Sharded Network
> ARCHEthic is using `sharding` technology to ensure distribution of transaction processing and storage to provide<br />
a very high scalability.

- Next generation consensus:
> ARCHEthic is using an universal consensus called `ARCH` based on Atomic Commitment using Heuristic Rotating election<br />
of a tiny set of validation nodes providing the highest level of security

- Optimized Replication and Self Repair
> Every transaction will be stored in a deterministic way on a set of nodes using a sharded storage layer. <br />
  Thus, every node will autonomously know all the nodes for a given transaction and ease the network 
  by only interrogating the closest elected nodes. 

- Distributed network without buttleneck
> ArchEthic rebuild the entire P2P layer to provide an efficient messaging between peers based on the Supervised Multicast <br />
using self discovery mechanism from incoming connection and network transactions.<br />
The system is able to maintain a qualified vision of the network while limiting the generation of requests

---

![logo](./archethic.svg ':size=300*300')

*Backed by the ArchEthic Foundation*


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\_coverpage.md
Contenu:
# ArchEthic Network <small>0.10</small>

> A truly decentralized and unlimited P2P network

[Github](https://github.com/archethic-foundation/archethic-node)
[Explorer](https://www.archethic.net)
[Get started](README.md)

<!-- background color -->

![color](#3596F2)



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\_sidebar.md
Contenu:
- [Welcome](README.md)
- Technology
  - [Transaction Chain](/network/transaction_chain/)
  - [ARCH Consensus](/network/arch/)
    - [Proof Of Work](/network/arch/proof_of_work.md)
  - [Sharding](/network/sharding/)
    - [Beacon Chain](/network/sharding/beacon_chain.md)
  - [Fee](/network/fee.md)
  - [P2P layer](/network/p2p/)
    - [Node](/network/p2p/node.md)
    - [Bootstrapping](/network/p2p/bootstrapping.md)
    - [Self Repair](/network/p2p/self_repair.md)
    - [Messaging](/network/p2p/messaging.md)  
  - [Oracle Chain](/network/oracle_chain.md)
  - [Smart Contract](/network/smart_contract/)
    - [Language](/network/smart_contract/language.md)
    - [Examples](/network/smart_contract/examples.md)
- Development 
  - [Core](/development/core/README.md)
  - Testnet
    - [Local](/development/testnet/local.md)
    - [Faucet](/development/testnet/faucet.md)

  - SDK
    - [Javascript](/development/sdk/js.md)
    - [Flutter](/development/sdk/flutter.md)


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\development\core\README.md
Contenu:
# Core Development

ArchEthic Node repository can be found [here](https://github.com/archethic-foundation/archethic-node)


## Technology Stack

ArchEthic Blockchain node used:
- Elixir
- C
- ScyllaDB

### Why Elixir ?

Elixir is a dynamic, functional language for building scalable and maintainable applications.

It leverages the Erlang VM, known for running low-latency, distributed, and fault-tolerant systems. <br />Elixir is successfully used in web development, embedded software, data ingestion, and multimedia processing, across a wide range of industries

When we are building P2P systems and Blockchain technologies we need to think about fault-tolerance, low-latency, concurrent/parallelism.
Elixir matches all those requirements </br /> 
Because All Elixir code runs inside lightweight threads of execution (called processes) that are isolated and exchange information via messages, we can build fast
processing of data which result in a high TPS for a better scalability.

The unavoidable truth about software running in production is that things will go wrong. <br />
Even more when we take network, file systems, and other third-party resources into account. <br />
Elixir provides supervisors which describe how to restart parts of your system when things go awry, going back to a known initial state that is guaranteed to work. <br />
This feature ensures in case on failure, the entire system will not be down, and the isolation provided by the processes and their restarsting strategy helps us to achieve it.

Functional programming promotes a coding style that helps developers write code that is short, concise, and maintainable.

Out of the box, Erlang VM provides the capability to hot reload code which is the best case scenarion if we want to provide an on-chain governance without restarting nodes.

### Why C ?

We need to interact with hardware components and C seems the best candidate, so we are using this language to communicate with TPM for instance. <br />
But also, for some intensive task which are really complex in computing, we rely C to perform those processing.

### Why ScyllaDB ?

ScyllaDB is a NoSQL database built from the idea of Cassandra - Wide Column Database - but with more efficiency in term of memory consumption and CPU processing.
As it's implemented in C++, it's faster and lightweight and takes advantage of low-level Linux primitives

We are using a Wide Column Database but we want to be able to fetch only some part of the data, so a column database fits really well for this kind of purpose.
Moreover, we want a database with a high throughput in writing and ScyllaDB fits really well with its LSM storage engine.

## Structure

Code base is splitted into domains (contexts) for better single responsibility principle:
- `TransactionChain`: Manage transaction data structure and chain management
- `DB`: Manage all the database queries
- `Crypto`: Manage all the cryptographic operations
- `P2P`: Manage the P2P node listing and node communication
- `Election`: Manage the node election algorithms
- `Mining`: Manage transaction validation
- `Replication`: Manage the replication
- `BeaconChain`: Manage BeaconChain subset and synchronization
- `OracleChain`: Manage OracleChain services, polling and scheduling
- `SharedSecrets`: Manage Shared Secrets scheduling and listing
- `SelfRepair` : Manage the SelfRepair scheduling
- `Bootstrap`: Manage the node bootstrapping


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\fee.md
Contenu:
# Fee

ArchEthic Blockchain is using specific heuristic algorithms to ensure the best transaction's distribution.

The fees are calculated according to the real costs of the network (size, complexity) and is based on the real value of the UCO (using [Oracle Chain](/network/oracle_chain.md))

## Distribution

Transaction's fee are distributed across all the actors during the transaction validation:
- `Coordinator Node`: 10% 
- `Cross validation Nodes`: 40%
- `Storage Nodes`: 50%

The remaining 10% will go the `Network Pool` as a burn mechanism to ensure a programmable destruction of UCO. 
<br />
This mechanism will ensure a deflation and therefore a way to increase the value of each UCO

## Calculation

The transaction's fee computation is based on some properties:
- Transaction's value
- Number of recipient
- Size of the transaction
- Number of replicas
- Complexity of the smart contract (TODO)


> Minimum fee: 0.1$ of the current UCO price

> Transaction value fee: minimum_fee * ( transaction_value / (minimum_fee * 1000) ) 

!> In case, there is not value (no uco to spend), a minimum fee is applied corresponding of 0.1$ of UCO

> Each byte will cost: 10<sup>-9</sup> of the current UCO's price

> After one recipient, each will cost: 10% of the current UCO's price

Formula:
```
Transaction Fee = fee_for_value + fee_for_storage + fee_for_complexity + cost_per_recipient
```

  




Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\oracle_chain.md
Contenu:
# OracleChain

ArchEthic Blockchain supports Off-Chain communication through a dedicated transaction chain called `OracleChain`.

It aims to gather external data to be used inside the network or the smart contract layer.

## How is it work ?

OracleChain behaves a bit like the BeaconChains except the transaction on the chain are generated every 10min but only when there is a new data updated.

It using long-polling to get data from external sources and submit a transaction through ARCH Consensus.

By using ARCH consensus, we ensure the atomic commitment of the data submitted and ensure validity of the information written into the transaction.

Each node received the new transaction from the OracleChain and can apply behaviors from this new data and notify smart contracts which depends on oracle updates.

## Services

The list of services supported by the OracleChain:

- UCO Price Feed: fetching UCO token price from Coingecko in USD/EUR currency and is used for the:
  - Transaction Fee algorithm
  - Auto reward of nodes which didn't receive enough mining rewards




Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\README.md
Contenu:
# ArchEthic Network


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\arch\proof_of_work.md
Contenu:
# Proof Of Work
 
Others blockchains are using the concept of `Proof of Work` to ensure an unpredictable and pseudo random election of block validation (mining).
<br />
But this technique requires a lot of energy consumption and can still be subject to exploit by HashRate control.

ArchEthic Blockchain is using a new kind of `Proof of Work` to ensure the authenticity of the transaction origination devices.
<br />
This allows the additional security requirements on transaction validation like:
- prohibit any transaction even in case of key theft
- allow user to consult their balance ony any smartphone but generate a transaction only on a trusted device
- enable the organizers of an election to ensure biometric identity of a voter

## Concepts

The `Proof Of Work` consists of finding the right public key associated to the `Origin Signature` of the transaction
<br />from a list of public keys known by the network.

This verification is performed during the `Validation Stamp` creation by the `Coordinator Node` and ensure the device is authorized to generate the transaction

## Origin Devices

Just like any other actor into the system, devices will have their own transaction chain allowing them to update their keys. 

> Each origin device public keys are grouped by family which helps nodes to determine which set of keys, must be played to produce the Proof of Work. (i.e: software, usb, biometric).

> Each origin device public key is encrypted and renewed by the network ensuring confidentiality and authenticity of devices.



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\arch\README.md
Contenu:
# ARCH Consensus
 
ArchEthic Blockchain is using a new consensus called `ARCH` (Atomic Rotating Commitment Heuristic) for a uncompromising consensus to support
<br />
high scalability and high throughput.

ArchEthic Blockchain is based on three properties:

* Security: Each transaction is validated atomically
* Data consistency: Algorithms ensure to access the latest write and maximum availability
* Fault tolerance: Allow nodes to operate independently even in case of disaster


`ARCH` consensus is defined by three concepts:
- `Atomic Commitment`: The most absolute form a consensus which implies 100% of concordant responses for the acceptal or refusal of the transaction validation
- `Heuristic`: Set of algorithms which manages the entire network allowing to elect in a decentralized and coordinated way the nodes in charge to validate or store the transaction chains
- `Rotating`: Node election is constantly changing. No nodes can predict which nodes will validate the transaction before its arrives

## Atomic Commitment

ArchEthic Blockchain is based on `Hypergeometric distribution` laws which from an unpredictable election and formal consensus make it possible to obtain
<br />with certainty (99.99999999%) the same answer by querying 197 nodes as would be obtained by querying 100 000 nodes.

Therefore, it makes possible the consensus establishment with a small part of nodes and can resist to attacks of 90% of malicious nodes. 
<br />
The risk of related availability is ensure by a strict management of the disruptive nodes which are banished after investigation of the origin of the disagreement.

By supporting more 90% of malicious nodes into its network, `ARCH` consensus is above aeronautical or nuclear standard, thanks to the `Atomic Commitment` which 
<br />
request the total aggreement of the validation nodes and from a `Malicious Detection` algorithm to detect the malicious nodes.


## Rotating Election

Each rotating election is unpredictable but still verifiable and reproducible.
The rotating algorithm sort a list of nodes based on:
- `Hash of transaction`: Unpredictable until the transaction arrives
- `Daily nonce`: Secret shared between the authorized nodes and renewed daily
- `Node public key`: Last node public key

The rotating election produces a proof, named: `Proof of Election` which can be verified by any other nodes to ensure the right election of nodes.

From this algorithm, we get a list of nodes which can be filter according to the constraints of the validation of the transaction.
- P2P availability
- Geographical distribution

## Workflow

When a transaction is willing to be validated, its follows the given workflow:

1. The transaction is received by any node (aka `Welcome node`)
2. The `Welcome Node` determines the validation nodes from the `Rotating Election` algorithm and forward the transaction
3. The validation nodes after receiving the transaction start some preliminary job to gather the context of the transaction:
   - Previous transaction
   - List of unspent outputs
4. After the context building, the `Cross Validation Nodes` communicate to the `Coordinator Node` the list of storage nodes involved to gather those information.
5. The `Coordinator Node` can build the `Validation Stamp` and compute the replication tree. Then it transmits them to the `Cross Validation Nodes`.
6. The `Cross Validation Nodes` verify the content of the `Validation Stamp`, sign with or without inconsistencies and send the `Cross Validation Stamp` to all the validation nodes involved.
7. Once all the `Cross Validation Stamps` are received and if the `Atomic Commitment` is reached, the replication phase starts.
8. Validation nodes send the transaction to the respective storages nodes:
- Storage nodes responsible for the new transaction chain
- Storage nodes responsible for the outputs of the transactions (transaction's movements addresses, node movements, recipients)
- Storage nodes responsible for the [Beacon Chain](/network/beacon_chain.md)
9. The storage for the new transaction chain will notify the validation nodes and the `Welcome Node` about the replication, and the `Welcome Node` will notify the client about it.


 


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\p2p\bootstrapping.md
Contenu:
# Bootstrapping 

ArchEthic Blockchain by using Network Transaction and Supervised Multicast, requires some actions to be performed 
when a node is bootstrapping. This operations will ensure synchronization and P2P awareness.

## Announcing

When a node wants the network the first time, it will request from a list of preconfigured nodes to reach (called "bootstrapping seeds"), the closest nodes from its position.

Then, it will generate a first node transaction including as data: ip, port, protocol, reward address, key certificate (to ensure the key is coming from an secure element)
Once the network will attest and verify its transaction, the node will be able to start a SelfRepair proecss

## Updates

When a nodes rejoin the network after some time, depending if its previous data expired, it will generate a new transaction with the new information

## Synchronization

Once the transaction is validated, the node will start by requesting the list of nodes.

Then, it will start the [Self-Repair](/network/p2p/self_repair.md) sequence to get and synchronize the missing transactions and publish its end of sync to the network.

By this way, the entire will know the existence the readyness of this node.


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\p2p\messaging.md
Contenu:
# Messaging

ArchEthic Blockchain is used a brand new P2P layer from the Supervised Multicast, but to ensure the best data transmission possible,
<br />we are using two modern approaches: `Stream Multiplexer` and `Binary Protocol`. 

Those two features helps to achieve a low latency P2P messaging.

## Stream Multiplexer

Stream Multiplexing allows multiple independent logical streams to all share a common underlying transport stream and <br />
there are many independent streams of communication between peers and have several concurrent streams open at the same time with a given remote peer.

Stream Multiplexing amortize the overhead of establishing transport connection and helps to distinguish which messages to handle in a concurrent way.

```
|---------|                           |---------|
| Service |                           | Service |
|---------|                           |---------|
    | Msg ID: 2    |------------|         |
    |--------------| Connection |---------| Msg ID: 1
                   |    TCP     |
    |--------------|------------|---------|
    | Msg ID: 1                           | Msg ID: 2
|---------|                           |---------|
| Service |                           | Service |
|---------|                           |---------|
```

## Binary Protocol

Network latency is very important to reach an unlimited and really scalable network and using binary protocol helps to reduce bandwith.

Different kind of solutions existing for binary protocol: Protobuf, Avro, Thrift, MsgPack, etc..
<br />
However to support a custom and efficient binary serialization, ArchEthic uses it own binary protocol through the transport layer
to reduce and to optimize by the message the data to send.

This aspect is important, when we are dealing with bits, to reduce byte size.

For example, if we want to serialize this bitstring: 11100000
- With existing solutions we may end up with a list of 8 bytes
- With a custom solution we serialize it with only 1 byte 


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\p2p\node.md
Contenu:
# Node

ArchEthic is using a structured and open P2P network based on some properties:

## Structure and Authentication 
Each node know the entire list of nodes allowed to participate in the network through the use of Node transaction chains.
Therefore, each connection is encrypted and authenticated by the last node public key

A node include a list P2P information such as:
- IP
- Port
- P2P Protocol (i.e TCP)
- First public key
- Last public key
- GeoPatch (for geographical distribution based on the GeoIP of the IP)
- NetworkPatch (for P2P responsivness based on the latency to reach it)
- Reward address (the address where the mining rewards should be sent)
- Global availability (from BeaconChain qualification)
- Local availability (from Supervised Multicast)
- Average availability (from BeaconChain qualification)
- Authorized
- Authorization Date

## Permisionless:
Any node can participate into the network as long as they have some hardware requirements such secure element to enclave the private keys
avoiding any disclosure of keys. 
Currently we are supporting: TPM 2.0
But others providers will be available with the time

However the network decides by itself, if it needs for validation nodes.

## Remuneration

Each is node is remunerated according to the its contribution to the network:
- for validation
- for information provision during the validation

!> A node is not remunered to replicate a transaction but it will be when it makes the transactions available to the network for the next transaction processing

> However, if a validation node didn't receive enough a mining rewards during the month, the Network Pool (from the UCO distribution) will send compensation. <br />
<br />
For example: if a node receive 30$ equivalent UCO, and if the rules say the minimum should be 50$, then the network pool will send 20$ to this node. <br />
  if this node receive 100$ of mining rewards, the network pool will node send any UCO to this node.  


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\p2p\README.md
Contenu:
# P2P Layer

ArchEthic Blockchain redesigned the entire P2P layer to be more effective and support an unlimited permissionless network.

## Why do you need something new ?

In the current P2P and distributed networks, there are two methods of communication for discovery and data propagation: 
- the Gossip mode, whose properties are defined by the knowledge of the outgoing neighbors, which means each node of the network will discover the properties of the other nodes by interrogating them one by one, usually randomly, performing some unnecessary network traffic and sending data through nearest nodes for propagation.

- the Broadcast mode whose properties are defined by the knowledge of the incoming neighbors, which uses incoming connections and dispatch the data to all the nodes.

## Supervised Multicast

ArchEthic is using a hybrid communication that uses Supervised Multicast which is closer to the properties of Broadcast networks and combines the following properties:

> Transaction Replication Process: Capitalizing on incoming and outgoing con- nection information during the replication process

> Network Transaction Chains: Using transaction and consensus to attest when a node joins the network and is propaged throught all the nodes

> Beacons Chains: Which using snapshots and sampling of P2P availability and produce summaries each day to maintain a qualified vision of the network

> Data propogation: By using sharding and distributed replication, only the required nodes will receive information and use their bandwidth to transmit data through (avoiding a lot of traffic)



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\p2p\self_repair.md
Contenu:
# Self-Repair

ArchEthic Blockchain is using a self-repair mechanism to be able to sync/re-sync missing transactions to be able
<br />to restore the state of a node.

Because ArchEthic is using a multidimensional sharding, a node needs to execute a self-repair on multiple occasions, to ensure data availability and security:
- When the node bootstrap
- When a node goes offline
- When the code and heuristic algorithms changes

## Identification

To be able to determine which transactions are missing, foreach cycle of repair, a date of last sync is persisted.
Therefore, we can decide from this date, the list of missing BeaconChain transactions to sync. (Reminder: BeaconChain summaries transactions across the entire network each day)

The Self-Repair will then request BeaconChain storage pools to get the missing transactions from those missing days

## Synchronization

Because we are using rotating election, nodes need to perform the `Storage Node Election` to determine if they need to store this transaction.

In that case, we will get the list existing storages nodes from the transaction's address to sync and request from the closest nodes the transaction to be replicated.

Once finalized, a new last date of sync is persisted for the next cycle.



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\sharding\beacon_chain.md
Contenu:
# Beacon Chain
 
ArchEthic Blockchain is using `Sharding` mechanism to ensure scalability in term of storage and validation.
<br />
But since there is no way in a well sharded and distributed network to know all the transaction in the system,
a `Beacon Chain` is used to keep a global synchronization and reference.

## Concepts

`Beacon Chain` is used as tracer/marker of a global state but to face some scalability issue, ArchEthic Blockchain is using `Sharding` also for the `BeaconChain`.

Which means than the `Beacon Chain` is sharded and splitted into `subset` defined by the transaction's address and a given date.
<br />
By example: a transaction's address starting by `0F` at a given day, will not be stored on the same subset as a transaction's address starting by `9F` for the same day.


## Transaction tracking and timestamping

Each time a transaction is validated, the validation nodes will send the transaction to the right Beacon Chain storage nodes, to transmit the address of the transaction and its timestamp.

For each Beacon Chain interval, a new slot is generated referencing all the transaction during this interval.
<br />
At the end of the day, a transaction chain is formed and a last transaction is computed to generate a summary of the current day for a given subset.

Because each transaction has its own storage nodes, `Beacon Chains` are balanced between the storage nodes to ensure a better scalability and distribution.

## Status and Network Coordinates of nodes

Beacon Chains also contain network status of the nodes where the public key starts by the Beacon Chain subset.

The storage nodes in each subset is in charge of:
- check the nodes availability
- gather networking information such as latency, bandwidth

At the end of the day, a transaction is formed as well and a last transaction is compute to generate a summary of node availability and network coordinates

## Slot

Each `Beacon Chain` is splitted during the day into multiple slots, defined by interval (for instance every 10 min).
<br />Those slot contains the following information:
- Transaction summaries: timestamping of the validated transactions
  - address: Transaction's address
  - timestamp: Transaction validation time
  - movements addresses: List of outputs addresses of the transaction
- End of node synchronization: timestamping when a node finished its synchronization
  - node public key: Node's first public key
  - timestamp: Time when the node synchronization ended
- P2P view:
     - availabilities: binary form of the availability of the sampled nodes for the given subset
     - network statistics: latency and bandwidth of the sampled nodes for the given subset


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\sharding\README.md
Contenu:
# Sharding
 
To become a unlimited decentralized network, ArchEthic Blockchain is using a feature call `Sharding`
<br />
uses to split processing and storage power to ensure a scalable system.

Thanks to the `Transaction Chain` paradigm, transactions can be splitted into chain, to ensure a concurrent processing 
<br />
as the opposive of traditional blockchains.

Other new blockchain networks start to use `Sharding` but sometimes no in a complete form: 
- either storage
- either validation

ArchEthic Blockchain supports a complete shardind scheme for validation and for storage.

## Validation

Each transaction is validated by a new set of rotating nodes.
<br />
This ensure the distribution of validation and the processing, to achieve a linear scalability and a high TPS.

Because transaction are using the UTXO model, there is not reality out of the transaction, so the network is not subject to issue like :
- cross shards synchronization
- state channels communication

To get the state of a transaction, only the transaction and the transaction inputs will be taken into consideration

## Storage

After the validation of the transaction, validation nodes will be in charge to send the transaction to several pool of nodes:
- Transaction Chain Storage Pool: All the transaction associated with the same chain must be replicated on the storage nodes associated with the new transaction's address.
- I/O Storage Pool: Each validated transaction is replicated on the storage nodes associated with the addresses of the transaction input/outputs:
  - Transaction movements addresses storage pools
  - Node movements public key storage pools
  - Recipients addresses storage pools
- Beacon Storage Pool: Each transaction address must be replicated on the storage nodes of the associated address subset [See BeaconChain](/network/beacon_chain.md)

> For each transaction, the Transaction Chain Storage Pool will change, assuring a completed distribution of nodes and the data replication. Nevertheless, nothing prevents the storage nodes to overlap within the chain.

## Rotating Election

Like the validation nodes election, storage nodes election is subject to a rotating election.
<br />In other terms, each transaction will have its own shard and storage nodes.

The storage node election is based on:
- the address of the transaction
- the storage nonce: a stable secret known by the network
- the list of nodes

This permits any node to perform this computation autonomously to reproduce this list and to request transaction from the closest node.

To ensure the best availability of the data, this list is refined by some critierias such as:
- P2P availability
- Geographical distribution



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\smart_contract\examples.md
Contenu:
# Examples

## Recurrent transfer 

```
# Send 1.0 each to the given address
actions triggered_by: interval, at: "0 0 0 * *" do
  set_type transfer
  add_uco_transfer to: "0D574D171A484F8DEAC2D61FC3F7CC984BEB52465D69B3B5F670090742CBF5CC", amount: 1.0
end
```

## ICO / Crowdfunding

```

# Ensure the next transaction will be a transfer
condition inherit: [
  type: transfer,
  uco_transfers: size() == 1
  # TODO: to provide more security, we should check the destination address is within the previous transaction inputs 
]


actions triggered_by: transaction do
  # Get the amount of uco send to this contract
  amount_send = transaction.uco_transfers[contract.address]

  if amount_send > 0 do
      # Convert UCO to the number of tokens to credit. Each UCO worth 10000 token
      token_to_credit = amount_send * 10000 

      # Send the new transaction
      set_type transfer
      add_nft_transfer to: transaction.address, nft: contract.address, amount: token_to_credit
  end 
end
```


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\smart_contract\language.md
Contenu:
# Smart Contract Language

ArchEthic Blockchain defines a new smart contract language which was designed to resolve the issue of smart contracts:
- Expressivness
- Simplify
- Security

Along with the new features of ArchEthic Smart Contracts (triggers, conditions, actions), a new custom language is defined

## Triggers/Actions

To define a trigger, we need to specify an action block with its trigger type and the following parameters (if presents)

For example:

- based on an incoming transaction
```
actions triggered_by: transaction do
  # do something when a receive transaction
end
```

- based on time interval
```
actions triggered_by: interval, at: "0 8 * * *" do
  # do something each day at 8AM
end
```

## Conditions

To define a condition, we need to specify a condition block with its subject and the list conditions by fields:
- `type`
- `content`
- `code`
- `authorized_keys`
- `secret`
- `uco_transfers`
- `nft_transfers`
- `previous_public_key`
- `origin_family`

For example:

- expecting the incoming transaction contains the content "hello"
```
condition transaction: [
    content: "Hello"
]
```

- expecting all the transaction in the chain should be generated from a biometric device
```
condition inherit: [
    origin_family: biometric
]
```


## Global variables

Smart Contract can used global variable in the different blocks:
   - `contract`: represent the actual contract
   - `transaction`: incoming transaction
   - (inherit condition only) `next`: next transaction on the chain
   - (inherit condition only) `previous`: previous transactiono on the chain 

Each of this variables contains the following fields:
- `address`
- `type`
- `content`
- `code`
- `authorized_keys`
- `secret`
- `previous_public_key`
- `recipients`
- `uco_transfers`
- `nft_transfers`

## Functions

ArchEthic Smart Contracts relies on function which can be used on condition or action blocks.

There is two category of functions:
- Utilities
- Statements (for transaction generation)

### Utilities

?> In the `condition` block, if no parameter is given the transaction's field value will be the first one 

- `hash(data)`: Perform a cryptographic hash
```
condition transaction: [
    content: hash(contract.code)
]
```

- `regex_match?(data, pattern)`: Verify a regular expression
```
condition transaction: [
    content: regex_match?("hello")
]
````

- `regex_extract(data, pattern)`: Extract data from a regular expression

- json_match?: Verify the data matches a JSONPath expression
```
condition oracle: [
    content: json_match?("$.uco.usd")
]
```

- `json_extract(data, pattern)`: Extract data from a JSONPath expression
```
condition oracle: [
    content: json_extract("$.uco.usd") > 0.2
]
```

### Statements

- `set_type`: Set the transaction type
```
actions triggered_by: transaction do
    set_type transfer
end
```

- `add_uco_transfer`: Add a new UCO transfer
```
actions triggered_by: transaction do
    add_uco_transfer to: "F28C3D5B3828AD3F8682F1B1D14A8507B829F65F7BE6C50427A6019CCB6801C", amount: 1.0
end
```

- `add_nft_transfer`: Add a new NFT transfer
```
actions triggered_by: transaction do
    add_nft_transfer: to: "AF28C3D5B3828AD3F8682F1B1D14A8507B829F65F7BE6C50427A6019CCB6801C", nft: "0D574D171A484F8DEAC2D61FC3F7CC984BEB52465D69B3B5F670090742CBF5CC", amount: 1.0
end
```

- `set_content`: Set the new content
```
actions triggered_by: transaction do
    set_content "hello"
end
```

- `set_code`: Set the new code
```
actions triggered_by: transaction do
    set_code """
    actions triggered_by: transaction do
      add_uco_transfer to: "0D574D171A484F8DEAC2D61FC3F7CC984BEB52465D69B3B5F670090742CBF5CC", amount: 2.0
    end
    """
end
```

- `add_authorized_key`: Add an authorized public key
```
actions triggered_by: transaction do
    add_authorized_key public_key: "0D574D171A484F8DEAC2D61FC3F7CC984BEB52465D69B3B5F670090742CBF5CC", encrypted_secret_key: "...."
end
```

- `add_recipient`: Add a contract address to reach
````
actions triggered_by: datetime, at: 1391309030 do
    add_recipient "0D574D171A484F8DEAC2D61FC3F7CC984BEB52465D69B3B5F670090742CBF5CC"
end


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\smart_contract\README.md
Contenu:
# Smart Contracts <!-- {{docsify-ignore-all}} -->

*Smart-contracts are in computing what robots are in real life: they perform actions according to events.* 

ArchEthic Blockchain leverages next generation of smart contract to make the development of decentralized application easier to bring a mass adoption of the Blockchain technology.

They introduces new features to this domain:
- Completly autonomous and can be triggered from internal states (date, transactions) or real life (OracleChain updates).
- Entirely modifiable: TransactionChains make update seemless
- Interpreted: Code is interpreted and atomically verified by the miners
- Without external reality: They are entirely based on the UTXO model and do not depend on the state of an internal database but only the transactions validated

ArchEthic Smart Contract is defined by: `triggers`, `conditions` and `actions`

- Triggers: events will automatically launch the execution of a contracts.
- Conditions: define the rules to accept new transactions (chain or UTXO)
- Actions: operations to perform from a triggers calls

## Autonomous

ArchEthic smart contracts autonomous behavior is due to the capability to define different kind of triggers:
- Datetime: when the current date matches this timestamp
- Interval: when the current dates matches this cron interval scheduler
- Transaction: when the contract receive a transaction in input (UTXO model)
- Oracle: when the OracleChain pushed new data

!> Since smart contracts can autonomous and create transactions on the behalf of the owner, transaction should authorize nodes to use the cryptographic keys to generate transaction.
<br />Then the contract has to specify a `inherit conditions` to accept new changes

## Modifiable:

ArchEthic relies on TransactionChain which means than a smart contract can have its own transaction chain.

Then, it subject to the same properties of the transaction chain: any last transaction of a chain is considered as the reference.

For example:

We deployed a smart contract with the address `0D574D171A484F8DEAC2D61FC3F7CC984BEB52465D69B3B5F670090742CBF5CC`.

Then we want to add feature or to fix an issue, we resend a transaction on this chain and we get the new address: `AF28C3D5B3828AD3F8682F1B1D14A8507B829F65F7BE6C50427A6019CCB6801C`

But clients which depends on the smart contract don't need to update their code or interaction, as each destination address is forwarded to the last one.

So if we send transaction to `0D574D171A484F8DEAC2D61FC3F7CC984BEB52465D69B3B5F670090742CBF5CC`, the code executed will be at `AF28C3D5B3828AD3F8682F1B1D14A8507B829F65F7BE6C50427A6019CCB6801C`

?> Also, because we are not relying on internal state and database, and only with the UTXO, we do need to provide migrations of data or funds, and neither implement cross shard synchronization

## Interpreted

ArchEthic smart contracts are interpreted instead of compiled, here are the reasons:

- Interpreted code is understandable by the human, and compiled code are only understandable by the computer.

- Intepreted code makes the transparency and audit of smart contracts easier as we do need to provide the source of the contracts

- Interpreted code makes verification and safety checks better, instead to execute a code in blindness, miners can step by step verify the instructions and avoid any security issues

## Stateless

ArchEthic Smart Contracts does not depend on internal state or databases, only the UTXO is used as inputs, it's not possible to make a database with them.

For example

in an e-commerce smartcontract, the smart-contract issued by a merchant will be able to define stocks, prices and interactions with its customers using a view which is continuously updated by the nodes responsible for storing the smart-contract and based on transactions validated to that same smart-contract

The "UTXO" operation does not give a status within a smart-contract but allows it to be calculated (in the example above the merchant cannot directly query a smart-contract on the status of orders, but can verify the proven status of orders through validated transactions).

The experience of a user or a merchant is absolutely identical since each state is irrefutable and unambiguous.

However, if required, we could easily snapshot data during time to have faster reads for archived data

!> Any data processed within the contract which is not stored in the next transaction or send somewhere will be lost


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\7ed3338f5a8bc2608f879e2525d38b691f960b09\priv\static\docs\network\transaction_chain\README.md
Contenu:
# TransactionChain
 
In the ArchEthic network, there is not blocks but only transactions, as each block is reduced to its atomic form - `transaction` with its own validation evidences.

## Principles

> Each validated transaction is stored as a chain than can only be updated from the last validation transaction in the chain

> For security reason, once the public key is disclosed, it is considered as expired, only the hash of the public key of the next transaction(aka `address`) is announced.
<br />This allows the next public key to be kept until the next transaction on the chain.

> Any addresses of a transaction chain can be used as destination address.
<br /> It's not necessary to specify the last transaction address in the chain.

> Transaction are using an *UTXO* (Unspent Transaction Output) model so, a transaction cannot change state
<br />There is not reality outside the validated transactions

> List of unspent outputs does not need to be specified by the sender of the transaction
<br />all unspent outputs will be reintegrated directly into the last transaction.

> The last transaction on a chain becomes the *authoritative* transaction. 


## Transaction structure 

- ### Pending transaction

A pending transaction is a transaction that does not have validation.
Its structure is described as below:

```
|-----------|------|------|---------------------|--------------------|------------------|
|  Address  | Type | Data | Previous public key | Previous signature | Origin signature |
|-----------|------|------|---------------------|--------------------|------------------|
                      |      
                      |
      |---------|------|--------|------|------------|
      | Content | Code | Ledger | Keys | Recipients |
      |---------|------|--------|------|------------|
                            |      |
                            |      |
                  |-----|-----|  |-----------------|--------|  
                  | UCO | NFT |  | Authorized keys | Secret |
                  |-----|-----|  |-----------------|--------|                     
  

```


- Address: Corresponds to the hash of the public key of the transaction
- Type: Defines the functional role of the transaction
- Data: Containes all the operations to be performed (transfers, smart contracts, key authorizations, etc.)
   - Content: Can contains any kind of data. It can be used to host some data (html page, text, image, code, etc.) 
   - Code: Defines the smart contract code to be interpreted by the node. More details on [Smart-Contracts](/network/smart_contracts/) section.
   - Ledger: Defines several types of ledger operations
      - UCO: for the cryptocurrency transfers
      - NFT: for non financial transactions (intended for P2P uses - as tokens, loyalties, etc.)
      - Stock: to manage inventory of items (Will be available soon)
   - Keys: Define some cryptographic delegations
      - Authorized keys: list of authorized keys to be able to decrypt secret
      - Secret: Encrypt content which can be decrypted by the authorized key
   - Recipients: Additional recipients to target smart contracts
- Previous public key: Corresponds to the public key associated to the previous transaction
- Previous signature: Corresponds to the signature of the private key associated with the mentioned previous public key
- Origin signature: Corresponds to the signature of the device or software that generated the transaction. This is used on the [Proof Of Work](/network/arch/proof_of_work.md) mechanism and is a necessary condition of its validation.

- ### Validated transaction

A validated transaction is a pending transaction completed with the validation proofs required by the Heuristic Algorithms. 
Those are defined by the given structure:

```
|------------------|-------------------------|
| Validation Stamp | Cross Validation Stamps |
|------------------|-------------------------|
         |                      |
         |             |-----------------|-----------|
         |             | Node public key | Signature |     
         |             |-----------------|-----------|
         |
|-----------|---------------|--------------------|-------------------|-------------------|------------|--------|-----------|
| Timestamp | Proof of Work | Proof of Integrity | Proof of Election | Ledger Operations | Recipients | Errors | Signature |
|-----------|---------------|--------------------|-------------------|-------------------|------------|--------|-----------|
                                                                           |
                                 |-----|-----------------------|----------------|-----------------|
                                 | Fee | Transaction movements | Node movements | Unspent outputs |
                                 |-----|-----------------------|----------------|-----------------|

```

- Validation Stamp: Stamp generated by the coordinator node
  - Proof of work: Corresponds to the public key matching the origin signature (More details on the [Proof of Work](/network/arch/proof_of_work.md) section).
  - Proof of integrity: Proves the the linkage of the previous transactions
  - Proof of election: Proves the validation nodes rotating election and permit to reproduce it later (See [Rotating Election](/network/arch/?id=rotating-election))
  - Ledger operations: Contains all the ledger operations that will be taken into account by the network
    - fee: Transaction's fee
    - transaction movements: Issuer and resolved transaction movements
    - Node movements: Effective payment of the nodes invovled during the validation
    - Unspent outputs: List of the remaning unspent outputs of the transaction chain after validation
  - Recipients: List of resolved addreses of the recipients
  - Errors: Any errors found in the validation (ie. pending transaction error)
  - Signature: Cryptographic signature of the entire stamp by the coordinator's key
- Cross validation stamps: To be considered as valid, the `Validation Stamp` must be joined as many `Cross Validation Stamp` as required by the Heuristic Algorithms. 
  They are signatures of the given validation stamp.
  - Node public key: Correspond to the node's public key which generate this `Cross Validation Stamp`'s signature
  - Signature: Correspond to the signature of the `Cross Validation Stamp` for the mentioned public key
  - Inconsistencies: In case of inconsistencies or disagreement, it will contain a list of inconsistencies noted





Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\8f9f18b4c2b607d216dcad614a06bd78bd667d4b\apps\uniris_shared_secrets\README.md
Contenu:
# UnirisSharedSecrets

**TODO: Add description**

## Installation

If [available in Hex](https://hex.pm/docs/publish), the package can be installed
by adding `uniris_shared_secrets` to your list of dependencies in `mix.exs`:

```elixir
def deps do
  [
    {:uniris_shared_secrets, "~> 0.1.0"}
  ]
end
```

Documentation can be generated with [ExDoc](https://github.com/elixir-lang/ex_doc)
and published on [HexDocs](https://hexdocs.pm). Once published, the docs can
be found at [https://hexdocs.pm/uniris_shared_secrets](https://hexdocs.pm/uniris_shared_secrets).



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\91941644a8eea20d46d52cd583e9e13e296e229f\priv\static\docs\development\sdk\dart.md
Contenu:
# Dart SDK

ArchEthic Blockchain Officel Dart SDK available on [Github](https://github.com/archethic-foundation/libdart)

---

This SDK will help you to generate transaction on top of ArchEthic Blockchain.

> Stay tuned for more updates


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\91941644a8eea20d46d52cd583e9e13e296e229f\priv\static\docs\development\sdk\js.md
Contenu:
# Javascript SDK

ArchEthic Offical Javascript SDK is available on [Github](https://github.com/archethic-foundation/libjs)

---

This SDK will help you to generate transaction on top of ArchEthic Blockchain.

> Stay tuned for more updates


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\91941644a8eea20d46d52cd583e9e13e296e229f\priv\static\docs\development\testnet\public.md
Contenu:
# Public Testnet

Coming Soon...


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\d31f735aab102bd9a27178d0ebd41fdea95f9459\apps\uniris_p2p_server\README.md
Contenu:
# Uniris P2P Server


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\ddfd334469bc2d3ed4d96f7717c3597671955133\apps\uniris_web\README.md
Contenu:
# UnirisWeb

To start your Phoenix server:

  * Install dependencies with `mix deps.get`
  * Start Phoenix endpoint with `mix phx.server`

Now you can visit [`localhost:4000`](http://localhost:4000) from your browser.

Ready to run in production? Please [check our deployment guides](https://hexdocs.pm/phoenix/deployment.html).

## Learn more

  * Official website: https://www.phoenixframework.org/
  * Guides: https://hexdocs.pm/phoenix/overview.html
  * Docs: https://hexdocs.pm/phoenix
  * Forum: https://elixirforum.com/c/phoenix-forum
  * Source: https://github.com/phoenixframework/phoenix


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\develop\CODE_OF_CONDUCT.md
Contenu:
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the
  overall community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or
  advances of any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email
  address, without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community include using an official e-mail address,
posting via an official social media account, or acting as an appointed
representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
ethic@archethic.net.
All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact**: A violation through a single incident or series
of actions.

**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved, including unsolicited interaction with
those enforcing the Code of Conduct, for a specified period of time. This
includes avoiding interactions in community spaces as well as external channels
like social media. Violating these terms may lead to a temporary or
permanent ban.

### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including
sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior,  harassment of an
individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within
the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.0, available at
https://www.contributor-covenant.org/version/2/0/code_of_conduct.html.

Community Impact Guidelines were inspired by [Mozilla's code of conduct
enforcement ladder](https://github.com/mozilla/diversity).

[homepage]: https://www.contributor-covenant.org

For answers to common questions about this code of conduct, see the FAQ at
https://www.contributor-covenant.org/faq. Translations are available at
https://www.contributor-covenant.org/translations.


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\develop\CONTRIBUTING.md
Contenu:
# Contributing

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to ARCHEthic node which is hosted in the [ARCHEthic Foundation](https://github.com/archethic-foundation) on GitHub. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[I don't want to read this whole thing, I just have a question!!!](#i-dont-want-to-read-this-whole-thing-i-just-have-a-question)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)
     * [Git Commit Messages](#git-commit-messages)


## Code of Conduct

This project and everyone participating in it is governed by the [ARCHEthic code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## I don't want to read this whole thing I just have a question!!!

> **Note:** Please don't file an issue to ask a question.

We have an official message board with a detailed FAQ and where the community chimes in with helpful advice if you have questions.

* [Github Discussions](https://github.com/archethic-foundation/archethic-node/discussions)
* [ARCHEthic Website](https://archethic.net)

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for ARCHEthic node. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report). Fill out [the required template](https://github.com/archethic-foundation/.github/blob/master/.github/ISSUE_TEMPLATE/bug_report.yml), the information it asks for helps us resolve issues faster.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

#### Before Submitting A Bug Report

* **Check the [discussions](https://github.com/archethic-foundation/archethic-node/discussions)** for a list of common questions and problems.
* **Check the [issue list](https://github.com/archethic-foundation/archethic-node/issues)** if it has been already opened.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/) and create an issue on that repository and provide the following information by filling in [the template](https://github.com/archethic-foundation/.github/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml).

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible. When listing steps, **don't just say what you did, but explain how you did it**.
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples. If you're providing snippets in the issue, use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **If you're reporting a crash**, include a crash report with a stack trace. nclude the crash report in the issue in a [code block](https://help.github.com/articles/markdown-basics/#multiple-lines), a [file attachment](https://help.github.com/articles/file-attachments-on-issues-and-pull-requests/), or put it in a [gist](https://gist.github.com/) and provide link to that gist.
* **If the problem is related to performance or memory**, include a screenshot of the `observer`
* **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened and share more information using the guidelines below.

Provide more context by answering these questions:

* **Did the problem start happening recently** (e.g. after updating to a new version) or was this always a problem?
* If the problem started happening recently, **can you reproduce the problem in an older version of the node?** What's the most recent version in which the problem doesn't happen?
* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for ARCHEThic node, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.

Before creating enhancement suggestions, please check [this list](#before-submitting-an-enhancement-suggestion) as you might find out that you don't need to create one. When you are creating an enhancement suggestion, please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion). Fill in [the template](https://github.com/archethic-foundation/.github/blob/master/.github/ISSUE_TEMPLATE/feature_request.yml), including the steps that you imagine you would take if the feature you're requesting existed.

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/) and create an issue on that repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a detailed description of the suggested enhancement** in as many details as possible.
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Explain why this enhancement would be useful** .

### Your First Code Contribution

Unsure where to begin contributing to Atom? You can start by looking through these `beginner` and `help-wanted` issues:

* [Beginner issues][beginner] - issues which should only require a few lines of code, and a test or two.
* [Help wanted issues][help-wanted] - issues which should be a bit more involved than `beginner` issues.

Both issue lists are sorted by total number of comments. While not perfect, number of comments is a reasonable proxy for impact a given change will have.

### Pull Requests

The process described here has several goals:

- Maintain ARCHEthic node's quality
- Fix problems that are important
- Enable a sustainable system for ARCHEthic's maintainers to review contributions

#### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :non-potable_water: `:non-potable_water:` when plugging memory leaks
    * :memo: `:memo:` when writing docs
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\develop\README.md
Contenu:
# Archethic

Welcome to the Archethic Node source repository ! This software enables you to build the first transaction chain and next generation of blockchain focused on scalability and human oriented.

Archethic features:

- Fast transaction processing (> 1M tps)
- Lower energy consumption than other blockchain
- Designed with a high level of security (ARCH consensus supporting 90% of maliciousness)
- Adaptive cryptographic algorithms (quantum resistant)
- Decentralized Identity and Self Sovereign Identity
- Smart contract platform powered by a built-in interpreter
- Strong scalability with geo secured sharding
- Soft-Real-Time P2P view with supervised networking

## Development

Our codebase aims to reach the guidelines of Elixir projects.
We are focusing on the best quality.

The source code can change to respect the best quality of reading and regarding best practices.

Current implemented features:

- Adaptive cryptography: different elliptic curves and software implementation
- Hybrid root of trust: mix of hardware and software cryptographic key to maintain trust and security
- TransactionChain: Transaction structure and transaction generation
- Smart Contract: interpreter coded with Elixir DSL through Meta-programming and AST
- Node election: heuristic validation and storage node selection
- P2P: Inter-node communication, supervised connection to detect the P2P view of nodes in almost real-time
- Transaction mining: ARCH consensus
- Beacon chain: Maintains a global view of the network (transactions, P2P view)
- Self-Repair: Self-healing mechanism allowing to resynchronize missing transactions
- Embedded explorer leveraging sharding to retrieve information
- Custom Binary protocol for data transmission
- Token minting
- Internal oracles (UCO Price Feed)
- Tailored embedded database

## Running a node for development purpose

### Using Elixir - MacOS specific setups

On Apple Silicon architecture, you might encounter issues running nodes.

Here is how to make it work.

#### Install openssl using brew

```sh
brew install openssl@3
```

#### Install erlang using `asdf`

```sh
cd <project_directory>
KERL_CONFIGURE_OPTIONS="--disable-jit --without-javac --without-wx --with-ssl=$(brew --prefix openssl@3)" asdf install
```

#### Locally update `exla` dependency

Edit `mix.exs` and replace the following `deps` item :

```elixir
      {:exla, "~> 0.5"},
```

by

```elixir
      {:exla, "~> 0.5.3"},
```

Then, install dependencies as usual :

```sh
mix deps.get
```

#### 🎉 You can run the node as usual

```sh
iex -S mix
```

### Using Elixir

Requirements:

- Libsodium: for the ed25519 to Curve25519 conversion
- OpenSSL 1.11
- Erlang OTP 25
- Elixir 1.14
- GMP (https://gmplib.org/)
- MiniUPnP used for port forwarding & IP lookup (https://miniupnp.tuxfamily.org/)
- Npm for static assets (https://nodejs.org/en/download)

Platforms supported:

- Linux (Ubuntu 18.04)
- Mac OS X ([See specific setups](#using-elixir---macos-specific-setups))

At first, clone the repository:

```bash
git clone https://github.com/archethic-foundation/archethic-node.git
cd archethic-node
```

Get dependencies:

```bash
mix deps.get
```

Install the static assets

```
cd assets ; npm install; cd -
```

To start a single node:

```bash
iex -S mix
```

To clean the data

```bash
make clean
```

To start mutiple node, you need to update some environment variables:

```bash
# Start the first node
iex -S mix

# Start second node
ARCHETHIC_CRYPTO_SEED=node2 ARCHETHIC_P2P_PORT=3003 ARCHETHIC_HTTP_PORT=4001 ARCHETHIC_HTTPS_PORT=5001 iex -S mix

# To start other node, increment the environment variables
```

### Using docker

Requires docker compose plugin

At first, clone the repository:

```bash
git clone https://github.com/archethic-foundation/archethic-node.git
cd archethic-node
```

Build the image:

```bash
docker build -t archethic-node .
```

To start a single node:

```bash
# You can run node up to node3
docker compose up node1
docker compose up node2
docker compose up node3
```

To start all nodes at the same time:

```bash
docker compose up
```

To run benchmarks:

```bash
docker compose up bench
```

To run the playbooks to validate non regression:

```bash
docker compose up validate
```

### Using snap

Work in progress ..

## Running a node for testnet / mainnet

Will be opened regarding roadmap advancement

## Contribution

Thank you for considering to help out with the source code.
We welcome contributions from anyone and are grateful for even the smallest of improvement.

Please to follow this workflow:

1. Fork it!
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create new Pull Request

## Licence

AGPL


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\meta\archethic-node_main_CODE_OF_CONDUCT.md
Contenu:
# Contributor Covenant Code of Conduct



## Our Pledge



We as members, contributors, and leaders pledge to make participation in our

community a harassment-free experience for everyone, regardless of age, body

size, visible or invisible disability, ethnicity, sex characteristics, gender

identity and expression, level of experience, education, socio-economic status,

nationality, personal appearance, race, religion, or sexual identity

and orientation.



We pledge to act and interact in ways that contribute to an open, welcoming,

diverse, inclusive, and healthy community.



## Our Standards



Examples of behavior that contributes to a positive environment for our

community include:



* Demonstrating empathy and kindness toward other people

* Being respectful of differing opinions, viewpoints, and experiences

* Giving and gracefully accepting constructive feedback

* Accepting responsibility and apologizing to those affected by our mistakes,

  and learning from the experience

* Focusing on what is best not just for us as individuals, but for the

  overall community



Examples of unacceptable behavior include:



* The use of sexualized language or imagery, and sexual attention or

  advances of any kind

* Trolling, insulting or derogatory comments, and personal or political attacks

* Public or private harassment

* Publishing others' private information, such as a physical or email

  address, without their explicit permission

* Other conduct which could reasonably be considered inappropriate in a

  professional setting



## Enforcement Responsibilities



Community leaders are responsible for clarifying and enforcing our standards of

acceptable behavior and will take appropriate and fair corrective action in

response to any behavior that they deem inappropriate, threatening, offensive,

or harmful.



Community leaders have the right and responsibility to remove, edit, or reject

comments, commits, code, wiki edits, issues, and other contributions that are

not aligned to this Code of Conduct, and will communicate reasons for moderation

decisions when appropriate.



## Scope



This Code of Conduct applies within all community spaces, and also applies when

an individual is officially representing the community in public spaces.

Examples of representing our community include using an official e-mail address,

posting via an official social media account, or acting as an appointed

representative at an online or offline event.



## Enforcement



Instances of abusive, harassing, or otherwise unacceptable behavior may be

reported to the community leaders responsible for enforcement at

ethic@archethic.net.

All complaints will be reviewed and investigated promptly and fairly.



All community leaders are obligated to respect the privacy and security of the

reporter of any incident.



## Enforcement Guidelines



Community leaders will follow these Community Impact Guidelines in determining

the consequences for any action they deem in violation of this Code of Conduct:



### 1. Correction



**Community Impact**: Use of inappropriate language or other behavior deemed

unprofessional or unwelcome in the community.



**Consequence**: A private, written warning from community leaders, providing

clarity around the nature of the violation and an explanation of why the

behavior was inappropriate. A public apology may be requested.



### 2. Warning



**Community Impact**: A violation through a single incident or series

of actions.



**Consequence**: A warning with consequences for continued behavior. No

interaction with the people involved, including unsolicited interaction with

those enforcing the Code of Conduct, for a specified period of time. This

includes avoiding interactions in community spaces as well as external channels

like social media. Violating these terms may lead to a temporary or

permanent ban.



### 3. Temporary Ban



**Community Impact**: A serious violation of community standards, including

sustained inappropriate behavior.



**Consequence**: A temporary ban from any sort of interaction or public

communication with the community for a specified period of time. No public or

private interaction with the people involved, including unsolicited interaction

with those enforcing the Code of Conduct, is allowed during this period.

Violating these terms may lead to a permanent ban.



### 4. Permanent Ban



**Community Impact**: Demonstrating a pattern of violation of community

standards, including sustained inappropriate behavior,  harassment of an

individual, or aggression toward or disparagement of classes of individuals.



**Consequence**: A permanent ban from any sort of public interaction within

the community.



## Attribution



This Code of Conduct is adapted from the [Contributor Covenant][homepage],

version 2.0, available at

https://www.contributor-covenant.org/version/2/0/code_of_conduct.html.



Community Impact Guidelines were inspired by [Mozilla's code of conduct

enforcement ladder](https://github.com/mozilla/diversity).



[homepage]: https://www.contributor-covenant.org



For answers to common questions about this code of conduct, see the FAQ at

https://www.contributor-covenant.org/faq. Translations are available at

https://www.contributor-covenant.org/translations.



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\meta\archethic-node_main_CONTRIBUTING.md
Contenu:
# Contributing



:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:



The following is a set of guidelines for contributing to ARCHEthic node which is hosted in the [ARCHEthic Foundation](https://github.com/archethic-foundation) on GitHub. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.



#### Table Of Contents



[Code of Conduct](#code-of-conduct)



[I don't want to read this whole thing, I just have a question!!!](#i-dont-want-to-read-this-whole-thing-i-just-have-a-question)



[How Can I Contribute?](#how-can-i-contribute)

  * [Reporting Bugs](#reporting-bugs)

  * [Suggesting Enhancements](#suggesting-enhancements)

  * [Your First Code Contribution](#your-first-code-contribution)

  * [Pull Requests](#pull-requests)

     * [Git Commit Messages](#git-commit-messages)





## Code of Conduct



This project and everyone participating in it is governed by the [ARCHEthic code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.



## I don't want to read this whole thing I just have a question!!!



> **Note:** Please don't file an issue to ask a question.



We have an official message board with a detailed FAQ and where the community chimes in with helpful advice if you have questions.



* [Github Discussions](https://github.com/archethic-foundation/archethic-node/discussions)

* [ARCHEthic Website](https://archethic.net)



## How Can I Contribute?



### Reporting Bugs



This section guides you through submitting a bug report for ARCHEthic node. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.



Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report). Fill out [the required template](https://github.com/archethic-foundation/.github/blob/master/.github/ISSUE_TEMPLATE/bug_report.yml), the information it asks for helps us resolve issues faster.



> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.



#### Before Submitting A Bug Report



* **Check the [discussions](https://github.com/archethic-foundation/archethic-node/discussions)** for a list of common questions and problems.

* **Check the [issue list](https://github.com/archethic-foundation/archethic-node/issues)** if it has been already opened.



#### How Do I Submit A (Good) Bug Report?



Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/) and create an issue on that repository and provide the following information by filling in [the template](https://github.com/archethic-foundation/.github/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml).



Explain the problem and include additional details to help maintainers reproduce the problem:



* **Use a clear and descriptive title** for the issue to identify the problem.

* **Describe the exact steps which reproduce the problem** in as many details as possible. When listing steps, **don't just say what you did, but explain how you did it**.

* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples. If you're providing snippets in the issue, use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).

* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.

* **Explain which behavior you expected to see instead and why.**

* **If you're reporting a crash**, include a crash report with a stack trace. nclude the crash report in the issue in a [code block](https://help.github.com/articles/markdown-basics/#multiple-lines), a [file attachment](https://help.github.com/articles/file-attachments-on-issues-and-pull-requests/), or put it in a [gist](https://gist.github.com/) and provide link to that gist.

* **If the problem is related to performance or memory**, include a screenshot of the `observer`

* **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened and share more information using the guidelines below.



Provide more context by answering these questions:



* **Did the problem start happening recently** (e.g. after updating to a new version) or was this always a problem?

* If the problem started happening recently, **can you reproduce the problem in an older version of the node?** What's the most recent version in which the problem doesn't happen?

* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens.



### Suggesting Enhancements



This section guides you through submitting an enhancement suggestion for ARCHEThic node, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.



Before creating enhancement suggestions, please check [this list](#before-submitting-an-enhancement-suggestion) as you might find out that you don't need to create one. When you are creating an enhancement suggestion, please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion). Fill in [the template](https://github.com/archethic-foundation/.github/blob/master/.github/ISSUE_TEMPLATE/feature_request.yml), including the steps that you imagine you would take if the feature you're requesting existed.



#### How Do I Submit A (Good) Enhancement Suggestion?



Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/) and create an issue on that repository and provide the following information:



* **Use a clear and descriptive title** for the issue to identify the suggestion.

* **Provide a detailed description of the suggested enhancement** in as many details as possible.

* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.

* **Explain why this enhancement would be useful** .



### Your First Code Contribution



Unsure where to begin contributing to Atom? You can start by looking through these `beginner` and `help-wanted` issues:



* [Beginner issues][beginner] - issues which should only require a few lines of code, and a test or two.

* [Help wanted issues][help-wanted] - issues which should be a bit more involved than `beginner` issues.



Both issue lists are sorted by total number of comments. While not perfect, number of comments is a reasonable proxy for impact a given change will have.



### Pull Requests



The process described here has several goals:



- Maintain ARCHEthic node's quality

- Fix problems that are important

- Enable a sustainable system for ARCHEthic's maintainers to review contributions



#### Git Commit Messages



* Use the present tense ("Add feature" not "Added feature")

* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")

* Limit the first line to 72 characters or less

* Reference issues and pull requests liberally after the first line

* Consider starting the commit message with an applicable emoji:

    * :art: `:art:` when improving the format/structure of the code

    * :racehorse: `:racehorse:` when improving performance

    * :non-potable_water: `:non-potable_water:` when plugging memory leaks

    * :memo: `:memo:` when writing docs

    * :bug: `:bug:` when fixing a bug

    * :fire: `:fire:` when removing code or files

    * :white_check_mark: `:white_check_mark:` when adding tests

    * :lock: `:lock:` when dealing with security

    * :arrow_up: `:arrow_up:` when upgrading dependencies

    * :arrow_down: `:arrow_down:` when downgrading dependencies

    * :shirt: `:shirt:` when removing linter warnings





Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\meta\archethic-node_main_README.md
Contenu:
# Archethic



Welcome to the Archethic Node source repository ! This software enables you to build the first transaction chain and next generation of blockchain focused on scalability and human oriented.



Archethic features:



- Fast transaction processing (> 1M tps)

- Lower energy consumption than other blockchain

- Designed with a high level of security (ARCH consensus supporting 90% of maliciousness)

- Adaptive cryptographic algorithms (quantum resistant)

- Decentralized Identity and Self Sovereign Identity

- Smart contract platform powered by a built-in interpreter

- Strong scalability with geo secured sharding

- Soft-Real-Time P2P view with supervised networking



## Development



Our codebase aims to reach the guidelines of Elixir projects.

We are focusing on the best quality.



The source code can change to respect the best quality of reading and regarding best practices.



Current implemented features:



- Adaptive cryptography: different elliptic curves and software implementation

- Hybrid root of trust: mix of hardware and software cryptographic key to maintain trust and security

- TransactionChain: Transaction structure and transaction generation

- Smart Contract: interpreter coded with Elixir DSL through Meta-programming and AST

- Node election: heuristic validation and storage node selection

- P2P: Inter-node communication, supervised connection to detect the P2P view of nodes in almost real-time

- Transaction mining: ARCH consensus

- Beacon chain: Maintains a global view of the network (transactions, P2P view)

- Self-Repair: Self-healing mechanism allowing to resynchronize missing transactions

- Embedded explorer leveraging sharding to retrieve information

- Custom Binary protocol for data transmission

- Token minting

- Internal oracles (UCO Price Feed)

- Tailored embedded database



## Running a node for development purpose



### Using Elixir - MacOS specific setups



On Apple Silicon architecture, you might encounter issues running nodes.



Here is how to make it work.



#### Install openssl using brew



```sh

brew install openssl@3

```



#### Install erlang using `asdf`



```sh

cd <project_directory>

KERL_CONFIGURE_OPTIONS="--disable-jit --without-javac --without-wx --with-ssl=$(brew --prefix openssl@3)" asdf install

```



#### Locally update `exla` dependency



Edit `mix.exs` and replace the following `deps` item :



```elixir

      {:exla, "~> 0.5"},

```



by



```elixir

      {:exla, "~> 0.5.3"},

```



Then, install dependencies as usual :



```sh

mix deps.get

```



#### 🎉 You can run the node as usual



```sh

iex -S mix

```



### Using Elixir



Requirements:



- Libsodium: for the ed25519 to Curve25519 conversion

- OpenSSL 1.11

- Erlang OTP 25

- Elixir 1.14

- GMP (https://gmplib.org/)

- MiniUPnP used for port forwarding & IP lookup (https://miniupnp.tuxfamily.org/)

- Npm for static assets (https://nodejs.org/en/download)



Platforms supported:



- Linux (Ubuntu 18.04)

- Mac OS X ([See specific setups](#using-elixir---macos-specific-setups))



At first, clone the repository:



```bash

git clone https://github.com/archethic-foundation/archethic-node.git

cd archethic-node

```



Get dependencies:



```bash

mix deps.get

```



Install the static assets



```

cd assets ; npm install; cd -

```



To start a single node:



```bash

iex -S mix

```



To clean the data



```bash

make clean

```



To start mutiple node, you need to update some environment variables:



```bash

# Start the first node

iex -S mix



# Start second node

ARCHETHIC_CRYPTO_SEED=node2 ARCHETHIC_P2P_PORT=3003 ARCHETHIC_HTTP_PORT=4001 ARCHETHIC_HTTPS_PORT=5001 iex -S mix



# To start other node, increment the environment variables

```



### Using docker



Requires docker compose plugin



At first, clone the repository:



```bash

git clone https://github.com/archethic-foundation/archethic-node.git

cd archethic-node

```



Build the image:



```bash

docker build -t archethic-node .

```



To start a single node:



```bash

# You can run node up to node3

docker compose up node1

docker compose up node2

docker compose up node3

```



To start all nodes at the same time:



```bash

docker compose up

```



To run benchmarks:



```bash

docker compose up bench

```



To run the playbooks to validate non regression:



```bash

docker compose up validate

```



### Using snap



Work in progress ..



## Running a node for testnet / mainnet



Will be opened regarding roadmap advancement



## Contribution



Thank you for considering to help out with the source code.

We welcome contributions from anyone and are grateful for even the smallest of improvement.



Please to follow this workflow:



1. Fork it!

2. Create your feature branch (git checkout -b my-new-feature)

3. Commit your changes (git commit -am 'Add some feature')

4. Push to the branch (git push origin my-new-feature)

5. Create new Pull Request



## Licence



AGPL



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\meta\pull_request_template.md
Contenu:
# Description



Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context. List any dependencies that are required for this change.



Fixes # (issue)



## Type of change



Please delete options that are not relevant.



- Bug fix (non-breaking change which fixes an issue)

- New feature (non-breaking change which adds functionality)

- Breaking change (fix or feature that would cause existing functionality to not work as expected)

- This change requires a documentation update



# How Has This Been Tested?



Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration



- Test A

- Test B



# Checklist:



- My code follows the style guidelines of this project

- I have performed a self-review of my own code

- I have commented my code, particularly in hard-to-understand areas

- I have made corresponding changes to the documentation

- My changes generate no new warnings

- I have added tests that prove my fix is effective or that my feature works

- New and existing unit tests pass locally with my changes

- Any dependent changes have been merged and published in downstream modules



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\v1.6.4\CODE_OF_CONDUCT.md
Contenu:
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming,
diverse, inclusive, and healthy community.

## Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes,
  and learning from the experience
* Focusing on what is best not just for us as individuals, but for the
  overall community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or
  advances of any kind
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or email
  address, without their explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

## Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

Community leaders have the right and responsibility to remove, edit, or reject
comments, commits, code, wiki edits, issues, and other contributions that are
not aligned to this Code of Conduct, and will communicate reasons for moderation
decisions when appropriate.

## Scope

This Code of Conduct applies within all community spaces, and also applies when
an individual is officially representing the community in public spaces.
Examples of representing our community include using an official e-mail address,
posting via an official social media account, or acting as an appointed
representative at an online or offline event.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
ethic@archethic.net.
All complaints will be reviewed and investigated promptly and fairly.

All community leaders are obligated to respect the privacy and security of the
reporter of any incident.

## Enforcement Guidelines

Community leaders will follow these Community Impact Guidelines in determining
the consequences for any action they deem in violation of this Code of Conduct:

### 1. Correction

**Community Impact**: Use of inappropriate language or other behavior deemed
unprofessional or unwelcome in the community.

**Consequence**: A private, written warning from community leaders, providing
clarity around the nature of the violation and an explanation of why the
behavior was inappropriate. A public apology may be requested.

### 2. Warning

**Community Impact**: A violation through a single incident or series
of actions.

**Consequence**: A warning with consequences for continued behavior. No
interaction with the people involved, including unsolicited interaction with
those enforcing the Code of Conduct, for a specified period of time. This
includes avoiding interactions in community spaces as well as external channels
like social media. Violating these terms may lead to a temporary or
permanent ban.

### 3. Temporary Ban

**Community Impact**: A serious violation of community standards, including
sustained inappropriate behavior.

**Consequence**: A temporary ban from any sort of interaction or public
communication with the community for a specified period of time. No public or
private interaction with the people involved, including unsolicited interaction
with those enforcing the Code of Conduct, is allowed during this period.
Violating these terms may lead to a permanent ban.

### 4. Permanent Ban

**Community Impact**: Demonstrating a pattern of violation of community
standards, including sustained inappropriate behavior,  harassment of an
individual, or aggression toward or disparagement of classes of individuals.

**Consequence**: A permanent ban from any sort of public interaction within
the community.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage],
version 2.0, available at
https://www.contributor-covenant.org/version/2/0/code_of_conduct.html.

Community Impact Guidelines were inspired by [Mozilla's code of conduct
enforcement ladder](https://github.com/mozilla/diversity).

[homepage]: https://www.contributor-covenant.org

For answers to common questions about this code of conduct, see the FAQ at
https://www.contributor-covenant.org/faq. Translations are available at
https://www.contributor-covenant.org/translations.


Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\v1.6.4\CONTRIBUTING.md
Contenu:
# Contributing

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to ARCHEthic node which is hosted in the [ARCHEthic Foundation](https://github.com/archethic-foundation) on GitHub. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

#### Table Of Contents

[Code of Conduct](#code-of-conduct)

[I don't want to read this whole thing, I just have a question!!!](#i-dont-want-to-read-this-whole-thing-i-just-have-a-question)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)
     * [Git Commit Messages](#git-commit-messages)


## Code of Conduct

This project and everyone participating in it is governed by the [ARCHEthic code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## I don't want to read this whole thing I just have a question!!!

> **Note:** Please don't file an issue to ask a question.

We have an official message board with a detailed FAQ and where the community chimes in with helpful advice if you have questions.

* [Github Discussions](https://github.com/archethic-foundation/archethic-node/discussions)
* [ARCHEthic Website](https://archethic.net)

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for ARCHEthic node. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

Before creating bug reports, please check [this list](#before-submitting-a-bug-report) as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report). Fill out [the required template](https://github.com/archethic-foundation/.github/blob/master/.github/ISSUE_TEMPLATE/bug_report.yml), the information it asks for helps us resolve issues faster.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.

#### Before Submitting A Bug Report

* **Check the [discussions](https://github.com/archethic-foundation/archethic-node/discussions)** for a list of common questions and problems.
* **Check the [issue list](https://github.com/archethic-foundation/archethic-node/issues)** if it has been already opened.

#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/) and create an issue on that repository and provide the following information by filling in [the template](https://github.com/archethic-foundation/.github/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml).

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible. When listing steps, **don't just say what you did, but explain how you did it**.
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples. If you're providing snippets in the issue, use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **If you're reporting a crash**, include a crash report with a stack trace. nclude the crash report in the issue in a [code block](https://help.github.com/articles/markdown-basics/#multiple-lines), a [file attachment](https://help.github.com/articles/file-attachments-on-issues-and-pull-requests/), or put it in a [gist](https://gist.github.com/) and provide link to that gist.
* **If the problem is related to performance or memory**, include a screenshot of the `observer`
* **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened and share more information using the guidelines below.

Provide more context by answering these questions:

* **Did the problem start happening recently** (e.g. after updating to a new version) or was this always a problem?
* If the problem started happening recently, **can you reproduce the problem in an older version of the node?** What's the most recent version in which the problem doesn't happen?
* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for ARCHEThic node, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.

Before creating enhancement suggestions, please check [this list](#before-submitting-an-enhancement-suggestion) as you might find out that you don't need to create one. When you are creating an enhancement suggestion, please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion). Fill in [the template](https://github.com/archethic-foundation/.github/blob/master/.github/ISSUE_TEMPLATE/feature_request.yml), including the steps that you imagine you would take if the feature you're requesting existed.

#### How Do I Submit A (Good) Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/) and create an issue on that repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a detailed description of the suggested enhancement** in as many details as possible.
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Explain why this enhancement would be useful** .

### Your First Code Contribution

Unsure where to begin contributing to Atom? You can start by looking through these `beginner` and `help-wanted` issues:

* [Beginner issues][beginner] - issues which should only require a few lines of code, and a test or two.
* [Help wanted issues][help-wanted] - issues which should be a bit more involved than `beginner` issues.

Both issue lists are sorted by total number of comments. While not perfect, number of comments is a reasonable proxy for impact a given change will have.

### Pull Requests

The process described here has several goals:

- Maintain ARCHEthic node's quality
- Fix problems that are important
- Enable a sustainable system for ARCHEthic's maintainers to review contributions

#### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :non-potable_water: `:non-potable_water:` when plugging memory leaks
    * :memo: `:memo:` when writing docs
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings



Fichier: rag_builder\local_storage\archethic-foundation_archethic-node\v1.6.4\README.md
Contenu:
# Archethic

Welcome to the Archethic Node source repository ! This software enables you to build the first transaction chain and next generation of blockchain focused on scalability and human oriented.

Archethic features:

- Fast transaction processing (> 1M tps)
- Lower energy consumption than other blockchain
- Designed with a high level of security (ARCH consensus supporting 90% of maliciousness)
- Adaptive cryptographic algorithms (quantum resistant)
- Decentralized Identity and Self Sovereign Identity
- Smart contract platform powered by a built-in interpreter
- Strong scalability with geo secured sharding
- Soft-Real-Time P2P view with supervised networking

## Development

Our codebase aims to reach the guidelines of Elixir projects.
We are focusing on the best quality.

The source code can change to respect the best quality of reading and regarding best practices.

Current implemented features:

- Adaptive cryptography: different elliptic curves and software implementation
- Hybrid root of trust: mix of hardware and software cryptographic key to maintain trust and security
- TransactionChain: Transaction structure and transaction generation
- Smart Contract: interpreter coded with Elixir DSL through Meta-programming and AST
- Node election: heuristic validation and storage node selection
- P2P: Inter-node communication, supervised connection to detect the P2P view of nodes in almost real-time
- Transaction mining: ARCH consensus
- Beacon chain: Maintains a global view of the network (transactions, P2P view)
- Self-Repair: Self-healing mechanism allowing to resynchronize missing transactions
- Embedded explorer leveraging sharding to retrieve information
- Custom Binary protocol for data transmission
- Token minting
- Internal oracles (UCO Price Feed)
- Tailored embedded database

## Running a node for development purpose

### Using Elixir - MacOS specific setups

On Apple Silicon architecture, you might encounter issues running nodes.

Here is how to make it work.

#### Install openssl using brew

```sh
brew install openssl@3
```

#### Install erlang using `asdf`

```sh
cd <project_directory>
KERL_CONFIGURE_OPTIONS="--disable-jit --without-javac --without-wx --with-ssl=$(brew --prefix openssl@3)" asdf install
```

#### Locally update `exla` dependency

Edit `mix.exs` and replace the following `deps` item :

```elixir
      {:exla, "~> 0.5"},
```

by

```elixir
      {:exla, "~> 0.5.3"},
```

Then, install dependencies as usual :

```sh
mix deps.get
```

#### 🎉 You can run the node as usual

```sh
iex -S mix
```

### Using Elixir

Requirements:

- Libsodium: for the ed25519 to Curve25519 conversion
- OpenSSL 1.11
- Erlang OTP 25
- Elixir 1.14
- GMP (https://gmplib.org/)
- MiniUPnP used for port forwarding & IP lookup (https://miniupnp.tuxfamily.org/)
- Npm for static assets (https://nodejs.org/en/download)

Platforms supported:

- Linux (Ubuntu 18.04)
- Mac OS X ([See specific setups](#using-elixir---macos-specific-setups))

At first, clone the repository:

```bash
git clone https://github.com/archethic-foundation/archethic-node.git
cd archethic-node
```

Get dependencies:

```bash
mix deps.get
```

Install the static assets

```
cd assets ; npm install; cd -
```

To start a single node:

```bash
iex -S mix
```

To clean the data

```bash
make clean
```

To start mutiple node, you need to update some environment variables:

```bash
# Start the first node
iex -S mix

# Start second node
ARCHETHIC_CRYPTO_SEED=node2 ARCHETHIC_P2P_PORT=3003 ARCHETHIC_HTTP_PORT=4001 ARCHETHIC_HTTPS_PORT=5001 iex -S mix

# To start other node, increment the environment variables
```

### Using docker

Requires docker compose plugin

At first, clone the repository:

```bash
git clone https://github.com/archethic-foundation/archethic-node.git
cd archethic-node
```

Build the image:

```bash
docker build -t archethic-node .
```

To start a single node:

```bash
# You can run node up to node3
docker compose up node1
docker compose up node2
docker compose up node3
```

To start all nodes at the same time:

```bash
docker compose up
```

To run benchmarks:

```bash
docker compose up bench
```

To run the playbooks to validate non regression:

```bash
docker compose up validate
```

### Using snap

Work in progress ..

## Running a node for testnet / mainnet

Will be opened regarding roadmap advancement

## Contribution

Thank you for considering to help out with the source code.
We welcome contributions from anyone and are grateful for even the smallest of improvement.

Please to follow this workflow:

1. Fork it!
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create new Pull Request

## Licence

AGPL


Fichier: rag_builder\metadata\metadata_generator.py
Contenu:
"""
metadata_generator.py
Generates metadata for files: chunking, embeddings, summarization, etc.
"""

from typing import Dict, Any
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from embeddings.embeddings import AbstractEmbeddingModel
from summarizers.summarizers import AbstractSummarizer
from metadata.metadata_utils import compute_file_hash_md5, detect_file_type, detect_programming_language, detect_natural_language
from keywords_extractors.keywords_extractors import AbstractKeywordExtractor
from chunks.chunking_strategy_factory import ChunkingStrategyFactory
from chunks.abstract_chunking_strategy import AbstractChunkingStrategy
import datetime

class MetadataGenerator:
    """Generates or updates metadata (chunks, embeddings, etc.) for files in the database."""

    def __init__(self, db_manager : DatabaseManager, file_storage_manager : FileStorageManager,
                 embedding_model: AbstractEmbeddingModel,
                 summarizer: AbstractSummarizer,
                 keyword_extractor: AbstractKeywordExtractor):
        """
        Args:
            db_manager (DatabaseManager): Provides access to the database.
            file_storage_manager (FileStorageManager): For retrieving file content.
            embedding_model (AbstractEmbeddingModel): Instance implementing the embedding interface.
            summarizer (AbstractSummarizer): Instance implementing the summarization interface.
            keyword_extractor (AbstractKeywordExtractor): Instance implementing the keyword extraction interface.
        """
        self.db_manager = db_manager
        self.file_storage = file_storage_manager
        self.embedding_model = embedding_model
        self.summarizer = summarizer
        self.keyword_extractor = keyword_extractor

    def extract_text_from_document(self, collection_item: Dict[str, Any], collection: str) -> str:
        """
        Extracts relevant textual content from a document based on its collection.

        Args:
            data (Dict): Document information from the database.
            collection (str): The MongoDB collection of the document.

        Returns:
            str: Extracted text for metadata processing.
        """
        # Files: Retrieve text from external storage or fallback to patch
        if collection in ["files", "main_files", "last_release_files"]:
            return self._extract_text_from_files(collection_item)
        # Commits: Combine commit message, patch, and list of impacted files
        elif collection == "commits":
            return self._extract_text_from_commits(collection_item)
        # Issues: Retrieve text from title and body
        elif collection == "issues":
            return self._extract_text_from_issues(collection_item)
        # Pull Requests: Retrieve text from title and body or external storage
        elif collection == "pull_requests":
            return self._extract_text_from_pull_requests(collection_item)

        return ""

    def update_metadata_for_collection(self, repo : str, db_collection: Dict[str, Any], collection_src: str) -> None:
        """
        Updates metadata for all documents in a given collection, filtering by repo if needed.
        
        Args:
            repo (str): The repository name to filter on.
            db_collection (Dict): The MongoDB collection name (ex. files, main_files, last_release_files, commits, pull_requests, issues).
            collection_src (str): The name of the collection source
        """

        collection_items = db_collection.find({"repo": repo})
        for collection_item in collection_items:
            text = self.extract_text_from_document(collection_item, collection_src)
            if text:
                self._generate_metadata_for_document(collection_item, collection_src, text)

    def _compute_metadata_id(self, repo: str, collection_src: str, collection_id: str) -> str:
        """
        Builds the metadata identifier in the format: meta_{repo}_{collection_src}_{collection_id}.

        Args:
            repo (str): Repository name.
            collection_src (str): Source collection name.
            collection_id (str): Document identifier from the source collection.

        Returns:
            str: Computed metadata identifier.
        """
        return f"meta_{repo}_{collection_src}_{collection_id}"

    def _extract_text_from_files(self, collection_item: Dict[str, Any]) -> str:
        """
        Extracts relevant textual content from a document based on files, main_files or last_release_files collections.

        Args:
            collection_item (Dict[str, Any]): Document information from the database.

        Returns:
            str: Extracted text for metadata processing.
        """
        file_url = collection_item.get("external_url")
        if file_url:
            return self.file_storage.fetch_file_content(file_url)
        return collection_item.get("patch", "").strip()  # Fallback if no external file is available

    def _extract_text_from_commits(self, collection_item: Dict[str, Any]) -> str:
        """
        Extracts relevant textual content from a document based on commits collection.

        Args:
            collection_item (DicDict[str, Any]t): Document information from the database.

        Returns:
            str: Extracted text for metadata processing.
        """
        # TODO: In future, use LLM to generate a better summary of commit changes.
        commit_message = collection_item.get("message", "").strip()
        files_changed = "\n".join(collection_item.get("files_changed", []))  # List impacted files
        return f"Commit Message:\n{commit_message}\n\nFiles Changed:\n{files_changed}".strip()
    
    def _extract_text_from_issues(self, collection_item: Dict[str, Any]) -> str:
        """
        Extracts relevant textual content from a document based on issues collection.

        Args:
            collection_item (Dict): Document information from the database.

        Returns:
            str: Extracted text for metadata processing.
        """
        issue_title = collection_item.get("title", "").strip()
        issue_body = collection_item.get("body", "").strip()
        
        # Fetch comments if available
        comments = self.db_manager.db.issues_comments.find({"issue_id": collection_item["_id"]})
        comments_text = "\n".join([c["comment_body"] for c in comments])
        return f"{issue_title}\n\n{issue_body}\n\nComments:\n{comments_text}".strip()

    def _extract_text_from_pull_requests(self, collection_item: Dict) -> str:
        """
        Extracts relevant textual content from a document based on pull_requests collection.

        Args:
            collection_item (Dict): Document information from the database.

        Returns:
            str: Extracted text for metadata processing.
        """
        pr_title = collection_item.get("title", "").strip()
        pr_body_url = collection_item.get("body_url")
        pr_body = self.file_storage.fetch_file_content(pr_body_url) if pr_body_url else collection_item.get("body", "").strip()

        # Fetch comments if available
        comments = self.db_manager.db.pull_requests_comments.find({"pr_id": collection_item["_id"]})
        comments_text = "\n".join([c["comment_body"] for c in comments])

        return f"{pr_title}\n\n{pr_body}\n\nComments:\n{comments_text}".strip()

    def _generate_metadata_for_document(self, collection_item: Dict[str, Any], collection_src: str, content : str) -> None:
        """
        Generates metadata for a single document and updates the corresponding chunks.
        Handles both new metadata creation and update of existing metadata.
        Also updates the metadata_id field in related collections.

        Args:
            collection_item (Dict[str, Any]): Document information from the database.
            collection_src (str): Source collection name.
            content (str): The text content extracted from the document.
        """

        if not content:
            return
        
        collection_id = str(collection_item.get("_id"))
        metadata_id = self._compute_metadata_id(collection_item["repo"], collection_src, collection_id)
        file_hash =  compute_file_hash_md5(content)

        # Check if metadata already exists
        existing_metadata = self.db_manager.db.metadata.find_one({"_id": metadata_id})
        current_metadata_version = 0  # Define current metadata version

        if existing_metadata is None:
            # New metadata document to be created.
            metadata_obj = self._create_metadata(collection_item, metadata_id, collection_src, collection_id, file_hash, content, current_metadata_version)
        else:
            # Update is needed if the file_hash differs or if metadata_version is outdated.
            metadata_obj = self._update_existing_metadata(existing_metadata, collection_item, file_hash, content, current_metadata_version)

        if metadata_obj is None:
            # No update
            return
        
        # Log metadata details before update to help trace potential size issues.
        num_chunks = len(metadata_obj.get("chunk_ids", []))
        content_length = len(content)
        print(f"[DEBUG] Updating metadata with id: {metadata_id}")
        print(f"[DEBUG] Repo: {collection_item['repo']}, Collection: {collection_src}, Document _id: {collection_id}")
        print(f"[DEBUG] File hash: {file_hash}, Content length: {content_length}, Number of chunks: {num_chunks}")

        # Update or insert the metadata document.
        self.db_manager.db.metadata.update_one({"_id": metadata_id}, {"$set": metadata_obj}, upsert=True)
        print(f"✅ Metadata {metadata_id} updated")

        # Update the source document with the metadata_id.
        self.db_manager.db[collection_src].update_one({"_id": collection_item["_id"]}, {"$set": {"metadata_id": metadata_id}})
        print(f"✅ collection {collection_src} with id {collection_id} is linked to metadata_id {metadata_id}")

    def _create_metadata(self, collection_item, metadata_id, collection_src, collection_id, file_hash, content, current_metadata_version):
        
        created_at = datetime.datetime.now(datetime.timezone.utc)
        has_filename = collection_src in ["files", "main_files", "last_release_files"]
        is_binary = False
        ext = "txt"
        file_type="doc"
        if has_filename:
            file_type = detect_file_type(collection_item["filename"])
            is_binary = file_type == "binary"
            ext = collection_item["filename"].split(".")[-1].lower()
        
        if is_binary:
            # TODO Currently the system doesn't handle binary files
            return None

        language = self._detect_language(collection_item, has_filename, content)
        settings = {
            "extension": ext,
            "language": language,
            "min_chunk_size": 300,
            "chunk_size": 1000,
            "overlap": 200
        }
        strategy = ChunkingStrategyFactory.get_strategy(file_type, settings)
        chunks_ids = self._create_chunks(metadata_id, strategy, content)
        tags = self.keyword_extractor.extract(content)
        description = ""
        if not is_binary and current_metadata_version != 0:
            # TODO not use description currently and try to accelerate process to create chunk and embeddings
            # TODO think how description can be use to improve the RAG system
            # that mean the content contains something that can be understood by the model
            description = self.summarizer.summarize(content)

        # Store the content of chunk in local_storage and get url to this content
        external_url = self.file_storage.store_file_content(content=content, repo=collection_item["repo"], reference_id="meta", filename=metadata_id)

        metadata_obj = {
                "_id": metadata_id,
                "repo": collection_item["repo"],
                "collection_src": collection_src,
                "collection_id": collection_id,
                "language": language,
                "description": description,
                "tags": tags,
                "chunk_ids": chunks_ids,
                "created_at": created_at,
                "updated_at": created_at,
                "source_url": external_url,
                "metadata_version": current_metadata_version,
                "file_hash": file_hash
            }
        
        return metadata_obj

    def _detect_language(self, collection_item, has_filename=False, content=None):
        language = "undefined"
        if (has_filename):
            file_type = detect_file_type(collection_item["filename"])
            ext = collection_item["filename"].split(".")[-1].lower()
            if file_type == "code":
                language = detect_programming_language(ext)
            elif file_type == "binary":
                language = "binary"
            else:
                language = detect_natural_language(content)
        return language

    def _update_existing_metadata(self, existing_metadata, collection_item, file_hash, content, current_metadata_version):
        previous_metadata_version = existing_metadata.get("metadata_version", 1)
        if (existing_metadata.get("file_hash") != file_hash or previous_metadata_version != current_metadata_version):
            # Remove obsolete chunks
            self.db_manager.db.chunks.delete_many({"metadata_id": existing_metadata.get("_id")})

            return self._create_metadata(collection_item=collection_item,
                                        metadata_id=existing_metadata.get("_id"),
                                        collection_src=existing_metadata.get("collection_src"),
                                        collection_id=existing_metadata.get("collection_id"),
                                        file_hash=file_hash,
                                        content=content,
                                        current_metadata_version=current_metadata_version)
        else:
            metadata_id = existing_metadata.get("_id")
            print(f"⏩ Skipping {metadata_id} (hash and metadata version unchanged)")
            return None

    def _create_chunks(self, metadata_id : str,
                       strategy: AbstractChunkingStrategy,
                       content: str):
        chunks = strategy.chunk(content)
        chunk_ids = []
        for i, chunk_text in enumerate(chunks):
            vector = self.embedding_model.encode(chunk_text)
            chunk_id = f"{metadata_id}_chunk_{i}"  # Format: meta_id_chunk_index
            chunk_doc = {
                "_id": chunk_id,
                "metadata_id": metadata_id,
                "chunk_index": i,
                "chunk_src": chunk_text,
                "embedding": vector
            }
            self.db_manager.db.chunks.update_one({"_id": chunk_id}, {"$set": chunk_doc}, upsert=True)
            chunk_ids.append(chunk_id)
        return chunk_ids


Fichier: rag_builder\metadata\metadata_manager.py
Contenu:
"""
metadata_manager.py
Handles the orchestration of metadata extraction, generation, and storage.
"""

from typing import List, Dict
from core.database_manager import DatabaseManager
from core.file_storage_manager import FileStorageManager
from metadata.metadata_generator import MetadataGenerator
from embeddings.embeddings import SentenceTransformerEmbeddingModel
from summarizers.summarizers import T5Summarizer
from keywords_extractors.keywords_extractors import YakeKeywordExtractor

class MetadataManager:
    """
    High-level controller for metadata updates across repositories.
    """

    def __init__(self, db_manager: DatabaseManager, file_storage: FileStorageManager):
        """
        Initializes MetadataManager with database and file storage access.

        Args:
            db_manager (DatabaseManager): Handles MongoDB interactions.
            file_storage (FileStorageManager): Manages file retrieval/storage.
        """
        self.db_manager = db_manager
        embedding_model = SentenceTransformerEmbeddingModel()
        summarizer = T5Summarizer()
        keywords_extractor = YakeKeywordExtractor()
        self.metadata_generator = MetadataGenerator(db_manager, file_storage, embedding_model, summarizer, keywords_extractor)

    def update_metadata_multiple_repos_specific_data(self, repos: List[str], selected_data: List[str]):
        """
        Updates metadata for all elements in a given repository.

        Args:
            repos (List[str]): List of gitHub repositories to update.
            selected_data (List[str]): Collections to update (e.g., ['files', 'main_files', 'last_release_files', 'commits', 'pull_requests', 'issues']).
        """
        for repo in repos:
            self.update_metadata_for_specific_data(repo, selected_data)

    def update_metadata_for_specific_data(self, repo: str, selected_data: List[Dict]):
        """
        Updates metadata for all elements in a given repository.

        Args:
            repo (str): GitHub repository name.
            collections (List[str]): Collections to update (e.g., ['files', 'commits', 'issues']).
        """
        
        for collection in selected_data:
            print(f"🔄 Updating metadata for '{repo}', collection '{collection}'...")
            self.metadata_generator.update_metadata_for_collection(repo, self.db_manager.db[collection], collection)
            print(f"✅ Metadata update completed for {collection} in {repo}.")


Fichier: rag_builder\metadata\metadata_utils.py
Contenu:
"""
metadata_utils.py
Provides utility functions for metadata processing.
"""

import hashlib
from langdetect import detect

def detect_file_type(filename: str) -> str:
    """
    Detects the type of a file based on its extension.

    Args:
        filename (str): The filename with extension.

    Returns:
        str: The detected file type (e.g., "code", "doc", "config").
    """
    extension_mapping = {
        "code": ["py", "js", "ts", "java", "c", "cpp", "h", "hpp", "cs", "go", "rb", "rs", "php", "swift", "kt", "ex", "exs"],
        "doc": ["md", "rst", "txt", "pdf", "doc", "docx"],
        "config": ["json", "yaml", "yml", "toml", "ini", "xml"],
        "log": ["log", "csv"],
        "binary": ["png", "jpg", "jpeg", "gif", "bmp", "svg", "mp3", "mp4", "mov", "avi", "zip", "tar", "gz", "7z", "rar", "mmdb", ".ico"],
        "unknown": []
    }
    
    ext = filename.split(".")[-1].lower()
    for category, extensions in extension_mapping.items():
        if ext in extensions:
            return category
    return "unknown"

def detect_programming_language(extension: str) -> str:
    """
    Detects the programming language based on file extension.

    Args:
        extension (str): File extension.

    Returns:
        str: The programming language detected.
    """
    language_mapping = {
        "python": ["py"],
        "javascript": ["js", "ts"],
        "solidity": ["sol"],
        "java": ["java"],
        "c": ["c", "h"],
        "cpp": ["cpp", "hpp"],
        "csharp": ["cs"],
        "go": ["go"],
        "ruby": ["rb"],
        "rust": ["rs"],
        "php": ["php"],
        "swift": ["swift"],
        "kotlin": ["kt"],
        "json": ["json"],
        "yaml": ["yaml", "yml"],
        "toml": ["toml"],
        "xml": ["xml"],
        "markdown": ["md", "rst", "txt"],
        "elixir" : ["exs", "ex"]
    }
    
    # Check using file extension
    for lang, extensions in language_mapping.items():
        if extension in extensions:
            return lang
        
    return "unknown"
    
def detect_natural_language(text):
    """
    Detects the natural language of a given text (English, French, etc.).
    """
    try:
        return detect(text)
    except:
        return "unknown"

def compute_file_hash(content: str) -> str:
    """
    Computes a SHA-256 hash for a file based on its content.

    Args:
        content (str): The file content.

    Returns:
        str: The computed hash.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def compute_file_hash_md5(content: str) -> str:
    """
    Computes a MD5 hash for a file based on its content.

    Args:
        content (str): The file content.

    Returns:
        str: The computed hash md5.
    """
    return hashlib.md5(content.encode("utf-8")).hexdigest()


Fichier: rag_builder\metadata\__init__.py
Contenu:


Fichier: rag_builder\server\local_storage_server.py
Contenu:
"""
local_storage_server.py
Provides a simple HTTP server to serve locally stored files.
"""

import http.server
import socketserver
import os

class LocalStorageServer:
    """
    A simple HTTP server that serves files from a local directory.
    """

    def __init__(self, port: int, storage_directory: str):
        """
        Initializes the local storage server.

        Args:
            port (int): The port on which the server will run.
            storage_directory (str): The directory to serve files from.
        """
        self.port = port
        self.storage_directory = storage_directory
        self.httpd = None

    def start_server(self):
        """
        Starts a blocking HTTP server on self.port, serving self.storage_directory.
        """
        handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
            *args, directory=self.storage_directory, **kwargs
        )
        self.httpd = socketserver.TCPServer(("", self.port), handler)
        print(f"[LocalStorageServer] Serving '{self.storage_directory}' at port {self.port}")
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            self.stop_server()

    def stop_server(self):
        """
        Stops the running HTTP server.
        """
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            print("[LocalStorageServer] Server stopped.")


Fichier: rag_builder\server\__init__.py
Contenu:


Fichier: rag_builder\summarizers\summarizers.py
Contenu:
from abc import ABC, abstractmethod

class AbstractSummarizer(ABC):
    @abstractmethod
    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """Summarize test provided"""
        pass

from transformers import pipeline

class T5Summarizer(AbstractSummarizer):
    def __init__(self, model_name: str = "t5-small"):
        self.pipeline = pipeline("summarization", model=model_name)

    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        # Truncated the text to avoid exceeding the model's capacity
        truncated_text = text[:2000]
        result = self.pipeline(truncated_text, max_length=max_length, min_length=min_length, do_sample=False)
        return result[0]['summary_text']

Fichier: rag_builder\summarizers\__init__.py
Contenu:


Fichier: rag_builder\tests\__init__.py
Contenu:

