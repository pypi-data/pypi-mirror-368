"""
Storage Backends for Knowledge Graph

Provides pluggable storage options: in-memory → DuckDB → external systems
"""

from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from .knowledge_graph import KGStorageBackend, KGEntity, KGRelationship, KGSearchResult


class DuckDBKGStorage:
    """
    DuckDB-based knowledge graph storage.
    
    Stores entities, relationships, and search results in DuckDB tables
    with proper indexing and querying capabilities.
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """Initialize DuckDB storage with database path"""
        self.db_path = db_path
        self._conn = None
        self._initialized = False
    
    async def _get_connection(self):
        """Get or create DuckDB connection"""
        if not self._conn:
            try:
                import duckdb
                self._conn = duckdb.connect(self.db_path)
                await self._initialize_tables()
            except ImportError:
                raise ImportError(
                    "DuckDB not installed. Install with: pip install duckdb"
                )
        return self._conn
    
    async def _initialize_tables(self):
        """Create KG tables if they don't exist"""
        if self._initialized:
            return
            
        conn = await self._get_connection()
        
        # Entities table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kg_entities (
                id VARCHAR PRIMARY KEY,
                type VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                properties JSON,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)
        
        # Relationships table  
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kg_relationships (
                id VARCHAR PRIMARY KEY,
                source_id VARCHAR NOT NULL,
                target_id VARCHAR NOT NULL,
                type VARCHAR NOT NULL,
                properties JSON,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (source_id) REFERENCES kg_entities(id),
                FOREIGN KEY (target_id) REFERENCES kg_entities(id)
            )
        """)
        
        # Search results table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kg_search_results (
                id VARCHAR PRIMARY KEY,
                query VARCHAR NOT NULL,
                results TEXT NOT NULL,
                result_count INTEGER,
                search_type VARCHAR,
                location VARCHAR,
                created_at TIMESTAMP NOT NULL
            )
        """)
        
        # Create indexes for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON kg_entities(type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_created ON kg_entities(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source ON kg_relationships(source_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_target ON kg_relationships(target_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_search_created ON kg_search_results(created_at)")
        
        self._initialized = True
    
    async def store_entity(self, entity: KGEntity) -> None:
        """Store entity in DuckDB"""
        conn = await self._get_connection()
        
        # Upsert entity
        conn.execute("""
            INSERT OR REPLACE INTO kg_entities 
            (id, type, name, properties, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            entity.id,
            entity.type,
            entity.name,
            json.dumps(entity.properties),
            entity.created_at,
            entity.updated_at
        ])
    
    async def store_relationship(self, relationship: KGRelationship) -> None:
        """Store relationship in DuckDB"""
        conn = await self._get_connection()
        
        conn.execute("""
            INSERT INTO kg_relationships 
            (id, source_id, target_id, type, properties, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            relationship.id,
            relationship.source_id,
            relationship.target_id,
            relationship.type,
            json.dumps(relationship.properties),
            relationship.created_at
        ])
    
    async def store_search_result(self, search_result: KGSearchResult) -> None:
        """Store search result in DuckDB"""
        conn = await self._get_connection()
        
        conn.execute("""
            INSERT INTO kg_search_results 
            (id, query, results, result_count, search_type, location, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            search_result.id,
            search_result.query,
            search_result.results,
            search_result.result_count,
            search_result.search_type,
            search_result.location,
            search_result.created_at
        ])
    
    async def get_entities(self, limit: int = 10, entity_type: Optional[str] = None) -> List[KGEntity]:
        """Get recent entities from DuckDB"""
        conn = await self._get_connection()
        
        if entity_type:
            query = """
                SELECT id, type, name, properties, created_at, updated_at 
                FROM kg_entities 
                WHERE type = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """
            rows = conn.execute(query, [entity_type, limit]).fetchall()
        else:
            query = """
                SELECT id, type, name, properties, created_at, updated_at 
                FROM kg_entities 
                ORDER BY created_at DESC 
                LIMIT ?
            """
            rows = conn.execute(query, [limit]).fetchall()
        
        entities = []
        for row in rows:
            entities.append(KGEntity(
                id=row[0],
                type=row[1],
                name=row[2],
                properties=json.loads(row[3]) if row[3] else {},
                created_at=row[4],
                updated_at=row[5]
            ))
        
        return entities
    
    async def get_search_results(self, limit: int = 5) -> List[KGSearchResult]:
        """Get recent search results from DuckDB"""
        conn = await self._get_connection()
        
        query = """
            SELECT id, query, results, result_count, search_type, location, created_at
            FROM kg_search_results 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        rows = conn.execute(query, [limit]).fetchall()
        
        results = []
        for row in rows:
            results.append(KGSearchResult(
                id=row[0],
                query=row[1],
                results=row[2],
                result_count=row[3],
                search_type=row[4],
                location=row[5],
                created_at=row[6]
            ))
        
        return results
    
    async def get_relationships(self, limit: int = 10) -> List[KGRelationship]:
        """Get recent relationships from DuckDB"""
        conn = await self._get_connection()
        
        query = """
            SELECT id, source_id, target_id, type, properties, created_at
            FROM kg_relationships 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        rows = conn.execute(query, [limit]).fetchall()
        
        relationships = []
        for row in rows:
            relationships.append(KGRelationship(
                id=row[0],
                source_id=row[1],
                target_id=row[2],
                type=row[3],
                properties=json.loads(row[4]) if row[4] else {},
                created_at=row[5]
            ))
        
        return relationships
    
    async def query_cypher(self, cypher_query: str) -> List[Dict[str, Any]]:
        """
        Execute Cypher-like queries on the knowledge graph.
        
        This is a simplified implementation - for full Cypher support,
        consider integrating with Neo4j or similar graph databases.
        """
        # TODO: Implement basic graph query patterns
        # For now, this is a placeholder for future graph query functionality
        raise NotImplementedError("Cypher queries not yet implemented")
    
    async def get_entity_neighbors(self, entity_id: str, max_depth: int = 1) -> List[KGEntity]:
        """Get entities connected to the given entity within max_depth hops"""
        conn = await self._get_connection()
        
        if max_depth == 1:
            # Direct neighbors only
            query = """
                SELECT DISTINCT e.id, e.type, e.name, e.properties, e.created_at, e.updated_at
                FROM kg_entities e
                JOIN kg_relationships r ON (e.id = r.source_id OR e.id = r.target_id)
                WHERE (r.source_id = ? OR r.target_id = ?) AND e.id != ?
            """
            rows = conn.execute(query, [entity_id, entity_id, entity_id]).fetchall()
        else:
            # For deeper traversal, we'd need recursive CTEs or iterative queries
            # This is a simplified implementation
            raise NotImplementedError("Multi-hop queries not yet implemented")
        
        entities = []
        for row in rows:
            entities.append(KGEntity(
                id=row[0],
                type=row[1], 
                name=row[2],
                properties=json.loads(row[3]) if row[3] else {},
                created_at=row[4],
                updated_at=row[5]
            ))
        
        return entities
    
    async def close(self):
        """Close DuckDB connection"""
        if self._conn:
            self._conn.close()
            self._conn = None


# Factory function for easy storage backend switching
def create_storage_backend(backend_type: str = "memory", **kwargs) -> KGStorageBackend:
    """
    Create a storage backend for knowledge graph.
    
    Args:
        backend_type: "memory" or "duckdb"
        **kwargs: Backend-specific configuration
    
    Returns:
        Storage backend instance
    """
    if backend_type == "memory":
        from .knowledge_graph import InMemoryKGStorage
        return InMemoryKGStorage()
    elif backend_type == "duckdb":
        db_path = kwargs.get("db_path", ":memory:")
        return DuckDBKGStorage(db_path)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")