// Function to generate random heart rate based on the state
function generateHR(state) {
  let hr;
  switch (state) {
    case "rest":
      hr = Math.floor(Math.random() * (80 - 60)) + 60; // Rest = 60–80 bpm
      break;
    case "low stress":
      hr = Math.floor(Math.random() * (100 - 80)) + 80; // Low stress = 80-100
      break;
    case "medium stress":
      hr = Math.floor(Math.random() * (120 - 100)) + 100; // Medium Stress = 100-120
      break;
    case "high stress":
      hr = Math.floor(Math.random() * (150 - 120)) + 120; // High Stress = 120-150
      break;

      hr = Math.floor(Math.random() * (120 - 80 + 1)) + 80; // Stress range (80-120 BPM)
    // Add variability spikes to simulate fluctuations (±10 BPM)
    // let variabilitySpike = Math.floor(Math.random() * 20) - 10; // Spikes within a range of ±10 BPM
    // hr += variabilitySpike;
    // Clamp the heart rate within the 80-120 BPM range
    // hr = Math.max(80, Math.min(120, hr));
    // break;
    // case "moderate intensity exercise":
    //   hr = Math.floor(Math.random() * (160 - 120 + 1)) + 120; // Moderate Exercise range (120-160 BPM)
    //   break;
    // case "high intensity exercise":
    //   hr = Math.floor(Math.random() * (200 - 160 + 1)) + 160; // High-Intensity Exercise range (160-200 BPM)
    //   break;
    default:
      hr = 70; // Default resting HR if no state matches
  }
  return hr;
}

let hrData = [];
const duration = 180;
state = "rest"; // Change to 'rest', 'stress', 'exercise', etc.
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
      y: { title: { display: true, text: "BPM" }, min: 50, max: 150 },
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

  // Update the voice signal visuals
  updateVoiceSignal(bpm);
}

// Function to start the simulation
function startSimulation() {
  // Display the elements
  document.getElementById("whitebg").style.display = "block";
  document.getElementById("whitebg2").style.display = "block";
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

function updateVoiceSignal(bpm) {
  const voiceSignal = document.getElementById("voiceSignal");
  voiceSignal.innerHTML = ""; // Clear existing waves

  const waveCount = 10; // Number of waves
  const intensity = bpm > 120 ? 1.5 : bpm > 80 ? 1.2 : 1.0; // Adjust wave height multiplier

  for (let i = 0; i < waveCount; i++) {
    const wave = document.createElement("div");
    const height = Math.random() * 100 * intensity + 20; // Random height with intensity factor

    wave.style.height = `${height}px`;
    wave.style.animationDelay = `${i * 0.1}s`;

    // Set gradient color based on BPM
    if (bpm >= 60 && bpm < 80) {
      wave.style.background =
        "linear-gradient(180deg, #00ffcc,rgb(38, 255, 0))";
    } else if (bpm >= 80 && bpm < 100) {
      wave.style.background =
        "linear-gradient(180deg,rgb(17, 0, 255),rgb(0, 221, 255))";
    } else if (bpm >= 100 && bpm < 120) {
      wave.style.background =
        "linear-gradient(180deg,rgb(255, 140, 0),rgb(255, 98, 0))";
    } else if (bpm >= 120) {
      wave.style.background =
        "linear-gradient(180deg,rgb(255, 0, 132), #ff0000)";
    }

    voiceSignal.appendChild(wave);
  }
}

// Add event listener to the stop button
document.getElementById("stop-hr-analysis").addEventListener("click", () => {
  stopSimulation();
});

// document.getElementById("state-selector").addEventListener("change", (e) => {
//   state = e.target.value;
//   if (!simulationInterval) {
//     startSimulation(); // Start simulation if not already running
//   }
// });

document.getElementById("state-selector").addEventListener("change", (e) => {
  state = e.target.value;

  // Check if a valid state is selected
  if (state !== "-") {
    // Send the selected state to the backend
    fetch("http://127.0.0.1:5000/state", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ state: state }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data.message); // Log confirmation message from the server
      })
      .catch((error) => {
        console.error("Error updating state:", error); // Handle error
      });
  }

  // Check if simulation is already running; if not, start it
  // if (!simulationInterval) {
  //   startSimulation(); // Start simulation if it's not already running
  // }
});
startSimulation();
