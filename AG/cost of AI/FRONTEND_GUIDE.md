# AI Cost Management - Frontend Implementation Guide

## Overview

This guide provides a complete frontend implementation for the AI Cost Management dashboard in CloudTuner.ai. The dashboard consolidates AI resource costs from AWS, Azure, and GCP, with intelligent recommendations for cost optimization.

## UI/UX Design

### Dashboard Layout

The AI Cost dashboard follows a clean, data-centric design with these key sections:

```
┌─────────────────────────────────────────────────────────────────┐
│  AI Cost Management                          [Filters] [Export]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Total Cost   │ │ AWS Cost     │ │ Savings      │            │
│  │ $12,450/mo   │ │ $6,200       │ │ $2,100       │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Cost Trends (Line Chart)                                 │   │
│  │                                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────┐ ┌─────────────────────────────┐  │
│  │ Cost by Provider (Pie)   │ │ Cost by Service (Bar)       │  │
│  │                          │ │                             │  │
│  └──────────────────────────┘ └─────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Resources Table with Inline Metrics                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 🎯 Cost Optimization Recommendations                     │   │
│  │  • Downsize SageMaker Endpoint (Save $1,200/mo)         │   │
│  │  • Switch to Savings Plan (Save $800/mo)                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Framework**: React 18+ with TypeScript
- **State Management**: React Context API + Custom Hooks
- **Charts**: Recharts or Chart.js
- **UI Components**: Custom components with Tailwind CSS (optional)
- **Data Fetching**: Axios or Fetch API
- **Date Handling**: date-fns

## Mock Data Module

```typescript
// src/mockData/aiCostData.ts

export interface AIResource {
  id: string;
  resourceId: string;
  resourceName: string;
  cloudProvider: 'AWS' | 'Azure' | 'GCP';
  serviceType: string;
  resourceType: string;
  region: string;
  accountId: string;
  monthlyCost: number;
  dailyCost: number;
  tags: Record<string, string>;
}

export interface CostDataPoint {
  date: string;
  cost: number;
  provider: string;
  category: string;
}

export interface Recommendation {
  id: string;
  resourceId: string;
  resourceName: string;
  cloudProvider: string;
  type: 'rightsizing' | 'pricing-model' | 'scheduling' | 'autoscaling' | 'decommission';
  title: string;
  description: string;
  currentMonthlyCost: number;
  estimatedMonthlySavings: number;
  savingsPercent: number;
  confidence: number;
  priority: 'critical' | 'high' | 'medium' | 'low';
  implementationEffort: 'low' | 'medium' | 'high';
  recommendedAction: any;
  supportingData: any;
  createdAt: string;
}

export const mockAIResources: AIResource[] = [
  {
    id: '1',
    resourceId: 'arn:aws:sagemaker:us-east-1:123456789:endpoint/ml-inference-prod',
    resourceName: 'ml-inference-prod',
    cloudProvider: 'AWS',
    serviceType: 'AmazonSageMaker',
    resourceType: 'endpoint',
    region: 'us-east-1',
    accountId: '123456789',
    monthlyCost: 3200,
    dailyCost: 106.67,
    tags: { environment: 'production', team: 'ml-ops' }
  },
  {
    id: '2',
    resourceId: 'arn:aws:bedrock:us-west-2:123456789:foundation-model/claude',
    resourceName: 'claude-api-integration',
    cloudProvider: 'AWS',
    serviceType: 'AmazonBedrock',
    resourceType: 'api',
    region: 'us-west-2',
    accountId: '123456789',
    monthlyCost: 1850,
    dailyCost: 61.67,
    tags: { environment: 'production', team: 'app-dev' }
  },
  {
    id: '3',
    resourceId: 'projects/my-project/locations/us-central1/endpoints/12345',
    resourceName: 'image-classification-endpoint',
    cloudProvider: 'GCP',
    serviceType: 'Vertex AI',
    resourceType: 'endpoint',
    region: 'us-central1',
    accountId: 'my-project',
    monthlyCost: 2400,
    dailyCost: 80,
    tags: { environment: 'production', team: 'cv-team' }
  },
  {
    id: '4',
    resourceId: '/subscriptions/abc123/resourceGroups/ml-rg/providers/Microsoft.MachineLearningServices/workspaces/ml-workspace',
    resourceName: 'ml-workspace',
    cloudProvider: 'Azure',
    serviceType: 'Microsoft.MachineLearningServices',
    resourceType: 'workspace',
    region: 'eastus',
    accountId: 'abc123',
    monthlyCost: 1600,
    dailyCost: 53.33,
    tags: { environment: 'production', team: 'data-science' }
  },
  {
    id: '5',
    resourceId: 'arn:aws:sagemaker:eu-west-1:123456789:training-job/model-training-v2',
    resourceName: 'model-training-v2',
    cloudProvider: 'AWS',
    serviceType: 'AmazonSageMaker',
    resourceType: 'training-job',
    region: 'eu-west-1',
    accountId: '123456789',
    monthlyCost: 850,
    dailyCost: 28.33,
    tags: { environment: 'development', team: 'ml-research' }
  }
];

