"""
Knowledge Graph Visualization
Renders knowledge graphs as ASCII art and structured text for development insights
"""

import logging
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
from .knowledge_graph import KnowledgeGraphManager, KGEntity, KGRelationship, KGSearchResult

logger = logging.getLogger(__name__)


class KGVisualizer:
    """Renders knowledge graphs in various visual formats for development insights"""
    
    def __init__(self, kg_manager: KnowledgeGraphManager):
        self.kg_manager = kg_manager
    
    async def render_ascii_graph(self, max_entities: int = 15, max_relationships: int = 10) -> str:
        """
        Render the knowledge graph as ASCII art showing entities and relationships
        
        Args:
            max_entities: Maximum entities to show (most recent)
            max_relationships: Maximum relationships to show
            
        Returns:
            ASCII art representation of the knowledge graph
        """
        try:
            entities = await self.kg_manager.query_entities()
            relationships = await self.kg_manager.storage.get_relationships()
            searches = await self.kg_manager.storage.get_search_results()
            
            # Limit to most recent items
            entities = entities[:max_entities]
            relationships = relationships[:max_relationships]
            searches = searches[:5]  # Recent searches
            
            if not entities and not searches:
                return "📊 Knowledge Graph: Empty\n"
            
            output = []
            output.append("=" * 80)
            output.append("📊 KNOWLEDGE GRAPH VISUALIZATION")
            output.append("=" * 80)
            
            # Show graph statistics
            stats = await self.kg_manager.get_stats()
            output.append(f"📈 Stats: {stats['total_entities']} entities, {stats['total_relationships']} relationships, {stats['total_searches']} searches")
            output.append("")
            
            # Render recent searches first (these drive everything)
            if searches:
                output.append("🔍 RECENT SEARCHES:")
                for i, search in enumerate(searches):
                    time_ago = self._time_ago(search.created_at)
                    result_preview = search.results[:100] + "..." if len(search.results) > 100 else search.results
                    output.append(f"  [{i+1}] 🔍 \"{search.query}\" ({search.search_type}) - {time_ago}")
                    output.append(f"      └─ {search.result_count} results: {result_preview}")
                output.append("")
            
            # Group entities by type for cleaner visualization
            entities_by_type = {}
            for entity in entities:
                if entity.type not in entities_by_type:
                    entities_by_type[entity.type] = []
                entities_by_type[entity.type].append(entity)
            
            # Render entities grouped by type
            if entities_by_type:
                output.append("🏷️  ENTITIES BY TYPE:")
                for entity_type, type_entities in entities_by_type.items():
                    emoji = self._get_entity_emoji(entity_type)
                    output.append(f"  {emoji} {entity_type.upper()} ({len(type_entities)}):")
                    
                    for entity in type_entities[:8]:  # Limit per type
                        time_ago = self._time_ago(entity.created_at)
                        props_preview = self._format_properties(entity.properties)
                        output.append(f"    • {entity.name} - {time_ago}")
                        if props_preview:
                            output.append(f"      └─ {props_preview}")
                    
                    if len(type_entities) > 8:
                        output.append(f"    ... and {len(type_entities) - 8} more")
                    output.append("")
            
            # Show relationships if any exist
            if relationships:
                output.append("🔗 RELATIONSHIPS:")
                relationship_map = self._build_relationship_map(entities, relationships)
                
                for rel in relationships[:max_relationships]:
                    source_name = relationship_map.get(rel.source_id, f"Entity-{rel.source_id[:8]}")
                    target_name = relationship_map.get(rel.target_id, f"Entity-{rel.target_id[:8]}")
                    time_ago = self._time_ago(rel.created_at)
                    
                    output.append(f"  • {source_name} --[{rel.type}]--> {target_name} - {time_ago}")
                
                if len(relationships) > max_relationships:
                    output.append(f"  ... and {len(relationships) - max_relationships} more relationships")
                output.append("")
            
            # Show knowledge flow (how entities connect to searches)
            flow_analysis = await self._analyze_knowledge_flow(entities, searches, relationships)
            if flow_analysis:
                output.append("🌊 KNOWLEDGE FLOW:")
                output.extend(flow_analysis)
                output.append("")
            
            output.append("=" * 80)
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error rendering ASCII graph: {e}")
            return f"❌ Error rendering knowledge graph: {e}"
    
    async def render_compact_summary(self) -> str:
        """Render a compact one-line summary of the KG state"""
        try:
            stats = await self.kg_manager.get_stats()
            
            if stats['total_entities'] == 0 and stats['total_searches'] == 0:
                return "🧠 KG: Empty"
            
            # Get most recent items for context
            recent_searches = await self.kg_manager.storage.get_search_results(limit=2)
            recent_entities = await self.kg_manager.query_entities(limit=3)
            
            summary_parts = [f"🧠 KG: {stats['total_entities']}E"]
            
            if stats['total_searches'] > 0:
                summary_parts.append(f"{stats['total_searches']}S")
            
            if stats['total_relationships'] > 0:
                summary_parts.append(f"{stats['total_relationships']}R")
            
            # Add recent activity
            if recent_searches:
                latest_search = recent_searches[0]
                query_preview = latest_search.query[:20] + "..." if len(latest_search.query) > 20 else latest_search.query
                summary_parts.append(f"last: \"{query_preview}\"")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            return f"🧠 KG: Error - {e}"
    
    async def render_structured_dump(self) -> str:
        """Render complete structured dump of KG for debugging"""
        try:
            entities = await self.kg_manager.query_entities()
            relationships = await self.kg_manager.storage.get_relationships()
            searches = await self.kg_manager.storage.get_search_results()
            
            output = []
            output.append("🗂️  COMPLETE KNOWLEDGE GRAPH DUMP")
            output.append("=" * 60)
            
            # Dump all searches
            if searches:
                output.append(f"\n📋 SEARCHES ({len(searches)}):")
                for i, search in enumerate(searches):
                    output.append(f"  [{i+1}] ID: {search.id}")
                    output.append(f"      Query: {search.query}")  
                    output.append(f"      Type: {search.search_type}")
                    output.append(f"      Results: {len(search.results)} chars")
                    output.append(f"      Count: {search.result_count}")
                    output.append(f"      Time: {search.created_at}")
                    output.append("")
            
            # Dump all entities
            if entities:
                output.append(f"\n📋 ENTITIES ({len(entities)}):")
                for i, entity in enumerate(entities):
                    output.append(f"  [{i+1}] ID: {entity.id}")
                    output.append(f"      Name: {entity.name}")
                    output.append(f"      Type: {entity.type}")
                    output.append(f"      Properties: {entity.properties}")
                    output.append(f"      Created: {entity.created_at}")
                    output.append("")
            
            # Dump all relationships
            if relationships:
                output.append(f"\n📋 RELATIONSHIPS ({len(relationships)}):")
                for i, rel in enumerate(relationships):
                    output.append(f"  [{i+1}] ID: {rel.id}")
                    output.append(f"      {rel.source_id} --[{rel.type}]--> {rel.target_id}")
                    output.append(f"      Properties: {rel.properties}")
                    output.append(f"      Created: {rel.created_at}")
                    output.append("")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"❌ Error creating structured dump: {e}"
    
    def _time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as 'X seconds/minutes ago'"""
        try:
            now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
            delta = now - timestamp
            
            if delta.total_seconds() < 60:
                return f"{int(delta.total_seconds())}s ago"
            elif delta.total_seconds() < 3600:
                return f"{int(delta.total_seconds() // 60)}m ago"
            else:
                return f"{int(delta.total_seconds() // 3600)}h ago"
        except:
            return "just now"
    
    def _get_entity_emoji(self, entity_type: str) -> str:
        """Get emoji for entity type"""
        emoji_map = {
            "search_action": "🔍",
            "browse_action": "🌐", 
            "function_call": "⚙️",
            "email_action": "📧",
            "person": "👤",
            "project": "📋",
            "finding": "💡",
            "browse_finding": "🔎",
            "calculation": "🧮"
        }
        return emoji_map.get(entity_type, "📦")
    
    def _format_properties(self, properties: Dict) -> str:
        """Format entity properties for display"""
        if not properties:
            return ""
        
        # Show key properties in a compact format
        key_props = []
        for key, value in properties.items():
            if key in ['success', 'result_count', 'site_count', 'content_length']:
                key_props.append(f"{key}: {value}")
            elif key == 'urls' and isinstance(value, list):
                key_props.append(f"urls: {len(value)} sites")
        
        return ", ".join(key_props[:3])  # Limit to 3 key properties
    
    def _build_relationship_map(self, entities: List[KGEntity], relationships: List[KGRelationship]) -> Dict[str, str]:
        """Build a map of entity IDs to names for relationship display"""
        entity_map = {entity.id: entity.name for entity in entities}
        return entity_map
    
    async def _analyze_knowledge_flow(self, entities: List[KGEntity], searches: List[KGSearchResult], relationships: List[KGRelationship]) -> List[str]:
        """Analyze how knowledge flows through the graph"""
        if not searches and not entities:
            return []
        
        flow = []
        
        # Show search -> entity flow
        if searches and entities:
            search_count = len(searches)
            entity_count = len(entities)
            rel_count = len(relationships)
            
            flow.append(f"  📥 {search_count} searches generated {entity_count} entities")
            
            if rel_count > 0:
                flow.append(f"  🔗 {rel_count} relationships connect the knowledge")
            
            # Show entity type diversity
            entity_types = set(e.type for e in entities)
            if len(entity_types) > 1:
                flow.append(f"  🏷️  Knowledge spans {len(entity_types)} types: {', '.join(sorted(entity_types))}")
        
        return flow


async def create_kg_visualizer(kg_manager: KnowledgeGraphManager) -> KGVisualizer:
    """Factory function to create a KG visualizer"""
    return KGVisualizer(kg_manager)


async def render_kg_snapshot(kg_manager: KnowledgeGraphManager, context: str = "") -> str:
    """
    Quick function to render a KG snapshot with context
    
    Args:
        kg_manager: The knowledge graph manager
        context: Context string (e.g., "after search", "before response")
        
    Returns:
        Formatted KG visualization
    """
    visualizer = KGVisualizer(kg_manager)
    
    header = f"📸 KG SNAPSHOT {context.upper()}" if context else "📸 KG SNAPSHOT"
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    snapshot = []
    snapshot.append(f"\n{header} @ {timestamp}")
    snapshot.append(await visualizer.render_ascii_graph())
    
    return "\n".join(snapshot)