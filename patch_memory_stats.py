#!/usr/bin/env python3
"""
Patch script to fix memory statistics method
"""

import os
import sys

def patch_memory_stats():
    """Patch the memory statistics method to work properly."""
    
    print("🔧 Patching Memory Statistics Method")
    print("=" * 50)
    
    # Read the current manager.py file
    manager_file = "/app/src/agentic_worm/memory/manager.py"
    
    try:
        with open(manager_file, 'r') as f:
            content = f.read()
        
        # Check if the method is already using real queries
        if "FOR doc IN @@collection FILTER doc.worm_id == @worm_id" in content:
            print("✅ Statistics method already has database queries")
        else:
            print("⚠️ Statistics method needs patching")
            
        # Create a simple working version
        new_stats_method = '''    async def get_memory_statistics(self, worm_id: str) -> Dict[str, Any]:
        """Get real memory statistics for a worm from the database."""
        stats = {
            "episodic_count": 0,
            "semantic_count": 0,
            "spatial_count": 0,
            "procedural_count": 0,
            "total_experiences": 0,
            "success_rate": 0.0,
            "locations_visited": 0,
            "strategies_learned": 0,
            "knowledge_facts": 0,
            "memory_confidence": 0.5,
            "insights": ["Loading memory statistics..."]
        }
        
        try:
            if not self.storage or not self.storage.db:
                stats["insights"] = ["Memory system not connected"]
                return stats
            
            # Simple direct queries for each collection
            try:
                # Count experiences
                cursor = self.storage.db.aql.execute(
                    "FOR doc IN experiences FILTER doc.worm_id == @worm_id COLLECT WITH COUNT INTO length RETURN length",
                    bind_vars={"worm_id": worm_id}
                )
                episodic_count = list(cursor)[0] if cursor else 0
                stats["episodic_count"] = episodic_count
                stats["total_experiences"] = episodic_count
                
                # Count spatial memories
                cursor = self.storage.db.aql.execute(
                    "FOR doc IN spatial_memories FILTER doc.worm_id == @worm_id COLLECT WITH COUNT INTO length RETURN length",
                    bind_vars={"worm_id": worm_id}
                )
                spatial_count = list(cursor)[0] if cursor else 0
                stats["spatial_count"] = spatial_count
                stats["locations_visited"] = spatial_count
                
                # Count strategies
                cursor = self.storage.db.aql.execute(
                    "FOR doc IN strategies FILTER doc.worm_id == @worm_id COLLECT WITH COUNT INTO length RETURN length",
                    bind_vars={"worm_id": worm_id}
                )
                strategy_count = list(cursor)[0] if cursor else 0
                stats["procedural_count"] = strategy_count
                stats["strategies_learned"] = strategy_count
                
                # Count knowledge facts
                cursor = self.storage.db.aql.execute(
                    "FOR doc IN knowledge_facts FILTER doc.worm_id == @worm_id COLLECT WITH COUNT INTO length RETURN length",
                    bind_vars={"worm_id": worm_id}
                )
                knowledge_count = list(cursor)[0] if cursor else 0
                stats["semantic_count"] = knowledge_count
                stats["knowledge_facts"] = knowledge_count
                
                # Calculate success rate
                if stats["total_experiences"] > 0:
                    cursor = self.storage.db.aql.execute(
                        "FOR doc IN experiences FILTER doc.worm_id == @worm_id AND doc.outcome == 'success' COLLECT WITH COUNT INTO length RETURN length",
                        bind_vars={"worm_id": worm_id}
                    )
                    success_count = list(cursor)[0] if cursor else 0
                    stats["success_rate"] = success_count / stats["total_experiences"]
                
                # Update memory confidence
                if stats["total_experiences"] > 0:
                    stats["memory_confidence"] = min(0.9, 0.5 + (stats["total_experiences"] * 0.05))
                
                # Generate insights
                insights = []
                if stats["total_experiences"] == 0:
                    insights.append("No experiences recorded yet")
                else:
                    insights.append(f"Learned from {stats['total_experiences']} experiences")
                    
                if stats["success_rate"] > 0.7:
                    insights.append("High success rate - effective strategies")
                elif stats["success_rate"] > 0.4:
                    insights.append("Moderate success rate - learning in progress")
                elif stats["total_experiences"] > 0:
                    insights.append("Low success rate - adapting strategies")
                    
                if stats["locations_visited"] > 5:
                    insights.append("Experienced explorer")
                elif stats["locations_visited"] > 0:
                    insights.append("Building spatial map")
                    
                if stats["strategies_learned"] > 0:
                    insights.append(f"Developed {stats['strategies_learned']} strategies")
                    
                stats["insights"] = insights if insights else ["Memory system active"]
                
                print(f"📊 Computed stats: episodic={stats['episodic_count']}, spatial={stats['spatial_count']}, success_rate={stats['success_rate']:.2f}")
                
            except Exception as e:
                print(f"❌ Query error: {e}")
                stats["insights"] = [f"Query error: {str(e)[:50]}"]
            
        except Exception as e:
            print(f"❌ Statistics error: {e}")
            stats["insights"] = [f"Error: {str(e)[:50]}"]
        
        return stats'''
        
        # Find and replace the method
        import re
        
        # Pattern to match the entire method
        pattern = r'async def get_memory_statistics\(self, worm_id: str\) -> Dict\[str, Any\]:.*?(?=\n    async def|\n    def|\nclass|\Z)'
        
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, new_stats_method, content, flags=re.DOTALL)
            
            # Write back to file
            with open(manager_file, 'w') as f:
                f.write(new_content)
            
            print("✅ Memory statistics method patched successfully")
            return True
        else:
            print("❌ Could not find method to patch")
            return False
            
    except Exception as e:
        print(f"❌ Patch failed: {e}")
        return False

if __name__ == "__main__":
    success = patch_memory_stats()
    print(f"\nPatch result: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1) 