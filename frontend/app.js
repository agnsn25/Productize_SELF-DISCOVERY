// ============================================================
// SELF-DISCOVER Playground — Frontend Logic
// ============================================================

const API_BASE = "";

// ---- DOM refs ----
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ---- Tab switching ----
$$(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    $$(".tab").forEach((b) => b.classList.remove("active"));
    $$(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    const panel = $(`#tab-${btn.dataset.tab}`);
    panel.classList.add("active");

    // Load structures when switching to solve/compare/structures
    if (btn.dataset.tab === "solve") loadStructures("solve-structure-select");
    if (btn.dataset.tab === "compare") loadStructures("compare-structure-select");
    if (btn.dataset.tab === "structures") loadStructuresList();
  });
});

// ---- Quick-fill pills ----
$$(".pill[data-fill]").forEach((pill) => {
  pill.addEventListener("click", () => {
    const target = $(`#${pill.dataset.fill}`);
    if (target) target.value = pill.dataset.value;
  });
});

// ---- Collapsible sections (delegated so it works for dynamically-shown panels) ----
document.addEventListener("click", (e) => {
  const header = e.target.closest(".collapsible");
  if (!header) return;
  if (e.target.closest(".btn-copy")) return;
  header.classList.toggle("open");
  const target = $(`#${header.dataset.target}`);
  if (target) target.classList.toggle("expanded");
});

// ---- Copy to clipboard ----
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("btn-copy")) {
    let text = "";
    if (e.target.dataset.copyTarget) {
      text = $(`#${e.target.dataset.copyTarget}`).textContent;
    } else if (e.target.dataset.copyBlock) {
      text = $(`#${e.target.dataset.copyBlock} code`).textContent;
    }
    if (text) {
      navigator.clipboard.writeText(text).then(() => {
        e.target.classList.add("copied");
        const orig = e.target.textContent;
        e.target.textContent = "Copied!";
        setTimeout(() => {
          e.target.classList.remove("copied");
          e.target.textContent = orig;
        }, 1500);
      });
    }
  }
});

// ============================================================
// Helpers
// ============================================================

function showLoading(btn) {
  btn.disabled = true;
  btn._origHTML = btn.innerHTML;
  btn.innerHTML = `<span class="spinner"></span> Working...`;
}

function hideLoading(btn) {
  btn.disabled = false;
  btn.innerHTML = btn._origHTML || btn.textContent;
}

let errorTimer;
function showError(msg) {
  const el = $("#global-error");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(errorTimer);
  errorTimer = setTimeout(() => el.classList.add("hidden"), 5000);
}

function formatJSON(obj) {
  try {
    if (typeof obj === "string") obj = JSON.parse(obj);
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

// Basic markdown-lite: bold, inline code, newlines
function renderMarkdown(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`(.+?)`/g, '<code style="background:var(--bg-input);padding:0.1em 0.35em;border-radius:3px;font-size:0.88em;">$1</code>')
    .replace(/\n/g, "<br>");
}

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    let msg;
    try {
      msg = JSON.parse(body).detail || body;
    } catch {
      msg = body;
    }
    throw new Error(msg || `Request failed (${res.status})`);
  }
  return res.json();
}

function renderList(ulEl, items) {
  ulEl.innerHTML = "";
  if (!items || !items.length) {
    ulEl.innerHTML = "<li>None</li>";
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = renderMarkdown(typeof item === "string" ? item : JSON.stringify(item));
    ulEl.appendChild(li);
  });
}

// ============================================================
// Structures dropdown loader
// ============================================================

async function loadStructures(selectId) {
  const sel = $(`#${selectId}`);
  try {
    const structures = await apiFetch("/api/structures");
    const currentVal = sel.value;
    sel.innerHTML = '<option value="">-- Select a structure --</option>';
    structures.forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s.id;
      const desc =
        s.task_description.length > 70
          ? s.task_description.slice(0, 70) + "..."
          : s.task_description;
      const date = s.created_at
        ? ` (${new Date(s.created_at).toLocaleDateString()})`
        : "";
      opt.textContent = `${desc}${date}`;
      sel.appendChild(opt);
    });
    if (currentVal) sel.value = currentVal;
  } catch (err) {
    showError("Failed to load structures: " + err.message);
  }
}

// Refresh buttons
$("#btn-refresh-solve").addEventListener("click", () =>
  loadStructures("solve-structure-select")
);
$("#btn-refresh-compare").addEventListener("click", () =>
  loadStructures("compare-structure-select")
);

// ============================================================
// DISCOVER TAB
// ============================================================

