import React, { useState } from 'react';
import { UIComponent, QuizResult } from '@/types/policy';
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card';
import StyledTextRenderer from './StyledTextRenderer';
import InteractiveQuizComponent from './InteractiveQuiz';

interface DynamicPolicyComponentProps {
  component: UIComponent;
}

export const DynamicPolicyComponent: React.FC<DynamicPolicyComponentProps> = ({ component }) => {
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizResults, setQuizResults] = useState<QuizResult | null>(null);

  const handleQuizComplete = (result: QuizResult) => {
    setQuizResults(result);
    console.log('Quiz completed:', result);
  };
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

  const getStyleBySensitivityScore = (score: number) => {
    if (score >= 8.0) return 'border-red-500 bg-red-50';
    if (score >= 6.0) return 'border-orange-400 bg-orange-50';
    if (score >= 4.0) return 'border-yellow-400 bg-yellow-50';
    return 'border-green-400 bg-green-50';
  };

  const getTextEmphasisStyle = (level: number, fontWeight: string) => {
    const baseStyle = 'transition-all duration-200';
    
    let emphasisStyle = '';
    switch (level) {
      case 5:
        emphasisStyle = 'text-red-900 font-bold';
        break;
      case 4:
        emphasisStyle = 'text-orange-800 font-semibold';
        break;
      case 3:
        emphasisStyle = 'text-yellow-700 font-medium';
        break;
      case 2:
        emphasisStyle = 'text-blue-700 font-normal';
        break;
      default:
        emphasisStyle = 'text-gray-700 font-normal';
    }
    
    return `${baseStyle} ${emphasisStyle}`;
  };

  // Use the enhanced numerical scores for styling
  const sensitivityScore = component.content.sensitivity_score || 5;
  const privacyImpact = component.content.privacy_impact_score || 5;
  const textEmphasis = component.content.text_emphasis_level || 1;
  const fontWeight = component.content.font_weight || 'normal';
  const highlightColor = component.content.highlight_color || 'neutral';
  const engagementLevel = component.content.engagement_level || 'standard';

  const cardStyle = getStyleBySensitivityScore(sensitivityScore);
  const textStyle = getTextEmphasisStyle(textEmphasis, fontWeight);

  const getIconByType = (type: string) => {
    switch (type) {
      case 'highlight_card':
        return '🌟';
      case 'risk_warning':
      case 'privacy_warning':
      case 'high_sensitivity_card':
        return '⚠️';
      case 'rights_interactive':
        return '⚖️';
      case 'data_collection_card':
        return '📊';
      case 'quiz_component':
        return '🎯';
      case 'interactive_component':
        return '🎮';
      default:
        return '📋';
    }
  };

  const getDisplayTitle = () => {
    const title = component.content.title || `Section ${component.priority}`;
    
    // Try to extract a meaningful title from the summary
    if (title.startsWith('Section ') && component.content.summary) {
      const summaryLines = component.content.summary.split('\n');
      const firstLine = summaryLines[0];
      
      // Look for headers in markdown format
      const headerMatch = firstLine.match(/^#+\s*(.+)/);
      if (headerMatch) {
        return headerMatch[1];
      }
      
      // Look for bold text that might be a title
      const boldMatch = firstLine.match(/\*\*(.+?)\*\*/);
      if (boldMatch) {
        return boldMatch[1];
      }
      
      // Use first meaningful line if not too long
      if (firstLine.length > 10 && firstLine.length < 80) {
        return firstLine.replace(/[*#]/g, '').trim();
      }
    }
    
    return title;
  };

  const styleClass = cardStyle;
  const icon = getIconByType(component.type);
  const displayTitle = getDisplayTitle();

  // Check if we have styled content to display
  const hasStyledSummary = component.content.styled_summary && 
    component.content.styled_summary.styling_applied && 
    component.content.styled_summary.segments.length > 0;

  return (
    <Card className={`${styleClass} border-l-4 transition-all duration-300 hover:shadow-lg`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <span className="text-xl">{icon}</span>
          <span className={textStyle}>{displayTitle}</span>
          <div className="ml-auto flex items-center gap-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              sensitivityScore >= 8.0 ? 'bg-red-100 text-red-800' :
              sensitivityScore >= 6.0 ? 'bg-orange-100 text-orange-800' :
              sensitivityScore >= 4.0 ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {sensitivityScore.toFixed(1)}/10
            </span>
            {component.content.requires_quiz && (
              <span className="px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                QUIZ
              </span>
            )}
            {component.content.requires_visual_aid && (
              <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                VISUAL
              </span>
            )}
            {hasStyledSummary && (
              <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                STYLED
              </span>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Enhanced Content Display */}
          {hasStyledSummary ? (
            <div className="mb-4">
              <StyledTextRenderer 
                styledContent={component.content.styled_summary}
                className="leading-relaxed"
              />
            </div>
          ) : (
            <div className={`prose prose-sm max-w-none ${textStyle} mb-4`}>
              <div dangerouslySetInnerHTML={{ 
                __html: component.content.summary?.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                  .replace(/\*(.*?)\*/g, '<em>$1</em>')
                  .replace(/\n/g, '<br/>')
              }} />
            </div>
          )}
          
          {/* Enhanced Scoring Display */}
          <div className="grid grid-cols-3 gap-3 text-sm">
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="font-semibold text-orange-600">{sensitivityScore.toFixed(1)}</div>
              <div className="text-xs text-gray-600">Sensitivity</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="font-semibold text-red-600">{privacyImpact.toFixed(1)}</div>
              <div className="text-xs text-gray-600">Privacy Impact</div>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="font-semibold text-blue-600">{component.content.user_control}/5</div>
              <div className="text-xs text-gray-600">User Control</div>
            </div>
          </div>

          {/* Key Concerns */}
          {component.content.key_concerns?.length > 0 && (
            <div className="bg-yellow-50 p-3 rounded-lg border-l-4 border-yellow-400">
              <h4 className="font-medium text-yellow-800 mb-2">🚨 Key Concerns:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
                {component.content.key_concerns.map((concern: string, index: number) => (
                  <li key={index}>{concern}</li>
                ))}
              </ul>
            </div>
          )}

          {/* User Rights */}
          {component.content.user_rights?.length > 0 && (
            <div className="bg-green-50 p-3 rounded-lg border-l-4 border-green-400">
              <h4 className="font-medium text-green-800 mb-2">⚖️ Your Rights:</h4>
              <div className="flex flex-wrap gap-2">
                {component.content.user_rights.map((right: string, index: number) => (
                  <span key={index} className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                    {right}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Engagement Level Indicator */}
          {engagementLevel !== 'standard' && (
            <div className={`p-3 rounded-lg border-l-4 ${
              engagementLevel === 'quiz' ? 'bg-purple-50 border-purple-400' :
              engagementLevel === 'interactive' ? 'bg-blue-50 border-blue-400' :
              'bg-gray-50 border-gray-400'
            }`}>
              <div className={`font-medium mb-1 ${
                engagementLevel === 'quiz' ? 'text-purple-800' :
                engagementLevel === 'interactive' ? 'text-blue-800' :
                'text-gray-800'
              }`}>
                {engagementLevel === 'quiz' ? '🎯 Interactive Quiz Recommended' :
                 engagementLevel === 'interactive' ? '🎮 Interactive Content' :
                 'Enhanced Content'}
              </div>
              <div className={`text-sm ${
                engagementLevel === 'quiz' ? 'text-purple-700' :
                engagementLevel === 'interactive' ? 'text-blue-700' :
                'text-gray-700'
              }`}>
                {engagementLevel === 'quiz' ? 'This section contains high-sensitivity content that would benefit from interactive learning.' :
                 engagementLevel === 'interactive' ? 'This section includes interactive elements for better understanding.' :
                 'This section has been enhanced for better comprehension.'}
              </div>
              
              {/* Quiz Button */}
              {component.content.requires_quiz && component.content.quiz && (
                <div className="mt-3">
                  <button
                    onClick={() => setShowQuiz(!showQuiz)}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium text-sm"
                  >
                    {showQuiz ? 'Hide Quiz' : 'Take Quiz'} 🎯
                  </button>
                  {quizResults && (
                    <span className="ml-3 px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                      Last Score: {quizResults.percentage}%
                    </span>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Interactive Quiz Component */}
          {showQuiz && component.content.quiz && (
            <div className="mt-4">
              <InteractiveQuizComponent
                quiz={component.content.quiz}
                onComplete={handleQuizComplete}
              />
            </div>
          )}

          {/* Display Priority and Importance */}
          <div className="flex justify-between items-center text-xs text-gray-500 pt-2 border-t border-gray-200">
            <span>Importance: {component.content.importance_score?.toFixed(2) || 'N/A'}</span>
            <span>Priority: #{component.priority}</span>
            <span>Entities: {component.metadata?.entities_count || 0}</span>
            {hasStyledSummary && (
              <span className="text-green-600">
                ✨ {component.content.styled_summary.total_segments} segments
              </span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 