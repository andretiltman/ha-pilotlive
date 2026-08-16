// PilotLive Graph Card
// Generic column/line chart for any PilotLive report sensor whose `rows`
// attribute holds a series of {label, value} rows (Turnover by Day, Turnover
// by Month, Turnover Comparison, Bill Average, ...). No date format, column
// name, or store is hardcoded — it renders whatever the entity's `rows`
// attribute contains, so the same card works across different stores and
// different reports.
//
// Config:
//   type: custom:pilotlive-graph-card
//   entity: sensor.pilotlive_store_turnover_by_day           (required)
//   title: Valley Brewery                                      (optional, defaults to entity friendly_name)
//   date_field: Date                                            (optional, default "Date")
//   value_field: Sales Incl                                      (optional, default "Sales Incl")
//   chart_type: column                                           (optional, "column" (default) or "line")
//   color: "#2a78d6"                                             (optional)
//   y_prefix: "R "                                               (optional, default "R ")
//   exclude_highlight: ["2"]                                     (optional, default ["2"] — PilotLive marks
//                                                                 subtotal/grand-total rows with highlight "2")
//   max_labels: 10                                               (optional, default 10 — thins x-axis labels
//                                                                 so they don't overlap on wide date ranges)
//
// The x-axis value (date_field) is used as-is for the bar label. If it parses
// as a recognised date shape — "dd/mm/yy(yy)", "yyyy-mm-dd", or "Mon yyyy" —
// rows are sorted chronologically; otherwise rows are left in report order
// (e.g. a report already ranked by period or category name).

const MONTHS = { jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5, jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11 };

class PilotliveGraphCard extends HTMLElement {
  setConfig(config) {
    if (!config.entity) throw new Error("pilotlive-graph-card: 'entity' is required");
    this._config = {
      date_field: "Date",
      value_field: "Sales Incl",
      chart_type: "column",
      color: "#2a78d6",
      y_prefix: "R ",
      exclude_highlight: ["2"],
      max_labels: 10,
      ...config,
    };
    this._root = this._root || this.attachShadow({ mode: "open" });
  }

