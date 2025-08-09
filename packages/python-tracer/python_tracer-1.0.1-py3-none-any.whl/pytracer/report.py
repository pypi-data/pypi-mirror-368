import json, html, os, textwrap
from pathlib import Path

_template = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>pytracer - Execution Report</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial; margin: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; font-size: 13px; }
    th { background: #f7f7f7; text-align: left; }
    tr:nth-child(even){ background: #fafafa; }
    .exc { background: #ffecec; }
    .summary { margin-bottom: 20px; }
    .mono { font-family: monospace; font-size: 12px; white-space: pre-wrap; }
    .badge { display:inline-block; padding:4px 8px; border-radius:8px; background:#eee; margin-right:6px; font-size:12px; }
  </style>
</head>
<body>
  <h1>pytracer - Execution Report</h1>
  <div class="summary">
    <span class="badge">Generated: <strong id="generated_at"></strong></span>
    <span class="badge">Total calls: <strong id="total_calls"></strong></span>
    <span class="badge">Total time (ms): <strong id="total_time"></strong></span>
    <span class="badge">Exceptions: <strong id="exceptions_count"></strong></span>
  </div>

  <h2>Function summary</h2>
  <div id="byfn"></div>

  <h2>All events</h2>
  <table id="events_table">
    <thead>
      <tr>
        <th>#</th><th>Func</th><th>Start (UTC)</th><th>Duration (ms)</th><th>Parent</th><th>Thread</th><th>Exception</th><th>Traceback</th>
      </tr>
    </thead>
    <tbody id="events_body"></tbody>
  </table>

<script>
const data = DATA_JSON_REPLACE;

document.getElementById('generated_at').textContent = data.generated_at;
document.getElementById('total_calls').textContent = data.summary.total_calls;
document.getElementById('total_time').textContent = data.summary.total_time_ms.toFixed(3);
document.getElementById('exceptions_count').textContent = data.summary.exceptions_count;

(function renderByFn(){ 
  const container = document.getElementById('byfn');
  const arr = data.summary.by_function;
  if(!arr.length){ container.textContent = 'No functions recorded'; return; }
  let html = '<table><thead><tr><th>Function</th><th>Count</th><th>Total ms</th><th>Max ms</th></tr></thead><tbody>';
  for(const r of arr){
    html += `<tr><td>${r.func}</td><td>${r.count}</td><td>${r.total_ms.toFixed(3)}</td><td>${r.max_ms.toFixed(3)}</td></tr>`;
  }
  html += '</tbody></table>';
  container.innerHTML = html;
})();

(function renderEvents(){
  const body = document.getElementById('events_body');
  const events = data.events;
  let html = '';
  for(const e of events){
    const exc = e.exception ? e.exception : '';
    const rowClass = e.exception ? 'exc' : '';
    html += `<tr class="${rowClass}">`;
    html += `<td>${e.id}</td>`;
    html += `<td>${e.func}</td>`;
    html += `<td>${e.start_time}</td>`;
    html += `<td>${(e.duration_ms||0).toFixed(3)}</td>`;
    html += `<td>${e.parent_id||''}</td>`;
    html += `<td>${e.thread_id}</td>`;
    html += `<td>${exc}</td>`;
    html += `<td><div class="mono">${e.traceback||''}</div></td>`;
    html += `</tr>`;
  }
  body.innerHTML = html;
})();
</script>
</body>
</html>
"""

def generate_html_report(monitor, out_path):
    """embed snapshot into an HTML file and write to out_path"""
    s = json.dumps(monitor.snapshot())
    html_content = _template.replace('DATA_JSON_REPLACE', s)
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html_content, encoding='utf8')
    return str(p.resolve())
