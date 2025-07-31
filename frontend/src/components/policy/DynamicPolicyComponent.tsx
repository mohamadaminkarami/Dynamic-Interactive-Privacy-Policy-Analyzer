import React, { useState, useRef } from 'react';
import { UIComponent, QuizResult } from '@/types/policy';
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card';
import StyledTextRenderer from './StyledTextRenderer';
import InteractiveQuizComponent from './InteractiveQuiz';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { motion } from 'framer-motion';

interface DynamicPolicyComponentProps {
  component: UIComponent;
  forceExpanded?: boolean;
  isDragging?: boolean;
} 

export const DynamicPolicyComponent: React.FC<DynamicPolicyComponentProps> = ({
  component,
  forceExpanded = false,
  isDragging = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizResults, setQuizResults] = useState<QuizResult | null>(null);
  
  // Ref for scrolling to quiz
  const quizRef = useRef<HTMLDivElement>(null);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({
    id: component.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  // Smart expansion logic based on sensitivity score, importance, and quiz requirements
  const shouldExpandByDefault = () => {
    const hasHighImportance = component.content.importance_score > 0.5;
    const hasHighSensitivity = component.content.sensitivity_score >= 6.0;
    const requiresQuiz = component.content.requires_quiz;
    
    return hasHighImportance || hasHighSensitivity || requiresQuiz;
  };

  // Determine actual expansion state - prioritize user interaction over defaults
  const actuallyExpanded = forceExpanded || isExpanded;

  const handleQuizComplete = (result: QuizResult) => {
    setQuizResults(result);
    // Don't hide the quiz immediately - let the quiz component handle showing results
  };

  const handleQuizClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!actuallyExpanded) {
      setIsExpanded(true);
    }
    setShowQuiz(true);
    
    // Scroll to quiz after it's rendered
    setTimeout(() => {
      if (quizRef.current) {
        quizRef.current.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center',
          inline: 'nearest'
        });
        // Optional: Add focus for accessibility
        quizRef.current.focus();
      }
    }, 100); // Small delay to ensure DOM is updated
  };

  const handleExpandToggle = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      setShowQuiz(false); // Close quiz when collapsing
    }
  };

  const handleExpandButtonClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    handleExpandToggle();
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high':
        return 'border-red-500 bg-red-50';
      case 'medium':
        return 'border-yellow-500 bg-yellow-50';
      case 'low':
        return 'border-green-500 bg-green-50';
      default:
        return 'border-gray-300 bg-white';
    }
  };

  const getIconByType = (type: string) => {
    switch (type) {
      case 'risk_warning':
        return '⚠️';
      case 'highlight_card':
        return '✨';
      case 'rights_interactive':
        return '🔒';
      case 'data_collection_card':
        return '📊';
      case 'quiz_component':
        return '🎯';
      default:
        return '📄';
    }
  };

  // Enhanced styling based on sensitivity
  const sensitivityScore = component.content.sensitivity_score;
  const privacyImpact = component.content.privacy_impact_score;
  
  const getTextStyle = () => {
    if (sensitivityScore >= 8) return 'text-red-800 font-bold';
    if (sensitivityScore >= 6) return 'text-red-700 font-semibold';
    if (sensitivityScore >= 4) return 'text-orange-700 font-medium';
    return 'text-gray-700';
  };

  const getCardStyle = () => {
    const baseStyle = getRiskColor(component.content.risk_level);
    if (isDragging || isSortableDragging) {
      return baseStyle + ' opacity-50 rotate-2 shadow-lg';
    }
    if (sensitivityScore >= 8) return baseStyle + ' ring-2 ring-red-500';
    if (sensitivityScore >= 6) return baseStyle + ' ring-1 ring-orange-500';
    return baseStyle;
  };

  const getBorderStyle = () => {
    if (sensitivityScore >= 8) return 'border-l-4 border-l-red-500';
    if (sensitivityScore >= 6) return 'border-l-4 border-l-orange-500';
    if (sensitivityScore >= 4) return 'border-l-4 border-l-yellow-500';
    return 'border-l-4 border-l-blue-500';
  };

  const getDisplayTitle = () => {
    const title = component.content.title || `Section ${component.priority}`;
    
    return title;
  };

  // Generate concise summary for collapsed state
  const getCollapsedSummary = () => {
    const keyPoints = [];
    
    // Add main purpose/activity from summary
    if (component.content.summary) {
      // Clean up the summary by removing redundant intro text and quotes
      const cleanedSummary = component.content.summary
        .replace(/^Here is a user-friendly summary of the privacy policy section:\s*-?\s*/i, '')
        .replace(/^Here is a user-friendly summary of the privacy policy section:\s*/i, '')
        .replace(/^Here is a user-friendly summary:\s*/i, '')
        .replace(/^Summary:\s*/i, '')
        .replace(/^["']|["']$/g, '') // Remove leading/trailing quotes
        .replace(/\s*["']\s*/g, ' ') // Remove quotes within text
        .trim();
      
      // For detailed summaries, try to extract key categories
      if (cleanedSummary.length > 100) {
        // Split by sentences and show first 2 key points
        const sentences = cleanedSummary.split(/[.!?]+/);
        for (let i = 0; i < Math.min(2, sentences.length); i++) {
          const sentence = sentences[i]?.trim();
          if (sentence && sentence.length > 15 && sentence !== getDisplayTitle()) {
            const cleanSentence = sentence
              .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
              .replace(/\*(.*?)\*/g, '$1')     // Remove italic markdown
              .replace(/#{1,6}\s*/g, '')       // Remove headers
              .trim();
            keyPoints.push(cleanSentence);
          }
        }
      } else {
        // For shorter summaries, use the whole thing
        const mainSentence = cleanedSummary;
        if (mainSentence && mainSentence.length > 10 && mainSentence !== getDisplayTitle()) {
          const cleanSentence = mainSentence
            .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
            .replace(/\*(.*?)\*/g, '$1')     // Remove italic markdown
            .replace(/#{1,6}\s*/g, '')       // Remove headers
            .trim();
          keyPoints.push(cleanSentence);
        }
      }
    }
    
    // Add key concerns as highlights
    if (component.content.key_concerns && component.content.key_concerns.length > 0) {
      const topConcern = component.content.key_concerns[0];
      if (topConcern && topConcern.length < 100) {
        keyPoints.push(`⚠️ ${topConcern}`);
      }
    }
    
    // Add user rights if any
    if (component.content.user_rights && component.content.user_rights.length > 0) {
      const rightsSummary = component.content.user_rights.length === 1 
        ? `✅ You have 1 right: ${component.content.user_rights[0]}`
        : `✅ You have ${component.content.user_rights.length} rights including ${component.content.user_rights[0]}`;
      keyPoints.push(rightsSummary);
    }
    
    // Add data types if any
    if (component.content.data_types && component.content.data_types.length > 0) {
      const dataTypesSummary = component.content.data_types.length <= 2
        ? `📊 Data: ${component.content.data_types.join(', ')}`
        : `📊 Data: ${component.content.data_types.slice(0, 2).join(', ')} and ${component.content.data_types.length - 2} more`;
      keyPoints.push(dataTypesSummary);
    }
    
    // If we don't have any key points, create a generic one
    if (keyPoints.length === 0) {
      keyPoints.push('📄 Privacy policy information');
    }
    
    return keyPoints.slice(0, 3); // Show maximum 3 key points
  };

  const cardStyle = getCardStyle();
  const textStyle = getTextStyle();
  const borderStyle = getBorderStyle();
  const icon = getIconByType(component.type);
  const displayTitle = getDisplayTitle();
  const collapsedSummary = getCollapsedSummary();

  // Check if we have styled content to display
  const hasStyledSummary = component.content.styled_summary && 
    component.content.styled_summary.styling_applied && 
    component.content.styled_summary.segments.length > 0;

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...attributes}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`${isDragging || isSortableDragging ? 'z-50' : ''}`}
    >
      <Card className={`${cardStyle} ${borderStyle} transition-all duration-200 hover:shadow-md`}>
        <div 
          className="pb-3 cursor-pointer select-none"
          onClick={handleExpandToggle}
        >
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Drag Handle */}
              <div 
                className="flex items-center gap-2"
                {...listeners}
                onClick={(e) => e.stopPropagation()} // Prevent expand/collapse when dragging
              >
                <span className="text-xl">{icon}</span>
              </div>
              
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-lg ${textStyle}`}>
                    {displayTitle}
                  </span>
                  
                  {/* Enhanced Sensitivity Badge */}
                  {sensitivityScore >= 6 && (
                    <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                      sensitivityScore >= 8 ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                    }`}>
                      {sensitivityScore >= 8 ? 'High Risk' : 'Moderate Risk'}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center gap-4 text-xs text-gray-800 font-semibold">
                  <span>Priority: #{component.priority}</span>
                  <span>Sensitivity: {sensitivityScore.toFixed(1)}/10</span>
                  <span>Impact: {privacyImpact.toFixed(1)}/10</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {/* Quiz indicator - only show if quiz actually exists */}
              {component.content.requires_quiz && component.content.quiz && (
                <button
                  onClick={handleQuizClick}
                  className="text-purple-600 text-sm font-medium hover:text-purple-700 hover:bg-purple-50 px-2 py-1 rounded transition-colors"
                >
                  🎯 Quiz
                </button>
              )}
              
              {/* Show quiz unavailable indicator if required but missing */}
              {component.content.requires_quiz && !component.content.quiz && (
                <span className="text-gray-500 text-xs px-2 py-1 bg-gray-100 rounded">
                  ⚠️ Quiz Unavailable
                </span>
              )}
              
              {/* Expansion arrow - clickable area */}
              <button
                onClick={handleExpandButtonClick}
                className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                aria-label={actuallyExpanded ? 'Collapse section' : 'Expand section'}
              >
                <motion.span
                  animate={{ rotate: actuallyExpanded ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                  className="text-gray-700 text-lg block"
                >
                  ▼
                </motion.span>
              </button>
            </div>
          </CardTitle>
        </CardHeader>
        </div>

        {/* Collapsed Summary */}
        {!actuallyExpanded && (
          <CardContent className="pt-0">
            <div className="space-y-2">
              {collapsedSummary.map((point, index) => (
                <div key={index} className="flex items-start gap-2 text-sm text-gray-800">
                  <span className="text-gray-600 mt-1">•</span>
                  <span className="font-semibold">{point}</span>
                </div>
              ))}
              
              {/* Quick stats */}
              <div className="flex flex-wrap gap-2 mt-3 pt-2 border-t border-gray-200">
                <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full font-medium">
                  {(component.content as any).reading_time || 1}min read
                </span>
        
              </div>
            </div>
          </CardContent>
        )}

        {/* Full Content - Only shown when expanded */}
        <CardContent>
          <div className={`transition-all duration-300 ease-in-out overflow-hidden ${
            actuallyExpanded ? 'max-h-none opacity-100' : 'max-h-0 opacity-0'
          }`}>
            <div className="space-y-4">
            {/* Enhanced Content Display */}
            {hasStyledSummary && component.content.styled_summary ? (
              <div className="mb-4">
                <StyledTextRenderer 
                  styledContent={component.content.styled_summary}
                  className="leading-relaxed"
                />
              </div>
            ) : (
              <div className={`prose prose-sm max-w-none ${textStyle} mb-4`}>
                <div dangerouslySetInnerHTML={{ 
                  __html: component.content.summary
                    ?.replace(/^Here is a user-friendly summary of the privacy policy section:\s*-?\s*/i, '')
                    ?.replace(/^Here is a user-friendly summary of the privacy policy section:\s*/i, '')
                    ?.replace(/^Here is a user-friendly summary:\s*/i, '')
                    ?.replace(/^Summary:\s*/i, '')
                    ?.replace(/^["']|["']$/g, '') // Remove leading/trailing quotes
                    ?.replace(/\s*["']\s*/g, ' ') // Remove quotes within text
                    ?.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    ?.replace(/\*(.*?)\*/g, '<em>$1</em>')
                    ?.replace(/\n/g, '<br/>')
                }} />
              </div>
            )}
            
            {/* Enhanced Scoring Display */}
            <div className="grid grid-cols-3 gap-3 text-sm">
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="font-semibold text-orange-600">{sensitivityScore.toFixed(1)}</div>
                <div className="text-xs text-gray-800 font-medium">Sensitivity</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="font-semibold text-red-600">{privacyImpact.toFixed(1)}</div>
                <div className="text-xs text-gray-800 font-medium">Privacy Impact</div>
              </div>
              <div className="text-center p-2 bg-gray-50 rounded">
                <div className="font-semibold text-blue-600">{component.content.user_control}/5</div>
                <div className="text-xs text-gray-800 font-medium">User Control</div>
              </div>
            </div>

            {/* Key Concerns */}
            {component.content.key_concerns?.length > 0 && (
              <div className="bg-red-50 p-3 rounded-lg">
                <h4 className="font-semibold text-red-800 mb-2">🚨 Key Concerns</h4>
                <ul className="text-sm text-red-700 space-y-1">
                  {component.content.key_concerns.map((concern, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-red-500 mt-1">•</span>
                      <span>{concern}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* User Rights */}
            {component.content.user_rights?.length > 0 && (
              <div className="bg-green-50 p-3 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-2">✅ Your Rights</h4>
                <ul className="text-sm text-green-700 space-y-1">
                  {component.content.user_rights.map((right, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-green-500 mt-1">•</span>
                      <span>{right}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Data Types */}
            {component.content.data_types?.length > 0 && (
              <div className="bg-blue-50 p-3 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">📊 Data Types Collected</h4>
                <div className="flex flex-wrap gap-2">
                  {component.content.data_types.map((dataType, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                      {dataType}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Quiz Section */}
            {component.content.requires_quiz && (
              <div className="bg-purple-50 p-3 rounded-lg">
                <h4 className="font-semibold text-purple-800 mb-2">🎯 Test Your Understanding</h4>
                <p className="text-sm text-purple-700 mb-3">
                  This section contains important information that affects your privacy.
                  {component.content.quiz ? ' Take the quiz to ensure you understand the implications.' : ' A quiz was recommended but is currently unavailable.'}
                </p>
                
                {component.content.quiz ? (
                  <div className="mt-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (showQuiz) {
                          setShowQuiz(false);
                          setQuizResults(null); // Clear results when hiding
                        } else {
                          setShowQuiz(true);
                        }
                      }}
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
                ) : (
                  <div className="mt-3 p-2 bg-yellow-100 border border-yellow-300 rounded">
                    <p className="text-sm text-yellow-800">
                      ⚠️ Quiz generation failed. This section was flagged as high-risk and would benefit from interactive learning.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Interactive Quiz Component */}
            {showQuiz && component.content.quiz && (
              <div ref={quizRef} className="mt-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 rounded-lg" tabIndex={-1}>
                <InteractiveQuizComponent
                  quiz={component.content.quiz}
                  onComplete={handleQuizComplete}
                  onClose={() => {
                    setShowQuiz(false);
                    setQuizResults(null);
                  }}
                />
              </div>
            )}

            {/* Display Priority and Importance */}
            <div className="flex justify-between items-center text-xs text-gray-700 pt-2 border-t border-gray-200">
              <span>Importance: {component.content.importance_score?.toFixed(2) || 'N/A'}</span>
              <span>Priority: #{component.priority}</span>
              <span>Entities: {component.metadata?.entities_count || 0}</span>
              {hasStyledSummary && (
                <span className="text-green-600">
                  ✨ {component.content.styled_summary?.total_segments} segments
                </span>
              )}
            </div>
          </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}; 