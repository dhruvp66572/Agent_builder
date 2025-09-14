import React from 'react';
import { Handle, Position } from 'reactflow';
import { MessageCircle } from 'lucide-react';

const UserQueryComponent = ({ data, selected }) => {
  return (
    <div className={`px-4 py-3 shadow-md rounded-md bg-blue-50 border-2 min-w-[200px] ${
      selected ? 'border-blue-600' : 'border-blue-300'
    }`}>
      <div className="flex items-center">
        <div className="rounded-full w-8 h-8 flex items-center justify-center bg-blue-100">
          <MessageCircle className="w-4 h-4 text-blue-600" />
        </div>
        <div className="ml-2">
          <div className="text-sm font-bold text-gray-900">User Query</div>
          <div className="text-xs text-gray-500">Entry point for user input</div>
        </div>
      </div>
      
      <div className="mt-2 text-xs text-gray-600">
        <div className="font-medium">Configuration:</div>
        <div>Placeholder: "{data.config?.placeholder || 'Enter your question...'}"</div>
        <div>Validation: {data.config?.validation ? 'Enabled' : 'Disabled'}</div>
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        className="w-3 h-3 bg-blue-500"
      />
    </div>
  );
};

export default UserQueryComponent;