export const mockCostTrends: CostDataPoint[] = [
  { date: '2024-11-01', cost: 320, provider: 'AWS', category: 'compute' },
  { date: '2024-11-01', cost: 180, provider: 'Azure', category: 'compute' },
  { date: '2024-11-01', cost: 150, provider: 'GCP', category: 'compute' },
  { date: '2024-11-02', cost: 335, provider: 'AWS', category: 'compute' },
  { date: '2024-11-02', cost: 175, provider: 'Azure', category: 'compute' },
  { date: '2024-11-02', cost: 160, provider: 'GCP', category: 'compute' },
  { date: '2024-11-03', cost: 310, provider: 'AWS', category: 'compute' },
  { date: '2024-11-03', cost: 190, provider: 'Azure', category: 'compute' },
  { date: '2024-11-03', cost: 155, provider: 'GCP', category: 'compute' },
  // ... more data points for 30 days
];

export const mockRecommendations: Recommendation[] = [
  {
    id: 'rec-1',
    resourceId: '1',
    resourceName: 'ml-inference-prod',
    cloudProvider: 'AWS',
    type: 'rightsizing',
    title: 'Downsize Inference Endpoint',
    description: 'GPU utilization is only 28.3%. Consider using a smaller instance type (ml.g4dn.xlarge → ml.g4dn.large) to reduce costs.',
    currentMonthlyCost: 3200,
    estimatedMonthlySavings: 1280,
    savingsPercent: 40,
    confidence: 0.85,
    priority: 'high',
    implementationEffort: 'medium',
    recommendedAction: {
      action: 'downsize_instance',
      currentInstance: 'ml.g4dn.xlarge',
      recommendedInstance: 'ml.g4dn.large',
      steps: [
        'Create new endpoint with ml.g4dn.large',
        'Test with production traffic',
        'Shift traffic using canary deployment',
        'Monitor for 48 hours',
        'Decommission old endpoint'
      ]
    },
    supportingData: {
      avgGpuUtilization: 28.3,
      avgCpuUtilization: 45.2,
      avgMemoryUtilization: 52.1,
      analysisPeriodDays: 30
    },
    createdAt: '2024-11-28T06:00:00Z'
  },
  {
    id: 'rec-2',
    resourceId: '2',
    resourceName: 'claude-api-integration',
    cloudProvider: 'AWS',
    type: 'pricing-model',
    title: 'Switch to Bedrock Provisioned Throughput',
    description: 'Consistent usage detected. Provisioned Throughput could reduce costs by ~30% compared to on-demand pricing.',
    currentMonthlyCost: 1850,
    estimatedMonthlySavings: 555,
    savingsPercent: 30,
    confidence: 0.90,
    priority: 'high',
    implementationEffort: 'low',
    recommendedAction: {
      action: 'switch_to_provisioned',
      currentModel: 'on-demand',
      recommendedModel: 'provisioned-throughput',
      commitmentTerm: '1_month',
      steps: [
        'Calculate required model units based on usage',
        'Purchase Provisioned Throughput',
        'Update application to use provisioned endpoint',
        'Monitor cost savings in billing dashboard'
      ]
    },
    supportingData: {
      avgDailyCost: 61.67,
      costVariance: 12.5,
      consistencyScore: 0.85,
      analysisPeriodDays: 30
    },
    createdAt: '2024-11-28T06:00:00Z'
  },
  {
    id: 'rec-3',
    resourceId: '3',
    resourceName: 'image-classification-endpoint',
    cloudProvider: 'GCP',
    type: 'scheduling',
    title: 'Implement Auto-Scheduling',
    description: 'Resource shows low usage during 10 hours per day (10 PM - 8 AM UTC). Auto-scheduling can save ~42% of costs.',
    currentMonthlyCost: 2400,
    estimatedMonthlySavings: 1000,
    savingsPercent: 42,
    confidence: 0.75,
    priority: 'medium',
    implementationEffort: 'medium',
    recommendedAction: {
      action: 'implement_scheduling',
      schedule: {
        shutdownHours: [22, 23, 0, 1, 2, 3, 4, 5, 6, 7],
        timezone: 'UTC'
      },
      steps: [
        'Create Cloud Scheduler jobs for shutdown (10 PM UTC)',
        'Create Cloud Scheduler jobs for startup (8 AM UTC)',
        'Implement graceful shutdown handling',
        'Test in development environment',
        'Enable monitoring for scheduled events'
      ]
    },
    supportingData: {
      offPeakHours: [22, 23, 0, 1, 2, 3, 4, 5, 6, 7],
      avgThroughputByHour: {
        '0': 0.02, '1': 0.01, '2': 0.01, '3': 0.03,
        '8': 2.5, '9': 3.2, '10': 3.8, '14': 4.1
      }
    },
    createdAt: '2024-11-27T06:00:00Z'
  },
  {
    id: 'rec-4',
    resourceId: '5',
    resourceName: 'model-training-v2',
    cloudProvider: 'AWS',
    type: 'pricing-model',
    title: 'Use Spot Instances for Training',
    description: 'Training jobs can tolerate interruptions. Using Spot Instances can reduce training costs by up to 70%.',
    currentMonthlyCost: 850,
    estimatedMonthlySavings: 595,
    savingsPercent: 70,
    confidence: 0.80,
    priority: 'medium',
    implementationEffort: 'low',
    recommendedAction: {
      action: 'use_spot_instances',
      steps: [
        'Enable checkpointing in training code',
        'Configure managed spot training in SageMaker',
        'Set appropriate max wait time',
        'Test interruption recovery',
        'Monitor training completion times'
      ]
    },
    supportingData: {
      avgTrainingDuration: '4.5 hours',
      interruptionTolerance: 'high',
      checkpointingEnabled: false
    },
    createdAt: '2024-11-26T06:00:00Z'
  }
];

