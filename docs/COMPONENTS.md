# Component Development Guide

This guide explains how to create custom components for the Agent Builder workflow platform, extending the core functionality with new node types and capabilities.

## Table of Contents
- [Component Architecture](#component-architecture)
- [Core Component Types](#core-component-types)
- [Creating Custom Components](#creating-custom-components)
- [Component Configuration](#component-configuration)
- [Component Registration](#component-registration)
- [Testing Components](#testing-components)
- [Best Practices](#best-practices)
- [Advanced Features](#advanced-features)

## Component Architecture

### Component Structure

Each component in Agent Builder consists of several parts:

```
Component/
├── ComponentName.js           # React component for UI rendering
├── ComponentNameConfig.js     # Configuration panel component
├── componentName.service.js   # Backend processing logic
├── componentName.schema.js    # Data validation schema
├── componentName.test.js      # Unit tests
└── index.js                  # Component exports
```

### Component Lifecycle

1. **Registration**: Component registered in component library
2. **Drag & Drop**: User drags component to workflow canvas
3. **Configuration**: User configures component properties
4. **Connection**: Component connected to other components
5. **Validation**: Workflow validates component configuration
6. **Execution**: Component processes data during workflow run

### Data Flow

Components communicate through a standardized data flow:

```javascript
Input Data → Component Processing → Output Data
     ↓              ↓                    ↓
  Validation    Configuration         Results
```

## Core Component Types

### 1. User Query Component

**Purpose**: Entry point for user input
**Input**: None (starting node)
**Output**: User query string

```javascript
// frontend/src/components/workflow/components/UserQueryComponent.js
import React from 'react';
import { Handle, Position } from 'reactflow';

const UserQueryComponent = ({ data, isConnectable }) => {
  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-blue-200">
      <div className="flex items-center">
        <div className="rounded-full w-3 h-3 bg-blue-500 mr-2"></div>
        <div>
          <div className="text-lg font-bold">User Query</div>
          <div className="text-gray-500 text-sm">Accepts user input</div>
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Right}
        id="query"
        isConnectable={isConnectable}
      />
    </div>
  );
};

export default UserQueryComponent;
```

### 2. Knowledge Base Component

**Purpose**: Document storage and retrieval
**Input**: Query string
**Output**: Relevant document passages

```javascript
// frontend/src/components/workflow/components/KnowledgeBaseComponent.js
import React from 'react';
import { Handle, Position } from 'reactflow';

const KnowledgeBaseComponent = ({ data, isConnectable }) => {
  const documentCount = data.documents?.length || 0;
  
  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-green-200">
      <div className="flex items-center">
        <div className="rounded-full w-3 h-3 bg-green-500 mr-2"></div>
        <div>
          <div className="text-lg font-bold">Knowledge Base</div>
          <div className="text-gray-500 text-sm">
            {documentCount} document{documentCount !== 1 ? 's' : ''}
          </div>
        </div>
      </div>
      <Handle
        type="target"
        position={Position.Left}
        id="query"
        isConnectable={isConnectable}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="context"
        isConnectable={isConnectable}
      />
    </div>
  );
};

export default KnowledgeBaseComponent;
```

### 3. LLM Engine Component

**Purpose**: AI processing and response generation
**Input**: Query + Context (optional)
**Output**: AI-generated response

```javascript
// frontend/src/components/workflow/components/LLMEngineComponent.js
import React from 'react';
import { Handle, Position } from 'reactflow';

const LLMEngineComponent = ({ data, isConnectable }) => {
  const modelName = data.model || 'gpt-3.5-turbo';
  
  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-purple-200">
      <div className="flex items-center">
        <div className="rounded-full w-3 h-3 bg-purple-500 mr-2"></div>
        <div>
          <div className="text-lg font-bold">LLM Engine</div>
          <div className="text-gray-500 text-sm">{modelName}</div>
        </div>
      </div>
      <Handle
        type="target"
        position={Position.Left}
        id="query"
        style={{ top: '30%' }}
        isConnectable={isConnectable}
      />
      <Handle
        type="target"
        position={Position.Left}
        id="context"
        style={{ top: '70%' }}
        isConnectable={isConnectable}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="response"
        isConnectable={isConnectable}
      />
    </div>
  );
};

export default LLMEngineComponent;
```

### 4. Output Component

**Purpose**: Display results to user
**Input**: Response data
**Output**: None (terminal node)

```javascript
// frontend/src/components/workflow/components/OutputComponent.js
import React from 'react';
import { Handle, Position } from 'reactflow';

const OutputComponent = ({ data, isConnectable }) => {
  const format = data.format || 'text';
  
  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-orange-200">
      <div className="flex items-center">
        <div className="rounded-full w-3 h-3 bg-orange-500 mr-2"></div>
        <div>
          <div className="text-lg font-bold">Output</div>
          <div className="text-gray-500 text-sm">Format: {format}</div>
        </div>
      </div>
      <Handle
        type="target"
        position={Position.Left}
        id="response"
        isConnectable={isConnectable}
      />
    </div>
  );
};

export default OutputComponent;
```

## Creating Custom Components

### Step 1: Define Component Schema

First, define the data schema for your component:

```javascript
// frontend/src/components/workflow/components/customComponent.schema.js
import { z } from 'zod';

export const CustomComponentSchema = z.object({
  id: z.string(),
  type: z.literal('custom'),
  position: z.object({
    x: z.number(),
    y: z.number()
  }),
  data: z.object({
    // Component-specific configuration
    apiEndpoint: z.string().url(),
    timeout: z.number().min(1000).max(30000).default(5000),
    retries: z.number().min(0).max(5).default(3),
    enabled: z.boolean().default(true)
  })
});

export const CustomComponentConfigSchema = z.object({
  apiEndpoint: z.string().url(),
  timeout: z.number().min(1000).max(30000),
  retries: z.number().min(0).max(5),
  enabled: z.boolean()
});
```

### Step 2: Create React Component

```javascript
// frontend/src/components/workflow/components/CustomComponent.js
import React from 'react';
import { Handle, Position } from 'reactflow';
import { Badge } from '@/components/ui/badge';

const CustomComponent = ({ data, selected, isConnectable }) => {
  const { apiEndpoint, enabled } = data;
  
  return (
    <div className={`px-4 py-2 shadow-md rounded-md bg-white border-2 ${
      selected ? 'border-blue-400' : 'border-gray-200'
    }`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className={`rounded-full w-3 h-3 mr-2 ${
            enabled ? 'bg-blue-500' : 'bg-gray-400'
          }`}></div>
          <div>
            <div className="text-lg font-bold">Custom API</div>
            <div className="text-gray-500 text-xs">
              {apiEndpoint ? new URL(apiEndpoint).hostname : 'Not configured'}
            </div>
          </div>
        </div>
        <Badge variant={enabled ? 'default' : 'secondary'}>
          {enabled ? 'Active' : 'Disabled'}
        </Badge>
      </div>
      
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        id="input"
        isConnectable={isConnectable}
        className="w-3 h-3"
      />
      
      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="output"
        isConnectable={isConnectable}
        className="w-3 h-3"
      />
    </div>
  );
};

export default CustomComponent;
```

### Step 3: Create Configuration Panel

```javascript
// frontend/src/components/workflow/components/CustomComponentConfig.js
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { CustomComponentConfigSchema } from './customComponent.schema';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const CustomComponentConfig = ({ node, onConfigChange }) => {
  const form = useForm({
    resolver: zodResolver(CustomComponentConfigSchema),
    defaultValues: {
      apiEndpoint: node.data.apiEndpoint || '',
      timeout: node.data.timeout || 5000,
      retries: node.data.retries || 3,
      enabled: node.data.enabled || true
    }
  });

  const onSubmit = (data) => {
    onConfigChange(node.id, data);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Custom API Component</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="apiEndpoint">API Endpoint</Label>
            <Input
              id="apiEndpoint"
              placeholder="https://api.example.com/endpoint"
              {...form.register('apiEndpoint')}
            />
            {form.formState.errors.apiEndpoint && (
              <p className="text-sm text-red-500">
                {form.formState.errors.apiEndpoint.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="timeout">Timeout (ms)</Label>
            <Input
              id="timeout"
              type="number"
              min="1000"
              max="30000"
              {...form.register('timeout', { valueAsNumber: true })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="retries">Retries</Label>
            <Input
              id="retries"
              type="number"
              min="0"
              max="5"
              {...form.register('retries', { valueAsNumber: true })}
            />
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="enabled"
              {...form.register('enabled')}
            />
            <Label htmlFor="enabled">Enable component</Label>
          </div>

          <Button type="submit" className="w-full">
            Save Configuration
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default CustomComponentConfig;
```

### Step 4: Implement Backend Service

```python
# backend/app/services/custom_component_service.py
from typing import Dict, Any, Optional
import httpx
import asyncio
from app.core.logging import logger

class CustomComponentService:
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def process(
        self, 
        input_data: str, 
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process input data using custom API endpoint
        """
        try:
            if not config.get('enabled', True):
                return {
                    'success': False,
                    'error': 'Component is disabled',
                    'output': None
                }
            
            api_endpoint = config.get('apiEndpoint')
            timeout = config.get('timeout', 5000) / 1000  # Convert to seconds
            retries = config.get('retries', 3)
            
            if not api_endpoint:
                raise ValueError("API endpoint not configured")
            
            # Prepare request payload
            payload = {
                'input': input_data,
                'timestamp': asyncio.get_event_loop().time()
            }
            
            # Attempt request with retries
            last_error = None
            for attempt in range(retries + 1):
                try:
                    response = await self.client.post(
                        api_endpoint,
                        json=payload,
                        timeout=timeout
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    return {
                        'success': True,
                        'output': result.get('output', result),
                        'metadata': {
                            'attempt': attempt + 1,
                            'response_time': response.elapsed.total_seconds(),
                            'status_code': response.status_code
                        }
                    }
                    
                except httpx.RequestError as e:
                    last_error = e
                    if attempt < retries:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    break
                except httpx.HTTPStatusError as e:
                    last_error = e
                    break
            
            return {
                'success': False,
                'error': f'Request failed: {str(last_error)}',
                'output': None
            }
            
        except Exception as e:
            logger.error(f"Custom component processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'output': None
            }
    
    async def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate component configuration
        """
        errors = []
        
        api_endpoint = config.get('apiEndpoint')
        if not api_endpoint:
            errors.append("API endpoint is required")
        elif not api_endpoint.startswith(('http://', 'https://')):
            errors.append("API endpoint must be a valid URL")
        
        timeout = config.get('timeout', 5000)
        if not isinstance(timeout, int) or timeout < 1000 or timeout > 30000:
            errors.append("Timeout must be between 1000 and 30000 milliseconds")
        
        retries = config.get('retries', 3)
        if not isinstance(retries, int) or retries < 0 or retries > 5:
            errors.append("Retries must be between 0 and 5")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test connection to API endpoint
        """
        try:
            api_endpoint = config.get('apiEndpoint')
            if not api_endpoint:
                return {'success': False, 'error': 'No API endpoint configured'}
            
            # Simple health check
            response = await self.client.get(
                api_endpoint,
                timeout=5.0
            )
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
```

### Step 5: Register Component

```javascript
// frontend/src/components/workflow/componentRegistry.js
import CustomComponent from './components/CustomComponent';
import CustomComponentConfig from './components/CustomComponentConfig';

export const componentTypes = {
  'user-query': UserQueryComponent,
  'knowledge-base': KnowledgeBaseComponent,
  'llm-engine': LLMEngineComponent,
  'output': OutputComponent,
  'custom': CustomComponent,  // Add your custom component
};

export const componentConfigs = {
  'user-query': UserQueryConfig,
  'knowledge-base': KnowledgeBaseConfig,
  'llm-engine': LLMEngineConfig,
  'output': OutputConfig,
  'custom': CustomComponentConfig,  // Add your custom config
};

export const componentCategories = {
  'Input': ['user-query'],
  'Processing': ['knowledge-base', 'llm-engine', 'custom'],  // Add to category
  'Output': ['output']
};

export const componentTemplates = {
  'custom': {
    type: 'custom',
    data: {
      apiEndpoint: '',
      timeout: 5000,
      retries: 3,
      enabled: true,
      label: 'Custom API'
    }
  }
};
```

```python
# backend/app/services/component_registry.py
from app.services.custom_component_service import CustomComponentService

class ComponentRegistry:
    def __init__(self):
        self.services = {
            'user_query': UserQueryService(),
            'knowledge_base': KnowledgeBaseService(),
            'llm_engine': LLMEngineService(),
            'output': OutputService(),
            'custom': CustomComponentService(),  # Register your service
        }
    
    def get_service(self, component_type: str):
        return self.services.get(component_type)
    
    def get_available_types(self):
        return list(self.services.keys())
```

## Component Configuration

### Configuration Schema Design

Use Zod (frontend) and Pydantic (backend) for consistent validation:

```javascript
// Frontend validation with Zod
import { z } from 'zod';

export const ComponentConfigSchema = z.object({
  // Common fields
  id: z.string(),
  type: z.string(),
  label: z.string().min(1).max(50),
  enabled: z.boolean().default(true),
  
  // Type-specific fields
  // Use discriminated unions for type-specific config
}).strict();
```

```python
# Backend validation with Pydantic
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any

class ComponentConfig(BaseModel):
    id: str
    type: str
    label: str = Field(..., min_length=1, max_length=50)
    enabled: bool = True
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['user_query', 'knowledge_base', 'llm_engine', 'output', 'custom']
        if v not in allowed_types:
            raise ValueError(f'Invalid component type: {v}')
        return v
    
    class Config:
        extra = 'forbid'
```

### Dynamic Configuration

For components that need dynamic configuration based on external data:

```javascript
// Dynamic configuration component
const DynamicConfig = ({ node, onConfigChange }) => {
  const [availableOptions, setAvailableOptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadOptions = async () => {
      setLoading(true);
      try {
        const response = await api.get(`/api/components/${node.type}/options`);
        setAvailableOptions(response.data);
      } catch (error) {
        console.error('Failed to load options:', error);
      } finally {
        setLoading(false);
      }
    };

    loadOptions();
  }, [node.type]);

  if (loading) return <Skeleton className="h-4 w-full" />;

  return (
    <Select value={node.data.selectedOption} onValueChange={handleChange}>
      {availableOptions.map(option => (
        <SelectItem key={option.id} value={option.id}>
          {option.label}
        </SelectItem>
      ))}
    </Select>
  );
};
```

## Component Registration

### Automated Registration

Create a plugin system for automatic component discovery:

```javascript
// frontend/src/components/workflow/componentLoader.js
const componentModules = import.meta.glob('./components/*Component.js');
const configModules = import.meta.glob('./components/*Config.js');

export async function loadComponents() {
  const components = {};
  const configs = {};

  // Load components
  for (const path in componentModules) {
    const module = await componentModules[path]();
    const name = path.match(/\.\/components\/(.+)Component\.js$/)[1];
    components[name] = module.default;
  }

  // Load configs
  for (const path in configModules) {
    const module = await configModules[path]();
    const name = path.match(/\.\/components\/(.+)Config\.js$/)[1];
    configs[name] = module.default;
  }

  return { components, configs };
}
```

```python
# backend/app/services/component_loader.py
import importlib
import pkgutil
from typing import Dict, Type
from app.services.base_component import BaseComponentService

def load_component_services() -> Dict[str, Type[BaseComponentService]]:
    """
    Automatically discover and load component services
    """
    services = {}
    
    # Import all modules in the services directory
    import app.services
    for importer, modname, ispkg in pkgutil.iter_modules(app.services.__path__):
        if modname.endswith('_service'):
            module = importlib.import_module(f'app.services.{modname}')
            
            # Find service classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseComponentService) and 
                    attr != BaseComponentService):
                    
                    service_name = modname.replace('_service', '')
                    services[service_name] = attr()
    
    return services
```

## Testing Components

### Unit Testing

```javascript
// frontend/src/components/workflow/components/__tests__/CustomComponent.test.js
import React from 'react';
import { render, screen } from '@testing-library/react';
import { ReactFlow, ReactFlowProvider } from 'reactflow';
import CustomComponent from '../CustomComponent';

const mockNode = {
  id: '1',
  type: 'custom',
  data: {
    apiEndpoint: 'https://api.example.com/test',
    timeout: 5000,
    retries: 3,
    enabled: true
  },
  position: { x: 0, y: 0 }
};

describe('CustomComponent', () => {
  const renderComponent = (props = {}) => {
    return render(
      <ReactFlowProvider>
        <ReactFlow nodes={[mockNode]} edges={[]}>
          <CustomComponent
            data={mockNode.data}
            isConnectable={true}
            {...props}
          />
        </ReactFlow>
      </ReactFlowProvider>
    );
  };

  test('renders component with correct title', () => {
    renderComponent();
    expect(screen.getByText('Custom API')).toBeInTheDocument();
  });

  test('shows API endpoint hostname', () => {
    renderComponent();
    expect(screen.getByText('api.example.com')).toBeInTheDocument();
  });

  test('shows active badge when enabled', () => {
    renderComponent();
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  test('shows disabled badge when disabled', () => {
    renderComponent({
      data: { ...mockNode.data, enabled: false }
    });
    expect(screen.getByText('Disabled')).toBeInTheDocument();
  });
});
```

```python
# backend/tests/services/test_custom_component_service.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.custom_component_service import CustomComponentService

@pytest.fixture
def custom_service():
    return CustomComponentService()

@pytest.mark.asyncio
class TestCustomComponentService:
    
    async def test_process_success(self, custom_service):
        config = {
            'apiEndpoint': 'https://api.example.com/test',
            'timeout': 5000,
            'retries': 3,
            'enabled': True
        }
        
        mock_response = AsyncMock()
        mock_response.json.return_value = {'output': 'test result'}
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.5
        
        with patch.object(custom_service.client, 'post', return_value=mock_response):
            result = await custom_service.process('test input', config)
        
        assert result['success'] is True
        assert result['output'] == 'test result'
        assert result['metadata']['status_code'] == 200

    async def test_process_disabled_component(self, custom_service):
        config = {'enabled': False}
        
        result = await custom_service.process('test input', config)
        
        assert result['success'] is False
        assert 'disabled' in result['error'].lower()

    async def test_validate_config_valid(self, custom_service):
        config = {
            'apiEndpoint': 'https://api.example.com',
            'timeout': 5000,
            'retries': 3
        }
        
        result = await custom_service.validate_config(config)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0

    async def test_validate_config_invalid_url(self, custom_service):
        config = {
            'apiEndpoint': 'invalid-url',
            'timeout': 5000,
            'retries': 3
        }
        
        result = await custom_service.validate_config(config)
        
        assert result['valid'] is False
        assert any('URL' in error for error in result['errors'])
```

### Integration Testing

```javascript
// frontend/src/components/workflow/__tests__/WorkflowIntegration.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import WorkflowBuilder from '../WorkflowBuilder';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false }
  }
});

describe('Workflow Integration', () => {
  test('can add custom component to workflow', async () => {
    const queryClient = createTestQueryClient();
    const user = userEvent.setup();

    render(
      <QueryClientProvider client={queryClient}>
        <WorkflowBuilder />
      </QueryClientProvider>
    );

    // Drag custom component from library
    const customComponent = screen.getByTestId('component-custom');
    const canvas = screen.getByTestId('workflow-canvas');

    await user.drag(customComponent, canvas);

    // Verify component was added
    await waitFor(() => {
      expect(screen.getByText('Custom API')).toBeInTheDocument();
    });
  });

  test('can configure custom component', async () => {
    // ... configuration test
  });

  test('can connect custom component to other components', async () => {
    // ... connection test
  });
});
```

## Best Practices

### 1. Component Design Principles

**Single Responsibility**: Each component should have one clear purpose
```javascript
// Good: Focused component
const EmailSenderComponent = ({ data }) => {
  // Only handles email sending logic
};

// Bad: Too many responsibilities
const NotificationComponent = ({ data }) => {
  // Handles email, SMS, push notifications, logging, etc.
};
```

**Composability**: Components should work well together
```javascript
// Design components to pass data in standard formats
const standardDataFormat = {
  content: string,
  metadata: object,
  timestamp: string,
  source: string
};
```

**Error Resilience**: Handle failures gracefully
```javascript
const ResilientComponent = ({ data }) => {
  const [error, setError] = useState(null);
  const [retrying, setRetrying] = useState(false);

  const handleError = (error) => {
    setError(error);
    // Log error, show user-friendly message, suggest fixes
  };

  const retry = () => {
    setRetrying(true);
    setError(null);
    // Retry logic
  };

  if (error) {
    return (
      <ErrorBoundary error={error} onRetry={retry} retrying={retrying} />
    );
  }

  return <ComponentContent {...data} />;
};
```

### 2. Performance Optimization

**Lazy Loading**: Load components only when needed
```javascript
import { lazy, Suspense } from 'react';

const CustomComponent = lazy(() => import('./components/CustomComponent'));

const ComponentRenderer = ({ type, ...props }) => {
  return (
    <Suspense fallback={<ComponentSkeleton />}>
      <CustomComponent {...props} />
    </Suspense>
  );
};
```

**Memoization**: Prevent unnecessary re-renders
```javascript
import React, { memo } from 'react';

const OptimizedComponent = memo(({ data, onConfigChange }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  // Custom comparison logic
  return prevProps.data.id === nextProps.data.id &&
         JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data);
});
```

### 3. Accessibility

**Keyboard Navigation**: Support keyboard interaction
```javascript
const AccessibleComponent = ({ data }) => {
  const handleKeyDown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      // Trigger component action
    }
  };

  return (
    <div
      tabIndex={0}
      role="button"
      aria-label={`${data.label} component`}
      onKeyDown={handleKeyDown}
    >
      {/* Component content */}
    </div>
  );
};
```

**Screen Reader Support**: Provide meaningful labels
```javascript
<div
  role="region"
  aria-labelledby={`${data.id}-title`}
  aria-describedby={`${data.id}-description`}
>
  <h3 id={`${data.id}-title`}>{data.label}</h3>
  <p id={`${data.id}-description`}>{data.description}</p>
</div>
```

### 4. Documentation

**Component Documentation**: Use JSDoc for comprehensive documentation
```javascript
/**
 * Custom API Component
 * 
 * Sends HTTP requests to external APIs and processes responses.
 * 
 * @component
 * @param {Object} data - Component configuration data
 * @param {string} data.apiEndpoint - The API endpoint URL
 * @param {number} data.timeout - Request timeout in milliseconds
 * @param {number} data.retries - Number of retry attempts
 * @param {boolean} data.enabled - Whether the component is enabled
 * @param {boolean} isConnectable - Whether handles can accept connections
 * @param {boolean} selected - Whether the component is currently selected
 * 
 * @example
 * <CustomComponent
 *   data={{
 *     apiEndpoint: 'https://api.example.com',
 *     timeout: 5000,
 *     retries: 3,
 *     enabled: true
 *   }}
 *   isConnectable={true}
 *   selected={false}
 * />
 */
const CustomComponent = ({ data, isConnectable, selected }) => {
  // Implementation
};
```

## Advanced Features

### 1. Dynamic Component Generation

Create components that generate other components:

```javascript
const TemplateGeneratorComponent = ({ data }) => {
  const [generatedComponents, setGeneratedComponents] = useState([]);

  const generateComponents = async () => {
    const template = data.template;
    const variations = data.variations;
    
    const components = variations.map((variation, index) => ({
      id: `${data.id}-generated-${index}`,
      type: template.type,
      position: {
        x: data.position.x + (index * 200),
        y: data.position.y + 100
      },
      data: { ...template.data, ...variation }
    }));
    
    setGeneratedComponents(components);
    data.onAddComponents?.(components);
  };

  return (
    <div className="template-generator">
      <Button onClick={generateComponents}>
        Generate {data.variations?.length || 0} Components
      </Button>
    </div>
  );
};
```

### 2. Real-time Component Updates

Components that update in real-time:

```javascript
const LiveDataComponent = ({ data }) => {
  const [liveData, setLiveData] = useState(null);

  useEffect(() => {
    const eventSource = new EventSource(data.streamEndpoint);
    
    eventSource.onmessage = (event) => {
      const newData = JSON.parse(event.data);
      setLiveData(newData);
    };

    return () => eventSource.close();
  }, [data.streamEndpoint]);

  return (
    <div className="live-component">
      <div className="live-indicator">
        <div className="pulse bg-green-500 w-2 h-2 rounded-full" />
        Live
      </div>
      <div className="data-display">
        {liveData ? JSON.stringify(liveData, null, 2) : 'Waiting for data...'}
      </div>
    </div>
  );
};
```

### 3. Conditional Component Rendering

Components that show/hide based on conditions:

```javascript
const ConditionalComponent = ({ data, workflow }) => {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const condition = data.visibilityCondition;
    if (condition) {
      const result = evaluateCondition(condition, workflow);
      setVisible(result);
    }
  }, [data.visibilityCondition, workflow]);

  if (!visible) return null;

  return (
    <div className="conditional-component">
      {/* Component content */}
    </div>
  );
};

function evaluateCondition(condition, workflow) {
  // Simple condition evaluation
  // In production, use a proper expression evaluator
  return new Function('workflow', `return ${condition}`)(workflow);
}
```

This comprehensive guide covers all aspects of component development in Agent Builder, from basic concepts to advanced features. Use it as a reference when creating new components or extending existing ones.