  getCardSize() {
    return 4;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _parseDate(label) {
    const s = String(label).trim();
    let m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})$/);
    if (m) {
      let [, dd, mm, yy] = m.map(Number);
      if (yy < 100) yy += 2000;
      const d = new Date(yy, mm - 1, dd);
      return isNaN(d.getTime()) ? null : d.getTime();
    }
    m = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
    if (m) {
      const [, yy, mm, dd] = m.map(Number);
      const d = new Date(yy, mm - 1, dd);
      return isNaN(d.getTime()) ? null : d.getTime();
    }
    m = s.match(/^([A-Za-z]{3,9})\.?\s+(\d{4})$/);
    if (m) {
      const mon = MONTHS[m[1].slice(0, 3).toLowerCase()];
      if (mon != null) return new Date(Number(m[2]), mon, 1).getTime();
    }
    return null;
  }

  _render() {
    const cfg = this._config;
    const state = this._hass.states[cfg.entity];
    const root = this._root;

    const rawRows = (state && state.attributes && state.attributes.rows) || null;
    const title = cfg.title || (state && state.attributes.friendly_name) || "Report";

    if (!rawRows) {
      root.innerHTML = this._shell(title, `<div class="empty">No data yet — waiting for the next report refresh.</div>`);
      return;
    }

    let points = rawRows
      .filter((r) => !cfg.exclude_highlight.includes(String(r.highlight)))
      .map((r) => ({
        label: r[cfg.date_field],
        value: parseFloat(String(r[cfg.value_field]).replace(/,/g, "")) || 0,
        sortKey: this._parseDate(r[cfg.date_field]),
      }))
      .filter((p) => p.label != null);

    if (points.every((p) => p.sortKey != null)) {
      points = points.slice().sort((a, b) => a.sortKey - b.sortKey);
    }

    if (!points.length) {
      root.innerHTML = this._shell(title, `<div class="empty">No rows to chart.</div>`);
      return;
    }

    root.innerHTML = this._shell(title, this._chart(points, cfg));
  }

  _chart(points, cfg) {
    const W = 800, H = 320;
    const padL = 64, padR = 16, padT = 16, padB = 44;
    const plotW = W - padL - padR, plotH = H - padT - padB;

    const values = points.map((p) => p.value);
    const maxV = Math.max(0, ...values);
    const minV = Math.min(0, ...values);
    const range = maxV - minV || 1;

    const yFor = (v) => padT + plotH - ((v - minV) / range) * plotH;
    const zeroY = yFor(0);

    const n = points.length;
    const slot = plotW / n;
    const barW = Math.max(2, slot * (cfg.chart_type === "line" ? 0 : 0.6));

    const ticks = 4;
    let gridLines = "", gridLabels = "";
    for (let i = 0; i <= ticks; i++) {
      const v = minV + (range * i) / ticks;
      const y = yFor(v);
      gridLines += `<line x1="${padL}" y1="${y}" x2="${W - padR}" y2="${y}" class="grid" />`;
      gridLabels += `<text x="${padL - 8}" y="${y}" text-anchor="end" dominant-baseline="middle" class="axis-label">${this._fmtAxis(v, cfg.y_prefix)}</text>`;
    }

    let bars = "";
    let linePoints = "";
    points.forEach((p, i) => {
      const cx = padL + slot * i + slot / 2;
      const y = yFor(p.value);
      if (cfg.chart_type === "line") {
        linePoints += `${cx},${y} `;
        bars += `<circle cx="${cx}" cy="${y}" r="3.5" fill="${cfg.color}"><title>${this._esc(p.label)}: ${this._fmtFull(p.value, cfg.y_prefix)}</title></circle>`;
      } else {
        const top = Math.min(y, zeroY);
        const h = Math.max(1, Math.abs(zeroY - y));
        bars += `<rect x="${cx - barW / 2}" y="${top}" width="${barW}" height="${h}" fill="${cfg.color}"><title>${this._esc(p.label)}: ${this._fmtFull(p.value, cfg.y_prefix)}</title></rect>`;
      }
    });
    if (cfg.chart_type === "line") {
      bars = `<polyline points="${linePoints.trim()}" fill="none" stroke="${cfg.color}" stroke-width="2" />` + bars;
    }

    const maxLabels = Math.max(2, cfg.max_labels);
    const step = Math.max(1, Math.ceil(n / maxLabels));
    let xLabels = "";
    points.forEach((p, i) => {
      if (i % step !== 0 && i !== n - 1) return;
      const cx = padL + slot * i + slot / 2;
      xLabels += `<text x="${cx}" y="${H - padB + 18}" text-anchor="middle" class="axis-label">${this._esc(p.label)}</text>`;
    });

    return `
      <svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet" class="chart">
        ${gridLines}
        <line x1="${padL}" y1="${zeroY}" x2="${W - padR}" y2="${zeroY}" class="zero-line" />
        ${bars}
        ${gridLabels}
        ${xLabels}
      </svg>`;
  }

  _shell(title, body) {
    return `
      <style>
        :host { display: block; }
        ha-card { padding: 16px 20px 20px; }
        .title { font-size: 16px; font-weight: 500; color: var(--primary-text-color); margin-bottom: 8px; }
        .chart { width: 100%; height: 260px; display: block; overflow: visible; }
        .grid { stroke: var(--divider-color); stroke-width: 1; }
        .zero-line { stroke: var(--secondary-text-color); stroke-width: 1; }
        .axis-label { font-size: 11px; fill: var(--secondary-text-color); }
        .empty { color: var(--secondary-text-color); font-size: 13px; padding: 8px 0; }
      </style>
      <ha-card>
        <div class="title">${this._esc(title)}</div>
        ${body}
      </ha-card>`;
  }

  _fmtAxis(v, prefix) {
    const abs = Math.abs(v);
    const compact = abs >= 1000 ? (v / 1000).toFixed(1) + "K" : Math.round(v).toLocaleString();
    return `${prefix}${compact}`;
  }

  _fmtFull(v, prefix) {
    return `${prefix}${v.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }

  _esc(s) {
    const div = document.createElement("div");
    div.textContent = String(s);
    return div.innerHTML;
  }

  static getStubConfig() {
    return { entity: "", title: "Report" };
  }
}

customElements.define("pilotlive-graph-card", PilotliveGraphCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "pilotlive-graph-card",
  name: "PilotLive Graph",
  description: "Generic column/line chart from any PilotLive report sensor's rows attribute",
});
