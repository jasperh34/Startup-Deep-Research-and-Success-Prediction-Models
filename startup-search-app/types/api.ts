export type CompanyCandidate = {
  id: string;
  companyId?: string;
  name: string;
  website?: string;
  description: string;
  location?: string;
  industry?: string;
  companyType?: string;
  foundingYear?: string;
  fundingStage?: string;
  matchReasons?: string[];
  sourceTypes?: string[];
  confidence: number;
  source: string;
  sourceUrl?: string;
};

export type CompanySearchResponse = {
  query: string;
  candidates: CompanyCandidate[];
  needsConfirmation: boolean;
};

export type StartupReport = {
  id: string;
  companyId?: string;
  companyName: string;
  website?: string;
  summary: string;
  status: "draft" | "ready";
  createdAt: string;
  sourceCount?: number;
  structuredJson?: Record<string, unknown>;
  sections: Array<{
    title: string;
    body: string;
  }>;
  signals: Array<{
    label: string;
    value: string;
    tone: "positive" | "neutral" | "negative";
  }>;
};
