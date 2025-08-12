# Documentation Review Template

Use this template when reviewing any documentation changes (README, CHANGELOG, docstrings, etc.)

## Pre-Review Checklist

### ✅ Policy Compliance Check
- [ ] Ran `python check_documentation_language.py [files]` with no violations
- [ ] No banned words (perfect, amazing, revolutionary, etc.)
- [ ] No excessive emojis (max 1 🚀 per document)
- [ ] No absolute statements ("always works", "never fails")

### ✅ Language Quality Check  
- [ ] Uses realistic qualifiers ("should", "typically", "generally")
- [ ] Honest about limitations where relevant
- [ ] Professional tone throughout
- [ ] Technical accuracy verified

### ✅ User Experience Check
- [ ] Sets appropriate expectations
- [ ] Provides fallback instructions for common issues  
- [ ] Clear about requirements/dependencies
- [ ] Tested claims where possible

## Review Questions

1. **Realism Test**: "Would I bet $100 that this works exactly as described for a random user?"
   - [ ] Yes, proceed
   - [ ] No, needs toning down

2. **Newcomer Test**: "Would this description mislead a first-time user?"
   - [ ] No, it's clear and honest
   - [ ] Yes, needs revision

3. **Failure Test**: "What happens if this doesn't work as described?"
   - [ ] User has clear next steps
   - [ ] User would be confused/frustrated

## Approval Criteria

**✅ APPROVE if:**
- All checklist items completed
- Language is factual and realistic
- User expectations properly managed
- Technical content verified

**❌ REQUEST CHANGES if:**
- Policy violations found
- Overselling language detected  
- Missing important limitations/caveats
- Unverified claims made

## Suggested Language Fixes

### Replace These Patterns:
```
"works perfectly" → "should work well"
"amazing results" → "good results"  
"revolutionary approach" → "new approach"
"guaranteed success" → "typically successful"
"never fails" → "is reliable"
```

### Add These Qualifiers:
```
"Improves performance" → "Generally improves performance"
"Solves the problem" → "Should help solve the problem"
"Works everywhere" → "Works in most environments"
```

---

## Reviewer Signature
- [ ] I have reviewed this documentation against the DOCUMENTATION_POLICY.md
- [ ] I confirm this follows "underpromise, overdeliver" principles
- [ ] I would trust these claims if I were a new user

**Reviewer**: ________________
**Date**: ________________
