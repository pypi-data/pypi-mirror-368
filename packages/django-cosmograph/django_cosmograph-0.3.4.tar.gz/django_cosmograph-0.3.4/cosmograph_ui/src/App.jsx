import { useEffect,useMemo, useState, useRef } from 'react'
import { Cosmograph,CosmographProvider } from '@cosmograph/react'
import "./App.css"

function Legend({ legend, toggleGroup }) {
  return (
    <div className="legend-box">
      {legend.map(({ group, colour, selected }) => (
        <div key={group} style={{ display: "flex", alignItems: "center", marginBottom: 4 }}>
          <input
            type="checkbox"
            checked={selected}
            onChange={() => toggleGroup(group)}
            style={{ marginRight: 8 }}
          />

          <span className="legend-dot" style={{ backgroundColor: colour }} ></span>
          <span>{group} {selected}</span>
        </div>
      ))}
    </div>
  );
}


export default function App({ data,params, legend:initialLegend }) {
  const cosmographRef = useRef(null)
  const graphRef = useRef(null);
  const [legend, setLegend] = useState(
  initialLegend.map(item => ({ ...item, selected: item.selected ?? true }))
);
  const selectedGroups = Object.fromEntries(
    legend.map(({ group, selected }) => [group, selected])
  );
  useEffect(() => {
    graphRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const colourMap = Object.fromEntries(legend.map(({ group, colour }) => [group, colour]));
  const {
    backgroundColor = "transparent",
    linkArrows = false,
    scaleNodesOnZoom = false,
    simulationGravity = 0.25,
    simulationRepulsion = 0.1,
    simulationRepulsionTheta = 1.7,
    simulationLinkDistance = 2,
    simulationFriction = 0.85,
    simulationCenter = 0.0,
    renderLinks = true,
    simulationDecay = 1000,
    simulationRepulsionFromMouse = 2.0,
    simulationLinkSpring = 1.0
  } = params || {};

  const graphNodeMap = useMemo(
    () => Object.fromEntries(data.nodes.map(n => [n.id, n])),
    [data.nodes]
  );
  const filteredGraph = useMemo(
    () => ({
      nodes: data.nodes.filter(
        node => selectedGroups[node.group]
      ),
      links: data.links.filter(
        link =>
        selectedGroups[graphNodeMap[link.source].group] &&
          selectedGroups[graphNodeMap[link.target].group]
      ),
    }),
    [data.nodes, data.links, graphNodeMap, selectedGroups]
  );

  const toggleGroup = (group) => {
    setLegend(legend.map(item =>
      item.group === group ? { ...item, selected: !item.selected } : item
    ));
  };

  const playPause = () => {
    if ((cosmographRef.current)?.isSimulationRunning) {
      (cosmographRef.current)?.pause();
    } else {
      (cosmographRef.current)?.start();
    }
  }
  const fitView = () => {
    (cosmographRef.current)?.fitView();
    graphRef.current?.scrollIntoView({ behavior: 'smooth' });
  }

  return (
    <div ref={graphRef}>
      <CosmographProvider>
        <Legend legend={legend} toggleGroup={toggleGroup} />
        <Cosmograph
          ref={cosmographRef}
          backgroundColor={backgroundColor}
          nodes={filteredGraph.nodes}
          links={filteredGraph.links}
          linkArrows={linkArrows}
          renderLinks={renderLinks}
          nodeColor={(d) =>  colourMap[d.group] ?? "blue"}
          nodeSize={(d) => d.size ?? 5}
          scaleNodesOnZoom={scaleNodesOnZoom}
          nodeLabelColor={(d) =>  colourMap[d.group] ?? "blue"}
          nodeLabelAccessor={(d) => d.label}
          simulationGravity={simulationGravity}
          simulationRepulsion={simulationRepulsion}
          simulationRepulsionTheta={simulationRepulsionTheta}
          simulationLinkDistance={simulationLinkDistance}
          simulationLinkSpring={simulationLinkSpring}
          simulationFriction={simulationFriction}
          simulationDecay={simulationDecay}
          simulationCenter={simulationCenter}
          simulationRepulsionFromMouse={simulationRepulsionFromMouse}
        />
        <div className="controls">
          <button
            onClick={playPause}
            className="control-button"
          >
            Pause/Play
          </button>
          <button
            onClick={fitView}
            className="control-button"
          >
            Fit
          </button>
        </div>
      </CosmographProvider>
    </div>
  )
}
