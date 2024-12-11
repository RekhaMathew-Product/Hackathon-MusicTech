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
const state = "rest"; // Change to 'rest', 'stress', 'exercise', etc.
let simulationInterval = null; // To store the interval ID

// Function to update heart rate visuals in real-time
function updateHR() {
  const bpm = generateHR(state);
  hrData.push(bpm);

  // Update the BPM display
  document.getElementById("bpm").innerText = `BPM: ${bpm}`;
}

// Function to start the simulation
function startSimulation() {
  document.getElementById("bpm").style.display = "block";

  if (!simulationInterval) {
    simulationInterval = setInterval(updateHR, 1000);
  }
}

// Add event listener to the start button
document.getElementById("start-hr-analysis").addEventListener("click", () => {
  if (!simulationInterval) {
    startSimulation();
  }
});
