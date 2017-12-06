var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
var LABELS = [ "Fingerprint", "User Agent", "Accept", "Accept Encoding", "Accept Language", "Plugins", "Screen resolution", "Platform", "Hardware Concurrency", "Html Canvas Data", "Webgl Vendor", "Webgl Renderer", "Audio Sample Rate", "Audio Base Latency", "Fonts Available", "logged in to"]
var DATA = JSON.parse(getData()).map(val => parseInt(val));

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
    backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),
    borderColor: window.chartColors.blue,
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

var port = document.domain == "localhost" ? 5000 : 80;

var socket = io.connect('http://' + document.domain + ':' + port + '/data');
socket.on('response', function(msg) {
  barChartData.datasets[0].data = JSON.parse(msg.data);
  window.myBar.update();
});
