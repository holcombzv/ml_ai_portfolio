document.getElementById("checkButton").addEventListener("click", () => {
  const text = document.getElementById("inputText").value;

  if (!text.trim()) {
    document.getElementById("result").innerText = "Please enter some text.";
    return;
  }

  // Simulate fake prediction result for now
  const fakeScore = Math.random(); // placeholder
  document.getElementById("result").innerText = 
    `Score: ${(fakeScore).toFixed(1)}%`;
    `Verdict: Real`;
});
