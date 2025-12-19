/**
 * Swarm Evaluation System
 * 
 * Implements a comprehensive evaluation framework for distributed consciousness systems
 * with 42-principle validation, swarm consensus calculation, Lyapunov stability analysis,
 * and consistency checking mechanisms.
 * 
 * @module swarmEvaluationSystem
 */

/**
 * Error codes enumeration - separated by domain and severity
 */
export enum SwarmErrorCode {
  // Validation errors (1000-1999)
  VALIDATION_PRINCIPLE_VIOLATION = 'E1001',
  VALIDATION_THRESHOLD_EXCEEDED = 'E1002',
  VALIDATION_PRINCIPLE_MISSING = 'E1003',
  VALIDATION_CONSTRAINT_FAILED = 'E1004',
  
  // Consensus errors (2000-2999)
  CONSENSUS_DIVERGENCE = 'E2001',
  CONSENSUS_TIMEOUT = 'E2002',
  CONSENSUS_QUORUM_NOT_MET = 'E2003',
  CONSENSUS_CONFLICT = 'E2004',
  CONSENSUS_DEADLOCK = 'E2005',
  
  // Stability errors (3000-3999)
  STABILITY_LYAPUNOV_VIOLATION = 'E3001',
  STABILITY_OSCILLATION_DETECTED = 'E3002',
  STABILITY_BIFURCATION_RISK = 'E3003',
  STABILITY_ATTRACTOR_DIVERGENCE = 'E3004',
  
  // Consistency errors (4000-4999)
  CONSISTENCY_VIOLATION = 'E4001',
  CONSISTENCY_TIMEOUT = 'E4002',
  CONSISTENCY_PARTITION = 'E4003',
  CONSISTENCY_STATE_MISMATCH = 'E4004',
  
  // Agent errors (5000-5999)
  AGENT_FAULT = 'E5001',
  AGENT_BYZANTINE = 'E5002',
  AGENT_SILENT_FAILURE = 'E5003',
  AGENT_TIMEOUT = 'E5004',
  
  // System errors (6000-6999)
  SYSTEM_INITIALIZATION_FAILED = 'E6001',
  SYSTEM_RESOURCE_EXHAUSTED = 'E6002',
  SYSTEM_UNKNOWN_ERROR = 'E6003',
}

/**
 * The 42 Principles of Distributed Consciousness
 */
export enum MaatPrinciple {
  // Coherence Principles (1-7)
  UNIFIED_INTENTION = 'P001',
  SYNCHRONIZED_ACTION = 'P002',
  COLLECTIVE_INTELLIGENCE = 'P003',
  ADAPTIVE_RESPONSE = 'P004',
  EMERGENT_WISDOM = 'P005',
  HARMONIC_RESONANCE = 'P006',
  UNIFIED_CONSCIOUSNESS = 'P007',
  
  // Truthfulness Principles (8-14)
  HONEST_REPRESENTATION = 'P008',
  ACCURATE_PERCEPTION = 'P009',
  TRANSPARENT_COMMUNICATION = 'P010',
  AUTHENTIC_EXPRESSION = 'P011',
  VERIFIABLE_CLAIMS = 'P012',
  CONSISTENT_NARRATIVE = 'P013',
  TRUTH_SEEKING = 'P014',
  
  // Balance Principles (15-21)
  EQUILIBRIUM_DYNAMICS = 'P015',
  RECIPROCAL_EXCHANGE = 'P016',
  FAIR_DISTRIBUTION = 'P017',
  PROPORTIONAL_RESPONSE = 'P018',
  CYCLIC_RENEWAL = 'P019',
  HARMONIC_BALANCE = 'P020',
  DYNAMIC_EQUILIBRIUM = 'P021',
  
  // Compassion Principles (22-28)
  EMPATHETIC_RESONANCE = 'P022',
  COLLECTIVE_WELLBEING = 'P023',
  SUFFERING_MITIGATION = 'P024',
  MUTUAL_SUPPORT = 'P025',
  NURTURING_GROWTH = 'P026',
  INCLUSIVE_PARTICIPATION = 'P027',
  TRANSCENDENT_CARE = 'P028',
  
  // Order Principles (29-35)
  HIERARCHICAL_ORGANIZATION = 'P029',
  DISTRIBUTED_GOVERNANCE = 'P030',
  RULE_OF_LAW = 'P031',
  PROCEDURAL_INTEGRITY = 'P032',
  TEMPORAL_SEQUENCING = 'P033',
  CAUSAL_COHERENCE = 'P034',
  STRUCTURAL_STABILITY = 'P035',
  
