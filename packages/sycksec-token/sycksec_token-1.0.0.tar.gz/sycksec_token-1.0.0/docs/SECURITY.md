# 🔐 Security Policy — SyckSec

Security is the core mission of SyckSec.  
We take vulnerabilities **seriously** and aim to resolve them quickly and responsibly.

---

## Supported Versions

We actively provide security updates for the following releases:

| Version          | Supported |
| ---------------- | --------- |
| SyckSec 2.x      | ✅        |
| SyckSec 1.x      | ❌ (upgrade required) |

---

## Reporting a Vulnerability

If you believe you have found a **security vulnerability** in SyckSec:

1. **Do not** open a public GitHub issue.
2. **Privately** email our security team at:

📧 **security@sycksec.com**  

3. Include in your email:
   - A clear description of the vulnerability  
   - Steps to reproduce the issue  
   - Your environment (OS, Python version, SyckSec version)  
   - Any possible fixes or recommendations you have  

4. Encrypt sensitive details using our PGP key:  
```

\-----BEGIN PGP PUBLIC KEY BLOCK-----
\[Your PGP public key here]
\-----END PGP PUBLIC KEY BLOCK-----

```

---

## Disclosure Policy

- We will acknowledge receipt of your report within **48 hours**.
- We will provide an initial assessment within **5 business days**.
- We will work with you to confirm the issue and develop a fix.
- We aim to release patches within **14 days** of confirmation, depending on severity.
- We will publicly disclose the vulnerability after:
- A fix is released  
- Users have had reasonable time to update  
- Or after **90 days** from initial report, whichever comes first

---

## Scope of Coverage

This policy applies to:

- The SyckSec **core library**
- Official SyckSec **CLI tools**
- SyckSec **SaaS backend** and official integrations

This policy does **not** cover:

- Third-party plugins or forks  
- Unofficial builds not distributed via `pip install sycksec` or our official Docker images

---

## Bounty Program

Currently, we do not offer monetary bug bounties.  
However, **all researchers will receive public credit** in our security advisories and the SyckSec Hall of Fame.

---

_Thank you for helping us make SyckSec safer for everyone._
