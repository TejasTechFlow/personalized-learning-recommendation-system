fetch('/api/progress-data').then(r => r.json()).then(d => {
  const colors = ['#22c55e', '#6c4cf1', '#cfcde0'];
  new Chart(c1, {type: 'doughnut', data: {labels: ['Completed', 'In progress', 'Not started'], datasets: [{data: d.doughnut, backgroundColor: colors}]}});
  new Chart(c2, {type: 'bar', data: {labels: d.weekly.labels, datasets: [{label: 'Hours', data: d.weekly.hours, backgroundColor: '#ff4f9a', borderRadius: 8}]}, options: {plugins: {legend: {display: false}}}});
  new Chart(c3, {type: 'bar', data: {labels: d.skills.labels, datasets: [{label: 'Skill %', data: d.skills.values, backgroundColor: '#6c4cf1', borderRadius: 8}]}, options: {scales: {y: {max: 100, beginAtZero: true}}, plugins: {legend: {display: false}}}});
  document.getElementById('overall').textContent = d.overall + '%';
  document.getElementById('hrs').textContent = d.hours + ' hours studied · ' + d.completed + ' courses completed';
});