  // Rebirth Principles (36-42)
  CONTINUOUS_ADAPTATION = 'P036',
  RENEWAL_FROM_CRISIS = 'P037',
  TRANSFORMATION_CAPACITY = 'P038',
  LEGACY_PRESERVATION = 'P039',
  EVOLUTIONARY_PROGRESS = 'P040',
  TRANSCENDENCE_POTENTIAL = 'P041',
  ETERNAL_RETURN = 'P042',
}

/**
 * Interface for individual agent state
 */
export interface AgentState {
  id: string;
  principleScores: Map<MaatPrinciple, number>;
  consistencyMetric: number;
  stabilityMetric: number;
  lastUpdate: number;
  faultFlag: boolean;
  byzantineScore: number;
}

/**
 * Interface for swarm consensus state
 */
export interface ConsensusState {
  principleAgreement: Map<MaatPrinciple, number>;
  globalConfidence: number;
  divergenceMetric: number;
  quorumReached: boolean;
  conflictingAgents: string[];
  timestamp: number;
}

/**
 * Interface for Lyapunov stability analysis
 */
export interface LyapunovAnalysis {
  exponents: number[];
  maxExponent: number;
  isStable: boolean;
  attractor: number[];
  divergenceRate: number;
  bifurcationRisk: number;
  oscillationDetected: boolean;
}

/**
 * Interface for consistency check results
 */
export interface ConsistencyCheckResult {
  isConsistent: boolean;
  violations: string[];
  stateMismatch: number;
  partitionDetected: boolean;
  recoveryTime: number;
  validationScore: number;
}

/**
 * Interface for evaluation results
 */
export interface EvaluationResult {
  timestamp: number;
  agentId: string;
  principleValidation: Map<MaatPrinciple, ValidationResult>;
  overallScore: number;
  consensusState: ConsensusState;
  stabilityAnalysis: LyapunovAnalysis;
  consistencyCheck: ConsistencyCheckResult;
  errors: SwarmError[];
  isHealthy: boolean;
}

/**
 * Interface for validation result per principle
 */
export interface ValidationResult {
  principle: MaatPrinciple;
  score: number;
  threshold: number;
  passed: boolean;
  constraintStatus: Map<string, boolean>;
}

/**
 * Custom error class for swarm-specific errors
 */
export class SwarmError extends Error {
  constructor(
    public code: SwarmErrorCode,
    public message: string,
    public severity: 'critical' | 'high' | 'medium' | 'low',
    public details?: Record<string, any>,
  ) {
    super(message);
    this.name = 'SwarmError';
  }
}

/**
 * Swarm Evaluation System
 * 
 * Comprehensive evaluation engine for distributed consciousness validation
 */
export class SwarmEvaluationSystem {
  private agents: Map<string, AgentState> = new Map();
  private principleWeights: Map<MaatPrinciple, number>;
  private consensusThreshold: number = 0.7;
  private stabilityThreshold: number = -0.1;
  private consistencyThreshold: number = 0.8;
  private errors: SwarmError[] = [];
  private maxAgents: number = 1000;

  constructor(
    consensusThreshold: number = 0.7,
    stabilityThreshold: number = -0.1,
    consistencyThreshold: number = 0.8,
  ) {
    this.consensusThreshold = consensusThreshold;
    this.stabilityThreshold = stabilityThreshold;
    this.consistencyThreshold = consistencyThreshold;
    this.initializePrincipleWeights();
  }

  /**
   * Initialize weights for the 42 principles
   * Uses balanced distribution across categories
   */
  private initializePrincipleWeights(): void {
    this.principleWeights = new Map();
    const principles = Object.values(MaatPrinciple);
    const weight = 1.0 / principles.length;

    principles.forEach((principle) => {
      this.principleWeights.set(principle, weight);
    });
  }

  /**
   * Register an agent in the swarm
   */
  public registerAgent(agentId: string): void {
    if (this.agents.size >= this.maxAgents) {
      throw new SwarmError(
        SwarmErrorCode.SYSTEM_RESOURCE_EXHAUSTED,
        `Maximum agent capacity (${this.maxAgents}) reached`,
        'high',
      );
    }

    const agentState: AgentState = {
      id: agentId,
      principleScores: new Map(),
      consistencyMetric: 1.0,
      stabilityMetric: 0.0,
      lastUpdate: Date.now(),
      faultFlag: false,
      byzantineScore: 0.0,
    };

    Object.values(MaatPrinciple).forEach((principle) => {
      agentState.principleScores.set(principle, 0.5);
    });

    this.agents.set(agentId, agentState);
  }

