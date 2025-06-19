# JS/webGL based graph layout and visualization libraries<!-- omit from toc -->

## Table of contents<!-- omit from toc -->

- [Required features](#required-features)
- [Surveys](#surveys)
- [Cytoscape.js](#cytoscapejs)
- [vis.js - network](#visjs---network)
- [Sigma.js](#sigmajs)

## Required features

- distinguish edges from arcs/arrows: curved arrows to avoid overlap of two arrows having same node adjacency
- dynamic data: varying nodes, edges and/or their attributes across time
- Compounding/Grouping/[Clustering](https://visjs.github.io/vis-network/examples/network/other/clustering.html) nodes in a box/container
- Various automatic Layout algorithm
  - some nodes position is manually given (and fixed)
  - dynamic/progressive layout adaptation (e.g. when adding a new node)
- Interactions:
  - Selectable edges
  - Draggable nodes: select a node, drag it and release it (node should then remain in place)
- Self-loops

## Surveys

Survey articles (refer below) tend to put forward

- `cytoscape.js`: [on github](https://github.com/cytoscape/cytoscape.js), [website](https://js.cytoscape.org/)
- `sgima.js`: [github](https://github.com/jacomyal/sigma.js), [website](https://www.sigmajs.org/)
- `vis.js-network`: [examples](https://visjs.github.io/vis-network/examples/)
- [G6](https://github.com/antvis/G6) that [seems way too Chinese](https://github.com/antvis/G6/blob/v5/README.zh-CN.md)

References

- [Ranking of JavaScript Graph Visualization Libraries by MingYi Zhao, Mar 2021](https://mingyizhao.medium.com/background-b553fda47349)
- [JavaScript Graph Drawing Libraries](https://github.com/anvaka/graph-drawing-libraries)
- [List of graph visualization libraries, by Elise Devau, 2019](https://elise-deux.medium.com/the-list-of-graph-visualization-libraries-7a7b89aab6a6)

## Cytoscape.js

- [Many applications](https://apps.cytoscape.org/) using the library (mainly biology oriented).
- Has a [`cola.js` (COnstrained LAyout) extension](https://github.com/cytoscape/cytoscape.js-cola)

Available features:

- [Compounding and dragging nodes](https://github.com/cytoscape/cytoscape.js-compound-drag-and-drop): the extension has [many limitations](https://github.com/cytoscape/cytoscape.js-compound-drag-and-drop#caveats)

## vis.js - network

- [Dot language](https://visjs.github.io/vis-network/examples/network/data/dotLanguage/dotPlayground.html): the support is _partial_ (e.g. no support of [dot clusters](https://graphviz.org/Gallery/directed/cluster.html))
- :white_check_mark: Edge: [selection](https://visjs.github.io/vis-network/examples/network/other/cursorChange.html), but dragging seems to act on the whole network
- Grouping/clustering nodes: [example](https://visjs.github.io/vis-network/examples/network/other/clustering.html)
- :white_check_mark: [Arrow types](https://visjs.github.io/vis-network/examples/network/edgeStyles/arrowTypes.html)
- Grouping:

## Sigma.js

General references/comments

- Tutorial [7 Helpful Sigma.js Examples to Master Graph Visualization, by Rapidops](https://rapidops.medium.com/7-helpful-sigma-js-examples-to-master-graph-visualization-a8cadf9e9b14)
- Arrested development [since 2024](https://github.com/jacomyal/sigma.js/commits/main/)

Available features

- [Layout algorithms](https://github.com/jacomyal/sigma.js/issues/939)
- [edge selection](https://stackoverflow.com/questions/49873693/sigma-js-how-to-keep-edge-selected-onclick)
- Curved arrows: [here](https://github.com/jacomyal/sigma.js/issues/951), [there](https://stackoverflow.com/questions/48909462/sigma-curve-and-curvedarrow-edge-type-renders-as-a-line)
- [Draggable nodes](https://stackoverflow.com/questions/20541831/sigma-js-is-there-a-way-to-drag-one-node-individually)

**Missing** features

- no [self-loops support](https://github.com/jacomyal/sigma.js/issues/1429) (edge ending at same node)
- no [node grouping](https://github.com/jacomyal/sigma.js/issues/586)
