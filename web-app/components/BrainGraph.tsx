'use client';

import React, { useCallback, useMemo, useRef, useEffect, useState } from 'react';
import { GraphData, ThoughtNode } from '@/lib/api';

// 动态导入 react-force-graph-2d (避免 SSR 问题)
import dynamic from 'next/dynamic';
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

interface BrainGraphProps {
    graph?: GraphData;
    currentName: string;
    width?: number;
    height?: number;
}

interface GraphNode {
    id: string;
    name: string;
    type: 'current' | 'parent' | 'child' | 'sibling' | 'jump';
    val: number; // 节点大小
}

interface GraphLink {
    source: string;
    target: string;
    type: 'parent' | 'child' | 'sibling' | 'jump';
}

// 节点颜色配置
const NODE_COLORS: Record<string, string> = {
    current: '#06b6d4',  // cyan-500
    parent: '#8b5cf6',   // violet-500
    child: '#10b981',    // emerald-500
    sibling: '#6b7280',  // gray-500
    jump: '#f59e0b',     // amber-500
};

// 连接线颜色
const LINK_COLORS: Record<string, string> = {
    parent: 'rgba(139, 92, 246, 0.6)',
    child: 'rgba(16, 185, 129, 0.6)',
    sibling: 'rgba(107, 114, 128, 0.4)',
    jump: 'rgba(245, 158, 11, 0.6)',
};

export default function BrainGraph({ graph, currentName, width = 280, height = 200 }: BrainGraphProps) {
    const graphRef = useRef<any>(null);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    // 将 TheBrain graph 数据转换为力导向图格式
    const graphData = useMemo(() => {
        if (!graph) return { nodes: [], links: [] };

        const nodes: GraphNode[] = [];
        const links: GraphLink[] = [];
        const nodeIds = new Set<string>();

        // 添加当前节点 (中心)
        const currentId = graph.activeThought?.id || 'current';
        nodes.push({
            id: currentId,
            name: currentName,
            type: 'current',
            val: 8, // 最大的节点
        });
        nodeIds.add(currentId);

        // 添加父节点
        graph.parents?.slice(0, 3).forEach((node: ThoughtNode) => {
            if (!nodeIds.has(node.id)) {
                nodes.push({ id: node.id, name: node.name, type: 'parent', val: 4 });
                nodeIds.add(node.id);
                links.push({ source: node.id, target: currentId, type: 'parent' });
            }
        });

        // 添加子节点
        graph.children?.slice(0, 5).forEach((node: ThoughtNode) => {
            if (!nodeIds.has(node.id)) {
                nodes.push({ id: node.id, name: node.name, type: 'child', val: 3 });
                nodeIds.add(node.id);
                links.push({ source: currentId, target: node.id, type: 'child' });
            }
        });

        // 添加兄弟节点
        graph.siblings?.slice(0, 2).forEach((node: ThoughtNode) => {
            if (!nodeIds.has(node.id)) {
                nodes.push({ id: node.id, name: node.name, type: 'sibling', val: 2 });
                nodeIds.add(node.id);
                links.push({ source: currentId, target: node.id, type: 'sibling' });
            }
        });

        // 添加跳转节点
        graph.jumps?.slice(0, 3).forEach((node: ThoughtNode) => {
            if (!nodeIds.has(node.id)) {
                nodes.push({ id: node.id, name: node.name, type: 'jump', val: 3 });
                nodeIds.add(node.id);
                links.push({ source: currentId, target: node.id, type: 'jump' });
            }
        });

        return { nodes, links };
    }, [graph, currentName]);

    // 节点绘制函数
    const nodeCanvasObject = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
        const label = node.name;
        const fontSize = Math.max(10 / globalScale, 3);
        const nodeRadius = node.type === 'current' ? 12 : 8;

        // 绘制节点圆形
        ctx.beginPath();
        ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI);
        ctx.fillStyle = NODE_COLORS[node.type] || '#ffffff';
        ctx.fill();

        // 当前节点添加发光效果
        if (node.type === 'current') {
            ctx.shadowColor = NODE_COLORS.current;
            ctx.shadowBlur = 15;
            ctx.beginPath();
            ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI);
            ctx.fill();
            ctx.shadowBlur = 0;
        }

        // 绘制节点边框
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.lineWidth = 1;
        ctx.stroke();

        // 绘制标签 (只在缩放足够大时显示)
        if (globalScale > 0.8) {
            ctx.font = `${fontSize}px -apple-system, BlinkMacSystemFont, sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillStyle = '#ffffff';

            // 截断过长的标签
            const maxLength = 12;
            const displayLabel = label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
            ctx.fillText(displayLabel, node.x, node.y + nodeRadius + 3);
        }
    }, []);

    // 连接线绘制
    const linkColor = useCallback((link: any) => {
        return LINK_COLORS[link.type] || 'rgba(255, 255, 255, 0.2)';
    }, []);

    // 初始化后居中并缩放
    useEffect(() => {
        if (graphRef.current && graphData.nodes.length > 0) {
            // 等待图谱渲染完成后居中
            setTimeout(() => {
                graphRef.current?.zoomToFit(300, 20);
            }, 500);
        }
    }, [graphData]);

    if (!mounted || !graph || graphData.nodes.length === 0) {
        return (
            <div className="brain-graph-placeholder">
                <span>🔗 加载图谱中...</span>
            </div>
        );
    }

    return (
        <div className="brain-graph-container">
            <div className="brain-graph-legend">
                <span className="legend-item parent">父</span>
                <span className="legend-item current">当前</span>
                <span className="legend-item child">子</span>
                <span className="legend-item jump">跳转</span>
            </div>
            <ForceGraph2D
                ref={graphRef}
                graphData={graphData}
                width={width}
                height={height}
                backgroundColor="transparent"
                nodeCanvasObject={nodeCanvasObject}
                linkColor={linkColor}
                linkWidth={2}
                linkCurvature={0.2}
                d3AlphaDecay={0.05}
                d3VelocityDecay={0.3}
                cooldownTime={1000}
                enableZoomInteraction={true}
                enablePanInteraction={true}
                enableNodeDrag={false}
                nodeLabel={(node: any) => node.name}
            />
        </div>
    );
}
