import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable,
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { UIComponent } from '@/types/policy';

interface Permission {
  id: string;
  title: string;
  description: string;
  riskLevel: 'low' | 'medium' | 'high';
  dataTypes: string[];
  purpose: string;
  required: boolean;
  impactLevel: number; // Impact level 1-5
  source: string; // Which section this permission comes from
}

interface PermissionConsentManagerProps {
  components: UIComponent[];
  onConsentChange: (permissions: Permission[]) => void;
}

interface DraggablePermissionProps {
  permission: Permission;
  isAgreed: boolean;
}

const DraggablePermission: React.FC<DraggablePermissionProps> = ({ permission, isAgreed }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: permission.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'border-red-400 bg-red-50';
      case 'medium': return 'border-yellow-400 bg-yellow-50';
      case 'low': return 'border-green-400 bg-green-50';
      default: return 'border-gray-400 bg-gray-50';
    }
  };

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      whileDrag={{ scale: 1.05, rotate: 2 }}
      className={`
        p-4 rounded-lg border-2 cursor-grab active:cursor-grabbing
        ${getRiskColor(permission.riskLevel)}
        ${isDragging ? 'opacity-50 shadow-2xl z-50' : ''}
        ${isAgreed ? 'opacity-70' : ''}
        transition-all duration-200 hover:shadow-md
      `}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">
            {permission.riskLevel === 'high' ? '🔴' : 
             permission.riskLevel === 'medium' ? '🟡' : '🟢'}
          </span>
          <h4 className="font-semibold text-gray-900">{permission.title}</h4>
          {permission.required && (
            <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
              Required
            </span>
          )}
        </div>
        <div className="text-gray-700 text-sm font-medium">⋮⋮</div>
      </div>
      
      <p className="text-sm text-gray-800 mb-3 font-medium">{permission.description}</p>
      
      <div className="space-y-2">
        <div className="flex flex-wrap gap-1">
          {permission.dataTypes.map((type, index) => (
            <span
              key={index}
              className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
            >
              {type}
            </span>
          ))}
        </div>
        
      </div>
    </motion.div>
  );
};

interface DropZoneProps {
  id: string;
  title: string;
  subtitle: string;
  permissions: Permission[];
  isActive: boolean;
  isEmpty: boolean;
  color: string;
}

const DropZone: React.FC<DropZoneProps> = ({ 
  id, 
  title, 
  subtitle, 
  permissions, 
  isActive, 
  isEmpty, 
  color 
}) => {
  const { setNodeRef, isOver } = useDroppable({
    id: id,
  });

  return (
    <div 
      ref={setNodeRef}
      className={`
        min-h-[400px] p-4 border-2 border-dashed rounded-lg transition-all duration-200
        ${isActive || isOver ? `border-${color}-400 bg-${color}-50 shadow-lg` : 'border-gray-300 bg-gray-50'}
        ${isOver ? 'ring-2 ring-opacity-50 ring-' + color + '-300' : ''}
      `}
    >
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-800 font-medium">{subtitle}</p>
        <div className="mt-2 text-sm text-gray-700">
          Drop permissions here to {title.toLowerCase().includes('agreed') ? 'agree' : 'decline'}
        </div>
      </div>
      
      {isEmpty && (
        <div className="flex items-center justify-center h-32 text-gray-600">
          <p className="text-sm font-medium">Drop permissions here</p>
        </div>
      )}
      
      <SortableContext
        items={permissions.map(p => p.id)}
        strategy={verticalListSortingStrategy}
      >
        <div className="space-y-3">
          {permissions.map((permission) => (
            <DraggablePermission
              key={permission.id}
              permission={permission}
              isAgreed={id === 'agreed'}
            />
          ))}
        </div>
      </SortableContext>
    </div>
  );
};