export const mockCostSummary = {
  totalCost: 12450,
  currency: 'USD',
  periodStart: '2024-11-01',
  periodEnd: '2024-11-28',
  breakdownByProvider: {
    AWS: 6200,
    Azure: 3100,
    GCP: 3150
  },
  breakdownByService: {
    'AmazonSageMaker': 4050,
    'AmazonBedrock': 1850,
    'Vertex AI': 2400,
    'Microsoft.MachineLearningServices': 1600,
    'AmazonRekognition': 1250,
    'Azure Cognitive Services': 1300
  },
  breakdownByCategory: {
    compute: 7800,
    inference: 3200,
    training: 1050,
    storage: 400
  }
};
```

## API Service Layer

```typescript
// src/services/aiCostService.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

// Toggle between mock and real API
const USE_MOCK_DATA = process.env.REACT_APP_USE_MOCK === 'true';

class AICostService {
  private client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async getCostSummary(filters: {
    startDate: string;
    endDate: string;
    cloudProvider?: string[];
    serviceType?: string[];
    accountId?: string[];
  }) {
    if (USE_MOCK_DATA) {
      const { mockCostSummary } = await import('../mockData/aiCostData');
      return mockCostSummary;
    }

    const params = new URLSearchParams();
    params.append('start_date', filters.startDate);
    params.append('end_date', filters.endDate);
    
    if (filters.cloudProvider) {
      filters.cloudProvider.forEach(p => params.append('cloud_provider', p));
    }
    if (filters.serviceType) {
      filters.serviceType.forEach(s => params.append('service_type', s));
    }
    if (filters.accountId) {
      filters.accountId.forEach(a => params.append('account_id', a));
    }

    const response = await this.client.get(`/ai-costs/summary?${params}`);
    return response.data;
  }

