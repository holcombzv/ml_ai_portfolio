chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "fakeNewsCheck",
    title: "Check Fake News",
    contexts: ["page"] // show on right-click anywhere on the page
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  console.log("Menu clicked:", info);

  if (info.menuItemId === "fakeNewsCheck") {
    // Inject script to grab full HTML of the page
    chrome.scripting.executeScript(
      {
        target: { tabId: tab.id },
        func: () => document.documentElement.outerHTML
      },
      (results) => {
        const html = results?.[0]?.result;

        if (!html) {
          chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: (msg) => alert(msg),
            args: ["Could not retrieve page HTML."]
          });
          return;
        }

        fetch("https://holcombzv-fake-news-detection-api.hf.space/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: html })
        })
          .then((res) => {
            if (!res.ok) {
              throw new Error(`API responded with status ${res.status}`);
            }
            return res.json();
          })
          .then((data) => {
            if (!data || typeof data.score !== "number" || !data.label) {
              throw new Error("Invalid response format from API");
            }

            chrome.scripting.executeScript({
              target: { tabId: tab.id },
              func: (score, label) => {
                alert(
                  `Score: ${(score * 100).toFixed(1)}%\nVerdict: ${label}`
                );
              },
              args: [data.score, data.label]
            });
          })
          .catch((err) => {
            console.error("API error:", err.message);
            chrome.scripting.executeScript({
              target: { tabId: tab.id },
              func: (msg) => alert("Fake News Check failed:\n" + msg),
              args: [err.message]
            });
          });
      }
    );
  }
});
