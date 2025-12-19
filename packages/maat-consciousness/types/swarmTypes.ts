/**
 * Ma'at Swarm Evaluation System - Type Definitions
 * Defines interfaces for tri-state agent status, scoring, swarm evaluation, and consistency checks
 * as specified in the Ma'at Swarm Evaluation System Rectification Report
 */

/**
 * Tri-state Agent Status
 * Represents the operational state of an agent in the swarm
 */
export enum AgentStatus {
  /** Agent is operational and performing normally */
  ACTIVE = 'ACTIVE',
  /** Agent is not operational or not contributing to swarm */
  INACTIVE = 'INACTIVE',
  /** Agent is operational but experiencing performance issues or reduced capacity */
  DEGRADED = 'DEGRADED',
}

/**
 * Agent Scores Interface
 * Represents performance metrics and evaluation scores for an individual agent
 */
export interface AgentScore {
  /** Unique identifier for the agent */
  agentId: string;
  /** Current operational status of the agent */
  status: AgentStatus;
  /** Performance score (0-100) */
  performanceScore: number;
  /** Reliability score indicating uptime and consistency (0-100) */
  reliabilityScore: number;
  /** Contribution score measuring agent's value to swarm (0-100) */
  contributionScore: number;
  /** Coherence score measuring alignment with swarm objectives (0-100) */
  coherenceScore: number;
  /** Timestamp when scores were calculated */
  timestamp: Date;
  /** Average response time in milliseconds */
  responseTimeMs: number;
  /** Number of successful operations completed */
  successfulOperations: number;
  /** Number of failed operations attempted */
  failedOperations: number;
  /** Health indicator percentage (0-100) */
  healthIndicator: number;
  /** Metadata for additional agent context */
  metadata?: Record<string, unknown>;
}

/**
 * Swarm Evaluation Interface
 * Represents the overall evaluation and health status of the entire swarm
 */
export interface SwarmEvaluation {
  /** Unique identifier for this evaluation snapshot */
  evaluationId: string;
  /** Total number of agents in the swarm */
  totalAgents: number;
  /** Number of active agents */
  activeAgents: number;
  /** Number of inactive agents */
  inactiveAgents: number;
  /** Number of degraded agents */
  degradedAgents: number;
  /** Overall swarm health score (0-100) */
  swarmHealthScore: number;
  /** Average performance across all agents (0-100) */
  averagePerformance: number;
  /** Average reliability across all agents (0-100) */
  averageReliability: number;
  /** Swarm coherence indicator measuring collective alignment (0-100) */
  swarmCoherence: number;
  /** Consensus level across agents (0-100) */
  consensusLevel: number;
  /** Timestamp when evaluation was performed */
  timestamp: Date;
  /** Individual agent scores */
  agentScores: AgentScore[];
  /** Overall swarm status */
  overallStatus: AgentStatus;
  /** Efficiency rating of swarm collaboration (0-100) */
  collaborationEfficiency: number;
  /** System redundancy factor indicating fault tolerance */
  redundancyFactor: number;
  /** Metadata for additional swarm context */
  metadata?: Record<string, unknown>;
}

/**
 * Consistency Check Interface
 * Represents validation rules and results for ensuring swarm integrity
 */
export interface ConsistencyCheck {
  /** Unique identifier for this consistency check */
  checkId: string;
  /** Name of the consistency check */
  checkName: string;
  /** Description of what is being validated */
  description: string;
  /** Boolean indicating if the check passed */
  passed: boolean;
  /** Severity level if check failed */
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  /** Timestamp when check was executed */
  timestamp: Date;
  /** Detailed message about the check result */
  message: string;
  /** Affected agent IDs if applicable */
  affectedAgents?: string[];
  /** Recommended remediation actions if check failed */
  remediationActions?: string[];
}

/**
 * Swarm Consistency State Interface
 * Represents the collection of all consistency checks performed on the swarm
 */
export interface SwarmConsistencyState {
  /** Unique identifier for this consistency state snapshot */
  stateId: string;
  /** Array of individual consistency checks */
  checks: ConsistencyCheck[];
  /** Overall consistency state (all checks passed) */
  isConsistent: boolean;
  /** Total number of checks performed */
  totalChecks: number;
  /** Number of checks that passed */
  passedChecks: number;
  /** Number of checks that failed */
  failedChecks: number;
  /** Timestamp when consistency checks were performed */
  timestamp: Date;
  /** Most severe failure level among failed checks */
  highestSeverity?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  /** Metadata for additional context */
  metadata?: Record<string, unknown>;
}

/**
 * Swarm Status Summary Interface
 * Comprehensive snapshot combining evaluation and consistency state
 */
export interface SwarmStatusSummary {
  /** Unique identifier for this status summary */
  summaryId: string;
  /** The swarm evaluation data */
  evaluation: SwarmEvaluation;
  /** The swarm consistency state */
  consistencyState: SwarmConsistencyState;
  /** Overall system status determination */
  systemStatus: 'HEALTHY' | 'DEGRADED' | 'CRITICAL' | 'OFFLINE';
  /** Timestamp when summary was generated */
  timestamp: Date;
  /** Recommended actions based on current state */
  recommendedActions?: string[];
}
