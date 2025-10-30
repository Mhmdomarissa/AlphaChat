# RAGFlow Pipeline: Excel Upload to Chat Retrieval

## 🎯 Your Scenario
- **File**: `Alpha Data MIS 12-2024 Final.xlsx` (multi-sheet Excel)
- **Sheets**: Abu Dhabi, Dubai, Sharjah, Saudi, Qatar
- **Query**: "What is BUDGET_2025 profit after tax for Sharjah?"

---

## PHASE 1: FILE UPLOAD & PARSING 🏃

### Step 1.1: File Detection
```
Location: /home/ec2-user/ragflow/rag/app/naive.py (line 489)
Code: re.search(r"\.(csv|xlsx?)$", filename, re.IGNORECASE)
```

**What Happens:**
- RAGFlow detects `.xlsx` extension
- Identifies file type: "Excel spreadsheet"
- Routes to ExcelParser

---

### Step 1.2: Excel Parsing with HTML Output
```python
excel_parser = ExcelParser()
sections = excel_parser.html(binary, chunk_rows=1)
```

**What Happens:**
- Opens the Excel file (multi-sheet workbook)
- Iterates through each sheet: Sharjah, Dubai, Abu Dhabi, etc.

#### For Each Sheet (e.g., "Sharjah"):
```python
# Current row in your Excel:
# B14: "G.P. MARGIN %" | C14: 68% | D14: 68% | E14: 62%

# Parser creates ONE chunk per row:
chunk = f"""
<div class='excel-chunk'>
  <div class='sheet-metadata'><strong>Sheet:</strong> Sharjah</div>
  <table>
    <tr><th>ROW</th><th>BUDGET_2025</th><th>BUDGET_2024</th><th>ACTUAL_2024</th></tr>
    <tr>
      <td>G.P. MARGIN %</td><td>68%</td><td>68%</td><td>62%</td>
    </tr>
  </table>
</div>
"""
```

**Result:**
- Each Excel row → 1 HTML chunk
- Chunk contains: Sheet name + Complete row with ALL columns
- Example: "G.P. MARGIN % | BUDGET_2025: 68% | BUDGET_2024: 68% | ACTUAL_2024: 62%"

---

## PHASE 2: CHUNKING & INDEXING 📝

### Step 2.1: Chunk Structure
```
Location: /home/ec2-user/ragflow/rag/flow/chunker/chunker.py
Method: _general() with naive_merge()
```

**What Happens:**
- Parser produces HTML chunks
- Chunker reads each chunk as structured text
- Config: `chunk_token_size = 512`, `delimiter = "\n"`

**Your Chunk Example:**
```json
{
  "text": "<div class='excel-chunk'><table><caption>Sharjah</caption><tr><td>G.P. MARGIN %</td><td>68%</td><td>68%</td><td>62%</td></tr></table></div>",
  "page_no": 0,
  "offset": 150,
  "meta": {
    "sheet": "Sharjah",
    "row_type": "metric"
  }
}
```

---

### Step 2.2: Text Tokenization
```
Location: rag/nlp.py
Method: rag_tokenizer()
```

**What Happens:**
- Converts HTML chunk text → tokens
- Example: "G.P. MARGIN %: 68%" → [token_1, token_2, token_3, ...]
- Count: ~150 tokens per chunk (within 512 limit)

---

### Step 2.3: Embedding Generation
```
Location: rag/llm/embedding_model.py
Model: BAAI/bge-large-en-v1.5
Method: encode()
```

**What Happens:**
1. Takes chunk text as input
2. Sends to embedding model (Ollama BGE-m3 on your server)
3. Model generates 1024-dimensional vector

**Example Vector:**
```python
chunk_text = "Sharjah: G.P. MARGIN %: 68%, BUDGET_2025: 68%, ACTUAL_2024: 62%"
embedding = model.encode(chunk_text)
# Result: [0.123, -0.456, 0.789, ..., 1024 dimensions]
# Vector represents semantic meaning of this financial metric
```

---

### Step 2.4: Vector Storage
```
Location: rag/db/vector_store.py
Database: Vector DB (Milvus/Pinecone/Chroma)
```

**What Happens:**
- Stores embedding in vector database
- Each chunk gets unique ID: `chunk_id = "doc_123_chunk_456"`
- Metadata stored: `{"sheet": "Sharjah", "row_type": "metric"}`

