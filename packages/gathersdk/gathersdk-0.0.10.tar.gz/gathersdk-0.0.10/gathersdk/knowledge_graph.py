"""
Knowledge Graph Management for GatherSDK

Provides automatic knowledge graph tracking for agent function calls with
flexible storage backends (in-memory → DuckDB → external systems).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Protocol
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import json
import uuid


@dataclass
class KGEntity:
    """Standard knowledge graph entity"""
    id: str
    type: str
    name: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass  
class KGRelationship:
    """Standard knowledge graph relationship"""
    id: str
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any]
    created_at: datetime


@dataclass
class KGSearchResult:
    """Search result with metadata"""
    id: str
    query: str
    results: str
    result_count: int
    search_type: str
    location: Optional[str]
    created_at: datetime


class KGStorageBackend(Protocol):
    """Protocol for knowledge graph storage backends"""
    
    async def store_entity(self, entity: KGEntity) -> None:
        """Store an entity"""
        ...
        
    async def store_relationship(self, relationship: KGRelationship) -> None:
        """Store a relationship"""
        ...
        
    async def store_search_result(self, search_result: KGSearchResult) -> None:
        """Store a search result"""
        ...
        
    async def get_entities(self, limit: int = 10, entity_type: Optional[str] = None) -> List[KGEntity]:
        """Get recent entities"""
        ...
        
    async def get_search_results(self, limit: int = 5) -> List[KGSearchResult]:
        """Get recent search results"""
        ...
        
    async def get_relationships(self, limit: int = 10) -> List[KGRelationship]:
        """Get recent relationships"""
        ...


class InMemoryKGStorage:
    """In-memory knowledge graph storage - fast and simple"""
    
    def __init__(self):
        self.entities: List[KGEntity] = []
        self.relationships: List[KGRelationship] = []
        self.search_results: List[KGSearchResult] = []
    
    async def store_entity(self, entity: KGEntity) -> None:
        # Update existing or add new
        for i, existing in enumerate(self.entities):
            if existing.id == entity.id:
                self.entities[i] = entity
                return
        self.entities.append(entity)
    
    async def store_relationship(self, relationship: KGRelationship) -> None:
        self.relationships.append(relationship)
    
    async def store_search_result(self, search_result: KGSearchResult) -> None:
        self.search_results.append(search_result)
    
    async def get_entities(self, limit: int = 10, entity_type: Optional[str] = None) -> List[KGEntity]:
        entities = self.entities
        if entity_type:
            entities = [e for e in entities if e.type == entity_type]
        return entities[-limit:] if entities else []
    
    async def get_search_results(self, limit: int = 5) -> List[KGSearchResult]:
        return self.search_results[-limit:] if self.search_results else []
    
    async def get_relationships(self, limit: int = 10) -> List[KGRelationship]:
        return self.relationships[-limit:] if self.relationships else []


class KnowledgeGraphManager:
    """
    Main interface for knowledge graph operations.
    
    Automatically tracks function calls, search results, and entities.
    Designed for easy upgrade from in-memory to persistent storage.
    """
    
    def __init__(self, storage: KGStorageBackend = None):
        self.storage = storage or InMemoryKGStorage()
    
    async def add_search(
        self, 
        query: str, 
        results: str, 
        search_type: str = "web",
        location: Optional[str] = None
    ) -> str:
        """Add search results to knowledge graph"""
        search_result = KGSearchResult(
            id=f"search_{uuid.uuid4().hex[:8]}",
            query=query,
            results=results,
            result_count=results.count("URL:"),
            search_type=search_type,
            location=location,
            created_at=datetime.now(timezone.utc)
        )
        
        await self.storage.store_search_result(search_result)
        return search_result.id
    
    async def add_entity(
        self,
        name: str,
        entity_type: str,
        properties: Dict[str, Any] = None,
        entity_id: Optional[str] = None
    ) -> str:
        """Add entity to knowledge graph"""
        now = datetime.now(timezone.utc)
        entity = KGEntity(
            id=entity_id or f"{entity_type}_{uuid.uuid4().hex[:8]}",
            type=entity_type,
            name=name,
            properties=properties or {},
            created_at=now,
            updated_at=now
        )
        
        await self.storage.store_entity(entity)
        return entity.id
    
    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Dict[str, Any] = None
    ) -> str:
        """Add relationship between entities"""
        relationship = KGRelationship(
            id=f"rel_{uuid.uuid4().hex[:8]}",
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            properties=properties or {},
            created_at=datetime.now(timezone.utc)
        )
        
        await self.storage.store_relationship(relationship)
        return relationship.id
    
    async def add_function_call(
        self,
        function_name: str,
        args: Dict[str, Any],
        result: str,
        execution_time: float = None
    ) -> str:
        """Add function call as entity with metadata"""
        return await self.add_entity(
            name=function_name,
            entity_type="function_call",
            properties={
                "args": args,
                "result_summary": result[:200] if result else "",
                "execution_time": execution_time,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def render_context(self, max_searches: int = 2, max_actions: int = 5) -> str:
        """Render knowledge graph as agent-readable context"""
        context_parts = []
        
        # Recent search results
        search_results = await self.storage.get_search_results(limit=max_searches)
        if search_results:
            context_parts.append("--- RECENT SEARCH RESULTS ---")
            for search in search_results:
                context_parts.append(f"Query: {search.query} ({search.result_count} results)")
                # Show first 3 URLs
                lines = search.results.split('\n')
                url_lines = [line for line in lines if 'URL:' in line][:3]
                for url_line in url_lines:
                    context_parts.append(f"  {url_line.strip()}")
            context_parts.append("")
        
        # Recent actions summary
        entities = await self.storage.get_entities(limit=max_actions)
        if entities:
            actions = []
            for entity in entities:
                if entity.type == "search_action":
                    result_count = entity.properties.get("result_count", 0)
                    actions.append(f"Search({result_count})")
                elif entity.type == "browse_action":
                    site_count = entity.properties.get("site_count", 0)
                    actions.append(f"Browse({site_count})")
                elif entity.type == "function_call":
                    actions.append(f"{entity.name}()")
            
            if actions:
                context_parts.append(f"ACTIONS: {' → '.join(actions)}")
                context_parts.append("")
        
        return '\n'.join(context_parts)
    
    async def query_entities(self, entity_type: Optional[str] = None, name_contains: Optional[str] = None, limit: Optional[int] = None) -> List[KGEntity]:
        """Query entities by type or name"""
        storage_limit = limit or 100
        entities = await self.storage.get_entities(limit=storage_limit, entity_type=entity_type)
        
        if name_contains:
            entities = [e for e in entities if name_contains.lower() in e.name.lower()]
        
        return entities
    
    async def get_stats(self) -> Dict[str, int]:
        """Get knowledge graph statistics"""
        entities = await self.storage.get_entities(limit=1000)
        relationships = await self.storage.get_relationships(limit=1000)
        search_results = await self.storage.get_search_results(limit=1000)
        
        return {
            "total_entities": len(entities),
            "total_relationships": len(relationships),
            "total_searches": len(search_results),
            "entity_types": len(set(e.type for e in entities)) if entities else 0
        }


# Convenience function for creating KG manager
def create_kg_manager(storage_backend: Optional[KGStorageBackend] = None) -> KnowledgeGraphManager:
    """Create a knowledge graph manager with optional custom storage"""
    return KnowledgeGraphManager(storage_backend)