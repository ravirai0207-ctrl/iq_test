# 🧠 Luminary NeuroIQ — 3D Standardized Cognitive Engine

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fravirai0207-ctrl%2FIq-test)

An advanced, light-themed 3D animated web platform that conducts standardized psychometric IQ assessments with real-time Three.js graphics, 100% live server question feeds, demographic calibration, and persistent cloud/local backend storage.

---

## 🌐 Live Deployment & Links

- **GitHub Repository**: [https://github.com/ravirai0207-ctrl/Iq-test](https://github.com/ravirai0207-ctrl/Iq-test)
- **1-Click Vercel Deploy**: [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fravirai0207-ctrl%2FIq-test)

---

## ✨ Features

- **Luminous 3D Animated Background**:
  - Built with **Three.js** featuring a continuous undulating 3D iridescent silk wave mesh, floating prismatic crystal polyhedrons, and pastel particle constellations.
  - Interactive cursor parallax tracking with real-time vertex rippling.
  - Category-aware ambient light shifting (indigo for patterns, sky cyan for numerical, violet for spatial, amber for logic, and coral rose for speed).

- **100% Live Question Server Feed**:
  - Assessment items are dynamically pulled live from global online question servers (e.g. **Open Trivia Database API** with tens of thousands of questions across Science, Mathematics, Technology, Computational Logic, Nature, and General Knowledge).
  - Every test session is unique — zero hardcoded questions!

- **Frictionless Direct Registration (NO OTP)**:
  - Simply enter Name & Age (with optional email) to immediately launch into calibration.
  - Candidate details and active test questions are securely persisted in SQLite.

- **Standardized Psychometric Standardization**:
  - Standardized psychometric formula ($\mu = 100, \sigma = 15$) calibrated across demographic age baselines.
  - High-DPI Gaussian population bell curve on HTML5 Canvas highlighting candidate's exact percentile ranking.
  - 5-domain cognitive metric breakdown with animated completion bars.
  - Official, high-resolution **Certificate of Cognitive Assessment** ready to print or save to PDF with clean `@media print` layout.

- **Vercel Cloud Ready**:
  - `vercel.json` edge routing configuration.
  - Serverless Python 3 runtime in `api/index.py` with `/tmp/iq_test.db` persistence.
  - Global edge CDN distribution for static assets in `public/`.

---

## 🚀 Local Run

```bash
python3 server.py
```
Visit: **[http://localhost:8000](http://localhost:8000)**