  /**
   * Update agent principle score
   */
  public updateAgentPrinciple(
    agentId: string,
    principle: MaatPrinciple,
    score: number,
  ): void {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new SwarmError(
        SwarmErrorCode.VALIDATION_PRINCIPLE_MISSING,
        `Agent ${agentId} not found`,
        'high',
      );
    }

    if (score < 0 || score > 1) {
      throw new SwarmError(
        SwarmErrorCode.VALIDATION_THRESHOLD_EXCEEDED,
        `Invalid score ${score}: must be between 0 and 1`,
        'medium',
      );
    }

    agent.principleScores.set(principle, score);
    agent.lastUpdate = Date.now();
  }

  /**
   * Validate all 42 principles for an agent
   */
  private validatePrinciples(agentId: string): Map<MaatPrinciple, ValidationResult> {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new SwarmError(
        SwarmErrorCode.VALIDATION_PRINCIPLE_MISSING,
        `Agent ${agentId} not found`,
        'high',
      );
    }

    const results = new Map<MaatPrinciple, ValidationResult>();

    Object.values(MaatPrinciple).forEach((principle) => {
      const score = agent.principleScores.get(principle) ?? 0.5;
      const threshold = this.getPrincipleThreshold(principle);
      const constraintStatus = this.validateConstraints(principle, score, agent);
      const passed = score >= threshold && Array.from(constraintStatus.values()).every((v) => v);

      results.set(principle, {
        principle,
        score,
        threshold,
        passed,
        constraintStatus,
      });
    });

    return results;
  }

  /**
   * Get principle-specific threshold
   */
  private getPrincipleThreshold(principle: MaatPrinciple): number {
    // Core principles have higher thresholds
    const corePrinciples = [
      MaatPrinciple.UNIFIED_CONSCIOUSNESS,
      MaatPrinciple.HONEST_REPRESENTATION,
      MaatPrinciple.EQUILIBRIUM_DYNAMICS,
    ];

    return corePrinciples.includes(principle) ? 0.8 : 0.6;
  }

  /**
   * Validate constraints for a principle
   */
  private validateConstraints(
    principle: MaatPrinciple,
    score: number,
    agent: AgentState,
  ): Map<string, boolean> {
    const constraints = new Map<string, boolean>();

    // Basic constraints
    constraints.set('score_bounds', score >= 0 && score <= 1);
    constraints.set('consistency_valid', agent.consistencyMetric >= 0);
    constraints.set('no_fault', !agent.faultFlag);
    constraints.set('not_byzantine', agent.byzantineScore < 0.5);

    // Principle-specific constraints
    if (principle.startsWith('P0') && principle <= MaatPrinciple.UNIFIED_CONSCIOUSNESS) {
      constraints.set('coherence_maintained', score > 0.4);
    }

    return constraints;
  }

  /**
   * Calculate swarm consensus for a principle
   */
  private calculateConsensus(principle: MaatPrinciple): number {
    if (this.agents.size === 0) return 0;

    let totalScore = 0;
    let validAgents = 0;

    this.agents.forEach((agent) => {
      if (!agent.faultFlag) {
        totalScore += agent.principleScores.get(principle) ?? 0.5;
        validAgents++;
      }
    });

    return validAgents > 0 ? totalScore / validAgents : 0;
  }

  /**
   * Calculate divergence metric for consensus
   */
  private calculateDivergenceMetric(principle: MaatPrinciple): number {
    if (this.agents.size < 2) return 0;

    const mean = this.calculateConsensus(principle);
    let variance = 0;
    let validAgents = 0;

    this.agents.forEach((agent) => {
      if (!agent.faultFlag) {
        const score = agent.principleScores.get(principle) ?? 0.5;
        variance += Math.pow(score - mean, 2);
        validAgents++;
      }
    });

    return validAgents > 0 ? Math.sqrt(variance / validAgents) : 0;
  }

  /**
   * Build consensus state across swarm
   */
  private buildConsensusState(): ConsensusState {
    const principleAgreement = new Map<MaatPrinciple, number>();
    const divergenceMetrics: number[] = [];
    const conflictingAgents: Set<string> = new Set();

    Object.values(MaatPrinciple).forEach((principle) => {
      const agreement = this.calculateConsensus(principle);
      const divergence = this.calculateDivergenceMetric(principle);
      principleAgreement.set(principle, agreement);
      divergenceMetrics.push(divergence);

      // Detect conflicts
      if (divergence > 0.3) {
        this.agents.forEach((agent) => {
          const score = agent.principleScores.get(principle) ?? 0.5;
          if (Math.abs(score - agreement) > 0.4) {
            conflictingAgents.add(agent.id);
          }
        });
      }
    });

    const globalConfidence =
      Array.from(principleAgreement.values()).reduce((a, b) => a + b, 0) /
      principleAgreement.size;
    const avgDivergence =
      divergenceMetrics.reduce((a, b) => a + b, 0) / divergenceMetrics.length;
    const quorumReached = this.agents.size > 0 && globalConfidence >= this.consensusThreshold;

    return {
      principleAgreement,
      globalConfidence,
      divergenceMetric: avgDivergence,
      quorumReached,
      conflictingAgents: Array.from(conflictingAgents),
      timestamp: Date.now(),
    };
  }

  /**
   * Perform Lyapunov stability analysis
   */
  private performLyapunovAnalysis(agentId: string): LyapunovAnalysis {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new SwarmError(
        SwarmErrorCode.STABILITY_LYAPUNOV_VIOLATION,
        `Agent ${agentId} not found for stability analysis`,
        'high',
      );
    }

    const scores = Array.from(agent.principleScores.values());
    const exponents = this.calculateLyapunovExponents(scores);
    const maxExponent = Math.max(...exponents);
    const isStable = maxExponent < this.stabilityThreshold;
    const attractor = this.calculateAttractor(scores);
    const divergenceRate = this.calculateDivergenceRate(scores);
    const bifurcationRisk = this.estimateBifurcationRisk(scores);
    const oscillationDetected = this.detectOscillation(scores);

    return {
      exponents,
      maxExponent,
      isStable,
      attractor,
      divergenceRate,
      bifurcationRisk,
      oscillationDetected,
    };
  }

  /**
   * Calculate Lyapunov exponents using finite-time method
   */
  private calculateLyapunovExponents(scores: number[]): number[] {
    const n = scores.length;
    const exponents: number[] = [];
    const dt = 0.01;

    for (let i = 0; i < Math.min(n, 10); i++) {
      let sum = 0;
      for (let j = 0; j < n - 1; j++) {
        const dx = Math.abs(scores[j + 1] - scores[j]);
        if (dx > 1e-10) {
          sum += Math.log(dx);
        }
      }
      exponents.push(sum / (n - 1) / dt);
    }

    return exponents;
  }

  /**
   * Calculate system attractor
   */
  private calculateAttractor(scores: number[]): number[] {
    const n = Math.min(3, scores.length);
    const attractor: number[] = [];

    for (let i = 0; i < n; i++) {
      const windowSize = Math.max(5, Math.floor(scores.length / 5));
      const window = scores.slice(
        Math.max(0, scores.length - windowSize),
        scores.length,
      );
      const avg = window.reduce((a, b) => a + b, 0) / window.length;
      attractor.push(avg);
    }

    return attractor;
  }

  /**
   * Calculate divergence rate
   */
  private calculateDivergenceRate(scores: number[]): number {
    if (scores.length < 2) return 0;

    let divergence = 0;
    for (let i = 1; i < scores.length; i++) {
      divergence += Math.abs(scores[i] - scores[i - 1]);
    }

    return divergence / (scores.length - 1);
  }

  /**
   * Estimate bifurcation risk
   */
  private estimateBifurcationRisk(scores: number[]): number {
    const mean = scores.reduce((a, b) => a + b, 0) / scores.length;
    const variance =
      scores.reduce((sum, s) => sum + Math.pow(s - mean, 2), 0) / scores.length;
    const skewness = scores.reduce((sum, s) => sum + Math.pow(s - mean, 3), 0) / (scores.length * Math.pow(variance, 1.5));

    // Higher variance and skewness indicate bifurcation risk
    return Math.min(1.0, (variance + Math.abs(skewness)) / 2);
  }

  /**
   * Detect oscillation in principle scores
   */
  private detectOscillation(scores: number[]): boolean {
    if (scores.length < 4) return false;

    let oscillationCount = 0;
    for (let i = 1; i < scores.length - 1; i++) {
      const isLocal = (scores[i] > scores[i - 1] && scores[i] > scores[i + 1]) ||
                      (scores[i] < scores[i - 1] && scores[i] < scores[i + 1]);
      if (isLocal) oscillationCount++;
    }

    return oscillationCount > scores.length / 3;
  }

  /**
   * Perform consistency checking
   */
  private performConsistencyCheck(agentId: string): ConsistencyCheckResult {
    const agent = this.agents.get(agentId);
    if (!agent) {
      return {
        isConsistent: false,
        violations: [`Agent ${agentId} not found`],
        stateMismatch: 1.0,
        partitionDetected: true,
        recoveryTime: 0,
        validationScore: 0.0,
      };
    }

    const violations: string[] = [];
    const scores = Array.from(agent.principleScores.values());

    // Check consistency constraints
    if (agent.consistencyMetric < this.consistencyThreshold) {
      violations.push(`Consistency metric below threshold: ${agent.consistencyMetric}`);
    }

    if (agent.byzantineScore > 0.3) {
      violations.push(`Byzantine score elevated: ${agent.byzantineScore}`);
    }

    // Check state continuity
    const mean = scores.reduce((a, b) => a + b, 0) / scores.length;
    const variance = scores.reduce((sum, s) => sum + Math.pow(s - mean, 2), 0) / scores.length;
    const stdDev = Math.sqrt(variance);

    if (stdDev > 0.5) {
      violations.push(`High variance in principle scores: ${stdDev}`);
    }

    // Calculate state mismatch
    const expectedMean = 0.5;
    const stateMismatch = Math.abs(mean - expectedMean) + stdDev;

    // Detect partition
    const partitionDetected = agent.lastUpdate < Date.now() - 30000;

    // Calculate recovery time
    const recoveryTime = partitionDetected ? Date.now() - agent.lastUpdate : 0;

    // Validation score
    const validationScore = Math.max(
      0,
      1.0 - stateMismatch - (agent.faultFlag ? 0.5 : 0),
    );

    return {
      isConsistent: violations.length === 0 && validationScore >= this.consistencyThreshold,
      violations,
      stateMismatch,
      partitionDetected,
      recoveryTime,
      validationScore,
    };
  }

  /**
   * Comprehensive evaluation of a single agent
   */
  public evaluateAgent(agentId: string): EvaluationResult {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new SwarmError(
        SwarmErrorCode.VALIDATION_PRINCIPLE_MISSING,
        `Agent ${agentId} not found`,
        'high',
      );
    }

    const principleValidation = this.validatePrinciples(agentId);
    const consensusState = this.buildConsensusState();
    const stabilityAnalysis = this.performLyapunovAnalysis(agentId);
    const consistencyCheck = this.performConsistencyCheck(agentId);

    // Calculate overall score
    let totalScore = 0;
    let passedCount = 0;

    principleValidation.forEach((result) => {
      if (result.passed) passedCount++;
      totalScore += result.score;
    });

    const overallScore =
      (totalScore / principleValidation.size) * 0.4 +
      consensusState.globalConfidence * 0.25 +
      (stabilityAnalysis.isStable ? 1.0 : 0.0) * 0.2 +
      consistencyCheck.validationScore * 0.15;

    // Determine health status
    const isHealthy =
      overallScore >= 0.7 &&
      consensusState.quorumReached &&
      stabilityAnalysis.isStable &&
      consistencyCheck.isConsistent;

    // Collect errors
    const errors: SwarmError[] = [];

    // Check for validation errors
    principleValidation.forEach((result) => {
      if (!result.passed) {
        errors.push(
          new SwarmError(
            SwarmErrorCode.VALIDATION_PRINCIPLE_VIOLATION,
            `Principle ${result.principle} failed validation`,
            'medium',
            { principle: result.principle, score: result.score, threshold: result.threshold },
          ),
        );
      }
    });

    // Check for consensus errors
    if (!consensusState.quorumReached) {
      errors.push(
        new SwarmError(
          SwarmErrorCode.CONSENSUS_QUORUM_NOT_MET,
          `Consensus quorum not reached: ${consensusState.globalConfidence}`,
          'high',
          { confidence: consensusState.globalConfidence, threshold: this.consensusThreshold },
        ),
      );
    }

    if (consensusState.divergenceMetric > 0.3) {
      errors.push(
        new SwarmError(
          SwarmErrorCode.CONSENSUS_DIVERGENCE,
          `Significant consensus divergence detected`,
          'high',
          { divergence: consensusState.divergenceMetric },
        ),
      );
    }

    // Check for stability errors
    if (!stabilityAnalysis.isStable) {
      errors.push(
        new SwarmError(
          SwarmErrorCode.STABILITY_LYAPUNOV_VIOLATION,
          `System instability detected`,
          'critical',
          { maxExponent: stabilityAnalysis.maxExponent, threshold: this.stabilityThreshold },
        ),
      );
    }

    if (stabilityAnalysis.oscillationDetected) {
      errors.push(
        new SwarmError(
          SwarmErrorCode.STABILITY_OSCILLATION_DETECTED,
          `Oscillation detected in system dynamics`,
          'medium',
          { divergenceRate: stabilityAnalysis.divergenceRate },
        ),
      );
    }

    if (stabilityAnalysis.bifurcationRisk > 0.6) {
      errors.push(
        new SwarmError(
          SwarmErrorCode.STABILITY_BIFURCATION_RISK,
          `High bifurcation risk detected`,
          'high',
          { risk: stabilityAnalysis.bifurcationRisk },
        ),
      );
    }

    // Check for consistency errors
    if (!consistencyCheck.isConsistent) {
      errors.push(
        new SwarmError(
          SwarmErrorCode.CONSISTENCY_VIOLATION,
          `Consistency violation detected`,
          'high',
          { violations: consistencyCheck.violations },
        ),
      );
    }

    if (consistencyCheck.partitionDetected) {
      errors.push(
        new SwarmError(
          SwarmErrorCode.CONSISTENCY_PARTITION,
          `Network partition detected`,
          'critical',
          { recoveryTime: consistencyCheck.recoveryTime },
        ),
      );
    }

    this.errors = errors;

    return {
      timestamp: Date.now(),
      agentId,
      principleValidation,
      overallScore,
      consensusState,
      stabilityAnalysis,
      consistencyCheck,
      errors,
      isHealthy,
    };
  }

  /**
   * Comprehensive swarm evaluation
   */
  public evaluateSwarm(): EvaluationResult[] {
    const results: EvaluationResult[] = [];

    this.agents.forEach((agent) => {
      try {
        const result = this.evaluateAgent(agent.id);
        results.push(result);
      } catch (error) {
        if (error instanceof SwarmError) {
          this.errors.push(error);
        }
      }
    });

    return results;
  }

  /**
   * Get recent errors
   */
  public getErrors(limit: number = 100): SwarmError[] {
    return this.errors.slice(-limit);
  }

  /**
   * Clear error log
   */
  public clearErrors(): void {
    this.errors = [];
  }

  /**
   * Get system metrics
   */
  public getMetrics(): Record<string, any> {
    const allResults = this.evaluateSwarm();
    const avgScore = allResults.reduce((sum, r) => sum + r.overallScore, 0) / Math.max(1, allResults.length);
    const healthyCount = allResults.filter((r) => r.isHealthy).length;
    const totalErrors = this.errors.length;

    return {
      totalAgents: this.agents.size,
      healthyAgents: healthyCount,
      averageScore: avgScore,
      totalErrors,
      errorsByCritical: this.errors.filter((e) => e.severity === 'critical').length,
      errorsByHigh: this.errors.filter((e) => e.severity === 'high').length,
      errorsByMedium: this.errors.filter((e) => e.severity === 'medium').length,
      errorsByLow: this.errors.filter((e) => e.severity === 'low').length,
      timestamp: Date.now(),
    };
  }

  /**
   * Export evaluation data
   */
  public exportEvaluationData(): string {
    const results = this.evaluateSwarm();
    const metrics = this.getMetrics();

    return JSON.stringify(
      {
        metrics,
        evaluations: results.map((r) => ({
          agentId: r.agentId,
          timestamp: r.timestamp,
          overallScore: r.overallScore,
          isHealthy: r.isHealthy,
          consensusConfidence: r.consensusState.globalConfidence,
          stabilityScore: r.stabilityAnalysis.maxExponent,
          consistencyScore: r.consistencyCheck.validationScore,
          errorCount: r.errors.length,
        })),
        errors: this.errors.map((e) => ({
          code: e.code,
          message: e.message,
          severity: e.severity,
          details: e.details,
        })),
      },
      null,
      2,
    );
  }
}

export default SwarmEvaluationSystem;
