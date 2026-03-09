function createBarChart(canvasId, labels, data, label) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  new Chart(el, {
    type: 'bar',
    data: { labels, datasets: [{ label, data }] },
    options: { responsive: true, maintainAspectRatio: false }
  });
}

function createScatterLikeChart(canvasId, xValues, yValues, labels) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  new Chart(el, {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Étudiants',
        data: xValues.map((x, i) => ({x, y: yValues[i] || 0, label: labels[i]}))
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              const raw = context.raw;
              return `${raw.label}: absences=${raw.x}, moyenne=${raw.y}`;
            }
          }
        }
      },
      scales: {
        x: { title: { display: true, text: 'Nombre d\'absences' } },
        y: { title: { display: true, text: 'Moyenne générale' } }
      }
    }
  });
}
