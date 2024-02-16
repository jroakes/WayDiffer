"""Constants for the diff viewer."""

WBM_REGEX = r"(?:https?:\\?\/\\?\/web\.archive\.org\\?\/web\\?\/\w+\\?\/|\\?\/web\\?\/\w+\\?\/https?:\\?\/\\?\/web\.archive\.org\\?\/screenshot\\?\/|(?<=\"|\')\\?\/web\\?\/\w+\\?\/)"
MAX_MEMENTO_LINES = 100
TOP_USERAGENTS_URL = "https://raw.githubusercontent.com/microlinkhq/top-user-agents/master/src/index.json"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
TIMEOUT = 120


CSS_CODE = """
body {
			  font-family: monospace;
			  white-space: pre;
			  position: relative;
        background: #fbfbfb;
			}
			#diff-container .line {
			  float: left;
			  width: 100%;
			}
			#diff-container .line-num {
			  color: #999;
			  padding-right: 10px;
			  margin-right: 10px;
			  display: inline-block;
			  width: auto;
			  border-right: 1px solid #ececec;
			}
			#diff-container .added {
			  background-color: #cfc;
			}
			#diff-container .deleted {
			  background-color: #fdd;
			}
			#diff-container {
			  margin: 0;
			  padding: 0;
			  float: left;
			  display: table;
			}
			/* Sticky sidebar */
			#sidebar {
			  position: fixed;
			  top: 0;
			  right: 0;
			  width: 20px;
			  height: 100%;
			  background-color: #ddd;
			  overflow-y: auto;
			  opacity: 0.25;
			}

			/* Marker styles */
			.marker {
			  background-color: #f00;
			  width: 100%;
			  margin: 0;
			  padding: 0;
			}
"""


JS_CODE = """
 document.addEventListener("DOMContentLoaded", function() {
 	const diffContainer = document.getElementById("diff-container");
 	const sidebar = document.getElementById("sidebar");
 	const lines = diffContainer.querySelectorAll(".line");
 	const screenHeight = window.innerHeight;
 	const lineNums = diffContainer.querySelectorAll("span.line-num");

 	// Calculate initial marker height based on screen height and number of lines
 	const initialMarkerHeight = screenHeight / lines.length;

 	lines.forEach(line => {
 		const added = line.querySelector(".added");
 		const deleted = line.querySelector(".deleted");
 		const marker = document.createElement("div");
 		marker.classList.add("marker");

 		// Set initial height for each marker
 		marker.style.height = `${initialMarkerHeight}px`;

 		// Determine and set the marker's background color
 		if (added && deleted) {
 			marker.style.backgroundColor = "orange";
 		} else if (added) {
 			marker.style.backgroundColor = "green";
 		} else if (deleted) {
 			marker.style.backgroundColor = "red";
 		} else {
 			marker.style.backgroundColor = "transparent";
 		}

 		// Append marker to sidebar
 		sidebar.appendChild(marker);
 	});

 	// After all markers are appended, check if total sidebar height exceeds screen height
 	const sidebarHeight = sidebar.scrollHeight;
  const screenHeightWithMargin = screenHeight - 40;

  console.log('sidebarHeight', sidebarHeight)
  console.log('screenHeightWithMargin', screenHeightWithMargin)

 	if (sidebarHeight > screenHeightWithMargin) {

 		console.log('Adjusting sidebar height')

 		const excessHeight = sidebarHeight - screenHeightWithMargin;
 		const backoffValue = excessHeight / lines.length; // Calculate backoff value per marker

 		// Adjust each marker's height to remove the excess
 		Array.from(sidebar.children).forEach(marker => {
 			const currentHeight = parseFloat(marker.style.height);
 			const adjustedHeight = currentHeight - backoffValue;
 			marker.style.height = `${adjustedHeight}px`;
 		});

    console.log('Updated sidebarHeight', sidebarHeight)
 	}

 	// Adjust line numbers
 	console.log('Adjusting line number width')
 	let maxWidth = 0;
 	lineNums.forEach(lineNum => {
 		// Temporarily set width to auto to accurately measure content width
 		lineNum.style.width = 'auto';
 		const width = lineNum.offsetWidth;
 		if (width > maxWidth) {
 			maxWidth = width;
 		}
 	});

 	// Set the width of all .line-num elements to maxWidth
 	lineNums.forEach(lineNum => {
 		lineNum.style.width = `${maxWidth}px`;
 	});


 });
 """

HTML_CODE = """
    <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Diff Viewer</title>
        <style>{css_code}</style>
      </head>
      <body>
        <div id="diff-container">{diff_content}</div>
        <div id="sidebar"></div>
        <script>{js_code}</script>
      </body>
    </html>
"""
