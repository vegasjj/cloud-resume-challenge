document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#resume-summarizer-form");
    const textarea = document.querySelector("#resume-text-input");
    const button = document.querySelector("#summarize-btn");
    const resultContainer = document.querySelector("#summary-result");
    const charCounter = document.querySelector("#char-counter");
    
    const MAX_LENGTH = 100000;
    const REQUEST_TIMEOUT_MS = 30000;
    const API_ENDPOINT = typeof APIM_CONFIG !== "undefined" ? APIM_CONFIG.API_ENDPOINT : "";
    const APIM_SUBSCRIPTION_KEY = typeof APIM_CONFIG !== "undefined" ? APIM_CONFIG.SUBSCRIPTION_KEY : "";

    if (!form || !textarea || !button || !resultContainer || !charCounter) {
        return;
    }

    const setStatus = (message, className = "summary-error") => {
        const p = document.createElement("p");
        p.className = className;
        p.textContent = message;
        resultContainer.replaceChildren(p);
    };

    textarea.addEventListener("input", () => {
        const remaining = MAX_LENGTH - textarea.value.length;
        charCounter.textContent = `${remaining.toLocaleString()} characters remaining`;
        charCounter.style.color = remaining < 500 ? "#c0392b" : "#999";
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (!APIM_SUBSCRIPTION_KEY) {
            setStatus("The app cannot communicate with the summarizer. Please contact support.");
            return;
        }

        const resumeText = textarea.value.trim();
        if (!resumeText) {
            setStatus("Please enter your resume text.");
            return;
        }

        if (resumeText.length > MAX_LENGTH) {
            setStatus(`Resume text exceeds maximum allowed length of ${MAX_LENGTH.toLocaleString()} characters.`);
            return;
        }

        button.disabled = true;
        button.textContent = "Summarizing...";
        setStatus("Analyzing your resume...", "summary-loading");

        try {
            const response = await fetch(API_ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Ocp-Apim-Subscription-Key": APIM_SUBSCRIPTION_KEY,
                },
                body: JSON.stringify({ resume_text: resumeText }),
                signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
            });

            const contentType = response.headers.get("content-type") || "";
            const rawText = await response.text();
            let data = null;

            if (contentType.includes("application/json")) {
                try {
                    data = JSON.parse(rawText);
                } catch {
                    // Fall back to null if JSON parsing fails
                }
            }

            if (response.status === 405) {
                setStatus("Invalid request. Please try again");
                return;
            }

            if (response.status === 429) {
                setStatus("Too many requests. Please wait a moment and try again.");
                return;
            }

            if (response.status === 413) {
                setStatus("Your resume text is too long. Please shorten it and try again.");
                return;
            }

            if (!response.ok) {
                const errorDetail = data?.message || rawText || "Unknown server error";
                throw new Error(`Status: ${response.status}. Detail: ${errorDetail}`);
            }

            if (data?.summary) {
                const content = document.createElement("div");
                const heading = document.createElement("h3");
                const summary = document.createElement("p");

                content.className = "summary-content";
                heading.textContent = "Summary";
                summary.textContent = data.summary;

                content.append(heading, summary);
                resultContainer.replaceChildren(content);
            } else {
                setStatus("No summary was returned. Please try again.");
            }
        } catch (error) {
            console.error("Resume summarizer error:", error);

            if (error.name === "TimeoutError" || error.name === "AbortError") {
                setStatus("The request timed out. Please try again.");
            } else {
                setStatus("An error occurred while summarizing. Please try again later.");
            }
        } finally {
            button.disabled = false;
            button.textContent = "Summarize";
        }
    });
});