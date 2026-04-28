// ── Reports ──
function todayISO() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 10);
}

function nowLocalDateTime() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
}

function initReportDates() {
  const today = todayISO();
  const reportDate = document.getElementById('report-date');
  const lookupDate = document.getElementById('lookup-report-date');
  const emotionDate = document.getElementById('emotion-report-date');
  const emotionTimestamp = document.getElementById('emotion-timestamp');
  if (reportDate && !reportDate.value) reportDate.value = today;
  if (lookupDate && !lookupDate.value) lookupDate.value = today;
  if (emotionDate && !emotionDate.value) emotionDate.value = today;
  if (emotionTimestamp && !emotionTimestamp.value) emotionTimestamp.value = nowLocalDateTime();
}

function resetReportForm() {
  document.getElementById('report-form').reset();
  initReportDates();
}

function resetEmotionForm() {
  document.getElementById('emotion-form').reset();
  const emotionDate = document.getElementById('emotion-report-date');
  const reportDate = document.getElementById('report-date');
  emotionDate.value = reportDate.value || todayISO();
  document.getElementById('emotion-timestamp').value = nowLocalDateTime();
}

function reportPayloadFromForm() {
  return {
    report_date: document.getElementById('report-date').value,
    water_intake: Number(document.getElementById('water-intake').value),
    food_intake: Number(document.getElementById('food-intake').value),
    weight: Number(document.getElementById('report-weight').value),
    short_message: document.getElementById('short-message').value.trim()
  };
}

function apiErrorMessage(detail) {
  if (Array.isArray(detail)) return detail.map(item => item.msg).join(', ');
  return detail || 'Request failed';
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }[char]));
}

function formatMetric(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(1) : '--';
}

function parseTagDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function formatTagTime(value) {
  const date = parseTagDate(value);
  if (!date) return String(value ?? '').replace('T', ' ');
  return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

function formatTagDate(value) {
  const date = parseTagDate(value);
  if (!date) return '';
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function voiceTagsHtml(voiceTags) {
  const entries = Object.entries(voiceTags || {})
    .sort(([a], [b]) => String(a).localeCompare(String(b)));

  if (!entries.length) return '';

  const rows = entries.map(([timestamp, tag], index) => `
    <div class="emotion-row">
      <div class="emotion-time">
        ${escapeHtml(formatTagTime(timestamp))}
        <span class="emotion-date">${escapeHtml(formatTagDate(timestamp))}</span>
      </div>
      <div class="emotion-marker"></div>
      <div class="emotion-card">
        <strong>${escapeHtml(tag)}</strong>
        <span>Entry ${index + 1} · ${escapeHtml(String(timestamp).replace('T', ' '))}</span>
      </div>
    </div>
  `).join('');

  return `
    <div class="report-tags">
      <h5>Emotion Timeline</h5>
      <div class="emotion-chart">${rows}</div>
    </div>
  `;
}

function displayReport(report) {
  const result = document.getElementById('report-result');
  if (!report) {
    result.className = 'report-result empty';
    result.textContent = 'No report selected';
    return;
  }

  result.className = 'report-result';
  const message = report.short_message?.trim() || 'No notes recorded.';
  const tags = voiceTagsHtml(report.voice_tags);
  result.innerHTML = `
    <div class="report-result-header">
      <div>
        <h4>Mochi Daily Report</h4>
        <span>${escapeHtml(report.report_date)}</span>
      </div>
      <span>Saved</span>
    </div>
    <div class="report-metrics">
      <div class="report-metric"><span>Water</span><strong>${formatMetric(report.water_intake)} ml</strong></div>
      <div class="report-metric"><span>Food</span><strong>${formatMetric(report.food_intake)} g</strong></div>
      <div class="report-metric"><span>Weight</span><strong>${formatMetric(report.weight)} kg</strong></div>
    </div>
    <p class="report-message">${escapeHtml(message)}</p>
    ${tags}
  `;
}

function displayVoiceTagsOnly(reportDate, voiceTags) {
  const result = document.getElementById('report-result');
  result.className = 'report-result';
  result.innerHTML = `
    <div class="report-result-header">
      <div>
        <h4>Emotion Tags</h4>
        <span>${escapeHtml(reportDate)}</span>
      </div>
      <span>No daily report</span>
    </div>
    ${voiceTagsHtml(voiceTags) || '<p class="report-message">No emotion tags recorded.</p>'}
  `;
}

async function submitReport(event) {
  event.preventDefault();

  const payload = reportPayloadFromForm();
  if (!payload.report_date || [payload.water_intake, payload.food_intake, payload.weight].some(Number.isNaN)) {
    toast('Complete all report fields', '⚠️');
    return;
  }

  const btn = document.getElementById('save-report-btn');
  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    const res = await fetch('/api/reports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(apiErrorMessage(data.detail));

    document.getElementById('lookup-report-date').value = payload.report_date;
    document.getElementById('emotion-report-date').value = payload.report_date;
    displayReport(data.report);
    toast('Report saved', '✓');
  } catch (err) {
    toast(err.message || 'Failed to save report', '⚠️');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save Report';
  }
}

async function submitEmotionTag(event) {
  event.preventDefault();

  const reportDate = document.getElementById('emotion-report-date').value || document.getElementById('report-date').value;
  const timestamp = document.getElementById('emotion-timestamp').value;
  const voiceType = document.getElementById('emotion-tag').value.trim();

  if (!reportDate || !timestamp || !voiceType) {
    toast('Complete the emotion tag fields', '⚠️');
    return;
  }

  const btn = document.getElementById('save-emotion-btn');
  btn.disabled = true;
  btn.textContent = 'Adding...';

  try {
    const res = await fetch(`/api/reports/${encodeURIComponent(reportDate)}/voice-tags`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ timestamp, voice_type: voiceType })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(apiErrorMessage(data.detail));

    document.getElementById('lookup-report-date').value = reportDate;
    if (data.report) displayReport(data.report);
    else displayVoiceTagsOnly(reportDate, data.voice_tags);

    document.getElementById('emotion-tag').value = '';
    document.getElementById('emotion-timestamp').value = nowLocalDateTime();
    toast('Emotion tag saved', '✓');
  } catch (err) {
    toast(err.message || 'Failed to save emotion tag', '⚠️');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Add Tag';
  }
}

async function loadReport() {
  const date = document.getElementById('lookup-report-date').value || document.getElementById('report-date').value;
  if (!date) {
    toast('Choose a report date', '⚠️');
    return;
  }

  document.getElementById('emotion-report-date').value = date;

  try {
    const res = await fetch(`/api/reports/${encodeURIComponent(date)}`);
    const data = await res.json().catch(() => ({}));

    if (res.status === 404) {
      const result = document.getElementById('report-result');
      result.className = 'report-result empty';
      result.textContent = 'No report found for this date';
      return;
    }
    if (!res.ok) throw new Error(apiErrorMessage(data.detail));

    displayReport(data.report);
    toast('Report loaded', '✓');
  } catch (err) {
    toast(err.message || 'Failed to load report', '⚠️');
  }
}

initReportDates();

