import json
import networkx as nx
from typing import Dict, List, Any, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3

class TaskKnowledgeGraph:
    """Advanced knowledge graph for task relationships and domain reasoning"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.entity_types = {
            'person': set(),
            'skill': set(),
            'project': set(),
            'technology': set(),
            'task_type': set()
        }
        self.relationship_types = {
            'has_skill': 'person -> skill',
            'works_on': 'person -> project',
            'uses_technology': 'task -> technology',
            'depends_on': 'task -> task',
            'similar_to': 'task -> task',
            'assigned_to': 'task -> person'
        }
        
    def build_from_database(self, db_path: str = "agent.db"):
        """Build knowledge graph from existing database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Load tasks and build initial graph
        cursor.execute("""
            SELECT task, owner, project, status, confidence 
            FROM tasks 
            WHERE task IS NOT NULL
        """)
        
        tasks = cursor.fetchall()
        
        for task, owner, project, status, confidence in tasks:
            # Add nodes
            self._add_task_node(task, confidence, status)
            if owner and owner != "Unassigned":
                self._add_person_node(owner)
                self.graph.add_edge(owner, task, relation='assigned_to', confidence=confidence)
            
            if project:
                self._add_project_node(project)
                self.graph.add_edge(project, task, relation='contains')
        
        # Extract entities and relationships using NLP
        self._extract_entities_and_relationships(tasks)
        
        # Build skill mappings
        self._build_skill_mappings(tasks)
        
        conn.close()
    
    def _add_task_node(self, task_name: str, confidence: float, status: str):
        """Add a task node to the graph"""
        self.graph.add_node(task_name, 
                          type='task',
                          confidence=confidence,
                          status=status,
                          created_at=datetime.now())
    
    def _add_person_node(self, person_name: str):
        """Add a person node to the graph"""
        if person_name not in self.graph:
            self.graph.add_node(person_name, 
                              type='person',
                              skills=set(),
                              task_count=0)
            self.entity_types['person'].add(person_name)
    
    def _add_project_node(self, project_name: str):
        """Add a project node to the graph"""
        if project_name not in self.graph:
            self.graph.add_node(project_name, 
                              type='project',
                              created_at=datetime.now())
            self.entity_types['project'].add(project_name)
    
    def _extract_entities_and_relationships(self, tasks: List[Tuple]):
        """Extract entities and relationships from task descriptions"""
        for task, owner, project, status, confidence in tasks:
            entities = self._extract_entities_from_text(task)
            
            # Add entity nodes and relationships
            for entity, entity_type in entities:
                if entity_type == 'skill':
                    self._add_skill_node(entity)
                    # Connect people who have this skill
                    if owner and owner != "Unassigned":
                        self.graph.add_edge(owner, entity, relation='has_skill')
                        self.graph.add_edge(entity, task, relation='relevant_for')
                
                elif entity_type == 'technology':
                    self._add_technology_node(entity)
                    self.graph.add_edge(task, entity, relation='uses_technology')
    
    def _extract_entities_from_text(self, text: str) -> List[Tuple[str, str]]:
        """Extract entities from task text using patterns"""
        entities = []
        
        # Technology keywords
        tech_keywords = {
            'python', 'javascript', 'react', 'nodejs', 'docker', 'aws', 'azure',
            'mongodb', 'postgresql', 'mysql', 'redis', 'kubernetes', 'git',
            'api', 'rest', 'graphql', 'microservices', 'frontend', 'backend',
            'database', 'testing', 'ci/cd', 'devops', 'security', 'ml', 'ai'
        }
        
        # Skill keywords
        skill_keywords = {
            'development', 'design', 'testing', 'deployment', 'documentation',
            'analysis', 'architecture', 'optimization', 'debugging', 'monitoring',
            'leadership', 'communication', 'planning', 'research'
        }
        
        text_lower = text.lower()
        words = text_lower.split()
        
        for word in words:
            if word in tech_keywords:
                entities.append((word, 'technology'))
            elif word in skill_keywords:
                entities.append((word, 'skill'))
        
        return entities
    
    def _add_skill_node(self, skill_name: str):
        """Add a skill node to the graph"""
        if skill_name not in self.graph:
            self.graph.add_node(skill_name, 
                              type='skill',
                              proficiency_level=0.0)
            self.entity_types['skill'].add(skill_name)
    
    def _add_technology_node(self, tech_name: str):
        """Add a technology node to the graph"""
        if tech_name not in self.graph:
            self.graph.add_node(tech_name, 
                              type='technology',
                              usage_count=0)
            self.entity_types['technology'].add(tech_name)
    
    def _build_skill_mappings(self, tasks: List[Tuple]):
        """Build skill mappings based on task completion history"""
        person_skills = defaultdict(lambda: defaultdict(int))
        
        for task, owner, project, status, confidence in tasks:
            if owner and owner != "Unassigned" and status == "completed":
                entities = self._extract_entities_from_text(task)
                for entity, entity_type in entities:
                    if entity_type == 'skill':
                        person_skills[owner][entity] += 1
        
        # Update skill proficiency levels
        for person, skills in person_skills.items():
            for skill, count in skills.items():
                if person in self.graph and skill in self.graph:
                    current_level = self.graph.nodes[skill].get('proficiency_level', 0)
                    # Simple proficiency calculation
                    new_level = min(1.0, current_level + (count * 0.1))
                    self.graph.nodes[skill]['proficiency_level'] = new_level
    
    def get_task_recommendations(self, task_description: str) -> List[Dict[str, Any]]:
        """Get intelligent task assignment recommendations using graph reasoning"""
        # Extract entities from new task
        entities = self._extract_entities_from_text(task_description)
        
        recommendations = []
        
        # Find candidates based on skills and experience
        candidates = self._find_candidate_owners(entities)
        
        for candidate, score in candidates:
            recommendations.append({
                'owner': candidate,
                'confidence': score,
                'reasoning': self._generate_reasoning(candidate, entities, task_description)
            })
        
        return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)
    
    def _find_candidate_owners(self, required_entities: List[Tuple[str, str]]) -> List[Tuple[str, float]]:
        """Find best candidate owners based on required entities"""
        candidates = defaultdict(float)
        
        # Get all people in the graph
        people = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'person']
        
        for person in people:
            score = 0.0
            
            # Check skill matches
            for entity, entity_type in required_entities:
                if entity_type == 'skill':
                    if self.graph.has_edge(person, entity):
                        proficiency = self.graph.nodes[entity].get('proficiency_level', 0)
                        score += proficiency * 0.4
                
                # Check technology experience
                elif entity_type == 'technology':
                    # Find tasks this person completed with this technology
                    tech_tasks = self._find_tasks_with_technology(person, entity)
                    score += len(tech_tasks) * 0.2
            
            # Consider overall task completion rate
            completion_rate = self._get_completion_rate(person)
            score += completion_rate * 0.3
            
            # Consider current workload
            workload_penalty = self._get_workload_penalty(person)
            score -= workload_penalty * 0.1
            
            candidates[person] = max(0, score)
        
        return [(person, score) for person, score in candidates.items() if score > 0.1]
    
    def _find_tasks_with_technology(self, person: str, technology: str) -> List[str]:
        """Find tasks completed by person using specific technology"""
        tasks = []
        
        # Get all tasks assigned to person
        if person in self.graph:
            for neighbor in self.graph.neighbors(person):
                if self.graph.nodes[neighbor].get('type') == 'task':
                    # Check if task uses this technology
                    if self.graph.has_edge(neighbor, technology):
                        tasks.append(neighbor)
        
        return tasks
    
    def _get_completion_rate(self, person: str) -> float:
        """Calculate task completion rate for a person"""
        total_tasks = 0
        completed_tasks = 0
        
        if person in self.graph:
            for neighbor in self.graph.neighbors(person):
                if self.graph.nodes[neighbor].get('type') == 'task':
                    total_tasks += 1
                    if self.graph.nodes[neighbor].get('status') == 'completed':
                        completed_tasks += 1
        
        return completed_tasks / max(1, total_tasks)
    
    def _get_workload_penalty(self, person: str) -> float:
        """Calculate workload penalty based on current active tasks"""
        active_tasks = 0
        
        if person in self.graph:
            for neighbor in self.graph.neighbors(person):
                if (self.graph.nodes[neighbor].get('type') == 'task' and 
                    self.graph.nodes[neighbor].get('status') in ['pending', 'in_progress']):
                    active_tasks += 1
        
        # Penalty increases with more active tasks
        return min(0.5, active_tasks * 0.1)
    
    def _generate_reasoning(self, candidate: str, entities: List[Tuple[str, str]], task_desc: str) -> str:
        """Generate human-readable reasoning for recommendation"""
        reasons = []
        
        # Skill-based reasoning
        skills = [e for e, t in entities if t == 'skill']
        if skills:
            skill_matches = []
            for skill in skills:
                if self.graph.has_edge(candidate, skill):
                    proficiency = self.graph.nodes[skill].get('proficiency_level', 0)
                    skill_matches.append(f"{skill} (proficiency: {proficiency:.1f})")
            
            if skill_matches:
                reasons.append(f"Has relevant skills: {', '.join(skill_matches)}")
        
        # Experience-based reasoning
        tech_entities = [e for e, t in entities if t == 'technology']
        if tech_entities:
            for tech in tech_entities:
                related_tasks = self._find_tasks_with_technology(candidate, tech)
                if related_tasks:
                    reasons.append(f"Completed {len(related_tasks)} tasks with {tech}")
        
        # Performance-based reasoning
        completion_rate = self._get_completion_rate(candidate)
        if completion_rate > 0.8:
            reasons.append(f"High completion rate: {completion_rate:.1%}")
        
        return "; ".join(reasons) if reasons else "Based on overall experience"
    
    def find_similar_tasks(self, task_description: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar tasks using graph-based similarity"""
        entities = self._extract_entities_from_text(task_description)
        
        similar_tasks = []
        
        # Get all task nodes
        tasks = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'task']
        
        for task in tasks:
            similarity = self._calculate_task_similarity(task_description, task, entities)
            if similarity > 0.3:  # Threshold for similarity
                similar_tasks.append({
                    'task': task,
                    'similarity': similarity,
                    'owner': self._get_task_owner(task),
                    'status': self.graph.nodes[task].get('status', 'unknown')
                })
        
        return sorted(similar_tasks, key=lambda x: x['similarity'], reverse=True)[:limit]
    
    def _calculate_task_similarity(self, new_task: str, existing_task: str, new_entities: List[Tuple[str, str]]) -> float:
        """Calculate similarity between tasks"""
        # Extract entities from existing task
        existing_entities = self._extract_entities_from_text(existing_task)
        
        # Entity overlap score
        new_entity_set = set(e for e, t in new_entities)
        existing_entity_set = set(e for e, t in existing_entities)
        
        if not new_entity_set or not existing_entity_set:
            return 0.0
        
        overlap = len(new_entity_set.intersection(existing_entity_set))
        union = len(new_entity_set.union(existing_entity_set))
        
        entity_similarity = overlap / union if union > 0 else 0.0
        
        # Text similarity (simple word overlap)
        new_words = set(new_task.lower().split())
        existing_words = set(existing_task.lower().split())
        
        text_overlap = len(new_words.intersection(existing_words))
        text_union = len(new_words.union(existing_words))
        text_similarity = text_overlap / text_union if text_union > 0 else 0.0
        
        # Weighted combination
        return (entity_similarity * 0.7) + (text_similarity * 0.3)
    
    def _get_task_owner(self, task: str) -> str:
        """Get the current owner of a task"""
        for predecessor in self.graph.predecessors(task):
            if self.graph.nodes[predecessor].get('type') == 'person':
                return predecessor
        return "Unassigned"
    
    def get_insights(self) -> Dict[str, Any]:
        """Generate insights from the knowledge graph"""
        insights = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'entity_distribution': {k: len(v) for k, v in self.entity_types.items()},
            'most_connected_nodes': [],
            'skill_coverage': {},
            'technology_usage': {}
        }
        
        # Most connected nodes
        degree_centrality = nx.degree_centrality(self.graph)
        insights['most_connected_nodes'] = sorted(
            degree_centrality.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # Skill coverage
        for skill in self.entity_types['skill']:
            if skill in self.graph:
                users = list(self.graph.predecessors(skill))
                insights['skill_coverage'][skill] = len(users)
        
        # Technology usage
        for tech in self.entity_types['technology']:
            if tech in self.graph:
                tasks = list(self.graph.predecessors(tech))
                insights['technology_usage'][tech] = len(tasks)
        
        return insights
