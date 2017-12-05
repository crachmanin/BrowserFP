var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
var LABELS = [ "Fingerprint", "User Agent", "Accept", "Accept Encoding", "Accept Language", "Plugins", "Screen resolution", "Platform", "Hardware Concurrency", "Html Canvas Data", "Webgl Vendor", "Webgl Renderer", "Audio Sample Rate", "Audio Base Latency", "Fonts Available", "logged in to"]
var DATA = JSON.parse(getData()).map(val => parseInt(val));
console.log(DATA);

function getData() {
  var result = null;
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET", "stats", false);
  xmlhttp.send();
  if (xmlhttp.status==200) {
    result = xmlhttp.responseText;
  }
  return result;
}

var color = Chart.helpers.color;
var barChartData = {
  labels: LABELS,
  datasets: [{
    label : '',
    backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
    borderColor: window.chartColors.red,
    borderWidth: 1,
    data: DATA
  }]
};

window.onload = function() {
  var ctx = document.getElementById("canvas").getContext("2d");
  window.myBar = new Chart(ctx, {
    type: 'bar',
    data: barChartData,
    options: {
      responsive: true,
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Unique Value Counts'
      },
      scales: {
        yAxes: [{
          ticks: {
            min : 0,
            stepSize : 1
          }
        }],
        xAxes: [{
          ticks: {
            autoSkip : false
          }
        }],
      }
    }
  });

};

var colorNames = Object.keys(window.chartColors);
document.getElementById('addDataset').addEventListener('click', function() {
  var colorName = colorNames[barChartData.datasets.length % colorNames.length];;
  var dsColor = window.chartColors[colorName];
  var newDataset = {
    label: 'Dataset ' + barChartData.datasets.length,
    backgroundColor: color(dsColor).alpha(0.5).rgbString(),
    borderColor: dsColor,
    borderWidth: 1,
    data: []
  };

  for (var index = 0; index < barChartData.labels.length; ++index) {
    newDataset.data.push(randomScalingFactor());
  }

  barChartData.datasets.push(newDataset);
  window.myBar.update();
});

document.getElementById('addData').addEventListener('click', function() {
  if (barChartData.datasets.length > 0) {
    var month = MONTHS[barChartData.labels.length % MONTHS.length];
    barChartData.labels.push(month);

    for (var index = 0; index < barChartData.datasets.length; ++index) {
      //window.myBar.addData(randomScalingFactor(), index);
      barChartData.datasets[index].data.push(randomScalingFactor());
    }

    window.myBar.update();
  }
});
