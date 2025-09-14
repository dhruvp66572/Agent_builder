import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Switch } from '../ui/switch';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Settings, FileText, Upload } from 'lucide-react';
import api from '../../lib/api';
import { useToast } from '../ui/toast';

const ConfigurationPanel = ({ selectedNode, onConfigUpdate, workflows }) => {
  const { addToast } = useToast();
  const [config, setConfig] = useState({});
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    if (selectedNode) {
      setConfig(selectedNode.data?.config || {});
    }
    fetchDocuments();
  }, [selectedNode]);

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/api/documents/');
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleConfigChange = (key, value) => {
    const newConfig = { ...config, [key]: value };
    setConfig(newConfig);
    if (selectedNode) {
      onConfigUpdate(selectedNode.id, newConfig);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const response = await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      addToast({
        title: 'Success',
        description: 'Document uploaded successfully',
      });
      
      fetchDocuments();
    } catch (error) {
      addToast({
        title: 'Error',
        description: 'Failed to upload document',
        variant: 'destructive',
      });
    } finally {
      setUploading(false);
    }
  };

  if (!selectedNode) {
    return (
      <div className="configuration-panel bg-white border-l border-gray-200 p-4 h-full">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Component Selected</h3>
            <p className="text-sm text-gray-600">
              Select a component on the canvas to configure its settings
            </p>
          </div>
        </div>
      </div>
    );
  }

  const renderConfigFields = () => {
    const componentType = selectedNode.type;

    switch (componentType) {
      case 'user-query':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="placeholder">Placeholder Text</Label>
              <Input
                id="placeholder"
                value={config.placeholder || ''}
                onChange={(e) => handleConfigChange('placeholder', e.target.value)}
                placeholder="Enter your question..."
              />
            </div>
            <div className="flex items-center space-x-2">
              <Switch
                id="validation"
                checked={config.validation || false}
                onCheckedChange={(checked) => handleConfigChange('validation', checked)}
              />
              <Label htmlFor="validation">Enable Input Validation</Label>
            </div>
          </div>
        );

      case 'knowledge-base':
        return (
          <div className="space-y-4">
            <div>
              <Label>Upload Documents</Label>
              <div className="mt-2 flex items-center space-x-2">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => document.getElementById('file-upload').click()}
                  disabled={uploading}
                >
                  <Upload className="w-4 h-4 mr-2" />
                  {uploading ? 'Uploading...' : 'Upload PDF'}
                </Button>
              </div>
            </div>
            
            <div>
              <Label>Linked Documents ({documents.length})</Label>
              <div className="mt-2 max-h-32 overflow-y-auto space-y-1">
                {documents.map((doc) => (
                  <div key={doc.id} className="flex items-center space-x-2 p-2 bg-gray-50 rounded text-sm">
                    <FileText className="w-4 h-4 text-gray-500" />
                    <span className="flex-1 truncate">{doc.original_filename}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      doc.embedding_status === 'completed' 
                        ? 'bg-green-100 text-green-800'
                        : doc.embedding_status === 'processing'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {doc.embedding_status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="search_limit">Search Result Limit</Label>
              <Input
                id="search_limit"
                type="number"
                min="1"
                max="20"
                value={config.search_limit || 5}
                onChange={(e) => handleConfigChange('search_limit', parseInt(e.target.value))}
              />
            </div>

            <div>
              <Label htmlFor="similarity_threshold">Similarity Threshold</Label>
              <Input
                id="similarity_threshold"
                type="number"
                min="0.1"
                max="1.0"
                step="0.1"
                value={config.similarity_threshold || 0.7}
                onChange={(e) => handleConfigChange('similarity_threshold', parseFloat(e.target.value))}
              />
            </div>
          </div>
        );

      case 'llm-engine':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="model">Model</Label>
              <Select
                value={config.model || 'gpt-3.5-turbo'}
                onValueChange={(value) => handleConfigChange('model', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                  <SelectItem value="gemini-1.5-flash">Gemini Pro</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="custom_prompt">Custom Prompt</Label>
              <Textarea
                id="custom_prompt"
                value={config.custom_prompt || ''}
                onChange={(e) => handleConfigChange('custom_prompt', e.target.value)}
                placeholder="Enter custom instructions for the AI..."
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="temperature">Temperature</Label>
              <Input
                id="temperature"
                type="number"
                min="0"
                max="2"
                step="0.1"
                value={config.temperature || 0.7}
                onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
              />
            </div>

            <div>
              <Label htmlFor="max_tokens">Max Tokens</Label>
              <Input
                id="max_tokens"
                type="number"
                min="100"
                max="4000"
                value={config.max_tokens || 1000}
                onChange={(e) => handleConfigChange('max_tokens', parseInt(e.target.value))}
              />
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="enable_web_search"
                checked={config.enable_web_search || false}
                onCheckedChange={(checked) => handleConfigChange('enable_web_search', checked)}
              />
              <Label htmlFor="enable_web_search">Enable Web Search</Label>
            </div>

            {config.enable_web_search && (
              <div>
                <Label htmlFor="web_search_queries">Web Search Result Limit</Label>
                <Input
                  id="web_search_queries"
                  type="number"
                  min="1"
                  max="10"
                  value={config.web_search_queries || 3}
                  onChange={(e) => handleConfigChange('web_search_queries', parseInt(e.target.value))}
                />
              </div>
            )}
          </div>
        );

      case 'output':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="format">Output Format</Label>
              <Select
                value={config.format || 'markdown'}
                onValueChange={(value) => handleConfigChange('format', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="text">Plain Text</SelectItem>
                  <SelectItem value="markdown">Markdown</SelectItem>
                  <SelectItem value="html">HTML</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="show_sources"
                checked={config.show_sources !== false}
                onCheckedChange={(checked) => handleConfigChange('show_sources', checked)}
              />
              <Label htmlFor="show_sources">Show Sources</Label>
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="show_execution_time"
                checked={config.show_execution_time || false}
                onCheckedChange={(checked) => handleConfigChange('show_execution_time', checked)}
              />
              <Label htmlFor="show_execution_time">Show Execution Time</Label>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-sm text-gray-600">
            No configuration options available for this component.
          </div>
        );
    }
  };

  return (
    <div className="configuration-panel bg-white border-l border-gray-200 p-4 h-full overflow-y-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Configure Component
          </CardTitle>
          <div className="text-sm text-gray-600">
            {selectedNode.type.split('-').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')}
          </div>
        </CardHeader>
        <CardContent>
          {renderConfigFields()}
        </CardContent>
      </Card>
    </div>
  );
};

export default ConfigurationPanel;