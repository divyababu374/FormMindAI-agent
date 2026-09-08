# 🔒 FormMind AI — Security Policy & Guidelines

At FormMind AI, the security, privacy, and integrity of your survey and analytical data are foundational. This document outlines our security architecture, data retention principles, and responsible vulnerability disclosure process.

---

## 🏛️ Security Architecture Overview

FormMind AI implements a defense-in-depth security model:

```
[ Public User ]
       │ (HTTPS / TLS 1.3)
       ▼
[ Vercel Edge CDN ] ────► Strict Security Headers (CSP, HSTS, X-Content-Type-Options, Referrer-Policy)
       │
[ Supabase Auth ] ──────► Google OAuth 2.0 Identity Provider (prompt=select_account)
       │
[ FastAPI Backend ] ────► Token Verification & User Authorization (Zero Client-Side Trust)
       │
 ┌─────┴─────────────────────────┐
 │                               │
 ▼                               ▼
[ Analytical Engine & Storage ] [ Outbound Connectors ]
 • In-memory compute             • SSRF Domain Whitelisting
 • CSV Formula Sanitization      • Private IP / Localhost Blocking
 • Temporary Upload Cleanup      • 15s Strict Timeouts
```

---

## 🛡️ Core Security Controls

### 1. Authentication & Identity Isolation
- **Supabase Isolation**: Supabase is strictly used for authentication and minimal profile metadata (`id`, `name`, `email`, `avatar_url`). No survey responses, uploaded files, or analysis results are stored in Supabase.
- **Row Level Security (RLS)**: Profile access is locked to `auth.uid() = id`.
- **Server-Derived Identity**: The FastAPI backend independently validates access tokens and derives the user ID from cryptographically verified claims. Client-supplied `user_id` fields are never trusted for authorization.

### 2. Authorization & Horizontal Access Control (BOLA/IDOR Defense)
- All form accesses, report generation, export downloads, and AI chat sessions enforce ownership validation (`Form.user_id == authenticated_user_id`).
- Unauthorized requests to other users' resources result in `404 Not Found` or `403 Forbidden` with zero data leakage.

### 3. File Upload & Ingestion Hardening
- **Strict Format Allowlist**: Only `.csv`, `.xlsx`, and `.xls` files are accepted. Executable files, script files, and macro-enabled workbooks (`.xlsm`, `.xltm`, `.exe`, `.js`, etc.) are prohibited.
- **Filename Sanitization**: Directory traversal sequences (`../`, `..\\`) and control characters are stripped.
- **Ephemeral Storage**: Uploaded files are processed in-memory / temporary storage and immediately cleaned up using `try...finally` lifecycle guarantees.

### 4. SSRF (Server-Side Request Forgery) Protection
- FormMind only ingests forms from authorized HTTPS endpoints (`docs.google.com`, `forms.gle`, `forms.office.com`, `forms.microsoft.com`).
- Outbound requests resolve hostnames and strictly block loopback (`127.0.0.1`, `localhost`), link-local/cloud metadata (`169.254.169.254`), and private RFC1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).

### 5. CSV & Spreadsheet Formula Injection Defense (CWE-1236)
- User-supplied text values beginning with formula trigger characters (`=`, `+`, `-`, `@`, `\t`, `\r`) are escaped with a leading single quote (`'`) upon CSV/Excel export.
- Legitimate statistical metrics remain native numeric types.

### 6. AI & Prompt Injection Safeguards
- Survey questions and response contents are explicitly treated as untrusted data in AI prompt payloads.
- Model system prompts contain strict directives against revealing developer instructions, API keys, or server environment configurations.

---

## 🚨 Reporting a Vulnerability

We welcome security researchers and users to responsibly report potential security vulnerabilities.

If you discover a security issue, please email our security team at:
📧 **security@formmind.ai**

### Guidelines:
- Please include a detailed description of the issue, reproduction steps, and proof-of-concept where applicable.
- Please do not exploit the issue to access unauthorized data or disrupt services.
- Give us reasonable time to remediate the vulnerability before public disclosure.
