"""
A minimalist line plotting package for live updates from jupyter notebooks. Works on google colab.

Example:

from lineplot import LinePlot
import numpy as np
import time

plot = LinePlot('green', 'blue')
for i in range(100):
    plot.add(loss=1 / (i + 1), acc=1 - np.random.rand() / (i + 1))
    time.sleep(0.25)
"""

__version__ = "0.1.5"

from IPython.display import display, HTML, Javascript
import random, json

class LinePlot:
    def __init__(self, *colors):
      """Instanciates a new line plot. A color needs to be provided for each metric."""
      if colors == []:
        colors = ['red', 'green', 'blue', 'gold', 'magenta', 'cyan']
      self.id = random.randint(1, 10000000)
      display(HTML(f"""
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<div style="width: 50%">
  <canvas id="chart{self.id}"></canvas>
</div>
"""))
      display(Javascript(f"""
function f() {{
  const ctx = document.getElementById('chart{self.id}').getContext('2d');
  window.chart{self.id} = new Chart(ctx, {{
      type: 'line',
      data: {{
        labels: [],
        datasets: []
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: true,
        animation: false,
      }}
    }});

  const mapping = {{}};
  const colors = {json.dumps(colors)};

  window.chart_add{self.id} = function(metrics) {{
    const chart = window.chart{self.id};
    chart.data.labels.push(chart.data.labels.length);
    for (const [key, value] of Object.entries(metrics)) {{
      if (mapping[key] === undefined) {{
        mapping[key] = chart.data.datasets.length;
        chart.data.datasets.push({{
          label: key,
          data: [value],
          borderWidth: 1,
          borderColor: colors[mapping[key] % colors.length],
          backgroundColor: colors[mapping[key] % colors.length],
          pointStyle: false,
        }});
      }} else {{
        chart.data.datasets[mapping[key]].data.push(value);
      }}
    }}
    chart.update();
  }}
}}
f();
"""))
      self.script = display(HTML('<script></script>'), display_id=True)

    def add(self, **metrics):
      """Adds metrics to the plot, specified as named arguments"""
      self.script.update(Javascript(f'''chart_add{self.id}({json.dumps(metrics)});'''))

