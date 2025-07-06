import React from 'react';
import { UIComponent } from '@/types/policy';
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card';

interface DynamicPolicyComponentProps {
  component: UIComponent;
}

export const DynamicPolicyComponent: React.FC<DynamicPolicyComponentProps> = ({ component }) => {
  const getStyleByRiskLevel = (riskLevel: string) => {
    switch (riskLevel) {
      case 'high':
        return 'border-red-400 bg-red-50';
      case 'medium':
        return 'border-yellow-400 bg-yellow-50';
      case 'low':
        return 'border-green-400 bg-green-50';
      default:
        return 'border-blue-400 bg-blue-50';
    }
  };

  const getIconByType = (type: string) => {
    switch (type) {
      case 'highlight_card':
        return '⭐';
      case 'risk_warning':
        return '⚠️';
      case 'rights_interactive':
        return '🛡️';
      case 'data_collection_card':
        return '📊';
      case 'standard_card':
      default:
        return '📄';
    }
  };

  const getRiskLevelColor = (risk: string) => {
    switch (risk) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // Convert markdown-style formatting to proper display
  const formatText = (text: string) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // **bold** to <strong>
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // *italic* to <em>
      .replace(/###\s(.*)/g, '<h3 class="text-lg font-semibold text-gray-800 mt-4 mb-2">$1</h3>') // ### headers
      .replace(/##\s(.*)/g, '<h2 class="text-xl font-bold text-gray-900 mt-4 mb-2">$1</h2>') // ## headers
      .replace(/####\s(.*)/g, '<h4 class="text-base font-medium text-gray-700 mt-3 mb-1">$1</h4>') // #### headers
      .replace(/\n\n/g, '</p><p class="mb-3">') // paragraph breaks
      .replace(/- (.*)/g, '<li class="ml-4">$1</li>'); // bullet points
  };

  // Get a meaningful title
  const getDisplayTitle = () => {
    // Try to extract a better title from the summary
    const summary = component.content.summary;
    
    // Look for headers in the summary
    const headerMatch = summary.match(/#+\s*([^:\n]+)/);
    if (headerMatch) {
      return headerMatch[1].trim();
    }
    
    // Look for the first sentence that looks like a title
    const sentences = summary.split(/[.!?]/);
    for (const sentence of sentences) {
      const trimmed = sentence.trim();
      if (trimmed.length > 10 && trimmed.length < 80 && !trimmed.includes('Here\'s') && !trimmed.includes('This')) {
        return trimmed;
      }
    }
    
    // Fallback to the component title, but make it more descriptive
    return component.content.title === 'Section 1' || component.content.title.startsWith('Section ') 
      ? `Privacy Policy Section ${component.priority}` 
      : component.content.title;
  };

  const styleClass = getStyleByRiskLevel(component.content.risk_level);
  const icon = getIconByType(component.type);
  const displayTitle = getDisplayTitle();
  const formattedSummary = formatText(component.content.summary);

  return (
    <Card className={`${styleClass} transition-all duration-200 hover:shadow-lg`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">{icon}</span>
          <span className="flex-1">{displayTitle}</span>
          <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${getRiskLevelColor(component.content.risk_level)}`}>
            {component.content.risk_level.toUpperCase()} RISK
          </span>
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="prose prose-sm max-w-none">
          <div 
            className="mb-4 text-gray-700 leading-relaxed"
            dangerouslySetInnerHTML={{ __html: `<p class="mb-3">${formattedSummary}</p>` }}
          />
        </div>

        {component.content.key_concerns.length > 0 && (
          <div className="mt-4 p-3 bg-orange-50 rounded-md border-l-4 border-orange-400">
            <h4 className="font-medium text-orange-800 mb-2 flex items-center gap-1">
              🚨 Key Concerns:
            </h4>
            <ul className="space-y-1 text-sm text-orange-700">
              {component.content.key_concerns.map((concern, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-orange-500 mt-1">•</span>
                  <span>{concern}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {component.content.user_rights.length > 0 && (
          <div className="mt-4 p-3 bg-blue-50 rounded-md border-l-4 border-blue-400">
            <h4 className="font-medium text-blue-800 mb-2 flex items-center gap-1">
              ⚖️ Your Rights:
            </h4>
            <ul className="space-y-1 text-sm text-blue-700">
              {component.content.user_rights.map((right, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span className="capitalize">{right.replace('_', ' ')}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {component.content.data_types.length > 0 && (
          <div className="mt-4 p-3 bg-purple-50 rounded-md border-l-4 border-purple-400">
            <h4 className="font-medium text-purple-800 mb-2">📋 Data Types:</h4>
            <div className="flex flex-wrap gap-2">
              {component.content.data_types.map((dataType, index) => (
                <span key={index} className="inline-flex items-center px-2 py-1 text-xs font-medium bg-purple-100 text-purple-800 rounded-full capitalize">
                  {dataType.replace('_', ' ')}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
          <div className="text-center p-3 bg-gray-50 rounded-md">
            <div className="font-medium text-gray-600 text-xs mb-1">User Control</div>
            <div className="text-xl font-bold text-blue-600">{component.content.user_control}/5</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-md">
            <div className="font-medium text-gray-600 text-xs mb-1">Transparency</div>
            <div className="text-xl font-bold text-green-600">{component.content.transparency_score}/5</div>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between text-xs text-gray-500 border-t pt-3">
          <span>Importance: {component.content.importance_score.toFixed(2)}</span>
          <span>Priority: #{component.priority}</span>
          <span>Entities: {component.metadata.entities_count}</span>
        </div>
      </CardContent>
    </Card>
  );
}; 