$("#btn-discover").addEventListener("click", async () => {
  const task = $("#discover-task").value.trim();
  if (!task) {
    showError("Please enter a task description.");
    return;
  }

  const btn = $("#btn-discover");
  showLoading(btn);
  $("#discover-results").classList.add("hidden");

  try {
    const data = await apiFetch("/api/discover", {
      method: "POST",
      body: JSON.stringify({ task_description: task }),
    });

    // Structure ID
    $("#discover-structure-id").textContent = data.id;

    // Selected modules
    renderList(
      $("#discover-selected-modules"),
      data.selected_modules
    );

    // Adapted modules
    renderList(
      $("#discover-adapted-modules"),
      data.adapted_modules
    );

    // Reasoning structure JSON
    const jsonEl = $("#discover-structure-json code");
    jsonEl.textContent = formatJSON(data.reasoning_structure);

    // Thinking traces
    const thinkEl = $("#discover-thinking");
    if (data.thinking_traces) {
      const traces =
        typeof data.thinking_traces === "string"
          ? data.thinking_traces
          : JSON.stringify(data.thinking_traces, null, 2);
      thinkEl.textContent = traces;
    } else {
      thinkEl.textContent = "No thinking traces available.";
    }

    $("#discover-results").classList.remove("hidden");
  } catch (err) {
    showError("Discovery failed: " + err.message);
  } finally {
    hideLoading(btn);
  }
});

// ============================================================
// SOLVE TAB
// ============================================================

$("#btn-solve").addEventListener("click", async () => {
  const structureId = $("#solve-structure-select").value;
  const problem = $("#solve-problem").value.trim();

  if (!structureId) {
    showError("Please select a reasoning structure.");
    return;
  }
  if (!problem) {
    showError("Please enter a problem to solve.");
    return;
  }

  const btn = $("#btn-solve");
  showLoading(btn);
  $("#solve-results").classList.add("hidden");

  try {
    const data = await apiFetch("/api/infer", {
      method: "POST",
      body: JSON.stringify({ structure_id: structureId, problem }),
    });

    // Reasoning trace
    $("#solve-reasoning").innerHTML = renderMarkdown(
      data.reasoning_trace || "No reasoning trace returned."
    );

    // Answer
    $("#solve-answer").innerHTML = renderMarkdown(
      data.answer || "No answer returned."
    );

    // Thinking trace
    const thinkEl = $("#solve-thinking");
    if (data.thinking_trace) {
      thinkEl.textContent =
        typeof data.thinking_trace === "string"
          ? data.thinking_trace
          : JSON.stringify(data.thinking_trace, null, 2);
    } else {
      thinkEl.textContent = "No thinking trace available.";
    }

    $("#solve-results").classList.remove("hidden");
  } catch (err) {
    showError("Solve failed: " + err.message);
  } finally {
    hideLoading(btn);
  }
});

// ============================================================
// COMPARE TAB
// ============================================================

$("#btn-compare").addEventListener("click", async () => {
  const structureId = $("#compare-structure-select").value;
  const problem = $("#compare-problem").value.trim();

  if (!structureId) {
    showError("Please select a reasoning structure.");
    return;
  }
  if (!problem) {
    showError("Please enter a problem to compare.");
    return;
  }

  const btn = $("#btn-compare");
  showLoading(btn);
  $("#compare-results").classList.add("hidden");

  try {
    const data = await apiFetch("/api/infer/compare", {
      method: "POST",
      body: JSON.stringify({ structure_id: structureId, problem }),
    });

    // Naive
    $("#compare-naive-reasoning").innerHTML = renderMarkdown(
      data.naive?.reasoning || "No reasoning returned."
    );
    $("#compare-naive-answer").innerHTML = renderMarkdown(
      data.naive?.answer || "No answer returned."
    );

    // SELF-DISCOVER
    $("#compare-sd-reasoning").innerHTML = renderMarkdown(
      data.self_discover?.reasoning_trace || "No reasoning trace returned."
    );
    $("#compare-sd-answer").innerHTML = renderMarkdown(
      data.self_discover?.answer || "No answer returned."
    );

    // Cost cards
    renderCostCards(data.token_usage);

    // Scale projections
    if (data.scale_projections && data.token_usage) {
      window._compareData = data;
      updateProjections(100);
      const slider = $("#projection-slider");
      slider.value = 100;
      $("#projection-count").textContent = "100";
      slider.oninput = () => {
        const n = parseInt(slider.value);
        $("#projection-count").textContent = n;
        updateProjections(n);
      };
    }

    // Thinking traces
    const thinkEl = $("#compare-thinking");
    if (data.thinking_traces) {
      thinkEl.textContent =
        typeof data.thinking_traces === "string"
          ? data.thinking_traces
          : JSON.stringify(data.thinking_traces, null, 2);
    } else {
      thinkEl.textContent = "No thinking traces available.";
    }

    $("#compare-results").classList.remove("hidden");
  } catch (err) {
    showError("Compare failed: " + err.message);
  } finally {
    hideLoading(btn);
  }
});

