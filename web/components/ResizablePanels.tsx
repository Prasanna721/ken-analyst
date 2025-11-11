"use client";

import { useState, useRef, useEffect } from "react";

interface ResizablePanelsProps {
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  defaultLeftWidth?: number;
}

export default function ResizablePanels({
  leftPanel,
  rightPanel,
  defaultLeftWidth = 50,
}: ResizablePanelsProps) {
  const [leftWidth, setLeftWidth] = useState(defaultLeftWidth);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = () => {
    setIsDragging(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;

      e.preventDefault();
      const containerRect = containerRef.current.getBoundingClientRect();
      const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;

      if (newLeftWidth >= 20 && newLeftWidth <= 80) {
        setLeftWidth(newLeftWidth);
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      document.body.style.userSelect = "";
    };

    if (isDragging) {
      document.body.style.userSelect = "none";
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      document.body.style.userSelect = "";
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging]);

  return (
    <div ref={containerRef} className="h-full flex">
      <div
        style={{ width: `${leftWidth}%` }}
        className="h-full overflow-auto"
      >
        {leftPanel}
      </div>

      <div
        onMouseDown={handleMouseDown}
        className="w-1 bg-border hover:bg-golden cursor-col-resize transition-colors"
      />

      <div
        style={{ width: `${100 - leftWidth}%` }}
        className="h-full overflow-auto"
      >
        {rightPanel}
      </div>
    </div>
  );
}
