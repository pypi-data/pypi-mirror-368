# EDAFLOW DOCUMENTATION POLICY
# "Underpromise, Overdeliver" Framework

## CORE PRINCIPLE
**Always set realistic expectations. Let the software exceed user expectations rather than fall short of promises.**

## FORBIDDEN LANGUAGE PATTERNS

### 🚫 BANNED WORDS & PHRASES
- "Perfect/Perfectly" → Use: "Improved", "Better", "Enhanced"
- "Amazing/Incredible" → Use: "Useful", "Helpful", "Effective"
- "Revolutionary" → Use: "New", "Updated", "Improved"
- "Ultimate/Best" → Use: "Good", "Reliable", "Solid"
- "Seamlessly/Effortlessly" → Use: "Easily", "Straightforwardly"
- "Guaranteed" → Use: "Should", "Typically", "Usually"
- "Never fails" → Use: "Reliable", "Stable"
- "Always works" → Use: "Works in most cases", "Generally works"

### 🚫 BANNED EMOJIS (Overuse)
- 🚀 (Rocket) - Maximum 1 per document, only for major releases
- ✨ (Sparkles) - Avoid entirely, too promotional
- 💥 (Explosion) - Never use
- 🔥 (Fire) - Never use

### 🚫 BANNED ABSOLUTE STATEMENTS
- "This will solve all your problems"
- "Works in every situation"  
- "Complete solution"
- "Everything you need"

## APPROVED LANGUAGE PATTERNS

### ✅ REALISTIC QUALIFIERS
- "Should work well in most cases"
- "Typically provides good results"
- "Generally improves performance"
- "May help with..."
- "Designed to improve..."
- "Aims to provide better..."

### ✅ HONEST LIMITATIONS
- "Note: May not work in all environments"
- "Limitation: Requires specific conditions"
- "Known issue: ..."
- "Currently supports..."

### ✅ PROFESSIONAL TONE
- Technical accuracy over marketing appeal
- Specific benefits over general claims
- Evidence-based statements over promotional language
- User-focused outcomes over feature lists

## MANDATORY REVIEW CHECKLIST

Before ANY documentation release, verify:

### 📋 CONTENT REVIEW
- [ ] No absolute promises ("perfect", "always", "never fails")
- [ ] No excessive rocket emojis (🚀 max 1 per document)
- [ ] Realistic expectations set for new features
- [ ] Known limitations mentioned where relevant
- [ ] Technical accuracy verified
- [ ] User scenarios tested where possible

### 📋 LANGUAGE AUDIT
- [ ] Replace "perfect" with "improved"/"better"
- [ ] Replace "amazing" with "useful"/"helpful"  
- [ ] Replace "works perfectly" with "should work well"
- [ ] Replace "guaranteed" with "typically"/"usually"
- [ ] Add qualifiers: "in most cases", "generally", "should"

### 📋 EXPECTATION MANAGEMENT
- [ ] Features described with appropriate caveats
- [ ] Installation/setup requirements clearly stated
- [ ] Compatibility limitations mentioned
- [ ] Performance expectations realistic

## IMPLEMENTATION STRATEGY

### 1. PRE-COMMIT HOOKS
Create automated checks for banned words/phrases in documentation files.

### 2. REVIEW TEMPLATES  
Standardized review templates that include policy compliance checks.

### 3. DOCUMENTATION STANDARDS
- Always include a "Limitations" or "Known Issues" section
- Use "should" instead of "will" for expected outcomes
- Provide fallback instructions when things don't work as expected

### 4. RELEASE PROCESS INTEGRATION
- Policy compliance check required before any release
- Documentation review by second person mandatory
- User testing of claims before publication

## EXAMPLES OF GOOD vs BAD

### ❌ BAD (Overselling)
```
🚀 Revolutionary new ML module! 
Perfect accuracy guaranteed!
Works amazingly in all situations!
Your models will be incredible!
```

### ✅ GOOD (Realistic)
```
New ML module added
Provides improved model evaluation tools
Generally works well with common datasets
Should help streamline your ML workflow
Note: Requires pandas >= 1.0 and scikit-learn >= 0.24
```

## ENFORCEMENT

### For Maintainers:
1. **Reference this policy** at the start of any documentation work
2. **Use the checklist** before submitting any PR with documentation changes
3. **Call out violations** in code reviews diplomatically
4. **Suggest alternatives** using approved language patterns

### For Contributors:
1. **Read this policy** before contributing documentation
2. **Self-review** using the checklist
3. **Focus on user value** rather than feature promotion
4. **Test claims** before making them in documentation

## POLICY VERSIONING

- **Version**: 1.0
- **Created**: August 12, 2025
- **Last Updated**: August 12, 2025
- **Review Schedule**: Quarterly
- **Owner**: Project Maintainers

---

## QUICK REFERENCE CARD

**When in doubt, ask:**
1. "Is this claim testable and verifiable?"
2. "What happens if this doesn't work for a user?"
3. "Am I setting realistic expectations?"
4. "Would I trust this description if I were a new user?"

**Golden Rule**: If you wouldn't bet $100 on the claim working exactly as described for a random user, tone it down.

---

*This policy should be linked in CONTRIBUTING.md and referenced in all documentation PRs.*
