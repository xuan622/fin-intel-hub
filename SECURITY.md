# Security TODO (Before Clawhub Release)

## Required Hardening

### HIGH Priority
- [ ] Input validation for ticker symbols (regex, length limits)
- [ ] Rate limiting (Alpha Vantage: 25/day, SEC: 10/min)
- [ ] API key validation before making calls

### MEDIUM Priority  
- [ ] Secure logging (no sensitive data leakage)
- [ ] Request/response caching (reduce API calls, improve speed)
- [ ] Error handling without info leakage

### LOW Priority
- [ ] Certificate pinning for APIs
- [ ] Request signing audit

## Notes
- All API keys currently use env vars (good)
- HTTPS enforced on all endpoints (good)
- Timeouts set on all requests (good)