  async getCostTrends(filters: {
    startDate: string;
    endDate: string;
    granularity: 'daily' | 'weekly' | 'monthly';
    cloudProvider?: string[];
  }) {
    if (USE_MOCK_DATA) {
      const { mockCostTrends } = await import('../mockData/aiCostData');
      return mockCostTrends;
    }

    const params = new URLSearchParams();
    params.append('start_date', filters.startDate);
    params.append('end_date', filters.endDate);
    params.append('granularity', filters.granularity);
    
    if (filters.cloudProvider) {
      filters.cloudProvider.forEach(p => params.append('cloud_provider', p));
    }

    const response = await this.client.get(`/ai-costs/trends?${params}`);
    return response.data;
  }

  async getResources() {
    if (USE_MOCK_DATA) {
      const { mockAIResources } = await import('../mockData/aiCostData');
      return mockAIResources;
    }

    const response = await this.client.get('/ai-costs/resources');
    return response.data;
  }

  async getRecommendations(filters?: {
    cloudProvider?: string[];
    recommendationType?: string[];
    priority?: string[];
    minSavings?: number;
  }) {
    if (USE_MOCK_DATA) {
      const { mockRecommendations } = await import('../mockData/aiCostData');
      return mockRecommendations;
    }

    const params = new URLSearchParams();
    if (filters?.cloudProvider) {
      filters.cloudProvider.forEach(p => params.append('cloud_provider', p));
    }
    if (filters?.recommendationType) {
      filters.recommendationType.forEach(t => params.append('recommendation_type', t));
    }
    if (filters?.priority) {
      filters.priority.forEach(p => params.append('priority', p));
    }
    if (filters?.minSavings) {
      params.append('min_savings', filters.minSavings.toString());
    }

    const response = await this.client.get(`/recommendations?${params}`);
    return response.data;
  }

  async acceptRecommendation(recommendationId: string) {
    if (USE_MOCK_DATA) {
      console.log('Mock: Accepting recommendation', recommendationId);
      return { status: 'success' };
    }

    const response = await this.client.post(`/recommendations/${recommendationId}/accept`);
    return response.data;
  }

  async rejectRecommendation(recommendationId: string, reason?: string) {
    if (USE_MOCK_DATA) {
      console.log('Mock: Rejecting recommendation', recommendationId, reason);
      return { status: 'success' };
    }

    const response = await this.client.post(`/recommendations/${recommendationId}/reject`, { reason });
    return response.data;
  }
}

export const aiCostService = new AICostService();
```

## Custom Hooks

```typescript
// src/hooks/useAICosts.ts
import { useState, useEffect } from 'react';
import { aiCostService } from '../services/aiCostService';

