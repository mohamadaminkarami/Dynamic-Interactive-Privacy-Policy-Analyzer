import React from 'react';
import { UIComponent } from '@/types/policy';
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card';

interface DynamicPolicyComponentProps {
  component: UIComponent;
}

export const DynamicPolicyComponent: React.FC<DynamicPolicyComponentProps> = ({ component }) => {
  const getStyleByType = (visualStyle: string) => {
    switch (visualStyle) {
      case 'warning':
        return 'border-yellow-400 bg-yellow-50';
      case 'error':
        return 'border-red-400 bg-red-50';
      case 'success':
        return 'border-green-400 bg-green-50';
      case 'info':
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

  const styleClass = getStyleByType(component.metadata.visual_style);
  const icon = getIconByType(component.type);

  return (
    <Card className={`${styleClass} transition-all duration-200 hover:shadow-lg`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">{icon}</span>
          {component.title}
          {component.metadata.requires_attention && (
            <span className="ml-2 inline-flex items-center px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
              Attention Required
            </span>
          )}
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        <div className="prose prose-sm max-w-none">
          {component.content.split('\n').map((paragraph, index) => (
            <p key={index} className="mb-2 text-gray-700 leading-relaxed">
              {paragraph}
            </p>
          ))}
        </div>

        {component.metadata.user_action_required && (
          <div className="mt-4 p-3 bg-blue-100 rounded-md">
            <p className="text-sm font-medium text-blue-800">
              👆 Action Required: This section requires your attention or action.
            </p>
          </div>
        )}

        {component.metadata.related_sections.length > 0 && (
          <div className="mt-4 text-sm text-gray-600">
            <p className="font-medium mb-1">Related sections:</p>
            <ul className="list-disc list-inside space-y-1">
              {component.metadata.related_sections.map((section, index) => (
                <li key={index}>{section}</li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
          <span>Importance Score: {component.importance_score.toFixed(2)}</span>
          <span>Type: {component.type.replace('_', ' ')}</span>
        </div>
      </CardContent>
    </Card>
  );
}; 