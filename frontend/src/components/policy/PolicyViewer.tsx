'use client';

import React, { useState } from 'react';
import { PrivacyPolicy, PolicyRequest } from '@/types/policy';
import { apiClient } from '@/lib/api';
import { DynamicPolicyComponent } from '@/components/policy/DynamicPolicyComponent';
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/Card';

export const PolicyViewer: React.FC = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<PrivacyPolicy | null>(null);
  const [error, setError] = useState<string | null>(null);
  
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

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dynamic Privacy Policy Analyzer
        </h1>
        <p className="text-gray-600">
          Transform privacy policies into user-centric, interactive presentations
        </p>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Analyze Privacy Policy</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="company_name" className="block text-sm font-medium text-gray-700 mb-1">
                Company Name *
              </label>
              <input
                type="text"
                id="company_name"
                name="company_name"
                value={formData.company_name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Tech Company Inc."
              />
            </div>

            <div>
              <label htmlFor="company_url" className="block text-sm font-medium text-gray-700 mb-1">
                Company URL
              </label>
              <input
                type="url"
                id="company_url"
                name="company_url"
                value={formData.company_url}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://example.com"
              />
            </div>

            <div>
              <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700 mb-1">
                Contact Email
              </label>
              <input
                type="email"
                id="contact_email"
                name="contact_email"
                value={formData.contact_email}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="privacy@example.com"
              />
            </div>

            <div>
              <label htmlFor="policy_content" className="block text-sm font-medium text-gray-700 mb-1">
                Privacy Policy Content *
              </label>
              <textarea
                id="policy_content"
                name="policy_content"
                value={formData.policy_content}
                onChange={handleInputChange}
                required
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Paste the privacy policy content here..."
              />
            </div>

            <button
              type="submit"
              disabled={isAnalyzing}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Policy'}
            </button>
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
                <h3 className="text-lg font-semibold mb-4">📊 Policy Analysis Summary</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center">
                    <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(result.document.overall_risk_level)}`}>
                      {result.document.overall_risk_level.toUpperCase()} RISK
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
                    <div className="text-sm text-gray-600">Processing Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-green-600">
                      {result.document.estimated_reading_time}min
                    </div>
                    <div className="text-sm text-gray-600">Reading Time</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {result.document.overall_sensitivity_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">Sensitivity Score</div>
                    <div className="text-xs text-gray-500">0-10 scale</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      {result.document.overall_privacy_impact.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">Privacy Impact</div>
                    <div className="text-xs text-gray-500">0-10 scale</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {result.document.compliance_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">Compliance</div>
                    <div className="text-xs text-gray-500">0-10 scale</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {result.document.readability_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">Readability</div>
                    <div className="text-xs text-gray-500">0-10 scale</div>
                  </div>
                </div>

                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm text-blue-800 mb-2">
                    Analysis of {result.document.company_name}'s privacy policy reveals {result.document.sections.length} key sections.
                    {result.document.high_risk_sections > 0 && (
                      <span className="text-red-600 font-medium"> {result.document.high_risk_sections} high-sensitivity sections require special attention.</span>
                    )}
                    {result.document.interactive_sections > 0 && (
                      <span className="text-purple-600 font-medium"> {result.document.interactive_sections} sections include interactive elements.</span>
                    )}
                  </div>
                  <div className="text-xs text-blue-600">
                    📋 Total: {result.document.total_word_count.toLocaleString()} words • 
                    📚 Sections: {result.document.sections.length} • 
                    ⚡ Interactive: {result.document.interactive_sections} • 
                    🚨 High-Risk: {result.document.high_risk_sections}
                  </div>
                </div>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  📱 Dynamic Policy Presentation
                </h2>
                <p className="text-gray-600 mb-6">
                  The following components are ranked by importance and presented in a user-centric format:
                </p>
                
                <div className="space-y-4">
                  {result.ui_components
                    .sort((a, b) => a.priority - b.priority)
                    .map((component) => (
                      <DynamicPolicyComponent key={component.id} component={component} />
                    ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}; 