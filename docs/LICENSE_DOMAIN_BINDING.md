# License domain binding

**Status:** implemented in the current PR; not yet merged.  
**Applies to:** SEO, Revenue, Matching and Safety Gateways.

## Request contract

Every authenticated request may send:

```http
X-License-Key: <bearer-license-key>
X-Site-Domain: customer.example
```

- A license created with `domain="*"` remains backward-compatible and accepts any/missing site-domain header.
- A license created with a concrete hostname is bound to that exact normalized hostname. A missing or mismatched `X-Site-Domain` returns HTTP 403.
- Domain input accepts a hostname or an HTTP(S) origin, normalizes IDNA and case, and rejects credentials, ports, paths, query strings and fragments.
- WordPress clients send the hostname from `home_url()` for JSON and multipart requests.
- The Gateway removes `X-Site-Domain` before proxying to upstream inference services; it is licensing metadata, not model input.

## Security boundary

Domain binding is a policy/anti-misconfiguration control, **not cryptographic proof of website ownership**. A caller who possesses a bearer license key can spoof this header. Keep license keys secret, transmit them only over HTTPS, and use private/network controls where appropriate. Do not describe this header as DRM or a substitute for key protection.

## Compatibility and migration

Existing licenses with no domain or `domain="*"` remain unrestricted. Existing licenses with a concrete domain become enforceable once the caller sends the matching header. Non-WordPress SDKs must add `X-Site-Domain` when using a bound license. A license can be intentionally unbound by issuing it with `domain="*"`; do not mutate existing customer records without an explicit migration plan.

## Tests

The shared Gateway contract suite covers:
- exact domain match;
- missing and mismatched domain rejection;
- URL/case normalization;
- invalid path/port rejection;
- wildcard compatibility;
- all four Gateways under the same test matrix.

WordPress plugin CI syntax-checks all PHP files and verifies that each pack's API client sends the domain header.
