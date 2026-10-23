---
title: "Spring Boot IDOR: Enforce Ownership on Every Order Query"
description: "Fix object-level authorization on order lookup, listing, and search. Parameterized SQL is not an ownership check; verify rejected access too."
pubDate: 2026-10-21
category: "java-ai-tools"
tags: ["claude code", "spring boot", "ai coding", "idor", "api security", "java-ai-cluster"]
image: "/og-default.jpg"
imageAlt: "AI Kit Guides"
keywords: ["claude code spring boot", "claude code security", "idor spring boot", "ai generated insecure code", "broken object level authorization", "spring boot api security"]
updatedDate: 2026-10-23
---

An authenticated Spring Boot endpoint can still expose another user's records if lookup, listing, or search trusts a caller-supplied owner. Object-level authorization must cover every access path.

This is a reconstructed teaching case based on an AI-built lab, not a personal production incident or a model-security benchmark. Unsupported third-party percentages and claims about how often agents miss authorization have been removed.

## Define the access policy

For this example, an ordinary user may see only their own orders. Administrative access, if required, needs a separate explicit policy. The authenticated principal supplies the user identity; a request parameter does not.

Decide whether inaccessible records return 403 or 404 according to the application's disclosure and error policy. Returning 404 can avoid revealing existence, but it does not replace authorization.

## Scope the lookup

Prefer a query that includes both the record ID and trusted owner. An illustrative Spring Data repository method is:

```java
Optional<AppOrder> findByIdAndOwnerUsername(Long id, String ownerUsername);
List<AppOrder> findByOwnerUsername(String ownerUsername);
List<AppOrder> findByOwnerUsernameAndOrderNumberContaining(
        String ownerUsername, String orderNumber);
```

These are interface fragments, assuming matching entity properties. The service should pass the authenticated identity and map entities to the application's response DTO rather than exposing every entity field by default.

The [downloadable Java fixture](/examples/java-verification.zip) demonstrates the ownership predicate and rejected access in memory. It does not verify Spring Security filters, HTTP responses, or database queries.

## Cover listing and search too

For the example policy, ignore a caller-supplied `owner` as an authorization source. Listing should derive the owner from the principal. Search should combine the principal's owner constraint with the search term.

A parameterized SQL query protects a different boundary: it avoids constructing SQL syntax from untrusted text. It does not add an ownership predicate. The earlier article fixed lookup and listing but left an unrestricted search example; that was an incomplete remediation.

If cross-user search is an administrative feature, enforce that role explicitly and test the ordinary-user rejection. Do not leave an unrestricted endpoint beside a protected lookup and call the API fixed.

## Test the complete access matrix

Use at least two ordinary identities with records belonging to each. Establish:

- The owner can access their record.
- Another authenticated user cannot access it by ID.
- Listing cannot be redirected to another owner through a parameter.
- Search cannot return another user's record.
- Anonymous access is handled by the authentication policy.
- Any administrative exception follows the documented role policy.

Inspect both the response and the underlying query or service behavior. A mocked authentication object without the real filter chain proves a narrower property than an HTTP integration test.

## Keep authorization at a reusable boundary

Service-layer checks help when the same action is invoked outside a controller. Spring's [method-security documentation](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html) describes another enforcement mechanism, but annotations require the corresponding configuration and invocation path.

Do not rely on an instruction file alone. Record ownership in the requirement, add negative tests, and review all data access paths. Automated static review may help locate risks, but absence of a finding does not establish the policy.

Use the [AI review guide](/blog/ai-code-review-java/) and [JUnit guide](/blog/ai-junit-tests/) for the surrounding checks. The [AFTER_COMMIT case](/blog/claude-code-after-commit-email-loss/) covers a different missing guarantee, durable delivery, and the [Java hub](/blog/ai-for-java-developers/) links the broader workflow.
