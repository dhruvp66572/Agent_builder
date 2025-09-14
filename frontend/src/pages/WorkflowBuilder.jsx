import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  useReactFlow,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { Button } from '../components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import ComponentLibrary from '../components/workflow/ComponentLibrary';
import ConfigurationPanel from '../components/workflow/ConfigurationPanel';
import ChatInterface from '../components/workflow/ChatInterface';
import UserQueryComponent from '../components/workflow/UserQueryComponent';
import KnowledgeBaseComponent from '../components/workflow/KnowledgeBaseComponent';
import LLMEngineComponent from '../components/workflow/LLMEngineComponent';
import OutputComponent from '../components/workflow/OutputComponent';

import { Play, Save, MessageSquare, Home, Check, AlertCircle } from 'lucide-react';
import api from '../lib/api';
import { useToast } from '../components/ui/toast';

const nodeTypes = {
  'user-query': UserQueryComponent,
  'knowledge-base': KnowledgeBaseComponent,
  'llm-engine': LLMEngineComponent,
  'output': OutputComponent,
};

let id = 0;
const getId = () => `dndnode_${id++}`;

const WorkflowBuilderFlow = () => {
  const { id: workflowId } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const reactFlowWrapper = useRef(null);
  const { project } = useReactFlow();

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [showChatDialog, setShowChatDialog] = useState(false);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validation, setValidation] = useState({ valid: true, errors: [] });

  useEffect(() => {
    if (workflowId) {
      loadWorkflow(workflowId);
    } else {
      // Create new workflow
      createNewWorkflow();
    }
  }, [workflowId]);

  const loadWorkflow = async (id) => {
    try {
      const response = await api.get(`/api/workflows/${id}`);
      const workflowData = response.data;
      setWorkflow(workflowData);
      
      if (workflowData.workflow_data) {
        const { nodes: loadedNodes = [], edges: loadedEdges = [] } = workflowData.workflow_data;
        setNodes(loadedNodes);
        setEdges(loadedEdges);
      }
    } catch (error) {
      addToast({
        title: 'Error',
        description: 'Failed to load workflow',
        variant: 'destructive',
      });
      navigate('/');
    }
  };

  const createNewWorkflow = async () => {
    try {
      const response = await api.post('/api/workflows/', {
        name: 'Untitled Workflow',
        description: '',
        workflow_data: { nodes: [], edges: [] },
      });
      setWorkflow(response.data);
    } catch (error) {
      addToast({
        title: 'Error',
        description: 'Failed to create workflow',
        variant: 'destructive',
      });
    }
  };

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');

      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode = {
        id: getId(),
        type,
        position,
        data: {
          config: getDefaultConfig(type),
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [project]
  );

  const getDefaultConfig = (type) => {
    switch (type) {
      case 'user-query':
        return { placeholder: 'Enter your question...', validation: false };
      case 'knowledge-base':
        return { documents: [], search_limit: 5, similarity_threshold: 0.7 };
      case 'llm-engine':
        return {
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          max_tokens: 1000,
          custom_prompt: '',
          enable_web_search: false,
          web_search_queries: 3,
        };
      case 'output':
        return { format: 'markdown', show_sources: true, show_execution_time: false };
      default:
        return {};
    }
  };

  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const onConfigUpdate = useCallback((nodeId, config) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, config } } : node
      )
    );
  }, []);

  const saveWorkflow = async () => {
    if (!workflow) return;

    setSaving(true);
    try {
      const workflowData = {
        nodes: nodes.map(node => ({
          ...node,
          selected: false // Remove selection state before saving
        })),
        edges: edges.map(edge => ({
          ...edge,
          selected: false
        }))
      };

      await api.put(`/api/workflows/${workflow.id}`, {
        workflow_data: workflowData,
      });

      addToast({
        title: 'Success',
        description: 'Workflow saved successfully',
      });
    } catch (error) {
      addToast({
        title: 'Error',
        description: 'Failed to save workflow',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  const validateWorkflow = async () => {
    if (!workflow) return;

    setValidating(true);
    try {
      const response = await api.post(`/api/workflows/${workflow.id}/validate`);
      setValidation(response.data);
      
      if (response.data.valid) {
        addToast({
          title: 'Success',
          description: 'Workflow is valid and ready to run',
        });
      } else {
        addToast({
          title: 'Validation Error',
          description: `Found ${response.data.errors.length} errors`,
          variant: 'destructive',
        });
      }
    } catch (error) {
      addToast({
        title: 'Error',
        description: 'Failed to validate workflow',
        variant: 'destructive',
      });
    } finally {
      setValidating(false);
    }
  };

  const buildStack = async () => {
    await saveWorkflow();
    await validateWorkflow();
    
    if (validation.valid) {
      setShowChatDialog(true);
    }
  };

  return (
    <div className="workflow-builder h-screen flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/')}
            className="flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Dashboard
          </Button>
          <div className="text-lg font-semibold text-gray-900">
            {workflow?.name || 'Loading...'}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={validateWorkflow}
            disabled={validating}
            className="flex items-center gap-2"
          >
            {validation.valid ? (
              <Check className="w-4 h-4 text-green-600" />
            ) : (
              <AlertCircle className="w-4 h-4 text-red-600" />
            )}
            {validating ? 'Validating...' : 'Validate'}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={saveWorkflow}
            disabled={saving}
            className="flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving...' : 'Save'}
          </Button>

          <Button
            size="sm"
            onClick={buildStack}
            className="flex items-center gap-2"
          >
            <Play className="w-4 h-4" />
            Build Stack
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowChatDialog(true)}
            className="flex items-center gap-2"
          >
            <MessageSquare className="w-4 h-4" />
            Chat with Stack
          </Button>
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Component Library */}
        <ComponentLibrary onDragStart={onDragStart} />

        {/* Canvas */}
        <div className="flex-1 relative" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="top-right"
          >
            <Controls />
            <MiniMap />
            <Background variant="dots" gap={12} size={1} />
            <Panel position="top-left">
              <div className="bg-white p-2 rounded-md shadow-sm border">
                <div className="text-xs text-gray-600">
                  Components: {nodes.length} | Connections: {edges.length}
                </div>
              </div>
            </Panel>
          </ReactFlow>
        </div>

        {/* Configuration Panel */}
        <ConfigurationPanel
          selectedNode={selectedNode}
          onConfigUpdate={onConfigUpdate}
          workflows={[workflow].filter(Boolean)}
        />
      </div>

      {/* Chat Dialog */}
      <Dialog open={showChatDialog} onOpenChange={setShowChatDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Chat with {workflow?.name}</DialogTitle>
          </DialogHeader>
          <ChatInterface
            workflow={workflow}
            onClose={() => setShowChatDialog(false)}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

const WorkflowBuilder = () => {
  return (
    <ReactFlowProvider>
      <WorkflowBuilderFlow />
    </ReactFlowProvider>
  );
};

export default WorkflowBuilder;