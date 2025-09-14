import React from 'react';
import { MessageCircle, Database, Brain, Monitor } from 'lucide-react';

const ComponentLibrary = ({ onDragStart }) => {
  const components = [
    {
      type: 'user-query',
      name: 'User Query',
      description: 'Entry point for user input',
      icon: MessageCircle,
      category: 'input',
      color: 'blue'
    },
    {
      type: 'knowledge-base',
      name: 'Knowledge Base',
      description: 'Document processing & vector search',
      icon: Database,
      category: 'processing',
      color: 'green'
    },
    {
      type: 'llm-engine',
      name: 'LLM Engine',
      description: 'AI language model processing',
      icon: Brain,
      category: 'processing',
      color: 'amber'
    },
    {
      type: 'output',
      name: 'Output',
      description: 'Display final response to user',
      icon: Monitor,
      category: 'output',
      color: 'purple'
    }
  ];

  const categories = [
    { id: 'input', name: 'Input', description: 'Components for receiving user input' },
    { id: 'processing', name: 'Processing', description: 'Data processing and AI operations' },
    { id: 'output', name: 'Output', description: 'Components for displaying results' }
  ];

  return (
    <div className="component-library bg-white border-r border-gray-200 p-4 h-full overflow-y-auto">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Components</h3>
        <p className="text-sm text-gray-600">Drag components to the canvas to build your workflow</p>
      </div>

      {categories.map((category) => (
        <div key={category.id} className="mb-6">
          <div className="mb-3">
            <h4 className="text-sm font-medium text-gray-900 uppercase tracking-wide">
              {category.name}
            </h4>
            <p className="text-xs text-gray-500 mt-1">{category.description}</p>
          </div>

          <div className="space-y-2">
            {components
              .filter((component) => component.category === category.id)
              .map((component) => {
                const IconComponent = component.icon;
                return (
                  <div
                    key={component.type}
                    className={`component-item border-l-4 border-${component.color}-400 hover:border-${component.color}-600 hover:bg-${component.color}-50 transition-all cursor-grab active:cursor-grabbing`}
                    draggable
                    onDragStart={(event) => onDragStart(event, component.type)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`rounded-lg w-10 h-10 bg-${component.color}-100 flex items-center justify-center flex-shrink-0`}>
                        <IconComponent className={`w-5 h-5 text-${component.color}-600`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {component.name}
                        </h4>
                        <p className="text-xs text-gray-500 mt-1">
                          {component.description}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      ))}

      <div className="mt-8 p-3 bg-gray-50 rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 mb-2">How to build:</h4>
        <ol className="text-xs text-gray-600 space-y-1">
          <li>1. Drag components to canvas</li>
          <li>2. Connect components with lines</li>
          <li>3. Configure each component</li>
          <li>4. Build and test your workflow</li>
        </ol>
      </div>
    </div>
  );
};

export default ComponentLibrary;