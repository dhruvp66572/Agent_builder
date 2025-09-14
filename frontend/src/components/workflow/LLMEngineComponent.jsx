import React from 'react';
import { Handle, Position } from 'reactflow';
import { Brain, Globe } from 'lucide-react';

const LLMEngineComponent = ({ data, selected }) => {
  return (
    <div className={`px-4 py-3 shadow-md rounded-md bg-amber-50 border-2 min-w-[200px] ${
      selected ? 'border-amber-600' : 'border-amber-300'
    }`}>
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        className="w-3 h-3 bg-amber-500"
      />
      
      <div className="flex items-center">
        <div className="rounded-full w-8 h-8 flex items-center justify-center bg-amber-100">
          <Brain className="w-4 h-4 text-amber-600" />
        </div>
        <div className="ml-2">
          <div className="text-sm font-bold text-gray-900">LLM Engine</div>
          <div className="text-xs text-gray-500">AI language processing</div>
        </div>
      </div>
      
      <div className="mt-2 text-xs text-gray-600">
        <div className="font-medium">Configuration:</div>
        <div>Model: {data.config?.model || 'gemini-1.5-flash'}</div>
        <div>Temperature: {data.config?.temperature || 0.7}</div>
        <div className="flex items-center gap-1">
          {data.config?.enable_web_search && <Globe className="w-3 h-3" />}
          <span>Web search: {data.config?.enable_web_search ? 'On' : 'Off'}</span>
        </div>
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        className="w-3 h-3 bg-amber-500"
      />
    </div>
  );
};

export default LLMEngineComponent;