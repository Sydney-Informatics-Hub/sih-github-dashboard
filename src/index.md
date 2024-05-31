---
title: SIH Github Dashboard
theme: [deep-space, parchment, wide]
---

# SIH Github Dashboard

```js
const repositories = FileAttachment("./data/repositories.csv").csv({typed: true});
const contributions = FileAttachment("./data/contributions.csv").csv({typed: true});
const forceGraphContributions = FileAttachment("./data/repo-graph.json").json();
```

```js
const selectedRepoInput = Inputs.select(repositories.map(d => d.name), {label: "Selected repository"});
const selectedRepoName = view(selectedRepoInput);
```

```js
const selectedRepo = repositories.filter(d => (d.name === selectedRepoName))[0];
const selectedRepoSummary = `${selectedRepo.name}: ${selectedRepo.description ? selectedRepo.description : ''}`;
document.getElementById("repoLink").href = selectedRepo.url;
```

```js
const repoContributions = contributions.filter(d => (d.repo_name === selectedRepoName));
const contributors = new Set(repoContributions.map(d => d.user_name));
```

```js
const repoContributionsPlot = Plot.plot({
    width: width * 0.4,
    height: 40 + new Set(repoContributions.map(d => d.user_name)).size * 30,
    marginLeft: 120,
    
    title: `Contributions to repository ${selectedRepoName}`,
    subtitle: "Note: a contribution is a commit to main branch. A pull request from a separate branch with many commits will count as one contribution",
    
    color: {
        type: "categorical",
        scheme: "Observable10"
    },
    x: {
        grid: true
    },
    marks: [
        Plot.axisY({anchor: "left", label: "Contributor", tickPadding: 10}),
        Plot.axisX({anchor: "top", label: "Contributions"}),
        Plot.axisX({anchor: "bottom", label: "", labelArrow: "none"}),
        Plot.barX(repoContributions, {x: "contributions", y: "user_name", fill: "user_name", tip: true, sort: {y: "-x"}}),
        Plot.ruleX([0]),,
        Plot.image(repoContributions, {
            x: d3.max(repoContributions, d => d.contributions) * 1.05,
            y: "user_name",
            src: d => d.avatar_url,
            r: 12,
            stroke: "#fff",
            preserveAspectRatio: "xMidYMin slice",
            title: "user_name"
        })
    ]
});
```


```js
const data = forceGraphContributions;
const height = width;

const selectedRepositoryColor = "#BEDCFE";
const repositoryColor = "#50A2A7";
const contributorColor = "#F5E0B7";

data.nodes.forEach(d => d.radius = +d.radius);
data.links.forEach(d => d.contributions = +d.contributions);

// Specify the color scale.
const color = d3.scaleOrdinal(["SelectedRepository", "Repository", "Contributor"], [selectedRepositoryColor, repositoryColor, contributorColor]);

// The force simulation mutates links and nodes, so create a copy
// so that re-evaluating this cell produces the same result.
const links = [];
const additionalNodeNames = new Set();
for (let linkObj of data.links) {
    if (contributors.has(linkObj.target)) {
        links.push({ ...linkObj });
        additionalNodeNames.add(linkObj.source);
    }
}

const nodes = [];
for (let nodeObj of data.nodes) {
    if ((nodeObj.group === "Repository") && (nodeObj.id === selectedRepoName)) {
        nodes.push({"id": nodeObj.id, "group": "SelectedRepository", "radius": nodeObj.radius * 2});
    } else if (((nodeObj.group === "Contributor") && contributors.has(nodeObj.id)) ||
        (additionalNodeNames.has(nodeObj.id))) {
        nodes.push({ ...nodeObj });
    }
}

// Create a simulation with several forces.
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id))
    .force("charge", d3.forceManyBody().strength(-500))
    .force("x", d3.forceX())
    .force("y", d3.forceY());

// Select the SVG container.
const svg = d3.select('#force-svg')
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [-width / 2, -height / 2, width, height])
    .attr("style", "max-width: 100%; height: auto;");

svg.selectAll("g").remove();

// Add a line for each link, and a circle for each node.
const link = svg.append("g")
    .attr("stroke", "#fff")
    .attr("stroke-opacity", 0.6)
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke-width", 1);

const node = svg.append("g")
    .attr("stroke", "#999")
    .attr("stroke-width", 1)
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", d => d.radius*2)
    .attr("fill", d => color(d.group));

node.append("title")
    .text(d => d.id);

// Add a drag behavior.
node.call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));

// Set the position attributes of links and nodes each time the simulation ticks.
simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
});

// Reheat the simulation when drag starts, and fix the subject position.
function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
}

// Update the subject (dragged node) position during drag.
function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
}

// Restore the target alpha so the simulation cools after dragging ends.
// Unfix the subject position now that it’s no longer being dragged.
function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
}

// When this cell is re-run, stop the previous simulation. (This doesn’t
// really matter since the target alpha is zero and the simulation will
// stop naturally, but it’s a good practice.)
invalidation.then(() => simulation.stop());
```

```js
document.getElementById("contributorSpan").style.backgroundColor = contributorColor;
document.getElementById("repositorySpan").style.backgroundColor = repositoryColor;
document.getElementById("selectedRepositorySpan").style.backgroundColor = selectedRepositoryColor;
```

<div class="card" >
    ${selectedRepoInput}
    ${selectedRepoSummary}
    <br>
    <a id="repoLink" target="_blank">Repository link</a>
</div>

<div class="grid grid-cols-2">
    <div class="card" id="force-container">
        <h2>Force graph for ${selectedRepoName}</h2>
        <span><mark id="contributorSpan">Contributors</mark></span><br>
        <span><mark id="repositorySpan">Contributor repositories</mark></span><br>
        <span><mark id="selectedRepositorySpan">Selected repository</mark></span><br>
        <svg id="force-svg"></svg>
    </div>
    <div class="card">
        ${resize((width) => repoContributionsPlot)}
    </div>
</div>
