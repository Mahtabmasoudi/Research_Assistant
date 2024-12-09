const fetchPapers = async () => {
  const keyword = document.getElementById("searchKeyword").value;
  const numResults = document.getElementById("numResults").value || 5;
  const apiUrl = `http://export.arxiv.org/api/query?search_query=all:${encodeURIComponent(keyword)}&start=0&max_results=${numResults}`;

  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "Fetching papers...";

  try {
    const response = await fetch(apiUrl);
    const text = await response.text();
    const parser = new DOMParser();
    const xml = parser.parseFromString(text, "text/xml");
    const entries = Array.from(xml.getElementsByTagName("entry"));

    resultsDiv.innerHTML = "";
    entries.forEach((entry) => {
      const title = entry.getElementsByTagName("title")[0].textContent;
      const summary = entry.getElementsByTagName("summary")[0].textContent;
      const pdfUrl = entry.getElementsByTagName("id")[0].textContent;

      const paperDiv = document.createElement("div");
      paperDiv.className = "paper";
      paperDiv.innerHTML = `
        <h3>${title}</h3>
        <p>${summary}</p>
        <a href="${pdfUrl}" target="_blank">Read Full Paper</a>
      `;
      resultsDiv.appendChild(paperDiv);
    });
  } catch (error) {
    resultsDiv.innerHTML = "Error fetching papers. Please try again.";
  }
};