// ============================================================
// STRUCTURES TAB
// ============================================================

async function loadStructuresList() {
  const container = $("#structures-list");
  try {
    const structures = await apiFetch("/api/structures");
    if (!structures.length) {
      container.innerHTML =
        '<div class="structures-empty">No structures found. Go to the Discover tab to create one.</div>';
      return;
    }
    container.innerHTML = structures
      .map(
        (s) => `
      <div class="structure-item" data-id="${s.id}">
        <div class="structure-item-header">
          <span class="structure-item-arrow">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
          </span>
          <div class="structure-item-info">
            <div class="structure-item-task">${s.task_description}</div>
            <div class="structure-item-meta">
              <span class="structure-item-id">${s.id.slice(0, 8)}...</span>
              <span>${s.created_at ? new Date(s.created_at).toLocaleDateString() : ""}</span>
            </div>
          </div>
        </div>
        <div class="structure-item-detail">
          <div class="structure-detail-inner">
            <div class="structures-loading" style="text-align:center;padding:20px;color:var(--text-muted);">Loading details...</div>
          </div>
        </div>
      </div>`
      )
      .join("");

    // Attach click handlers
    container.querySelectorAll(".structure-item-header").forEach((header) => {
      header.addEventListener("click", () => {
        const item = header.closest(".structure-item");
        const wasOpen = item.classList.contains("open");
        item.classList.toggle("open");
        if (!wasOpen && !item.dataset.loaded) {
          loadStructureDetail(item);
        }
      });
    });
  } catch (err) {
    showError("Failed to load structures: " + err.message);
  }
}

async function loadStructureDetail(item) {
  const id = item.dataset.id;
  const inner = item.querySelector(".structure-detail-inner");
  try {
    const s = await apiFetch(`/api/structures/${id}`);
    item.dataset.loaded = "true";

    const selectedHtml = (s.selected_modules || [])
      .map((m) => `<li>${renderMarkdown(m)}</li>`)
      .join("");

    const adaptedHtml = (s.adapted_modules || [])
      .map((m) => `<li>${renderMarkdown(m)}</li>`)
      .join("");

    const structureJson = formatJSON(s.reasoning_structure);

    inner.innerHTML = `
      <div class="detail-section">
        <h4>Selected Modules</h4>
        <ul>${selectedHtml || "<li>None</li>"}</ul>
      </div>
      <div class="detail-section">
        <h4>Adapted Modules</h4>
        <ul>${adaptedHtml || "<li>None</li>"}</ul>
      </div>
      <div class="detail-section">
        <h4>Reasoning Structure</h4>
        <pre><code>${structureJson.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</code></pre>
      </div>
      <div class="structure-detail-actions">
        <button class="btn-use-structure" data-use-id="${id}" data-use-tab="solve">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48 2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48 2.83-2.83"/></svg>
          Use in Solve
        </button>
        <button class="btn-use-structure" data-use-id="${id}" data-use-tab="compare">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
          Use in Compare
        </button>
      </div>
    `;

    // Attach "Use in" button handlers
    inner.querySelectorAll(".btn-use-structure").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const targetTab = btn.dataset.useTab;
        const structId = btn.dataset.useId;

        // Switch to target tab
        $$(".tab").forEach((t) => t.classList.remove("active"));
        $$(".tab-panel").forEach((p) => p.classList.remove("active"));
        const tabBtn = document.querySelector(`.tab[data-tab="${targetTab}"]`);
        tabBtn.classList.add("active");
        $(`#tab-${targetTab}`).classList.add("active");

        // Load structures dropdown and select this one
        const selectId = targetTab === "solve" ? "solve-structure-select" : "compare-structure-select";
        await loadStructures(selectId);
        $(`#${selectId}`).value = structId;
      });
    });
  } catch (err) {
    inner.innerHTML = `<div style="padding:16px;color:var(--error);">Failed to load details: ${err.message}</div>`;
  }
}

// Refresh button
$("#btn-refresh-structures").addEventListener("click", () => loadStructuresList());

