import React, { useState, useEffect, useRef } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent } from '../ui/card';
import { Send, Bot, User, Loader, AlertCircle } from 'lucide-react';
import api from '../../lib/api';
import { useToast } from '../ui/toast';

const ChatInterface = ({ workflow, onClose }) => {
  const { addToast } = useToast();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [session, setSession] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    createChatSession();
  }, [workflow]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const createChatSession = async () => {
    if (!workflow) return;

    try {
      const response = await api.post('/api/chat/sessions', {
        workflow_id: workflow.id,
        session_name: `Chat with ${workflow.name}`,
      });
      setSession(response.data);
    } catch (error) {
      addToast({
        title: 'Error',
        description: 'Failed to create chat session',
        variant: 'destructive',
      });
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || !workflow || loading) return;

    const userMessage = {
      id: Date.now(),
      message: inputValue,
      message_type: 'user',
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await api.post('/api/chat/execute', {
        workflow_id: workflow.id,
        query: inputValue,
        session_id: session?.id,
      });

      const assistantMessage = {
        ...response.data,
        id: response.data.id || Date.now() + 1,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        message: '',
        response: 'Sorry, there was an error processing your request. Please try again.',
        message_type: 'assistant',
        created_at: new Date().toISOString(),
        execution_data: { error: error.message },
      };

      setMessages(prev => [...prev, errorMessage]);
      
      addToast({
        title: 'Error',
        description: 'Failed to execute workflow',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatResponse = (response) => {
    if (!response) return '';
    
    // Simple markdown-like formatting
    return response
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br />');
  };

  const MessageComponent = ({ message }) => {
    const isUser = message.message_type === 'user';
    const content = isUser ? message.message : message.response;
    const hasError = message.execution_data?.error;

    return (
      <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
            {hasError ? (
              <AlertCircle className="w-4 h-4 text-red-500" />
            ) : (
              <Bot className="w-4 h-4 text-blue-600" />
            )}
          </div>
        )}
        
        <Card className={`max-w-[80%] ${isUser ? 'bg-blue-50' : hasError ? 'bg-red-50' : 'bg-gray-50'}`}>
          <CardContent className="p-3">
            <div 
              className="text-sm"
              dangerouslySetInnerHTML={{ 
                __html: isUser ? content : formatResponse(content)
              }}
            />
            
            {/* Show execution details for assistant messages */}
            {!isUser && message.execution_data && !hasError && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="text-xs text-gray-600">
                  {message.execution_data.execution_time && (
                    <div>Execution time: {message.execution_data.execution_time.toFixed(2)}s</div>
                  )}
                  {message.execution_data.llm_model && (
                    <div>Model: {message.execution_data.llm_model}</div>
                  )}
                  {message.execution_data.web_search_performed && (
                    <div>Web search: Enabled</div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        
        {isUser && (
          <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
            <User className="w-4 h-4 text-gray-600" />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-[60vh]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>Start a conversation with your workflow!</p>
            <p className="text-sm mt-2">Ask any question and see how your components work together.</p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageComponent key={message.id} message={message} />
          ))
        )}
        
        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <Loader className="w-4 h-4 text-blue-600 animate-spin" />
            </div>
            <Card className="bg-gray-50">
              <CardContent className="p-3">
                <div className="text-sm text-gray-600">
                  Processing your request...
                </div>
              </CardContent>
            </Card>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={loading}
            className="flex-1"
          />
          <Button 
            onClick={sendMessage} 
            disabled={loading || !inputValue.trim()}
            size="sm"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="text-xs text-gray-500 mt-2">
          Press Enter to send • Shift+Enter for new line
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;