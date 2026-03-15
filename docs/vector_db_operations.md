# Vector Database Operations Guide

This document explains the core concepts and operations of Vector Databases as demonstrated in this application.

## 1. What is a Vector Database?

Traditional databases (like SQL) store data in tables and rows and search by exact matches or keywords. 
A **Vector Database** stores data as mathematical vectors (arrays of numbers) and searches based on **semantic similarity**.

### Embeddings
An embedding is a vector representation of data (like text). It captures the "meaning" of the data such that similar concepts are closer together in the vector space.

Example:
- "The cat is on the mat" -> `[0.12, -0.98, ...]`
- "A feline is resting" -> `[0.11, -0.97, ...]`
- "I like ice cream" -> `[0.85, 0.44, ...]`

In this space, the first two sentences would be very "close" to each other.

## 2. Core Operations

### Insert (Indexing)
1. **Extraction**: Get text from a document (PDF, TXT, etc.).
2. **Chunking**: Split text into smaller, overlapping parts.
3. **Embedding**: Pass chunks through a model to get vectors.
4. **Storage**: Save the vector + metadata + original text in the DB.

### Search (Querying)
1. **Query Embedding**: Convert the search phrase (e.g., "What is a vector?") into a vector.
2. **Similarity Calculation**: Find the vectors in the database that are most similar to the query vector.
3. **Retrieval**: Return the top K matching chunks and their metadata.

### Delete
- You can delete specific documents (by their source name) or entire collections to start fresh.

## 3. Similarity Metrics

- **Cosine Similarity**: Measures the angle between two vectors. Values range from 1 (identical) to -1 (opposite). This is the most common metric for text.
- **Euclidean Distance (L2)**: Measures the straight-line distance between two points. Smaller means more similar.
- **Dot Product**: Multiplies corresponding elements and sums them up. Larger (positive) means more similar.

---
*Created for the Vector DB Demonstration Project.*
