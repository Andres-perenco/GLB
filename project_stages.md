# Project Stages & Engineering Roadmap

## Completed Milestones

1. **BSW & Production Test Ingestion**
   - Database retrieval of wellbore tests for BSW calculation (single test selection or average of latest tests).
   - Ingestion of manual parameters (BSW / WCT) via API payload and CSV uploads.
2. **Optimization KPIs**
   - Global optimization maximum operational envelope calculation.
   - Constrained optimization KPI calculating additional gas delta required to reach maximum production.
3. **Database Integration & Fallback**
   - Real-time production test retrieval from Snowflake (`RAW` and `PROD` schemas).
   - Resilient mock fallback when Snowflake is offline or unreachable in local environments.
4. **Standalone Backend Migration**
   - Decoupled from Streamlit frontend to operate strictly as a REST API service.
   - Relational persistence of field and well optimization runs using SQLModel and SQLite.
   - Prediction and confidence intervals implemented for curve fitting regressors.

---

## Planned / Upcoming Tasks (TODO)

1. **Stochastic & Advanced Modeling**
   - Gaussian process regression to derive prior performance curves from historical well tests.
   - Incorporate dynamic BSW as a function of injection gas rate (\(Q_{gl}\)) to weight oil production curves.
   - Confidence and prediction intervals integrated directly into the optimization pipeline.
2. **Database & API Expansions**
   - Dedicated table and schema for global optimization runs and envelope tracking.
   - Support dynamic \(N\)-well CSV parsing with arbitrary column definitions.
   - Optional configurable Maximum Production Rate (MPR) constraints (physical and economic limits).
3. **AI & Automated Reporting**
   - Automated LLM-generated diagnostic summary of optimization runs and gas efficiency.
   - Automated anomaly detection for deviant well performance tests.

---

## Ideas & Explorations

- Ingestion connector for Automated Testing Systems (ATS).
- Historical window query endpoints with date-range filters for well test trend analysis.
- Endpoints to return confidence fidelity percentages based on point density and residuals.