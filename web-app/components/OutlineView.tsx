import React from 'react';
import { GraphData } from '@/lib/api';

interface OutlineViewProps {
    graph?: GraphData;
    currentName: string;
}

export default function OutlineView({ graph, currentName }: OutlineViewProps) {
    if (!graph) return null;

    return (
        <div className="outline-view">
            <div className="outline-section outline-parents">
                <div className="outline-label">父节点</div>
                <div className="outline-nodes">
                    {graph.parents?.slice(0, 3).map((parent) => (
                        <div key={parent.id} className="outline-node parent-node" title={parent.name}>
                            {parent.name}
                        </div>
                    ))}
                </div>
            </div>

            <div className="outline-connector"></div>

            <div className="outline-section outline-siblings">
                <div className="outline-nodes">
                    {graph.siblings?.[0] && (
                        <div className="outline-node sibling-node" title={graph.siblings[0].name}>
                            {graph.siblings[0].name}
                        </div>
                    )}

                    <div className="outline-node current-node" title={currentName}>
                        {currentName}
                    </div>

                    {graph.siblings?.[1] && (
                        <div className="outline-node sibling-node" title={graph.siblings[1].name}>
                            {graph.siblings[1].name}
                        </div>
                    )}
                </div>
            </div>

            <div className="outline-connector"></div>

            <div className="outline-section outline-children">
                <div className="outline-label">子节点</div>
                <div className="outline-nodes">
                    {graph.children?.slice(0, 5).map((child) => (
                        <div key={child.id} className="outline-node child-node" title={child.name}>
                            {child.name}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
