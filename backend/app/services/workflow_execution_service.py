from sqlalchemy.orm import Session
from typing import Dict, Any, List
import time

from app.models import Workflow, WorkflowDocument, Document
from app.services.document_service import DocumentService
from app.services.llm_service import LLMService

class WorkflowExecutionService:
    def __init__(self):
        self.document_service = DocumentService()
        self.llm_service = LLMService()
    
    async def execute_workflow(
        self, 
        workflow_id: int, 
        query: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Execute a complete workflow"""
        start_time = time.time()
        
        # Get workflow
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow_data = workflow.workflow_data
        nodes = workflow_data.get('nodes', [])
        edges = workflow_data.get('edges', [])
        
        # Build execution order
        execution_order = self._build_execution_order(nodes, edges)
        
        # Execute workflow
        context = {"query": query}
        execution_log = []
        
        for node_id in execution_order:
            node = next((n for n in nodes if n['id'] == node_id), None)
            if not node:
                continue
            
            component_type = node['type']
            component_data = node.get('data', {})
            
            # Execute component
            step_result = await self._execute_component(
                component_type, 
                component_data, 
                context, 
                workflow_id, 
                db
            )
            
            execution_log.append({
                "component": component_type,
                "node_id": node_id,
                "result": step_result,
                "timestamp": time.time()
            })
            
            # Update context with results
            context.update(step_result)
        
        execution_time = time.time() - start_time
        
        return {
            "response": context.get("final_response", "No response generated"),
            "execution_time": execution_time,
            "execution_log": execution_log,
            "context": context
        }
    
    def _build_execution_order(self, nodes: List[Dict], edges: List[Dict]) -> List[str]:
        """Build the execution order based on node connections"""
        # Simple topological sort
        in_degree = {node['id']: 0 for node in nodes}
        graph = {node['id']: [] for node in nodes}
        
        # Build graph
        for edge in edges:
            source = edge['source']
            target = edge['target']
            graph[source].append(target)
            in_degree[target] += 1
        
        # Find starting nodes (usually user-query)
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            current = queue.pop(0)
            execution_order.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return execution_order
    
    async def _execute_component(
        self, 
        component_type: str, 
        component_data: Dict[str, Any], 
        context: Dict[str, Any], 
        workflow_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Execute a single component"""
        
        if component_type == "user-query":
            return await self._execute_user_query(component_data, context)
        
        elif component_type == "knowledge-base":
            return await self._execute_knowledge_base(component_data, context, workflow_id, db)
        
        elif component_type == "llm-engine":
            return await self._execute_llm_engine(component_data, context)
        
        elif component_type == "output":
            return await self._execute_output(component_data, context)
        
        else:
            raise ValueError(f"Unknown component type: {component_type}")
    
    async def _execute_user_query(
        self, 
        component_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute user query component"""
        # User query component just passes the query through
        return {
            "user_query": context.get("query", ""),
            "component_output": context.get("query", "")
        }
    
    async def _execute_knowledge_base(
        self, 
        component_data: Dict[str, Any], 
        context: Dict[str, Any], 
        workflow_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """Execute knowledge base component"""
        config = component_data.get('config', {})
        
        # Get linked documents
        workflow_docs = db.query(WorkflowDocument).filter(
            WorkflowDocument.workflow_id == workflow_id
        ).all()
        
        document_ids = [wd.document_id for wd in workflow_docs]
        
        if not document_ids:
            return {
                "knowledge_base_results": [],
                "context_text": "",
                "component_output": "No documents linked to workflow"
            }
        
        # Search documents
        query = context.get("query", "")
        search_limit = config.get("search_limit", 5)
        similarity_threshold = config.get("similarity_threshold", 0.7)
        
        try:
            search_results = await self.document_service.search_documents(
                query, 
                document_ids, 
                search_limit, 
                similarity_threshold
            )
            
            # Build context text
            context_text = "\n\n".join([
                f"Source: {result['metadata']['filename']}\nContent: {result['content']}"
                for result in search_results
            ])
            
            return {
                "knowledge_base_results": search_results,
                "context_text": context_text,
                "component_output": context_text
            }
            
        except Exception as e:
            return {
                "knowledge_base_results": [],
                "context_text": "",
                "component_output": f"Error searching documents: {str(e)}"
            }
    
    async def _execute_llm_engine(
        self, 
        component_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute LLM engine component"""
        config = component_data.get('config', {})
        
        query = context.get("query", "")
        knowledge_context = context.get("context_text", "")
        
        model = config.get("model", "gemini-1.5-flash")  # Use Gemini Pro as default
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 1000)
        custom_prompt = config.get("custom_prompt", "")
        enable_web_search = config.get("enable_web_search", False)
        web_search_queries = config.get("web_search_queries", 3)
        
        try:
            if enable_web_search:
                result = await self.llm_service.generate_response_with_web_search(
                    query,
                    knowledge_context,
                    model,
                    temperature,
                    max_tokens,
                    custom_prompt,
                    web_search_queries
                )
            else:
                result = await self.llm_service.generate_response(
                    query,
                    knowledge_context,
                    model,
                    temperature,
                    max_tokens,
                    custom_prompt
                )
            
            return {
                "llm_response": result["response"],
                "llm_model": result["model"],
                "llm_usage": result["usage"],
                "web_results": result.get("web_results", []),
                "component_output": result["response"]
            }
            
        except Exception as e:
            return {
                "llm_response": f"Error generating response: {str(e)}",
                "llm_model": model,
                "llm_usage": {},
                "web_results": [],
                "component_output": f"Error: {str(e)}"
            }
    
    async def _execute_output(
        self, 
        component_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute output component"""
        config = component_data.get('config', {})
        
        # Get the response from LLM or previous component
        response = context.get("llm_response") or context.get("component_output", "")
        
        format_type = config.get("format", "markdown")
        show_sources = config.get("show_sources", True)
        show_execution_time = config.get("show_execution_time", False)
        
        # Format response
        formatted_response = response
        
        if show_sources and context.get("knowledge_base_results"):
            sources = []
            for result in context["knowledge_base_results"]:
                sources.append(f"- {result['metadata']['filename']} (similarity: {result['similarity']:.2f})")
            
            if sources:
                formatted_response += f"\n\n**Sources:**\n" + "\n".join(sources)
        
        if show_execution_time and context.get("execution_time"):
            formatted_response += f"\n\n*Execution time: {context['execution_time']:.2f}s*"
        
        return {
            "final_response": formatted_response,
            "format": format_type,
            "component_output": formatted_response
        }