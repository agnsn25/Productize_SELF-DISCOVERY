// ============================================================
// Pricing Calculator — Interactive margin & savings calculator
// ============================================================

const COGS_DISCOVERY = 0.284;   // Our cost per discovery call (USD)
const COGS_INFERENCE = 0.037;   // Our cost per inference call (USD)
const COGS_COT_SINGLE = 0.02;  // Cost of a single CoT call (USD)

const $ = (sel) => document.querySelector(sel);

// Input elements
const inputs = {
  discoveryPrice: $("#calc-discovery-price"),
  inferencePrice: $("#calc-inference-price"),
  structures:     $("#calc-structures"),
  queries:        $("#calc-queries"),
  cotScPasses:    $("#calc-cot-sc-passes"),
};

function fmtUsd(n) {
  if (n >= 1000) return "$" + n.toLocaleString("en-US", { minimumFractionDigits: 0, maximumFractionDigits: 0 });
  if (n >= 100) return "$" + n.toFixed(0);
  if (n >= 1) return "$" + n.toFixed(2);
  return "$" + n.toFixed(4);
}

function recalculate() {
  const discoveryPrice = parseFloat(inputs.discoveryPrice.value) || 0;
  const inferencePrice = parseFloat(inputs.inferencePrice.value) || 0;
  const structures     = parseInt(inputs.structures.value) || 0;
  const queriesPerStruct = parseInt(inputs.queries.value) || 0;
  const cotScPasses    = parseInt(inputs.cotScPasses.value) || 20;

  const totalQueries = structures * queriesPerStruct;

  // Revenue
  const discoveryRevenue = structures * discoveryPrice;
  const inferenceRevenue = totalQueries * inferencePrice;
  const totalRevenue = discoveryRevenue + inferenceRevenue;

  // COGS
  const discoveryCogs = structures * COGS_DISCOVERY;
  const inferenceCogs = totalQueries * COGS_INFERENCE;
  const totalCogs = discoveryCogs + inferenceCogs;

  // Profit & margin
  const grossProfit = totalRevenue - totalCogs;
  const grossMargin = totalRevenue > 0 ? (grossProfit / totalRevenue) * 100 : 0;

  // Update result cards
  $("#calc-revenue").textContent = fmtUsd(totalRevenue);
  $("#calc-cogs").textContent = fmtUsd(totalCogs);
  $("#calc-profit").textContent = fmtUsd(grossProfit);
  $("#calc-margin").textContent = grossMargin.toFixed(1) + "%";

  // Customer savings
  const customerCost = totalRevenue; // what they pay us
  const cotScCostPerQuery = cotScPasses * COGS_COT_SINGLE;
  const cotScCost = totalQueries * cotScCostPerQuery;
  const savings = cotScCost - customerCost;
  const savingsPct = cotScCost > 0 ? (savings / cotScCost) * 100 : 0;

  $("#calc-customer-cost").textContent = fmtUsd(customerCost);
  $("#calc-cotsc-cost").textContent = fmtUsd(cotScCost);
  $("#calc-savings").textContent = fmtUsd(Math.max(0, savings));
  $("#calc-savings-pct").textContent = `(${savingsPct.toFixed(0)}% cheaper)`;

  // Update legend
  $("#legend-passes").textContent = cotScPasses;

  // Scale chart
  renderScaleChart(discoveryPrice, inferencePrice, cotScPasses);
}

function renderScaleChart(discoveryPrice, inferencePrice, cotScPasses) {
  const steps = [1, 10, 50, 100, 500, 1000];
  const cotScPerQuery = cotScPasses * COGS_COT_SINGLE;

  const data = steps.map((n) => ({
    n,
    cotSc:   n * cotScPerQuery,
    sdFull:  discoveryPrice + n * inferencePrice,
    sdInf:   n * inferencePrice,
  }));

  const maxCost = Math.max(...data.map((d) => Math.max(d.cotSc, d.sdFull)));

  const chart = $("#scale-chart");
  chart.innerHTML = data.map((d) => {
    const cotScPct = maxCost > 0 ? (d.cotSc / maxCost) * 100 : 0;
    const sdFullPct = maxCost > 0 ? (d.sdFull / maxCost) * 100 : 0;
    const sdInfPct = maxCost > 0 ? (d.sdInf / maxCost) * 100 : 0;

    return `
      <div class="scale-row">
        <span class="scale-label">${d.n} queries</span>
        <div class="scale-bars">
          <div class="scale-bar" style="width:${Math.max(cotScPct, 0.5)}%;background:var(--error);"></div>
          <div class="scale-bar" style="width:${Math.max(sdFullPct, 0.5)}%;background:var(--g-blue);"></div>
          <div class="scale-bar" style="width:${Math.max(sdInfPct, 0.5)}%;background:var(--g-green);"></div>
        </div>
        <span class="scale-value">${fmtUsd(d.cotSc)} / ${fmtUsd(d.sdFull)}</span>
      </div>`;
  }).join("");
}

// Attach listeners
Object.values(inputs).forEach((input) => {
  input.addEventListener("input", recalculate);
});

// Initial calculation
recalculate();
