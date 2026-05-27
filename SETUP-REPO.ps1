# PivotMap Repository Setup Script
# Run this after creating the GitHub repo and pushing branches
# Prerequisites: gh CLI must be installed and authenticated (gh auth login)

$OWNER = "gabriel-wan"
$REPO = "PivotMap"
$REPO_PATH = "$OWNER/$REPO"

Write-Host "=== PivotMap GitHub Setup ===" -ForegroundColor Green
Write-Host "Repository: https://github.com/$REPO_PATH`n"

# ============================================================================
# PHASE 1: BRANCH PROTECTION
# ============================================================================
Write-Host "PHASE 1: Setting up branch protection on main..." -ForegroundColor Cyan

try {
    gh api repos/$REPO_PATH/branches/main/protection `
        --method PUT `
        --field 'required_status_checks={"strict":true,"contexts":["ci/pytest","ci/lint"]}' `
        --field enforce_admins=false `
        --field 'required_pull_request_reviews={"required_approving_review_count":1,"dismiss_stale_reviews":true}' `
        --field restrictions=null
    Write-Host "✅ Branch protection enabled on main`n" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Branch protection setup failed (may already be configured): $_`n" -ForegroundColor Yellow
}

# ============================================================================
# PHASE 2: LABELS
# ============================================================================
Write-Host "PHASE 2: Creating labels..." -ForegroundColor Cyan

$labels = @(
    # Type labels
    @{name = "type:feature"; color = "0075ca"; description = "New feature"}
    @{name = "type:bug"; color = "d73a4a"; description = "Bug or broken behaviour"}
    @{name = "type:test"; color = "e4e669"; description = "Tests and QA"}
    @{name = "type:docs"; color = "c2e0c6"; description = "Documentation"}
    @{name = "type:chore"; color = "e1e4e8"; description = "Setup, config, CI/CD"}
    @{name = "type:research"; color = "d4c5f9"; description = "Investigation or spike"}
    
    # Component labels
    @{name = "comp:agent"; color = "5319e7"; description = "MiroFlow agent layer"}
    @{name = "comp:frontend"; color = "0052cc"; description = "Next.js / React Flow UI"}
    @{name = "comp:api"; color = "006b75"; description = "FastAPI backend"}
    @{name = "comp:db"; color = "1d76db"; description = "PostgreSQL / pgvector schema"}
    @{name = "comp:scraper"; color = "0e8a16"; description = "Institution module scraper"}
    @{name = "comp:schema"; color = "f9d0c4"; description = "Proof graph / roadmap schema"}
    @{name = "comp:ci"; color = "fef2c0"; description = "CI/CD and tooling"}
    
    # Priority labels
    @{name = "priority:critical"; color = "b60205"; description = "Blocks others, fix now"}
    @{name = "priority:high"; color = "e99695"; description = "Core hackathon deliverable"}
    @{name = "priority:medium"; color = "f9d0c4"; description = "Important but not blocking"}
    @{name = "priority:low"; color = "fef2c0"; description = "Nice to have"}
    
    # Phase labels
    @{name = "phase-1"; color = "0e8a16"; description = "Phase 1: Foundation (Week 1-2)"}
    @{name = "phase-2"; color = "e4a820"; description = "Phase 2: Core pipeline (Week 3-4)"}
    @{name = "phase-3"; color = "d93f0b"; description = "Phase 3: Polish & demo (Week 5)"}
    
    # Status labels
    @{name = "status:blocked"; color = "b60205"; description = "Blocked by another issue"}
    @{name = "status:in-review"; color = "0075ca"; description = "PR open, awaiting review"}
    @{name = "status:needs-test"; color = "e4e669"; description = "Awaiting test coverage"}
)

foreach ($label in $labels) {
    try {
        gh label create $label.name `
            --color $label.color `
            --description $label.description `
            --force 2>$null
        Write-Host "  ✅ $($label.name)"
    }
    catch {
        Write-Host "  ⚠️ $($label.name) (may already exist)"
    }
}
Write-Host "`n✅ Labels created`n" -ForegroundColor Green

# ============================================================================
# PHASE 3: MILESTONES
# ============================================================================
Write-Host "PHASE 3: Creating milestones..." -ForegroundColor Cyan

$milestones = @(
    @{title = "1.1 - Repo & Infrastructure"; description = "Docker, CI, DB schema, branch setup"; due = "2026-05-07T23:59:59Z"}
    @{title = "1.2 - Agent Skeleton"; description = "MiroFlow config, JD parser, planner stub"; due = "2026-05-10T23:59:59Z"}
    @{title = "1.3 - Data Layer Core"; description = "Module DB scraper, PostgreSQL schema, pgvector"; due = "2026-05-12T23:59:59Z"}
    @{title = "2.1 - Research & Verification"; description = "Research agent, verifier, temporal tagger"; due = "2026-05-18T23:59:59Z"}
    @{title = "2.2 - Proof Mapper"; description = "Proof graph output, module validator"; due = "2026-05-22T23:59:59Z"}
    @{title = "2.3 - Frontend Graph Canvas"; description = "React Flow proof graph, evidence panel"; due = "2026-05-26T23:59:59Z"}
    @{title = "3.1 - Integration & Testing"; description = "E2E tests, merge conflicts resolved, CI green"; due = "2026-05-29T23:59:59Z"}
    @{title = "3.2 - Demo & Open-Source"; description = "Demo case, README, adapter docs, v1.0.0"; due = "2026-06-01T23:59:59Z"}
)

foreach ($milestone in $milestones) {
    try {
        gh api repos/$REPO_PATH/milestones `
            -f title=$milestone.title `
            -f description=$milestone.description `
            -f due_on=$milestone.due 2>$null
        Write-Host "  ✅ $($milestone.title)"
    }
    catch {
        Write-Host "  ⚠️ $($milestone.title) (may already exist)"
    }
}
Write-Host "`n✅ Milestones created`n" -ForegroundColor Green

Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "  1. Run the issue creation script: SETUP-ISSUES.ps1"
Write-Host "  2. Repo: https://github.com/$REPO_PATH`n"
