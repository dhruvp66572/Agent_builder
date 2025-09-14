import React from 'react';
import { Handle, Position } from 'reactflow';
import { Database, FileText } from 'lucide-react';

const KnowledgeBaseComponent = ({ data, selected }) => {
  return (
    <div className={`px-4 py-3 shadow-md rounded-md bg-green-50 border-2 min-w-[200px] ${
      selected ? 'border-green-600' : 'border-green-300'
    }`}>
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        className="w-3 h-3 bg-green-500"
      />
      
      <div className="flex items-center">
        <div className="rounded-full w-8 h-8 flex items-center justify-center bg-green-100">
          <Database className="w-4 h-4 text-green-600" />
        </div>
        <div className="ml-2">
          <div className="text-sm font-bold text-gray-900">Knowledge Base</div>
          <div className="text-xs text-gray-500">Document processing & search</div>
        </div>
      </div>
      
      <div className="mt-2 text-xs text-gray-600">
        <div className="font-medium">Configuration:</div>
        <div className="flex items-center gap-1">
          <FileText className="w-3 h-3" />
          <span>{data.config?.documents?.length || 0} documents</span>
        </div>
        <div>Search limit: {data.config?.search_limit || 5}</div>
        <div>Similarity: {data.config?.similarity_threshold || 0.7}</div>
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        className="w-3 h-3 bg-green-500"
      />
    </div>
  );
};

export default KnowledgeBaseComponent;