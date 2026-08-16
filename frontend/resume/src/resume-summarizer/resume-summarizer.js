document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("resume-summarizer-form");
    const textarea = document.getElementById("resume-text-input");
    const button = document.getElementById("summarize-btn");
    const resultContainer = document.getElementById("summary-result");
    const charCounter = document.getElementById("char-counter");
    const MAX_LENGTH = 10000;

    // if (!form || !textarea || !button || !resultContainer || !charCounter) {
    //     return;
    // }

    // Character counter
    textarea.addEventListener("input", function () {
        const remaining = MAX_LENGTH - textarea.value.length;
        charCounter.textContent = `${remaining.toLocaleString()} characters remaining`;
        charCounter.style.color = remaining < 500 ? "#c0392b" : "#999";
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const resumeText = textarea.value.trim();
        if (!resumeText) {
            resultContainer.innerHTML =
                '<p class="summary-error">Please enter your resume text.</p>';
            return;
        }

        // Set loading state
        button.disabled = true;
        button.textContent = "Summarizing...";
        resultContainer.innerHTML =
            '<p class="summary-loading">Analyzing your resume...</p>';

        fetch(
            "https://func-crc-prod-001.azurewebsites.net/api/resume_summarizer",
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ resume_text: resumeText }),
            }
        )
            .then(async (response) => {
                const contentType = response.headers.get("content-type") || "";
                const rawText = await response.text();
                let data = null;

                if (contentType.includes("application/json")) {
                    try {
                        data = JSON.parse(rawText);
                    } catch (err) {
                        // fall back to text
                    }
                }

                if (!response.ok) {
                    const errorDetail =
                        data && data.message ? data.message : rawText;
                    throw new Error(
                        `Status code: ${response.status}. Detail: ${errorDetail}`
                    );
                }

                return data;
            })
            .then((data) => {
                if (data && data.summary) {
                    const summaryDiv = document.createElement("div");
                    summaryDiv.className = "summary-content";
                    const heading = document.createElement("h3");
                    heading.textContent = "Summary";
                    const paragraph = document.createElement("p");
                    paragraph.textContent = data.summary;
                    summaryDiv.appendChild(heading);
                    summaryDiv.appendChild(paragraph);
                    resultContainer.innerHTML = "";
                    resultContainer.appendChild(summaryDiv);
                } else {
                    resultContainer.innerHTML =
                        '<p class="summary-error">No summary was returned. Please try again.</p>';
                }
            })
            .catch((error) => {
                console.error("Resume summarizer error:", error);
                resultContainer.innerHTML =
                    '<p class="summary-error">An error occurred while summarizing. Please try again later.</p>';
            })
            .finally(() => {
                button.disabled = false;
                button.textContent = "Summarize";
            });
    });

    // function escapeHtml(text) {
    //     const div = document.createElement("div");
    //     div.textContent = text;
    //     return div.innerHTML.replace(/\n/g, "<br>");
    // }
});
