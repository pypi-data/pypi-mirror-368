# Implementing "Underpromise, Overdeliver" Policy

## Integration Strategy

### 1. Pre-Commit Hook Setup
Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: documentation-language-check
        name: Check documentation language policy
        entry: python check_documentation_language.py
        language: python
        files: \.(md|py|rst|txt)$
        pass_filenames: true
```

### 2. GitHub Actions Integration
Add to `.github/workflows/documentation-check.yml`:
```yaml
name: Documentation Policy Check
on: [push, pull_request]
jobs:
  documentation-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check Documentation Language
        run: python check_documentation_language.py
```

### 3. Pull Request Template Update
Add to `.github/pull_request_template.md`:
```markdown
## Documentation Review Checklist
- [ ] Ran documentation language checker with no violations
- [ ] Followed "underpromise, overdeliver" policy
- [ ] Used realistic language (no "perfect", "amazing", etc.)
- [ ] Included limitations/caveats where relevant
```

### 4. Release Process Integration
Add mandatory step to release checklist:
```markdown
## Pre-Release Documentation Review
- [ ] All documentation reviewed against DOCUMENTATION_POLICY.md  
- [ ] Language checker passes with zero violations
- [ ] Claims tested and verified where possible
- [ ] Known issues documented
```

## Training Materials

### For New Contributors
1. **Read**: DOCUMENTATION_POLICY.md
2. **Use**: DOCUMENTATION_REVIEW_TEMPLATE.md  
3. **Run**: `python check_documentation_language.py` before submitting
4. **Remember**: "Would I bet money this works as described?"

### For Maintainers  
1. **Reference policy** in every documentation PR review
2. **Use review template** consistently
3. **Suggest specific improvements** using approved language patterns
4. **Lead by example** in your own documentation

## Enforcement Levels

### Level 1: Automated (Pre-commit/CI)
- Catches obvious banned words
- Flags excessive emojis
- Identifies absolute statements

### Level 2: Peer Review (Human)
- Reviews context and nuance
- Checks realistic expectations
- Verifies technical accuracy

### Level 3: User Testing (Optional but Recommended)
- Test claims with real users when possible
- Document actual results vs. promises
- Update documentation based on real-world feedback

## Maintenance Schedule

### Quarterly Review (Every 3 Months)
- Review policy effectiveness
- Update banned words list based on violations
- Refine checker script based on false positives/negatives
- Survey user feedback on documentation accuracy

### Annual Audit (Yearly)
- Full documentation review against policy
- Update language patterns based on industry changes
- Review competitor documentation for tone comparison
- Major policy updates if needed

## Success Metrics

### Quantitative
- Zero documentation policy violations in releases
- Reduced user complaints about feature expectations
- Lower GitHub issue rates related to "doesn't work as described"

### Qualitative  
- User feedback indicates realistic expectations
- Documentation builds trust rather than disappointment
- Professional reputation for honest communication

---

## Quick Start for Immediate Use

1. **Copy** `DOCUMENTATION_POLICY.md` to your project root
2. **Run** `python check_documentation_language.py` on existing docs
3. **Fix** any violations found
4. **Add** policy link to your CONTRIBUTING.md
5. **Use** review template for next documentation PR

**Remember**: This policy protects user trust and project reputation by ensuring honest, realistic communication about capabilities and limitations.
