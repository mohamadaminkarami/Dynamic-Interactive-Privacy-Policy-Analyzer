'use client';

import React, { useState } from 'react';
import { PrivacyPolicy, PolicyRequest, UIComponent } from '@/types/policy';
import { apiClient } from '@/lib/api';
import { DynamicPolicyComponent } from '@/components/policy/DynamicPolicyComponent';
import { PermissionConsentManager } from '@/components/policy/PermissionConsentManager';
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card';
import { motion, AnimatePresence } from 'framer-motion';

export const PolicyViewer: React.FC = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<PrivacyPolicy | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [allExpanded, setAllExpanded] = useState(false); // Default to collapsed for better UX
  const [activeTab, setActiveTab] = useState<'policy' | 'permissions'>('policy');
  const [consentedPermissions, setConsentedPermissions] = useState<any[]>([]);
  
  const [formData, setFormData] = useState<PolicyRequest>({
    policy_content: '',
    company_name: '',
    company_url: '',
    document_type: 'privacy_policy',
    contact_email: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiClient.analyzePolicy(formData);
      setResult(response);
      setConsentedPermissions([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePermissionConsentChange = (permissions: any[]) => {
    setConsentedPermissions(permissions);
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

  const getUserFriendlinessStars = (score: number) => {
    return '⭐'.repeat(Math.round(score));
  };

  const sortedComponents = result?.ui_components?.sort((a, b) => a.priority - b.priority) || [];

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dynamic Privacy Policy Analyzer
        </h1>
        <p className="text-gray-700 font-medium">
          Transform privacy policies into user-centric, interactive presentations with consent management
        </p>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-xl text-gray-800 mb-2">Analyze Privacy Policy</CardTitle>
          <p className="text-gray-700 text-sm font-medium">Enter your company information and privacy policy content to get started</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label htmlFor="company_name" className="block text-sm font-semibold text-gray-800 mb-2">
                  Company Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="company_name"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 bg-white border-2 border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-4 focus:ring-blue-100 focus:border-blue-500 focus:outline-none transition-all duration-200 shadow-sm"
                  placeholder="e.g., Tech Company Inc."
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="company_url" className="block text-sm font-semibold text-gray-800 mb-2">
                  Company URL
                </label>
                <input
                  type="url"
                  id="company_url"
                  name="company_url"
                  value={formData.company_url}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white border-2 border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-4 focus:ring-blue-100 focus:border-blue-500 focus:outline-none transition-all duration-200 shadow-sm"
                  placeholder="https://example.com"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="contact_email" className="block text-sm font-semibold text-gray-800 mb-2">
                Contact Email
              </label>
              <input
                type="email"
                id="contact_email"
                name="contact_email"
                value={formData.contact_email}
                onChange={handleInputChange}
                className="w-full px-4 py-3 bg-white border-2 border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-4 focus:ring-blue-100 focus:border-blue-500 focus:outline-none transition-all duration-200 shadow-sm"
                placeholder="privacy@company.com"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="policy_content" className="block text-sm font-semibold text-gray-800 mb-2">
                Privacy Policy Content <span className="text-red-500">*</span>
              </label>
              <textarea
                id="policy_content"
                name="policy_content"
                value={formData.policy_content}
                onChange={handleInputChange}
                required
                rows={10}
                className="w-full px-4 py-3 bg-white border-2 border-gray-300 rounded-lg text-gray-900 placeholder-gray-500 focus:ring-4 focus:ring-blue-100 focus:border-blue-500 focus:outline-none transition-all duration-200 shadow-sm resize-vertical"
                placeholder="Paste the privacy policy content here..."
              />
              <p className="text-xs text-gray-600 mt-1 font-medium">
                Minimum 100 characters recommended for accurate analysis
              </p>
            </div>

            <div className="pt-4">
              {/* Form validation indicator */}
              {formData.company_name && formData.policy_content && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-green-700 font-medium">Form is ready to analyze</span>
                  </div>
                </div>
              )}
              
              <button
                type="submit"
                disabled={isAnalyzing || !formData.company_name || !formData.policy_content}
                className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                {isAnalyzing ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Analyzing Privacy Policy...
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <span>🔍</span>
                    Analyze Privacy Policy
                  </div>
                )}
              </button>
            </div>
          </form>
        </CardContent>
      </Card>

      {error && (
        <Card className="mb-8 border-red-400 bg-red-50">
          <CardContent>
            <div className="flex items-center gap-2">
              <span className="text-red-600 text-xl">❌</span>
              <div>
                <h3 className="font-medium text-red-800">Error</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="text-2xl">📊</span>
                Policy Analysis Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-white p-6 rounded-lg shadow-md mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Policy Analysis Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center">
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(result.document.overall_risk_level)}`}>
                      <div className="text-sm text-gray-800 font-semibold">
                        {result.document.overall_risk_level.charAt(0).toUpperCase() + 
                         result.document.overall_risk_level.slice(1)} Risk
                      </div>
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl mb-1">
                      {getUserFriendlinessStars(result.document.user_friendliness_score)}
                    </div>
                    <div className="text-sm text-gray-600">
                      User Friendliness ({result.document.user_friendliness_score}/5)
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-blue-600">
                      {result.processing_time.toFixed(1)}s
                    </div>
                    <div className="text-sm text-gray-800 font-medium">Processing Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-600">
                      {result.document.estimated_reading_time}min
                    </div>
                    <div className="text-sm text-gray-800 font-medium">Reading Time</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Risk Assessment</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-800 font-medium">Overall Sensitivity:</span>
                        <span className="text-gray-900 font-semibold">{result.document.overall_sensitivity_score}/10</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-800 font-medium">Privacy Impact:</span>
                        <span className="text-gray-900 font-semibold">{result.document.overall_privacy_impact}/10</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-800 font-medium">Compliance Score:</span>
                        <span className="text-gray-900 font-semibold">{result.document.compliance_score}/10</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Content Overview</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-800 font-medium">Total Sections:</span>
                        <span className="text-gray-900 font-semibold">{result.ui_components.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-800 font-medium">High-Risk Sections:</span>
                        <span className="text-gray-900 font-semibold">{result.document.high_risk_sections}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-800 font-medium">Interactive Sections:</span>
                        <span className="text-gray-900 font-semibold">{result.document.interactive_sections}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Tab Navigation */}
              <div className="flex gap-2 mb-6">
                <button
                  onClick={() => setActiveTab('policy')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === 'policy'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  📱 Policy Sections
                </button>
                <button
                  onClick={() => setActiveTab('permissions')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    activeTab === 'permissions'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  🔐 Permission Consent
                </button>
              </div>

              <AnimatePresence mode="wait">
                {activeTab === 'policy' && (
                  <motion.div
                    key="policy"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="flex justify-between items-center mb-4">
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">
                          Privacy Policy Sections
                        </h2>
                        <p className="text-gray-700 font-medium">
                          Interactive sections ordered by importance. Click to expand details.
                        </p>
                      </div>
                      <button
                        onClick={() => setAllExpanded(!allExpanded)}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium text-sm"
                      >
                        {allExpanded ? '📤 Collapse All' : '📥 Expand All'}
                      </button>
                    </div>
                    
                    <div className="space-y-4">
                      {sortedComponents.map((component) => (
                        <DynamicPolicyComponent 
                          key={component.id} 
                          component={component} 
                          forceExpanded={allExpanded}
                        />
                      ))}
                    </div>
                  </motion.div>
                )}

                {activeTab === 'permissions' && (
                  <motion.div
                    key="permissions"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <PermissionConsentManager
                      components={sortedComponents}
                      onConsentChange={handlePermissionConsentChange}
                    />
                    
                    {/* Consent Summary */}
                    {consentedPermissions.length > 0 && (
                      <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <h3 className="font-semibold text-green-800 mb-2">
                          ✅ Consent Summary
                        </h3>
                        <p className="text-sm text-green-700 mb-2">
                          You have consented to {consentedPermissions.length} permission{consentedPermissions.length !== 1 ? 's' : ''}:
                        </p>
                        <ul className="text-sm text-green-700 space-y-1">
                          {consentedPermissions.map((permission, index) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-green-500 mt-1">✓</span>
                              <span>{permission.title} - {permission.description}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}; 