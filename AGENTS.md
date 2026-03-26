## Learned User Preferences
- Prefers global environment variable management over per-workspace `.env` files when possible.

## Learned Workspace Facts
- The project uses `SPEC.md` phase-gate tracking, and the Power BI proof artifact path is `screenshots/powerbi_dashboard.png`.
- **Fabric / M365 billing sanity (gozeroshot.dev — `alynch@gozeroshot.dev`):** Check licenses at [Microsoft 365 My account → Subscriptions](https://portal.office.com/account) — expect **Microsoft Fabric (Free)** (+ Purview Discovery, Exchange Foundation, Power BI free); org tenant view often has **no payment methods section**. Trial countdown + **Cancel trials** live in [Microsoft Fabric](https://app.fabric.microsoft.com/) → profile. **Azure CLI** for this user: ARM lists **0 subscriptions** (tenant-only context) — no PAYG sub to bill via Azure RM.
