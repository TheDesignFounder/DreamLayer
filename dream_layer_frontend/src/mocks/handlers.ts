import { http, HttpResponse } from "msw";

let currentProgress = 0;
let isRunning = false;

export const handlers = [
  // Mock progress endpoint
  http.get("/queue/progress", () => {
    if (!isRunning && currentProgress === 0) {
      // Start simulation
      isRunning = true;
      simulateProgress();
    }

    return HttpResponse.json({
      percent: currentProgress,
      status: currentProgress < 100 ? "processing" : "complete",
      message:
        currentProgress < 25
          ? "Initializing..."
          : currentProgress < 50
          ? "Processing..."
          : currentProgress < 75
          ? "Generating..."
          : currentProgress < 100
          ? "Finalizing..."
          : "Complete!",
    });
  }),

  // Reset progress for testing
  http.post("/queue/reset", () => {
    currentProgress = 0;
    isRunning = false;
    return HttpResponse.json({ success: true });
  }),
];

function simulateProgress() {
  const interval = setInterval(() => {
    if (currentProgress < 100) {
      // Simulate realistic progress increments
      const increment = Math.random() * 15 + 5; // 5-20% increments
      currentProgress = Math.min(100, currentProgress + increment);
    } else {
      clearInterval(interval);
      isRunning = false;
      // Reset after completion for next test
      setTimeout(() => {
        currentProgress = 0;
      }, 2000);
    }
  }, 800); // Update every 800ms to simulate real work
}