**Storage Structure:**
```
Vector DB Entry:
{
  "id": "chunk_456",
  "text": "G.P. MARGIN %: 68% (BUDGET_2025), 68% (BUDGET_2024), 62% (ACTUAL_2024)",
  "embedding": [0.123, -0.456, ...],
  "metadata": {
    "source": "Alpha Data MIS.xlsx",
    "sheet": "Sharjah",
    "file_id": "doc_123"
  }
}
```

---

## PHASE 3: QUERY TIME 🔍

### Step 3.1: User Query Input
```
Query: "What is BUDGET_2025 profit after tax for Sharjah?"
```

**What Happens:**
- User types query in chat interface
- Query sent to `/api/v1/chats` endpoint
- Query processed by LLM service

---

### Step 3.2: Query Embedding
```
Location: rag/llm/embedding_model.py
Method: encode(query)
```

**What Happens:**
- Same embedding model (BAAI/bge-large-en-v1.5) generates embedding for query

**Example:**
```python
query = "What is BUDGET_2025 profit after tax for Sharjah?"
query_embedding = [0.234, -0.567, 0.891, ..., 1024 dimensions]
# Vector represents: "financial profit Sharjah 2025 tax"
```

---

### Step 3.3: Semantic Similarity Search
```
Location: rag/db/vector_store.py
Method: similarity_search()
```

**What Happens:**
1. Calculate cosine similarity between query embedding and all chunk embeddings
2. Formula: `similarity = cosine(query_vec, chunk_vec)`
3. Rank chunks by similarity score (highest = most relevant)

**Search Results:**
```python
# Top 3 most similar chunks:

Chunk A (Score: 0.92):
  Text: "Sharjah: OPERATING PROFIT: 1,613 (BUDGET_2025)"
  Why: High score because "profit" matches query

Chunk B (Score: 0.89):
  Text: "Sharjah: GROSS PROFIT: 3,700 (BUDGET_2025)"
  Why: "profit" and "Sharjah" match

Chunk C (Score: 0.87):
  Text: "Sharjah: NET PROFIT: 1,435 (BUDGET_2025)"
  Why: "net profit" is similar to "profit after tax"

# Retrieved: top_n=3 chunks (configurable in service_conf.yaml)
```

---

### Step 3.4: Reranking (Optional Enhancement)
```
Location: rag/llm/rerank_model.py
Model: bge-reranker-v2
```

**What Happens:**
1. Reranker receives query + top N chunks
2. Reranker scores each chunk's relevance to query
3. Reorders chunks by reranking score

**Reranking Logic:**
```python
# Before reranking:
Chunk A: Score 0.92 (OPERATING PROFIT)
Chunk B: Score 0.89 (GROSS PROFIT)  
Chunk C: Score 0.87 (NET PROFIT)

# After reranking (query: "profit after tax"):
Chunk C: Score 0.95 (NET PROFIT - most relevant!)
Chunk A: Score 0.85 (OPERATING PROFIT)
Chunk B: Score 0.82 (GROSS PROFIT)

# NET PROFIT rises to top because it directly matches "profit after tax"
```

---

### Step 3.5: Context Assembly for LLM
```
Location: rag/app/qa.py
Method: prepare_context()
```

**What Happens:**
- Combines retrieved chunks into LLM context
- Adds system prompt
- Respects `max_context_tokens = 16000` (from config)

**Context Structure:**
```
System Prompt:
"You are a professional AI assistant specializing in document analysis."

User Query:
"What is BUDGET_2025 profit after tax for Sharjah?"

Retrieved Context (top 3 chunks):
"
[Sharjah]
OPERATING PROFIT: 1,613 (BUDGET_2025)
OPERATING PROFIT%: 30%

[Sharjah]  
NET PROFIT: 1,435 (BUDGET_2025)
NET PROFIT%: 26%

[Sharjah]
GROSS PROFIT: 3,700 (BUDGET_2025)
"
```

---

### Step 3.6: LLM Inference
```
Location: rag/app/qa.py
Model: Qwen2.5-7B-Instruct (via vLLM)
```

**What Happens:**
1. Sends context + query to Qwen model
2. Model analyzes context and generates answer
3. Model identifies: "profit after tax" = "NET PROFIT"
4. Model extracts: "1,435" from Sharjah sheet
5. Returns structured response