export const useAICosts = (filters: {
  startDate: string;
  endDate: string;
  cloudProvider?: string[];
  serviceType?: string[];
}) => {
  const [summary, setSummary] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [resources, setResources] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [summaryData, trendsData, resourcesData] = await Promise.all([
          aiCostService.getCostSummary(filters),
          aiCostService.getCostTrends({
            ...filters,
            granularity: 'daily'
          }),
          aiCostService.getResources()
        ]);

        if (isMounted) {
          setSummary(summaryData);
          setTrends(trendsData);
          setResources(resourcesData);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to fetch cost data');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [filters.startDate, filters.endDate, JSON.stringify(filters.cloudProvider), JSON.stringify(filters.serviceType)]);

  return { summary, trends, resources, loading, error };
};

// src/hooks/useRecommendations.ts
import { useState, useEffect } from 'react';
import { aiCostService } from '../services/aiCostService';

export const useRecommendations = (filters?: any) => {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await aiCostService.getRecommendations(filters);

        if (isMounted) {
          setRecommendations(data);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message || 'Failed to fetch recommendations');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchRecommendations();

    return () => {
      isMounted = false;
    };
  }, [JSON.stringify(filters)]);

  const acceptRecommendation = async (id: string) => {
    try {
      await aiCostService.acceptRecommendation(id);
      setRecommendations(prev => prev.filter(r => r.id !== id));
    } catch (err: any) {
      setError(err.message || 'Failed to accept recommendation');
    }
  };

  const rejectRecommendation = async (id: string, reason?: string) => {
    try {
      await aiCostService.rejectRecommendation(id, reason);
      setRecommendations(prev => prev.filter(r => r.id !== id));
    } catch (err: any) {
      setError(err.message || 'Failed to reject recommendation');
    }
  };

  return {
    recommendations,
    loading,
    error,
    acceptRecommendation,
    rejectRecommendation
  };
};
```

## React Components

### Main Dashboard Component

```typescript
// src/components/AICostDashboard.tsx
import React, { useState } from 'react';
import { format, subDays } from 'date-fns';
import { useAICosts } from '../hooks/useAICosts';
import { useRecommendations } from '../hooks/useRecommendations';
import CostSummaryCards from './CostSummaryCards';
import CostTrendChart from './CostTrendChart';
import CostBreakdownCharts from './CostBreakdownCharts';
import ResourcesTable from './ResourcesTable';
import RecommendationsList from './RecommendationsList';
import FilterPanel from './FilterPanel';

const AICostDashboard: React.FC = () => {
  const [filters, setFilters] = useState({
    startDate: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd'),
    cloudProvider: undefined as string[] | undefined,
    serviceType: undefined as string[] | undefined
  });

  const { summary, trends, resources, loading, error } = useAICosts(filters);
  const { recommendations, acceptRecommendation, rejectRecommendation } = useRecommendations();

  if (loading) {
    return <div className="loading">Loading AI cost data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  const totalSavings = recommendations.reduce((sum, rec) => sum + rec.estimatedMonthlySavings, 0);

  return (
    <div className="ai-cost-dashboard">
      <div className="dashboard-header">
        <h1>AI Cost Management</h1>
        <FilterPanel filters={filters} onChange={setFilters} />
      </div>

      <CostSummaryCards 
        summary={summary} 
        potentialSavings={totalSavings}
      />

      <CostTrendChart trends={trends} />

      <CostBreakdownCharts summary={summary} />

      <ResourcesTable resources={resources} />

      <RecommendationsList
        recommendations={recommendations}
        onAccept={acceptRecommendation}
        onReject={rejectRecommendation}
      />
    </div>
  );
};

export default AICostDashboard;
```

### Cost Summary Cards

```typescript
// src/components/CostSummaryCards.tsx
import React from 'react';

interface Props {
  summary: any;
  potentialSavings: number;
}

const CostSummaryCards: React.FC<Props> = ({ summary, potentialSavings }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="cost-summary-cards">
      <div className="summary-card total-cost">
        <div className="card-icon">💰</div>
        <div className="card-content">
          <h3>Total AI Cost</h3>
          <p className="amount">{formatCurrency(summary?.totalCost || 0)}</p>
          <span className="period">This Month</span>
        </div>
      </div>

      <div className="summary-card provider-breakdown">
        <div className="card-icon">☁️</div>
        <div className="card-content">
          <h3>Multi-Cloud Breakdown</h3>
          <div className="provider-costs">
            <div className="provider-item">
              <span className="provider-name">AWS</span>
              <span className="provider-cost">{formatCurrency(summary?.breakdownByProvider?.AWS || 0)}</span>
            </div>
            <div className="provider-item">
              <span className="provider-name">Azure</span>
              <span className="provider-cost">{formatCurrency(summary?.breakdownByProvider?.Azure || 0)}</span>
            </div>
            <div className="provider-item">
              <span className="provider-name">GCP</span>
              <span className="provider-cost">{formatCurrency(summary?.breakdownByProvider?.GCP || 0)}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="summary-card savings">
        <div className="card-icon">🎯</div>
        <div className="card-content">
          <h3>Potential Savings</h3>
          <p className="amount savings-amount">{formatCurrency(potentialSavings)}</p>
          <span className="period">Based on Recommendations</span>
        </div>
      </div>
    </div>
  );
};

