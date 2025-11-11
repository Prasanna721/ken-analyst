"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getWorkspaceById, getDocuments } from "@/lib/api";
import WorkplaceLeftPanel from "@/components/WorkplaceLeftPanel";

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

export default function WorkplacePage() {
  const params = useParams();
  const workplaceId = params.workplace_id as string;

  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadWorkplaceData = async () => {
      try {
        setLoading(true);
        setError(null);

        const workspaceData = await getWorkspaceById(workplaceId);
        if (!workspaceData.response) {
          setError("Workspace not found");
          return;
        }

        setWorkspace(workspaceData.response);

        const documentsData = await getDocuments(workplaceId);
        setDocuments(documentsData.response || []);
      } catch (err: any) {
        setError(err.message || "Failed to load workplace data");
      } finally {
        setLoading(false);
      }
    };

    loadWorkplaceData();
  }, [workplaceId]);

  return (
    <div className="h-screen flex flex-col overflow-hidden relative">
      <h1 className="font-heading font-medium text-6xl absolute top-8 right-8 text-text-secondary opacity-30 z-0 pointer-events-none">
        Ken
      </h1>

      <div className="flex-1 flex overflow-hidden relative z-10">
        <WorkplaceLeftPanel
          workspace={workspace}
          documents={documents}
          loading={loading}
          error={error}
        />

        <div className="flex-1 bg-background-secondary p-8">
          {loading ? (
            <div className="flex items-center justify-center h-full text-text-secondary">
              Loading...
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full text-text-secondary">
              {error}
            </div>
          ) : workspace ? (
            <div>
              <h2 className="font-heading text-2xl mb-4">{workspace.name}</h2>
              <div className="text-text-secondary">
                {workspace.ticker} • {new Date(workspace.created_at).toLocaleDateString()}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
