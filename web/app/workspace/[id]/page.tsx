"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { createWorkspace, getWorkspaceById, getDocuments } from "@/lib/api";
import ResizablePanels from "@/components/ResizablePanels";
import WorkspaceLeftPanel from "@/components/WorkspaceLeftPanel";
import DocumentViewer from "@/components/DocumentViewer";

interface Document {
  id: string;
  workspace_id: string;
  doc_type: string;
  file_path: string;
  filing_date: string | null;
  reporting_date: string | null;
  doc_id: string | null;
}

interface Workspace {
  id: string;
  name: string;
  ticker: string;
  created_at: string;
}

export default function WorkspacePage() {
  const params = useParams();
  const workspaceId = params.id as string;
  const getPendingWorkspace = useWorkspaceStore((state) => state.getPendingWorkspace);
  const removePendingWorkspace = useWorkspaceStore((state) => state.removePendingWorkspace);

  const [status, setStatus] = useState<"idle" | "creating" | "success" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const hasInitialized = useRef(false);

  useEffect(() => {
    if (hasInitialized.current) return;
    hasInitialized.current = true;

    const pendingData = getPendingWorkspace(workspaceId);

    if (pendingData) {
      setStatus("creating");
      initializeNewWorkspace(pendingData);
    } else {
      loadExistingWorkspace();
    }
  }, [workspaceId, getPendingWorkspace, removePendingWorkspace]);

  const initializeNewWorkspace = async (pendingData: any) => {
    try {
      const result = await createWorkspace(
        pendingData.workspaceId,
        pendingData.ticker,
        pendingData.file
      );

      setWorkspace(result.response.workspace);
      setDocuments(result.response.documents || []);
      setStatus("success");
      removePendingWorkspace(workspaceId);
    } catch (err: any) {
      setStatus("error");
      setError(err.message || "Failed to create workspace");
    }
  };

  const loadExistingWorkspace = async () => {
    try {
      setStatus("creating");
      const workspaceData = await getWorkspaceById(workspaceId);

      if (!workspaceData.response) {
        setStatus("error");
        setError("Workspace not found");
        return;
      }

      setWorkspace(workspaceData.response);

      const documentsData = await getDocuments(workspaceId);
      setDocuments(documentsData.response || []);
      setStatus("success");
    } catch (err: any) {
      setStatus("error");
      setError(err.message || "Failed to load workspace");
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden relative">
      <h1 className="font-heading font-medium text-6xl absolute top-8 right-8 text-text-secondary opacity-30 z-0 pointer-events-none">
        Ken
      </h1>

      <div className="flex-1 overflow-hidden relative z-10">
        <ResizablePanels
          leftPanel={
            <WorkspaceLeftPanel
              status={status}
              error={error}
              workspace={workspace}
              documents={documents}
              onDocumentSelect={setSelectedDocument}
            />
          }
          rightPanel={
            <DocumentViewer
              document={selectedDocument}
              onClose={() => setSelectedDocument(null)}
            />
          }
          defaultLeftWidth={35}
        />
      </div>
    </div>
  );
}
