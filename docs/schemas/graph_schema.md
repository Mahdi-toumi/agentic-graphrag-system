# Movie Knowledge Graph Schema

## Overview
This document defines the graph schema for the movie recommendation system using Neo4j.

## Node Types

### Movie
- **Properties**:
  - `id` (String, unique): Movie identifier
  - `title` (String): Movie title
  - `year` (Integer): Release year
  - `rating` (Float): IMDb rating
  - `budget` (Integer): Production budget in USD
  - `revenue` (Integer): Box office revenue in USD
  - `overview` (String): Movie description
  - `embedding` (Vector[384]): Text embedding for semantic search

### Person
- **Properties**:
  - `name` (String, unique): Person's full name
  - `type` (String): "actor" or "director"

### Genre
- **Properties**:
  - `name` (String, unique): Genre name (e.g., "Action", "Drama")

### Keyword
- **Properties**:
  - `name` (String, unique): Keyword/theme (e.g., "artificial intelligence")

## Relationships

### ACTED_IN
- **From**: Person (actor)
- **To**: Movie
- **Properties**: None

### DIRECTED
- **From**: Person (director)
- **To**: Movie
- **Properties**: None

### HAS_GENRE
- **From**: Movie
- **To**: Genre
- **Properties**: None

### HAS_KEYWORD
- **From**: Movie
- **To**: Keyword
- **Properties**: None

## Graph Visualization

```
(Person:Director)-[:DIRECTED]->(Movie)-[:HAS_GENRE]->(Genre)
                                  |
                                  |-[:HAS_KEYWORD]->(Keyword)
                                  |
(Person:Actor)-[:ACTED_IN]--------+
```

## Example Cypher Queries

### Create Movie Node
```cypher
CREATE (m:Movie {
  id: 'm1',
  title: 'The Matrix',
  year: 1999,
  rating: 8.7,
  budget: 63000000,
  revenue: 463517383,
  overview: 'A computer hacker learns about the true nature of reality...'
})
```

### Find Movies by Director
```cypher
MATCH (d:Person {type: 'director'})-[:DIRECTED]->(m:Movie)
WHERE d.name = 'Christopher Nolan'
RETURN m.title, m.year, m.rating
ORDER BY m.rating DESC
```

### Find Similar Movies by Genre and Keywords
```cypher
MATCH (m1:Movie {title: 'The Matrix'})-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(m2:Movie)
MATCH (m1)-[:HAS_KEYWORD]->(k:Keyword)<-[:HAS_KEYWORD]-(m2)
WHERE m1 <> m2
RETURN m2.title, COUNT(DISTINCT g) + COUNT(DISTINCT k) AS similarity
ORDER BY similarity DESC
LIMIT 5
```

## Vector Search Integration

Movies will have embeddings generated from their `overview` text using `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).

### Create Vector Index
```cypher
CREATE VECTOR INDEX movie_embeddings IF NOT EXISTS
FOR (m:Movie)
ON m.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}}
```

### Semantic Search Query
```cypher
MATCH (m:Movie)
CALL db.index.vector.queryNodes('movie_embeddings', 5, $query_embedding)
YIELD node, score
RETURN node.title, node.overview, score
ORDER BY score DESC
```