// Also auto-load when the tab is first shown (in case tab click handler misses it)
const structuresObserver = new MutationObserver(() => {
  const panel = $("#tab-structures");
  if (panel.classList.contains("active") && !panel.dataset.loaded) {
    panel.dataset.loaded = "true";
    loadStructuresList();
  }
});
structuresObserver.observe($("#tab-structures"), { attributes: true, attributeFilter: ["class"] });

// ============================================================
// COST TRACKING
// ============================================================

function fmtCost(usd) {
  if (usd == null) return "N/A";
  if (usd < 0.01) return "$" + usd.toFixed(6);
  return "$" + usd.toFixed(4);
}

function fmtTokens(n) {
  if (n == null || n === 0) return "0";
  if (n >= 1000) return (n / 1000).toFixed(1) + "k";
  return String(n);
}

function renderCostCards(tokenUsage) {
  const container = $("#compare-cost-cards");
  if (!tokenUsage) {
    container.innerHTML = "";
    return;
  }

  const cards = [
    {
      label: "Naive (1 pass)",
      accent: "var(--naive-accent)",
      data: tokenUsage.naive,
    },
    {
      label: "SD Inference Only",
      accent: "var(--sd-accent)",
      data: tokenUsage.sd_inference_only,
    },
    {
      label: "SD Full (discovery + inference)",
      accent: "var(--g-blue)",
      data: tokenUsage.sd_full,
    },
  ];

  container.innerHTML = cards
    .map(
      (c) => `
    <div class="cost-card" style="border-top: 3px solid ${c.accent}">
      <div class="cost-card-label">${c.label}</div>
      <div class="cost-card-cost">${fmtCost(c.data?.cost_usd)}</div>
      <div class="cost-card-tokens">
        <span>In: ${fmtTokens(c.data?.input_tokens)}</span>
        <span>Out: ${fmtTokens(c.data?.output_tokens)}</span>
        <span>Think: ${fmtTokens(c.data?.thinking_tokens)}</span>
      </div>
    </div>`
    )
    .join("");
}

function updateProjections(n) {
  const data = window._compareData;
  if (!data || !data.token_usage) return;

  const naive = data.token_usage.naive;
  const sdInf = data.token_usage.sd_inference_only;
  const sdFull = data.token_usage.sd_full;
  const k = data.cot_sc_passes || 20;

  const naiveCost = n * (naive?.cost_usd || 0);
  const cotScCost = n * k * (naive?.cost_usd || 0);
  const sdInfCost = n * (sdInf?.cost_usd || 0);
  const sdFullCost =
    sdFull?.discovery_cost_usd != null
      ? sdFull.discovery_cost_usd + n * (sdInf?.cost_usd || 0)
      : null;

  const rows = [
    { name: "Naive", calls: n, cost: naiveCost },
    { name: `CoT-SC (${k} passes)`, calls: n * k, cost: cotScCost },
    {
      name: "SD Full",
      calls: sdFullCost != null ? 3 + n : "N/A",
      cost: sdFullCost,
    },
    { name: "SD Inference Only", calls: n, cost: sdInfCost },
  ];

  const tbody = $("#projection-table tbody");
  tbody.innerHTML = rows
    .map((r) => {
      const savings =
        r.cost != null && cotScCost > 0
          ? ((1 - r.cost / cotScCost) * 100).toFixed(1) + "%"
          : "N/A";
      return `<tr>
        <td>${r.name}</td>
        <td>${typeof r.calls === "number" ? r.calls.toLocaleString() : r.calls}</td>
        <td>${fmtCost(r.cost)}</td>
        <td>${savings}</td>
      </tr>`;
    })
    .join("");

  const maxCost = Math.max(
    naiveCost,
    cotScCost,
    sdFullCost || 0,
    sdInfCost
  );
  const barData = [
    { name: "Naive", cost: naiveCost, color: "var(--naive-accent)" },
    { name: "CoT-SC", cost: cotScCost, color: "var(--error)" },
    { name: "SD Full", cost: sdFullCost, color: "var(--g-blue)" },
    { name: "SD Inf", cost: sdInfCost, color: "var(--sd-accent)" },
  ];

  const chart = $("#projection-bar-chart");
  chart.innerHTML = barData
    .map((b) => {
      const pct =
        b.cost != null && maxCost > 0
          ? Math.max((b.cost / maxCost) * 100, 1)
          : 0;
      return `
      <div class="bar-row">
        <span class="bar-label">${b.name}</span>
        <div class="bar-track">
          <div class="bar-fill" style="width:${pct}%;background:${b.color}"></div>
        </div>
        <span class="bar-value">${fmtCost(b.cost)}</span>
      </div>`;
    })
    .join("");
}
