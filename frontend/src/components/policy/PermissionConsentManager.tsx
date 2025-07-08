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
        ${isDragging ? 'opacity-50' : ''}
        ${isAgreed ? 'opacity-70' : ''}
        transition-all duration-200
      `}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">
            {permission.riskLevel === 'high' ? '🔴' : 
             permission.riskLevel === 'medium' ? '🟡' : '🟢'}
          </span>
          <h4 className="font-semibold text-gray-800">{permission.title}</h4>
          {permission.required && (
            <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
              Required
            </span>
          )}
        </div>
        <div className="text-gray-400 text-sm">⋮⋮</div>
      </div>
      
      <p className="text-sm text-gray-600 mb-3">{permission.description}</p>
      
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
        
        <div className="text-xs text-gray-500">
          <span className="font-medium">Purpose:</span> {permission.purpose}
        </div>
        
        <div className="text-xs text-gray-500">
          <span className="font-medium">From:</span> {permission.source}
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
        ${isActive || isOver ? `border-${color}-400 bg-${color}-50` : 'border-gray-300 bg-gray-50'}
      `}
    >
      <div className="text-center mb-4">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <p className="text-sm text-gray-600">{subtitle}</p>
        <div className="mt-2 text-sm text-gray-500">
          {permissions.length} permission{permissions.length !== 1 ? 's' : ''}
        </div>
      </div>
      
      {isEmpty && (
        <div className="flex items-center justify-center h-32 text-gray-400">
          <div className="text-center">
            <div className="text-4xl mb-2">📋</div>
            <p className="text-sm">Drag permissions here</p>
          </div>
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
      // Extract data collection permissions
      if (component.content.data_types && component.content.data_types.length > 0) {
        extractedPermissions.push({
          id: `data_collection_${component.id}`,
          title: 'Data Collection',
          description: `Allow collection of ${component.content.data_types.join(', ')}`,
          riskLevel: component.content.sensitivity_score >= 7 ? 'high' : 
                     component.content.sensitivity_score >= 5 ? 'medium' : 'low',
          dataTypes: component.content.data_types,
          purpose: 'Service provision and functionality',
          required: true,
          source: component.content.title || `Section ${component.priority}`,
        });
      }

      // Extract sharing permissions from key concerns
      if (component.content.key_concerns) {
        component.content.key_concerns.forEach((concern, index) => {
          if (concern.toLowerCase().includes('shar') || concern.toLowerCase().includes('third party')) {
            extractedPermissions.push({
              id: `sharing_${component.id}_${index}`,
              title: 'Data Sharing',
              description: concern,
              riskLevel: 'high',
              dataTypes: component.content.data_types || ['Personal information'],
              purpose: 'Third-party services and advertising',
              required: false,
              source: component.content.title || `Section ${component.priority}`,
            });
          }
        });
      }

      // Extract marketing permissions
      if (component.content.summary?.toLowerCase().includes('marketing') || 
          component.content.summary?.toLowerCase().includes('advertising')) {
        extractedPermissions.push({
          id: `marketing_${component.id}`,
          title: 'Marketing Communications',
          description: 'Allow use of your data for marketing and promotional purposes',
          riskLevel: 'medium',
          dataTypes: ['Email address', 'Usage data'],
          purpose: 'Marketing and promotions',
          required: false,
          source: component.content.title || `Section ${component.priority}`,
        });
      }

      // Extract analytics permissions
      if (component.content.summary?.toLowerCase().includes('analytic') || 
          component.content.summary?.toLowerCase().includes('tracking')) {
        extractedPermissions.push({
          id: `analytics_${component.id}`,
          title: 'Analytics & Tracking',
          description: 'Allow collection and analysis of usage data for improving services',
          riskLevel: 'medium',
          dataTypes: ['Browsing data', 'Usage patterns'],
          purpose: 'Service improvement and analytics',
          required: false,
          source: component.content.title || `Section ${component.priority}`,
        });
      }
    });

    // Remove duplicates and set initial state
    const uniquePermissions = extractedPermissions.filter((permission, index, self) => 
      index === self.findIndex(p => p.title === permission.title && p.source === permission.source)
    );

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

    // Determine source and target
    const isInAvailable = availablePermissions.find(p => p.id === activeId);
    const isInAgreed = agreedPermissions.find(p => p.id === activeId);

    // Move to agreed permissions
    if (overId === 'agreed' && isInAvailable) {
      setAvailablePermissions(prev => prev.filter(p => p.id !== activeId));
      setAgreedPermissions(prev => [...prev, permission]);
    }
    
    // Move back to available permissions
    else if (overId === 'available' && isInAgreed) {
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
            📋 Permission Consent Manager
          </h2>
          <p className="text-gray-600">
            Drag permissions from left to right to indicate your consent. 
            Required permissions are marked and must be accepted.
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
          <h3 className="font-semibold text-gray-800 mb-2">Consent Summary</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Required permissions:</span> {requiredPermissions.length}
            </div>
            <div>
              <span className="font-medium">Optional permissions:</span> {optionalPermissions.length}
            </div>
            <div>
              <span className="font-medium">Permissions granted:</span> {agreedPermissions.length}
            </div>
            <div>
              <span className="font-medium">Pending permissions:</span> {availablePermissions.length}
            </div>
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
            initial={{ scale: 1.05, opacity: 0.8 }}
            animate={{ scale: 1.05, opacity: 0.8 }}
            className="transform rotate-2"
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