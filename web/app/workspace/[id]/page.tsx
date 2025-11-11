"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import Layout from "@/components/Layout";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { createWorkspace } from "@/lib/api";
import ResizablePanels from "@/components/ResizablePanels";
import WorkspaceLeftPanel from "@/components/WorkspaceLeftPanel";
import WorkspaceRightPanel from "@/components/WorkspaceRightPanel";

export default function WorkspacePage() {
  const params = useParams();
  const workspaceId = params.id as string;
  const getPendingWorkspace = useWorkspaceStore((state) => state.getPendingWorkspace);
  const removePendingWorkspace = useWorkspaceStore((state) => state.removePendingWorkspace);

  const [status, setStatus] = useState<"idle" | "creating" | "success" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [workspaceData, setWorkspaceData] = useState<any>(null);
  const hasInitialized = useRef(false);

  useEffect(() => {
    if (hasInitialized.current) return;

    const pendingData = getPendingWorkspace(workspaceId);

    if (!pendingData) {
      setStatus("error");
      setError("No workspace data found");
      return;
    }

    hasInitialized.current = true;
    setStatus("creating");

    const initializeWorkspace = async () => {
      try {
        const result = await createWorkspace(
          pendingData.workspaceId,
          pendingData.ticker,
          pendingData.file
        );

        setWorkspaceData(result.response);
        setStatus("success");
        removePendingWorkspace(workspaceId);
      } catch (err: any) {
        setStatus("error");
        setError(err.message || "Failed to create workspace");
      }
    };

    initializeWorkspace();
  }, [workspaceId, getPendingWorkspace, removePendingWorkspace]);

  return (
    <Layout>
      <ResizablePanels
        leftPanel={
          <WorkspaceLeftPanel
            status={status}
            error={error}
            workspaceData={workspaceData}
          />
        }
        rightPanel={<WorkspaceRightPanel />}
        defaultLeftWidth={50}
      />
    </Layout>
  );
}