**LLM Output:**
```json
{
  "answer": "The BUDGET_2025 profit after tax for Sharjah is 1,435.",
  "source": "Alpha Data MIS 12-2024 Final.xlsx (Sharjah sheet)",
  "confidence": 0.95,
  "sources": [
    {
      "text": "NET PROFIT: 1,435 (BUDGET_2025)",
      "chunk_id": "chunk_456"
    }
  ]
}
```

---

## PHASE 4: RESPONSE GENERATION 📤

### Step 4.1: Response Formatting
```
Location: rag/app/one.py
Method: chat()
```

**What Happens:**
- Formats LLM output for UI display
- Includes source citations
- Provides confidence score

**Final Response to User:**
```
💬 Assistant:
The BUDGET_2025 profit after tax for Sharjah is 1,435.
Source: Alpha Data MIS 12-2024 Final.xlsx (Sharjah sheet)
```

---

## 🔄 WHY THIS WORKS NOW

### Before Fix (Broken):
```
Chunk Structure: 12 rows per chunk
Chunk Text: "G.P. MARGIN: 68% ... TOTAL EXPENDITURE: -1837 ..."
Problem: Mixing multiple metrics in one chunk
Result: Can't distinguish "BUDGET_2025" vs "ACTUAL_2024" columns
Query: "profit after tax 2025" → Returns wrong year's data
```

### After Fix (Working):
```
Chunk Structure: 1 row per chunk
Chunk Text: "G.P. MARGIN: 68% (BUDGET_2025), 68% (BUDGET_2024), 62% (ACTUAL_2024)"
Benefit: Each chunk = One metric with all columns
Result: Can match exact column requested
Query: "profit after tax 2025" → Returns 2025 data correctly
```

---

## 📊 PIPELINE SUMMARY

```
1. UPLOAD: Excel file → RAGFlow API
2. PARSE: Multi-sheet → Individual rows (chunk_rows=1)
3. CHUNK: Each row = One chunk with all columns
4. EMBED: Chunk text → 1024-dim vector
5. STORE: Vector + metadata in DB
6. QUERY: User question
7. EMBED QUERY: Question → 1024-dim vector
8. SEARCH: Find top 3 similar chunks (cosine similarity)
9. RERANK: Reorder by relevance (optional)
10. ASSEMBLE: Query + chunks → LLM context
11. LLM: Generate answer from context
12. RESPOND: Return answer to user
```

---

## ✅ KEY CONFIGURATIONS

From `service_conf.yaml`:
```yaml
retrieval:
  similarity_threshold: 0.6    # Minimum similarity to consider
  top_n: 3                     # Retrieve top 3 chunks

rerank:
  enabled: true                 # Use reranker for better accuracy
  model: "bge-reranker-v2"

llm:
  max_context_tokens: 16000    # Maximum context for LLM
  max_tokens: 512               # Maximum response length
```

---

## 🎯 REAL EXAMPLE: Your Sharjah Query

**Your Excel Row:**
```
Sheet: Sharjah
Row: NET PROFIT | BUDGET_2025: 1,435 | BUDGET_2024: 1,395 | ACTUAL_2024: 1,600
```

**After Parsing (Chunk 1):**
```html
<div class='excel-chunk'>
  <div class='sheet-metadata'>Sheet: Sharjah</div>
  <table>
    <tr><td>NET PROFIT</td><td>1,435</td><td>1,395</td><td>1,600</td></tr>
  </table>
</div>
```

**After Embedding:**
```
Vector: [0.15, -0.23, 0.78, ..., 1024 dims]
Semantic meaning: "net profit sharjah financial"
```

**Query Embedding:**
```
Query: "profit after tax"
Vector: [0.14, -0.22, 0.79, ..., 1024 dims]
Semantic meaning: "tax profit net financial"
```

**Similarity Score:**
```
Cosine similarity: 0.92 (very high!)
Rank: #1 most relevant chunk
```

**LLM Context:**
```
User: What is BUDGET_2025 profit after tax for Sharjah?

Context:
  Sheet: Sharjah
  NET PROFIT (BUDGET_2025): 1,435
  NET PROFIT (BUDGET_2024): 1,395
  NET PROFIT (ACTUAL_2024): 1,600
```

**LLM Response:**
```
The BUDGET_2025 profit after tax for Sharjah is 1,435.
```

✅ **ACCURATE!** Because each chunk contains complete row with all columns!

