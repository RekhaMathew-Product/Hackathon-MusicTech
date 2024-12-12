// Function to generate random heart rate based on the state
function generateHR(state) {
  let hr;
  switch (state) {
    case "rest":
      hr = Math.floor(Math.random() * (80 - 60 + 1)) + 60; // Resting range (60-80 BPM)
      break;
    case "low intensity exercise":
      // Mild Activity range (80-120 BPM)
      hr = Math.floor(Math.random() * (120 - 80 + 1)) + 80;
      break;
    case "stress":
      // Stress range with added variability (80-120 BPM, with spikes)
      hr = Math.floor(Math.random() * (120 - 80 + 1)) + 80; // Stress range (80-120 BPM)
      // Add variability spikes to simulate fluctuations (±10 BPM)
      let variabilitySpike = Math.floor(Math.random() * 20) - 10; // Spikes within a range of ±10 BPM
      hr += variabilitySpike;
      // Clamp the heart rate within the 80-120 BPM range
      hr = Math.max(80, Math.min(120, hr));
      break;
    case "moderate intensity exercise":
      hr = Math.floor(Math.random() * (160 - 120 + 1)) + 120; // Moderate Exercise range (120-160 BPM)
      break;
    case "high intensity exercise":
      hr = Math.floor(Math.random() * (200 - 160 + 1)) + 160; // High-Intensity Exercise range (160-200 BPM)
      break;
    default:
      hr = 70; // Default resting HR if no state matches
  }
  return hr;
}

let hrData = [];
const duration = 120;
// const state = "rest"; // Change to 'rest', 'stress', 'exercise', etc.
let simulationInterval = null; // To store the interval ID

// Chart.js setup
const ctx = document.getElementById("hrChart").getContext("2d");
const hrChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: Array.from({ length: duration }, (_, i) => i + 1), // 1 to 60 seconds
    datasets: [
      {
        label: "Heart Rate (BPM)",
        data: [],
        borderColor: "red",
        borderWidth: 2,
        fill: false,
      },
    ],
  },
  options: {
    responsive: true,
    scales: {
      x: { title: { display: true, text: "Time (s)" } },
      y: { title: { display: true, text: "BPM" }, min: 50, max: 200 },
    },
  },
});

// Function to update the chart with new data
function updateChart(chart, data) {
  chart.data.datasets[0].data = data;
  chart.update();
}

// Function to update heart rate visuals in real-time
function updateHR() {
  const bpm = generateHR(state);
  hrData.push(bpm);

  // Keep only the last 60 seconds of data
  if (hrData.length > duration) {
    hrData.shift();
  }

  // Update the heart animation speed
  const heart = document.getElementById("heart");
  heart.style.animationDuration = `${60 / bpm}s`;

  // Update the BPM display
  document.getElementById("bpm").innerText = `BPM: ${bpm}`;

  // Update the chart
  updateChart(hrChart, hrData);
}

// Function to start the simulation
function startSimulation() {
  // Display the elements
  document.getElementById("heart").style.display = "block";
  document.getElementById("bpm").style.display = "block";
  const hrChart = document.getElementById("hrChart");

  // Add the show-canvas class to make the canvas visible with custom size
  hrChart.style.display = "block"; // Make the canvas visible immediately
  hrChart.classList.add("show-canvas");

  // Restart the heart pulsating animation
  const heart = document.getElementById("heart");
  heart.style.animationPlayState = "running";

  // Start the interval to update HR
  // Start the interval to update HR
  if (!simulationInterval) {
    simulationInterval = setInterval(updateHR, 1000);
  }
}

function stopSimulation() {
  if (simulationInterval) {
    clearInterval(simulationInterval);
    simulationInterval = null;
  }
  // Stop the heart pulsating animation
  const heart = document.getElementById("heart");
  heart.style.animationPlayState = "paused";
}

// Add event listener to the stop button
document.getElementById("stop-hr-analysis").addEventListener("click", () => {
  stopSimulation();
});

document.getElementById("state-selector").addEventListener("change", (e) => {
  state = e.target.value;
  if (!simulationInterval) {
    startSimulation(); // Start simulation if not already running
  }
});