export const PermissionConsentManager: React.FC<PermissionConsentManagerProps> = ({ 
  components, 
  onConsentChange 
}) => {
  const [availablePermissions, setAvailablePermissions] = useState<Permission[]>([]);
  const [agreedPermissions, setAgreedPermissions] = useState<Permission[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [draggedPermission, setDraggedPermission] = useState<Permission | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  // Extract permissions from components
  React.useEffect(() => {
    const extractedPermissions: Permission[] = [];
    
    components.forEach((component) => {
      // Debug logging for permission extraction
      if (component.content.title || component.content.summary) {
        console.log('Processing component:', {
          id: component.id,
          title: component.content.title,
          summary: component.content.summary?.substring(0, 100) + '...',
          sensitivity_score: component.content.sensitivity_score,
          privacy_impact_score: component.content.privacy_impact_score,
          data_sharing_risk: component.content.data_sharing_risk,
          data_types: component.content.data_types,
          key_concerns: component.content.key_concerns
        });
      }
      // Extract data collection permissions - also check key_concerns for data types
      const hasDataTypes = component.content.data_types && component.content.data_types.length > 0;
      const hasDataInConcerns = component.content.key_concerns?.some(concern => 
        ['payment', 'financial', 'biometric', 'health', 'location', 'personal'].some(dataType =>
          concern.toLowerCase().includes(dataType)));
      
      if (hasDataTypes || hasDataInConcerns) {
        const sensitivityScore = component.content.sensitivity_score ?? 5;
        const privacyImpact = component.content.privacy_impact_score ?? 5;
        // Map 0-10 scale to 1-5 scale: more granular mapping
        const avgScore = (sensitivityScore + privacyImpact) / 2;
        const impactLevel = avgScore <= 2 ? 1 : 
                           avgScore <= 4 ? 2 : 
                           avgScore <= 6 ? 3 : 
                           avgScore <= 8 ? 4 : 5;
        
        // For debugging: force varied impact levels if scores are using defaults
        const debugImpactLevel = extractedPermissions.length % 5 + 1;
        
        // Check for critical data types in both data_types array and key_concerns
        const hasRequiredDataTypes = component.content.data_types?.some(type => 
          ['payment', 'financial', 'biometric', 'health'].some(critical => 
            type.toLowerCase().includes(critical))) ||
          component.content.key_concerns?.some(concern => 
            ['payment', 'financial', 'biometric', 'health'].some(critical => 
              concern.toLowerCase().includes(critical)));
              
        const hasRequiredSummary = component.content.summary?.toLowerCase().includes('required') ||
          component.content.summary?.toLowerCase().includes('mandatory') ||
          component.content.title?.toLowerCase().includes('mandatory') ||
          component.content.title?.toLowerCase().includes('required');
        
        console.log('Data collection permission:', {
          sensitivityScore, privacyImpact, avgScore, impactLevel,
          data_types: component.content.data_types,
          hasRequiredDataTypes,
          hasRequiredSummary,
          summary: component.content.summary?.substring(0, 50)
        });
        
        extractedPermissions.push({
          id: `data_collection_${component.id}`,
          title: 'Data Collection',
          description: hasDataTypes ? 
            `Allow collection of ${component.content.data_types.join(', ')}` :
            `Collection of sensitive data including ${component.content.key_concerns?.filter(c => 
              ['payment', 'financial', 'biometric', 'health', 'location', 'personal'].some(dt => 
                c.toLowerCase().includes(dt))).slice(0,2).join(', ') || 'personal information'}`,
          riskLevel: sensitivityScore >= 7 ? 'high' : 
                     sensitivityScore >= 5 ? 'medium' : 'low',
          dataTypes: hasDataTypes ? component.content.data_types : 
            ['Biometric data', 'Payment information', 'Health data', 'Personal information'],
          purpose: 'Service provision and functionality',
          required: hasRequiredDataTypes || hasRequiredSummary,
          impactLevel: (sensitivityScore === 5 && privacyImpact === 5) ? debugImpactLevel : Math.min(5, impactLevel),
          source: component.content.title || `Section ${component.priority}`,
        });
      }

      // Extract sharing permissions from key concerns
      if (component.content.key_concerns) {
        component.content.key_concerns.forEach((concern, index) => {
          if (concern.toLowerCase().includes('shar') || concern.toLowerCase().includes('third party')) {
            const dataSharingRisk = component.content.data_sharing_risk || 7;
            const privacyImpact = component.content.privacy_impact_score || 6;
            // Map 0-10 scale to 1-5 scale: more granular mapping
            const avgScore = (dataSharingRisk + privacyImpact) / 2;
            const impactLevel = avgScore <= 2 ? 1 : 
                               avgScore <= 4 ? 2 : 
                               avgScore <= 6 ? 3 : 
                               avgScore <= 8 ? 4 : 5;
            
            extractedPermissions.push({
              id: `sharing_${component.id}_${index}`,
              title: 'Data Sharing',
              description: concern,
              riskLevel: dataSharingRisk >= 8 ? 'high' : 
                         dataSharingRisk >= 6 ? 'medium' : 'low',
              dataTypes: component.content.data_types || ['Personal information'],
              purpose: 'Third-party services and advertising',
              required: concern.toLowerCase().includes('required') || 
                       concern.toLowerCase().includes('necessary') ||
                       concern.toLowerCase().includes('must') ||
                       dataSharingRisk >= 9,
              impactLevel: Math.min(5, impactLevel),
              source: component.content.title || `Section ${component.priority}`,
            });
          }
        });
      }

      // Extract marketing permissions
      if (component.content.summary?.toLowerCase().includes('marketing') || 
          component.content.summary?.toLowerCase().includes('advertising')) {
        const sensitivityScore = component.content.sensitivity_score || 4;
        const privacyImpact = component.content.privacy_impact_score || 3;
        // Map 0-10 scale to 1-5 scale, marketing typically has lower scores
        const avgScore = (sensitivityScore + privacyImpact) / 2;
        const impactLevel = avgScore <= 2 ? 1 : 
                           avgScore <= 4 ? 2 : 
                           avgScore <= 6 ? 3 : 
                           avgScore <= 8 ? 4 : 5;
        
        extractedPermissions.push({
          id: `marketing_${component.id}`,
          title: 'Marketing Communications',
          description: 'Allow use of your data for marketing and promotional purposes',
          riskLevel: sensitivityScore >= 6 ? 'high' : 
                     sensitivityScore >= 4 ? 'medium' : 'low',
          dataTypes: ['Email address', 'Usage data'],
          purpose: 'Marketing and promotions',
          required: component.content.summary?.toLowerCase().includes('mandatory') ||
                   component.content.summary?.toLowerCase().includes('required'),
          impactLevel: Math.min(5, impactLevel),
          source: component.content.title || `Section ${component.priority}`,
        });
      }

      // Extract analytics permissions
      if (component.content.summary?.toLowerCase().includes('analytic') || 
          component.content.summary?.toLowerCase().includes('tracking')) {
        const sensitivityScore = component.content.sensitivity_score || 5;
        const dataSharingRisk = component.content.data_sharing_risk || 4;
        // Map 0-10 scale to 1-5 scale
        const avgScore = (sensitivityScore + dataSharingRisk) / 2;
        const impactLevel = avgScore <= 2 ? 1 : 
                           avgScore <= 4 ? 2 : 
                           avgScore <= 6 ? 3 : 
                           avgScore <= 8 ? 4 : 5;
        
        extractedPermissions.push({
          id: `analytics_${component.id}`,
          title: 'Analytics & Tracking',
          description: 'Allow collection and analysis of usage data for improving services',
          riskLevel: sensitivityScore >= 7 ? 'high' : 
                     sensitivityScore >= 5 ? 'medium' : 'low',
          dataTypes: ['Browsing data', 'Usage patterns'],
          purpose: 'Service improvement and analytics',
          required: component.content.summary?.toLowerCase().includes('essential') ||
                   component.content.summary?.toLowerCase().includes('necessary') ||
                   sensitivityScore >= 8,
          impactLevel: Math.min(5, impactLevel),
          source: component.content.title || `Section ${component.priority}`,
        });
      }
    });

    // Remove duplicates and set initial state
    const uniquePermissions = extractedPermissions.filter((permission, index, self) => 
      index === self.findIndex(p => p.title === permission.title && p.source === permission.source)
    );

    // Debug: Log final permissions to understand what's being generated
    console.log('🎯 FINAL EXTRACTED PERMISSIONS:', uniquePermissions.map(p => ({
      title: p.title,
      impactLevel: p.impactLevel,
      required: p.required,
      riskLevel: p.riskLevel,
      description: p.description.substring(0, 50) + '...'
    })));

    setAvailablePermissions(uniquePermissions);
    setAgreedPermissions([]);
  }, [components]);

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    setActiveId(active.id as string);
    
    const permission = [...availablePermissions, ...agreedPermissions].find(p => p.id === active.id);
    setDraggedPermission(permission || null);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    
    setActiveId(null);
    setDraggedPermission(null);
    
    if (!over) {
      return;
    }

    const activeId = active.id as string;
    const overId = over.id as string;
    
    // Find the permission being dragged
    const permission = [...availablePermissions, ...agreedPermissions].find(p => p.id === activeId);
    if (!permission) return;

    // Determine source and target zones
    const isInAvailable = availablePermissions.find(p => p.id === activeId);
    const isInAgreed = agreedPermissions.find(p => p.id === activeId);

    // Determine target zone - check if overId is a zone or a permission within a zone
    let targetZone = overId;
    
    // If dropping on a permission, find which zone it belongs to
    if (overId !== 'agreed' && overId !== 'available') {
      const overPermissionInAgreed = agreedPermissions.find(p => p.id === overId);
      const overPermissionInAvailable = availablePermissions.find(p => p.id === overId);
      
      if (overPermissionInAgreed) {
        targetZone = 'agreed';
      } else if (overPermissionInAvailable) {
        targetZone = 'available';
      }
    }

    // Prevent dropping on the same zone where the item already is
    if ((targetZone === 'agreed' && isInAgreed) || (targetZone === 'available' && isInAvailable)) {
      return;
    }

    // Move to agreed permissions
    if (targetZone === 'agreed' && isInAvailable) {
      setAvailablePermissions(prev => prev.filter(p => p.id !== activeId));
      setAgreedPermissions(prev => [...prev, permission]);
    }
    
    // Move back to available permissions
    else if (targetZone === 'available' && isInAgreed) {
      setAgreedPermissions(prev => prev.filter(p => p.id !== activeId));
      setAvailablePermissions(prev => [...prev, permission]);
    }
  };

  // Update parent component when consent changes
  React.useEffect(() => {
    onConsentChange(agreedPermissions);
  }, [agreedPermissions, onConsentChange]);

  const requiredPermissions = availablePermissions.filter(p => p.required);
  const optionalPermissions = availablePermissions.filter(p => !p.required);

  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Permission Consent Manager
          </h2>
          <p className="text-gray-700 font-medium">
            Drag and drop permissions to manage your consent preferences
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Available Permissions */}
          <div>
            <DropZone
              id="available"
              title="Available Permissions"
              subtitle="Permissions you can grant to the company"
              permissions={availablePermissions}
              isActive={activeId !== null}
              isEmpty={availablePermissions.length === 0}
              color="blue"
            />
          </div>

          {/* Agreed Permissions */}
          <div>
            <DropZone
              id="agreed"
              title="Agreed Permissions"
              subtitle="Permissions you've consented to"
              permissions={agreedPermissions}
              isActive={activeId !== null}
              isEmpty={agreedPermissions.length === 0}
              color="green"
            />
          </div>
        </div>

        {/* Summary */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">Consent Summary</h3>
          <div className="space-y-2">
            {agreedPermissions.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-green-800 mb-1">✅ Agreed Permissions ({agreedPermissions.length})</h4>
                <ul className="text-xs text-green-700 space-y-1">
                  {agreedPermissions.map(p => (
                    <li key={p.id} className="font-medium">• {p.title}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {availablePermissions.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-800 mb-1">⏳ Available Permissions ({availablePermissions.length})</h4>
                <ul className="text-xs text-gray-700 space-y-1">
                  {availablePermissions.map(p => (
                    <li key={p.id} className="font-medium">• {p.title}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {requiredPermissions.length > 0 && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">
                ⚠️ <strong>{requiredPermissions.length}</strong> required permission{requiredPermissions.length !== 1 ? 's' : ''} 
                must be accepted to use the service.
              </p>
            </div>
          )}
        </div>
      </div>

      <DragOverlay>
        {draggedPermission && (
          <motion.div
            initial={{ scale: 1.05, opacity: 0.9 }}
            animate={{ scale: 1.05, opacity: 0.9 }}
            className="transform rotate-2 shadow-2xl z-50"
            style={{
              filter: 'drop-shadow(0 10px 20px rgba(0, 0, 0, 0.3))',
            }}
          >
            <DraggablePermission 
              permission={draggedPermission} 
              isAgreed={false}
            />
          </motion.div>
        )}
      </DragOverlay>
    </DndContext>
  );
}; 