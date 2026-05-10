const DASHBOARD_DATA_URL = `${import.meta.env.BASE_URL}demo_results.json`;

const numberFormat = new Intl.NumberFormat('en-US');
const percentFormat = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 0,
  style: 'percent',
});

const fieldFormatters = {
  total_documents: (value) => numberFormat.format(value),
  auto_export_count: (value) => numberFormat.format(value),
  auto_export_rate: (value) => percentFormat.format(value),
  human_review_count: (value) => numberFormat.format(value),
  blocked_count: (value) => numberFormat.format(value),
  average_confidence: (value) => percentFormat.format(value),
  average_risk_score: (value) => Number(value).toFixed(1),
  review_ratio: (_value, summary) => `${summary.human_review_count} / ${summary.total_documents}`,
  review_caption: (_value, summary) => `${summary.blocked_count} blocked · avg risk ${Number(summary.average_risk_score).toFixed(1)}`,
};

function formatField(field, summary) {
  const formatter = fieldFormatters[field];
  return formatter ? formatter(summary[field], summary) : summary[field];
}

function humanizeRule(rule) {
  return rule.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function updateSummaryFields(summary) {
  document.querySelectorAll('[data-engine-field]').forEach((element) => {
    const field = element.dataset.engineField;

    if (field in fieldFormatters || summary[field] !== undefined) {
      element.textContent = formatField(field, summary);
    }
  });
}

function createProgressItem({ label, meta, value, width, fillClass, itemClass, nameClass, valueClass, trackClass, fillBaseClass }) {
  const item = document.createElement('div');
  item.className = itemClass;

  const content = document.createElement('div');
  const top = document.createElement('div');
  top.className = itemClass === 'sla-item' ? 'sla-top' : '';

  const name = document.createElement('div');
  name.className = nameClass;
  name.textContent = label;

  const valueNode = document.createElement('div');
  valueNode.className = valueClass;
  valueNode.textContent = value;

  if (itemClass === 'sla-item') {
    top.append(name, valueNode);
    content.append(top);
  } else {
    const metaNode = document.createElement('div');
    metaNode.className = 'reason-meta';
    metaNode.textContent = meta;
    content.append(name, metaNode);
  }

  const track = document.createElement('div');
  track.className = trackClass;

  const fill = document.createElement('div');
  fill.className = [fillBaseClass, fillClass].filter(Boolean).join(' ');
  fill.style.width = `${width}%`;
  track.append(fill);
  content.append(track);

  if (itemClass === 'sla-item') {
    item.append(content);
  } else {
    item.append(content, valueNode);
  }

  return item;
}

function renderRouteDistribution(summary) {
  const list = document.querySelector('[data-engine-routes]');
  if (!list || !summary.route_distribution) return;

  list.replaceChildren(...Object.entries(summary.route_distribution).map(([route, count]) => {
    const share = summary.total_documents ? Math.round((count / summary.total_documents) * 100) : 0;

    return createProgressItem({
      label: route,
      value: numberFormat.format(count),
      width: share,
      itemClass: 'sla-item',
      nameClass: 'sla-name',
      valueClass: 'sla-value',
      trackClass: 'sla-track',
      fillBaseClass: 'sla-fill',
    });
  }));
}

function renderValidationIssues(summary) {
  const list = document.querySelector('[data-engine-validation-issues]');
  if (!list || !Array.isArray(summary.top_validation_issues)) return;

  const maxCount = Math.max(...summary.top_validation_issues.map((issue) => issue.count), 1);
  const items = summary.top_validation_issues.map((issue, index) => {
    const width = Math.max(12, Math.round((issue.count / maxCount) * 100));
    const fillClass = index === 0 ? 'danger' : index < 3 ? 'warn' : '';

    return createProgressItem({
      label: humanizeRule(issue.rule),
      meta: `Validation issue found in ${issue.count} documents`,
      value: numberFormat.format(issue.count),
      width,
      fillClass,
      itemClass: 'reason-row',
      nameClass: 'reason-name',
      valueClass: 'reason-value',
      trackClass: 'reason-track',
      fillBaseClass: 'reason-fill',
    });
  });

  list.replaceChildren(...items);
}

export async function loadDashboardData() {
  try {
    const response = await fetch(DASHBOARD_DATA_URL, { cache: 'no-cache' });
    if (!response.ok) return;

    const data = await response.json();
    const summary = data.batch_summary;
    if (!summary) return;

    updateSummaryFields(summary);
    renderRouteDistribution(summary);
    renderValidationIssues(summary);
  } catch {
    // Keep the polished static dashboard intact when the JSON copy is unavailable.
  }
}
