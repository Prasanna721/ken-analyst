"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { generateWorkspaceId } from "@/lib/utils";

export default function CreateWorkspaceCard() {
  const router = useRouter();
  const addPendingWorkspace = useWorkspaceStore((state) => state.addPendingWorkspace);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  const handleCreateWorkspace = () => {
    if (!file) return;

    const workspaceId = generateWorkspaceId();
    addPendingWorkspace({ workspaceId, file });
    router.push(`/workspace/${workspaceId}`);
  };

  if (file) {
    return (
      <div className="h-56 border border-golden flex flex-col items-center justify-center p-6">
        <div className="text-text-primary mb-4 text-center truncate w-full">
          {file.name}
        </div>
        <button
          onClick={handleCreateWorkspace}
          className="px-6 py-3 bg-golden text-white hover:bg-golden-dark transition-colors"
        >
          Create Workspace
        </button>
      </div>
    );
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`h-56 border border-golden flex flex-col items-center justify-center cursor-pointer transition-colors ${
        isDragging ? "bg-golden-light/50" : "hover:bg-golden-light/30"
      }`}
    >
      <div className="text-4xl mb-4 text-text-primary">+</div>
      <h2 className="font-heading text-3xl text-text-primary mb-2 text-center">
        Add files, build <span className="text-golden font-medium">financial models</span>
      </h2>
      <p className="text-text-secondary text-sm text-center">
        Drop a file and analyze financial data
      </p>
    </div>
  );
}
