# API Design

## Current Endpoints

### Authentication
- `GET /login` - Initiate OAuth flow
- `GET /oauth2callback` - OAuth callback handler
- `GET /logout` - Clear session
- `GET /api/check_auth` - Check authentication status

### Settings
- `GET /api/settings` - Retrieve user settings
- `POST /api/settings` - Update user settings

### Briefing
- `GET /api/fetch_emails` - Fetch and analyze newsletters
  - **Rate Limit:** 3 requests per day (Free tier), Unlimited (Pro tier)
  - **Returns:** 429 Too Many Requests when limit exceeded
- `POST /api/generate_audio` - Generate audio briefing
- `POST /api/share` - Create shareable briefing link
- `GET /api/shared/<share_id>` - Retrieve shared briefing

## Design Principles
- RESTful conventions
- JSON responses
- Session-based auth
- Error handling with appropriate HTTP status codes
- Rate limiting to prevent abuse and control costs

## Rate Limiting

**Implementation:** Flask-Limiter with in-memory storage

**Current Limits:**
- **Free Tier:** 3 briefings per day per user
- **Pro Tier:** Unlimited (to be implemented with user tier check)
- **Global:** 200 requests/day, 50 requests/hour per IP

**Error Response (429):**
```json
{
  "error": "Daily limit reached. Upgrade to Pro for unlimited briefings."
}
```

**Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `Retry-After`: Seconds until limit resets

## Future Considerations
- User tier-based rate limiting (Free vs Pro)
- API versioning (`/api/v1/`)
- Webhook support
- Redis-backed rate limiting for multi-instance deployments
