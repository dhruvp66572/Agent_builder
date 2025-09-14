import React from 'react';
import { Handle, Position } from 'reactflow';
import { Monitor, Eye } from 'lucide-react';

const OutputComponent = ({ data, selected }) => {
  return (
    <div className={`px-4 py-3 shadow-md rounded-md bg-purple-50 border-2 min-w-[200px] ${
      selected ? 'border-purple-600' : 'border-purple-300'
    }`}>
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        className="w-3 h-3 bg-purple-500"
      />
      
      <div className="flex items-center">
        <div className="rounded-full w-8 h-8 flex items-center justify-center bg-purple-100">
          <Monitor className="w-4 h-4 text-purple-600" />
        </div>
        <div className="ml-2">
          <div className="text-sm font-bold text-gray-900">Output</div>
          <div className="text-xs text-gray-500">Display final response</div>
        </div>
      </div>
      
      <div className="mt-2 text-xs text-gray-600">
        <div className="font-medium">Configuration:</div>
        <div>Format: {data.config?.format || 'markdown'}</div>
        <div className="flex items-center gap-1">
          {data.config?.show_sources && <Eye className="w-3 h-3" />}
          <span>Sources: {data.config?.show_sources ? 'Show' : 'Hide'}</span>
        </div>
        <div>Execution time: {data.config?.show_execution_time ? 'Show' : 'Hide'}</div>
      </div>
    </div>
  );
};

export default OutputComponent;