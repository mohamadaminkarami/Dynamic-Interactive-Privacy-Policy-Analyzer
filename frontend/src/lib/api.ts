import { PrivacyPolicy, PolicyAnalyzeRequest } from '@/types/policy';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class PolicyApiClient {
  private static instance: PolicyApiClient;
  private baseUrl: string;

  private constructor() {
    this.baseUrl = API_BASE_URL;
  }

  public static getInstance(): PolicyApiClient {
    if (!PolicyApiClient.instance) {
      PolicyApiClient.instance = new PolicyApiClient();
    }
    return PolicyApiClient.instance;
  }

  /**
   * Analyze a privacy policy
   */
  async analyzePolicy(request: PolicyAnalyzeRequest): Promise<PrivacyPolicy> {
    const response = await fetch(`${this.baseUrl}/api/v1/policy/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to analyze policy');
    }

    return response.json();
  }

  /**
   * Get API health status
   */
  async getHealth(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error('API health check failed');
    }

    return response.json();
  }

  /**
   * Get available models
   */
  async getModels(): Promise<{ models: string[] }> {
    const response = await fetch(`${this.baseUrl}/models`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch models');
    }

    return response.json();
  }
}

export const apiClient = PolicyApiClient.getInstance(); 