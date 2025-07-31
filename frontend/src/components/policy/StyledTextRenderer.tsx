import React from 'react';
import { StyledContent, TextSegment } from '@/types/policy';

interface StyledTextRendererProps {
  styledContent: StyledContent;
  className?: string;
}

export const StyledTextRenderer: React.FC<StyledTextRendererProps> = ({ 
  styledContent, 
  className = '' 
}) => {
  // If styling is not applied, render the original text
  if (!styledContent.styling_applied || styledContent.segments.length === 0) {
    return (
      <div className={`text-gray-800 font-medium ${className}`}>
        {styledContent.original_text}
      </div>
    );
  }

  const getHighlightClass = (color: string) => {
    switch (color) {
      case 'red':
        return 'bg-red-100 border-red-300';
      case 'orange':
        return 'bg-orange-100 border-orange-300';
      case 'yellow':
        return 'bg-yellow-100 border-yellow-300';
      case 'blue':
        return 'bg-blue-100 border-blue-300';
      case 'neutral':
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getTextColorClass = (color: string) => {
    switch (color) {
      case 'red':
        return 'text-red-800';
      case 'orange':
        return 'text-orange-800';
      case 'blue':
        return 'text-blue-800';
      case 'default':
      default:
        return 'text-gray-900';
    }
  };

  const getFontWeightClass = (weight: string) => {
    switch (weight) {
      case 'bold':
        return 'font-bold';
      case 'medium':
        return 'font-medium';
      case 'normal':
      default:
        return 'font-normal';
    }
  };

  const getEmphasisClass = (emphasis: number) => {
    switch (emphasis) {
      case 5:
        return 'shadow-md ring-2 ring-red-200';
      case 4:
        return 'shadow-sm ring-1 ring-orange-200';
      case 3:
        return 'shadow-sm ring-1 ring-yellow-200';
      case 2:
        return 'shadow-sm';
      default:
        return '';
    }
  };

  const renderSegment = (segment: TextSegment, index: number) => {
    const highlightClass = getHighlightClass(segment.highlight_color);
    const textColorClass = getTextColorClass(segment.text_color);
    const fontWeightClass = getFontWeightClass(segment.font_weight);
    const emphasisClass = getEmphasisClass(segment.text_emphasis);
    
    const combinedClass = `
      inline-block px-2 py-1 my-1 rounded-md transition-all duration-200
      ${highlightClass} ${textColorClass} ${fontWeightClass} ${emphasisClass}
      ${segment.requires_attention ? 'hover:shadow-lg hover:ring-2 hover:ring-orange-300 cursor-pointer relative group' : ''}
    `.trim();

    return (
      <span
        key={segment.id}
        className={combinedClass}
      >
        {segment.text}
        {segment.requires_attention && (
          <>
            <span className="ml-1 text-xs">⚠️</span>
            {/* Custom Tooltip */}
            <div className="absolute top-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
              <div className="font-medium">High Sensitivity ({segment.sensitivity_score.toFixed(1)}/10)</div>
              <div className="text-gray-300">Type: {segment.context_type.replace('_', ' ')}</div>
              {segment.key_terms && segment.key_terms.length > 0 && (
                <div className="text-gray-300">Terms: {segment.key_terms.join(', ')}</div>
              )}
              {/* Tooltip Arrow */}
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
            </div>
          </>
        )}
      </span>
    );
  };

  return (
    <div className={`styled-text-container ${className}`}>
      {/* Styling Statistics */}
      {styledContent.high_sensitivity_count > 0 && (
        <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg relative">
          <div className="flex items-center gap-2 text-sm text-red-800">
            <span className="text-red-600">🚨</span>
            <span className="font-medium">
              {styledContent.high_sensitivity_count} high-sensitivity segments found
            </span>
            <span className="text-xs text-red-600">
              ({styledContent.total_segments} total segments)
            </span>
          </div>
        </div>
      )}

      {/* Rendered Segments */}
      <div className="space-y-2 leading-relaxed">
        {styledContent.segments.map((segment, index) => (
          <React.Fragment key={segment.id}>
            {renderSegment(segment, index)}
            {/* Add spacing between segments */}
            {index < styledContent.segments.length - 1 && <span className="text-gray-800"> </span>}
          </React.Fragment>
        ))}
      </div>

      {/* Context Legend */}
      {styledContent.segments.some(s => s.requires_attention) && (
        <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="text-xs font-medium text-gray-800 mb-2">📍 Content Types:</div>
          <div className="flex flex-wrap gap-2 text-xs">
            {Array.from(new Set(styledContent.segments.map(s => s.context_type))).map(type => (
              <span key={type} className="px-2 py-1 bg-white border border-gray-300 rounded-full text-gray-800 font-medium">
                {type.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StyledTextRenderer; 