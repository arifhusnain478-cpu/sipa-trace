export const RiskClass = {
  NONE: 0,
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
  CRITICAL: 4,
} as const;

export type RiskClass = (typeof RiskClass)[keyof typeof RiskClass];

export interface TraceCard {
  seq: number;
  ts: number;
  stage: string;
  action_type: string;
  inputs_digest: string;
  outputs_digest: string;
  risk_class: RiskClass;
  reversible: boolean;
  state_delta: Record<string, number | string | boolean>;
  prev_hash: string;
  hash: string;
}

export interface DiffResult {
  changed_fields: string[];
  risk_escalated: boolean;
  risk_deescalated: boolean;
  became_irreversible: boolean;
  state_delta_added: Record<string, any>;
  state_delta_removed: Record<string, any>;
  state_delta_changed: Record<string, [any, any]>;
}

export interface VerifyStatus {
  valid: boolean;
  card_count: number;
  error?: string;
}