export default CostSummaryCards;
```

### Cost Trend Chart

```typescript
// src/components/CostTrendChart.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';

interface Props {
  trends: any[];
}

const CostTrendChart: React.FC<Props> = ({ trends }) => {
  // Aggregate by date and provider
  const aggregatedData = trends.reduce((acc, item) => {
    const date = item.date;
    if (!acc[date]) {
      acc[date] = { date, AWS: 0, Azure: 0, GCP: 0, total: 0 };
    }
    acc[date][item.provider] = (acc[date][item.provider] || 0) + item.cost;
    acc[date].total += item.cost;
    return acc;
  }, {} as Record<string, any>);

  const chartData = Object.values(aggregatedData).map((item: any) => ({
    ...item,
    date: format(parseISO(item.date), 'MMM dd')
  }));

  return (
    <div className="cost-trend-chart">
      <h2>Cost Trends</h2>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
          <Legend />
          <Line type="monotone" dataKey="AWS" stroke="#FF9900" strokeWidth={2} />
          <Line type="monotone" dataKey="Azure" stroke="#0078D4" strokeWidth={2} />
          <Line type="monotone" dataKey="GCP" stroke="#4285F4" strokeWidth={2} />
          <Line type="monotone" dataKey="total" stroke="#000000" strokeWidth={3} strokeDasharray="5 5" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CostTrendChart;
```

### Recommendations List

```typescript
// src/components/RecommendationsList.tsx
import React, { useState } from 'react';
import { Recommendation } from '../mockData/aiCostData';

interface Props {
  recommendations: Recommendation[];
  onAccept: (id: string) => void;
  onReject: (id: string, reason?: string) => void;
}

const RecommendationsList: React.FC<Props> = ({ recommendations, onAccept, onReject }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#d32f2f';
      case 'high': return '#f57c00';
      case 'medium': return '#fbc02d';
      case 'low': return '#7cb342';
      default: return '#757575';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'rightsizing': return '📏';
      case 'pricing-model': return '💳';
      case 'scheduling': return '⏰';
      case 'autoscaling': return '📊';
      case 'decommission': return '🗑️';
      default: return '💡';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="recommendations-section">
      <h2>🎯 Cost Optimization Recommendations</h2>
      <p className="section-subtitle">
        {recommendations.length} recommendations • Potential savings: {formatCurrency(
          recommendations.reduce((sum, r) => sum + r.estimatedMonthlySavings, 0)
        )}/month
      </p>

      <div className="recommendations-list">
        {recommendations.map(rec => (
          <div key={rec.id} className="recommendation-card">
            <div className="rec-header" onClick={() => setExpandedId(expandedId === rec.id ? null : rec.id)}>
              <div className="rec-icon">{getTypeIcon(rec.type)}</div>
              <div className="rec-main">
                <div className="rec-title-row">
                  <h3>{rec.title}</h3>
                  <span className="rec-provider">{rec.cloudProvider}</span>
                </div>
                <p className="rec-resource">{rec.resourceName}</p>
                <p className="rec-description">{rec.description}</p>
              </div>
              <div className="rec-savings">
                <div className="savings-amount">{formatCurrency(rec.estimatedMonthlySavings)}</div>
                <div className="savings-label">monthly savings</div>
                <div className="savings-percent">{rec.savingsPercent}%</div>
              </div>
              <div className="rec-metadata">
                <span 
                  className="priority-badge" 
                  style={{ backgroundColor: getPriorityColor(rec.priority) }}
                >
                  {rec.priority}
                </span>
                <span className="effort-badge">{rec.implementationEffort} effort</span>
                <span className="confidence-badge">
                  {(rec.confidence * 100).toFixed(0)}% confidence
                </span>
              </div>
            </div>

            {expandedId === rec.id && (
              <div className="rec-details">
                <div className="rec-actions-section">
                  <h4>Recommended Actions:</h4>
                  <ol>
                    {rec.recommendedAction.steps?.map((step: string, idx: number) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ol>
                </div>

                <div className="rec-data-section">
                  <h4>Supporting Data:</h4>
                  <pre>{JSON.stringify(rec.supportingData, null, 2)}</pre>
                </div>

                <div className="rec-buttons">
                  <button 
                    className="btn btn-accept" 
                    onClick={() => onAccept(rec.id)}
                  >
                    ✓ Accept & Implement
                  </button>
                  <button 
                    className="btn btn-reject" 
                    onClick={() => onReject(rec.id)}
                  >
                    ✗ Dismiss
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecommendationsList;
```

## Styling

```css
/* src/styles/AICostDashboard.css */

.ai-cost-dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.dashboard-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
}

/* Cost Summary Cards */
.cost-summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 16px;
  transition: transform 0.2s;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 48px;
}

.card-content h3 {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
  font-weight: 500;
}

.card-content .amount {
  font-size: 36px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.savings-amount {
  color: #22c55e;
}

.card-content .period {
  font-size: 12px;
  color: #999;
}

.provider-costs {
  margin-top: 12px;
}

.provider-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.provider-name {
  font-weight: 500;
  color: #666;
}

.provider-cost {
  font-weight: 600;
  color: #1a1a1a;
}

/* Charts */
.cost-trend-chart,
.cost-breakdown-charts {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
}

.cost-trend-chart h2,
.recommendations-section h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #1a1a1a;
}

/* Recommendations */
.recommendations-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-subtitle {
  color: #666;
  margin-bottom: 24px;
  font-size: 14px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-card {
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.recommendation-card:hover {
  border-color: #3b82f6;
}

.rec-header {
  display: flex;
  gap: 16px;
  padding: 20px;
  cursor: pointer;
  align-items: flex-start;
}

.rec-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.rec-main {
  flex: 1;
}

.rec-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.rec-title-row h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.rec-provider {
  background: #f3f4f6;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.rec-resource {
  font-size: 14px;
  color: #666;
  margin: 4px 0;
}

.rec-description {
  font-size: 14px;
  color: #1a1a1a;
  margin-top: 8px;
}

.rec-savings {
  text-align: right;
  flex-shrink: 0;
}

.savings-amount {
  font-size: 28px;
  font-weight: 700;
  color: #22c55e;
}

.savings-label {
  font-size: 11px;
  color: #666;
}

.savings-percent {
  font-size: 14px;
  font-weight: 600;
  color: #22c55e;
  margin-top: 4px;
}

.rec-metadata {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.priority-badge,
.effort-badge,
.confidence-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  color: white;
}

.priority-badge {
  /* Color set inline based on priority */
}

.effort-badge {
  background: #6b7280;
  color: white;
}

.confidence-badge {
  background: #3b82f6;
  color: white;
}

.rec-details {
  padding: 20px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.rec-actions-section h4,
.rec-data-section h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #374151;
}

.rec-actions-section ol {
  padding-left: 20px;
}

.rec-actions-section li {
  margin-bottom: 8px;
  color: #1f2937;
}

.rec-data-section pre {
  background: #1f2937;
  color: #e5e7eb;
  padding: 16px;
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
}

.rec-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-accept {
  background: #22c55e;
  color: white;
}

.btn-accept:hover {
  background: #16a34a;
}

.btn-reject {
  background: #ef4444;
  color: white;
}

.btn-reject:hover {
  background: #dc2626;
}
```

## Integration Instructions

1. **Install Dependencies**:
```bash
npm install axios recharts date-fns
```

2. **Environment Variables** (`.env`):
```env
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_USE_MOCK=true
```

3. **Import Dashboard**:
```typescript
import AICostDashboard from './components/AICostDashboard';

function App() {
  return <AICostDashboard />;
}
```

4. **Switch to Real API**: Set `REACT_APP_USE_MOCK=false` once backend is ready
