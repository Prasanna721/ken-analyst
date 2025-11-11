"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getWorkspaces } from "@/lib/api";

interface Workspace {
  id: string;
  name: string;
  ticker: string;
  created_at: string;
}

export default function WorkspaceList() {
  const router = useRouter();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      const data = await getWorkspaces();
      setWorkspaces(data.response || []);
    } catch (error) {
      console.error("Failed to load workspaces:", error);
      setWorkspaces([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-text-secondary">Loading workspaces...</div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto">
      {workspaces.length === 0 ? (
        <div className="text-text-secondary text-center py-8">
          No workspaces yet. Create one to get started.
        </div>
      ) : (
        <div className="space-y-3">
          {workspaces.map((workspace) => (
            <div
              key={workspace.id}
              onClick={() => router.push(`/workspace/${workspace.id}`)}
              className="p-4 border border-border hover:bg-golden-light transition-colors cursor-pointer"
            >
              <div className="font-medium text-text-primary">{workspace.name}</div>
              <div className="text-sm text-text-secondary mt-1">
                {workspace.ticker} • {new Date(workspace.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
