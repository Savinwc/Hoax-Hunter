// HTML canvas element where the chart will be drawn
const canvas = document.getElementById('polarchart');

// Data for the chart
const data = {
  labels: ['January', 'February', 'March', 'April', 'May'],
  datasets: [{
    label: 'Sales',
    data: [12, 19, 3, 5, 21],
    backgroundColor: [
      'rgba(255, 99, 132, 0.2)',
      'rgba(54, 162, 235, 0.2)',
      'rgba(255, 206, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(153, 102, 255, 0.2)'
    ],
    borderColor: [
      'rgba(255, 99, 132, 1)',
      'rgba(54, 162, 235, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)'
    ],
    borderWidth: 1
  }]
};

// Options for the chart
const options = {
  scale: {
    ticks: {
      beginAtZero: true
    }
  },
  plugins: {
    datalabels: {
      color: 'black',
      font: {
        weight: 'bold'
      },
      formatter: function(value, context) {
        return value;
      }
    }
  }
};

// Create the chart
const polarAreaChart = new Chart(canvas, {
  type: 'polarArea',
  data: data,
  options: options
});