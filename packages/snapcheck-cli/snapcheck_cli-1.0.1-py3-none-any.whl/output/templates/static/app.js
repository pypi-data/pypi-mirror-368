// output/templates/static/app.js
document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ SnapCheck UI Loaded");

  // --------------------------
  // BRAND & META
  // --------------------------
  document.title = "SnapCheck — Audit Report";
  // inject favicon if missing
  (function ensureFavicon() {
    if (!document.querySelector('link[rel="icon"], link[rel="shortcut icon"]')) {
      const link = document.createElement("link");
      link.rel = "icon";
      link.href = "/static/logo.png";
      document.head.appendChild(link);
    }
  })();

  // --------------------------
  // THEME TOGGLE (persists)
  // --------------------------
  const themeToggle = document.getElementById("toggleTheme");
  const setTheme = (t) => {
    document.documentElement.classList.toggle("dark", t === "dark");
    localStorage.setItem("snap_theme", t);
  };
  setTheme(localStorage.getItem("snap_theme") || "light");
  if (themeToggle) {
    themeToggle.addEventListener("click", () =>
      setTheme(document.documentElement.classList.contains("dark") ? "light" : "dark")
    );
  }

  // --------------------------
  // PRINT CSS (for nice PDFs)
  // --------------------------
  (function injectPrintCSS() {
    const css = `
      @media print {
        .sc-header, [data-action="toggle"], #toggleTheme { display: none !important; }
        body { background: #fff !important; color: #000 !important; }
        .sc-card { break-inside: avoid; border-color: #ccc !important; }
        .sc-kpi { box-shadow: none !important; }
        canvas { max-height: 200px !important; }
      }
    `;
    const style = document.createElement("style");
    style.type = "text/css";
    style.media = "print";
    style.appendChild(document.createTextNode(css));
    document.head.appendChild(style);
  })();

  // --------------------------
  // KPI CLICK → SCROLL (with keyboard)
  // --------------------------
  document.querySelectorAll("[data-scroll-to]").forEach((btn) => {
    // keyboard
    btn.tabIndex = 0;
    btn.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        btn.click();
      }
    });
    // click
    btn.addEventListener("click", () => {
      const target = btn.dataset.scrollTo;
      const el = document.querySelector(`[data-plugin="${target}"]`);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // --------------------------
  // COLLAPSE / EXPAND PER PLUGIN (aria-friendly)
  // --------------------------
  document.querySelectorAll("section[data-plugin]").forEach((section, idx) => {
    const toggleBtn = section.querySelector("[data-action='toggle']");
    const body = section.querySelector("[data-body]");
    if (toggleBtn && body) {
      const bodyId = body.id || `plugin-body-${idx}`;
      body.id = bodyId;
      toggleBtn.setAttribute("aria-controls", bodyId);
      toggleBtn.setAttribute("aria-expanded", "true");
      toggleBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const hidden = body.classList.toggle("hidden");
        toggleBtn.textContent = hidden ? "Expand" : "Collapse";
        toggleBtn.setAttribute("aria-expanded", hidden ? "false" : "true");
      });
    }
  });

  // --------------------------
  // PERSIST HELPERS
  // --------------------------
  const LSK = {
    search: "snap_search",
    sev: "snap_sev_filters",
    plugins: "snap_plugin_filters",
  };
  const save = (k, v) => localStorage.setItem(k, JSON.stringify(v));
  const load = (k, fallback) => {
    try { return JSON.parse(localStorage.getItem(k)) ?? fallback; }
    catch { return fallback; }
  };

  // --------------------------
  // SEARCH (persists)
  // --------------------------
  const searchInput = document.getElementById("search");
  const applySearch = () => {
    const term = (searchInput?.value || "").toLowerCase();
    document.querySelectorAll("section[data-plugin]").forEach((section) => {
      const text = section.innerText.toLowerCase();
      section.style.display = text.includes(term) ? "" : "none";
    });
    save(LSK.search, searchInput?.value || "");
  };
  if (searchInput) {
    const prev = load(LSK.search, "");
    if (prev) {
      searchInput.value = prev;
      applySearch();
    }
    searchInput.addEventListener("input", applySearch);
  }

  // --------------------------
  // FILTERS (severity + plugin) with persistence
  // --------------------------
  function applyFilters() {
    const selectedSev = Array.from(document.querySelectorAll(".severity-filter:checked")).map((c) => c.value);
    const selectedPlugins = Array.from(document.querySelectorAll(".plugin-filter:checked")).map((c) => c.value);

    document.querySelectorAll("section[data-plugin]").forEach((section) => {
      const plugin = section.dataset.plugin;
      const status = section.dataset.status;
      const matchesSev = selectedSev.length === 0 || selectedSev.includes(status);
      const matchesPlugin = selectedPlugins.length === 0 || selectedPlugins.includes(plugin);
      section.style.display = matchesSev && matchesPlugin ? "" : "none";
    });

    save(LSK.sev, selectedSev);
    save(LSK.plugins, selectedPlugins);
  }

  // restore persisted filter state
  (function restoreFilters() {
    const sevPrev = load(LSK.sev, null);
    const plugPrev = load(LSK.plugins, null);
    if (sevPrev) {
      document.querySelectorAll(".severity-filter").forEach((c) => {
        c.checked = sevPrev.includes(c.value);
      });
    }
    if (plugPrev) {
      document.querySelectorAll(".plugin-filter").forEach((c) => {
        c.checked = plugPrev.includes(c.value);
      });
    }
    applyFilters();
  })();

  document.querySelectorAll(".severity-filter").forEach((chk) => chk.addEventListener("change", applyFilters));
  document.querySelectorAll(".plugin-filter").forEach((chk) => chk.addEventListener("change", applyFilters));

  // --------------------------
  // FINDING SEVERITY STYLING (soft backgrounds)
  // --------------------------
  document.querySelectorAll("[data-severity]").forEach((el) => {
    const sev = el.dataset.severity;
    if (sev === "PASS") el.classList.add("border-green-400", "bg-green-50");
    if (sev === "WARN") el.classList.add("border-yellow-400", "bg-yellow-50");
    if (sev === "FAIL") el.classList.add("border-red-400", "bg-red-50");
    if (sev === "INFO") el.classList.add("border-blue-400", "bg-blue-50");
  });

  // Subtle hover on KPI tiles
  document.querySelectorAll("[data-kpi]").forEach((kpi) => {
    kpi.classList.add("transition", "hover:scale-105", "hover:shadow-lg");
  });

  // --------------------------
  // EMPTY STATE CARDS
  // --------------------------
  (function addEmptyStates() {
    document.querySelectorAll("section[data-plugin]").forEach((section) => {
      const body = section.querySelector("[data-body]");
      if (!body) return;
      const hasFindings = body.querySelectorAll(".finding").length > 0;
      if (!hasFindings) {
        const empty = document.createElement("div");
        empty.className = "border rounded-xl p-4 text-sm opacity-70";
        empty.textContent = "No issues found.";
        body.appendChild(empty);
      }
    });
  })();

  // --------------------------
  // EXPORT JSON (no backend)
  // --------------------------
  (function wireExportJSON() {
    const btn = Array.from(document.querySelectorAll('a.sc-btn-primary, button.sc-btn-primary'))
      .find(el => /export json/i.test(el.textContent || ""));
    if (!btn) return;

    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const report = collectReportData();
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      const ts = new Date().toISOString().split("T")[0];
      a.href = url;
      a.download = `snapcheck-report-${ts}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });

    function collectReportData() {
      // KPIs
      const kpis = Array.from(document.querySelectorAll("[data-kpi]")).map((el) => ({
        key: el.dataset.kpi,
        label: el.querySelector("div:first-child")?.textContent?.trim() || "",
        value: el.querySelector("div:nth-child(2)")?.textContent?.trim() || "",
      }));

      // Plugins
      const plugins = {};
      document.querySelectorAll('section[data-plugin]:not([data-plugin="correlation"])').forEach((sec) => {
        const plugin = sec.dataset.plugin;
        const status = sec.dataset.status;
        const findings = Array.from(sec.querySelectorAll(".finding")).map((f) => ({
          title: f.querySelector("strong")?.textContent?.trim() || "",
          severity: f.dataset.severity || "",
          message: f.querySelector("p")?.textContent?.trim() || "",
        }));
        plugins[plugin] = { status, findings };
      });

      // Correlation
      let correlation = [];
      const corr = document.querySelector('section[data-plugin="correlation"] [data-body]');
      if (corr) {
        correlation = Array.from(corr.querySelectorAll(".finding")).map((f) => ({
          title: f.querySelector("strong")?.textContent?.trim() || "",
          severity: f.dataset.severity || "",
          message: f.querySelector("p")?.textContent?.trim() || "",
        }));
      }

      return {
        generated_at: new Date().toISOString(),
        title: document.title,
        kpis,
        plugins,
        correlation,
      };
    }
  })();

  // --------------------------
  // CHARTS (Lazy-loaded via IntersectionObserver)
  // --------------------------
  const BRAND = { accent: "#ffbb34" }; // Snap Yellow

  function withBrandColors(cfg) {
    const copy = JSON.parse(JSON.stringify(cfg || {}));
    (copy.datasets || []).forEach((ds) => {
      if (!ds.borderColor) ds.borderColor = BRAND.accent;
      if (!ds.backgroundColor) ds.backgroundColor = BRAND.accent + "33"; // alpha
      if ((copy.type || "line") === "line") {
        if (ds.fill === undefined) ds.fill = false;
        if (!ds.tension) ds.tension = 0.25;
      }
    });
    return copy;
  }

  function addSkeleton(el) {
    if (!el) return;
    el.parentElement?.classList.add("relative");
    const sk = document.createElement("div");
    sk.className =
      "chart-skeleton absolute inset-0 animate-pulse rounded-xl";
    sk.style.background =
      "linear-gradient(90deg, rgba(0,0,0,0.06), rgba(0,0,0,0.02), rgba(0,0,0,0.06))";
    el.parentElement.appendChild(sk);
  }

  function removeSkeleton(el) {
    const sk = el?.parentElement?.querySelector(".chart-skeleton");
    if (sk) sk.remove();
  }

  function renderChartById(canvasId, chartCfg) {
    const el = document.getElementById(canvasId);
    if (!el || !chartCfg || typeof Chart === "undefined") return;
    const cfg = withBrandColors(chartCfg);
    new Chart(el.getContext("2d"), {
      type: cfg.type || "line",
      data: { labels: cfg.labels || [], datasets: cfg.datasets || [] },
      options: Object.assign(
        {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: true } },
          interaction: { mode: "index", intersect: false },
          scales: { x: { grid: { display: false } }, y: { grid: { color: "rgba(0,0,0,.05)" } } },
        },
        cfg.options || {}
      ),
    });
  }

  function lazyInitCharts() {
    if (!window.SNAPCHECK_CHARTS || typeof Chart === "undefined") return;

    // Collect canvases and map each to its config
    const map = new Map();

    // Global
    if (window.SNAPCHECK_CHARTS.cost) {
      const id = "chart-cost";
      const el = document.getElementById(id);
      if (el) {
        map.set(el, window.SNAPCHECK_CHARTS.cost);
        addSkeleton(el);
      }
    }

    // Per-plugin
    if (window.SNAPCHECK_CHARTS.per_plugin) {
      Object.entries(window.SNAPCHECK_CHARTS.per_plugin).forEach(([plugin, cfg]) => {
        const id = `chart-${plugin}`;
        const el = document.getElementById(id);
        if (el) {
          map.set(el, cfg);
          addSkeleton(el);
        }
      });
    }

    // Legacy: any charts keyed by canvas id
    Object.entries(window.SNAPCHECK_CHARTS).forEach(([key, cfg]) => {
      if (key === "cost" || key === "per_plugin") return;
      const el = document.getElementById(key);
      if (el) {
        map.set(el, cfg);
        addSkeleton(el);
      }
    });

    if (map.size === 0) return;

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            const cfg = map.get(el);
            if (cfg) {
              renderChartById(el.id, cfg);
              removeSkeleton(el);
              map.delete(el);
              io.unobserve(el);
            }
          }
        });
      },
      { rootMargin: "0px 0px 200px 0px", threshold: 0.1 }
    );

    map.forEach((_, el) => io.observe(el));
  }

  lazyInitCharts();
});