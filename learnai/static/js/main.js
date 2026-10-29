const csrf = document.querySelector('meta[name=csrf-token]').content;
async function post(url, body = {}) {
  const r = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf}, body: JSON.stringify(body)});
  const d = await r.json();
  if (!r.ok) alert(d.error || 'Something went wrong. Please try again.');
  return d;
}
// Live "You may also be interested in..." suggestions
const box = document.getElementById('interests');
if (box) {
  const render = async () => {
    const sel = [...box.querySelectorAll('input:checked')].map(i => 'i=' + encodeURIComponent(i.value)).join('&');
    const out = document.getElementById('suggest');
    const list = sel ? await (await fetch('/api/suggest?' + sel)).json() : [];
    out.innerHTML = list.length ? 'You may also be interested in: ' + list.map(t => `<button type="button" class="btn btn-sm btn-outline-primary me-1" data-add="${t}">+ ${t}</button>`).join('') : '';
  };
  box.addEventListener('change', render);
  document.getElementById('suggest').addEventListener('click', e => {
    const t = e.target.dataset.add; if (!t) return;
    [...box.querySelectorAll('input')].find(i => i.value === t).checked = true; render();
  });
  document.querySelectorAll('.skill-range').forEach(r => r.addEventListener('input', () => r.previousElementSibling.querySelector('.sv').textContent = r.value));
  render();
}
document.addEventListener('click', async e => {
  const b = e.target.closest('[data-start],[data-addpath],.rate'); if (!b) return;
  if (b.classList.contains('rate')) { e.preventDefault(); const d = await post('/api/feedback/' + b.dataset.cid, {rating: +b.dataset.r}); if (d.ok) b.parentElement.textContent = 'Thanks for your rating!'; return; }
  if (b.dataset.addpath) { const d = await post('/api/path/' + b.dataset.addpath); if (d.ok) { b.textContent = 'In learning path'; b.disabled = true; } return; }
  const d = await post('/api/progress/' + b.dataset.start, {step: 25});
  if (d.pct !== undefined) location.href = '/learning-path';
});
