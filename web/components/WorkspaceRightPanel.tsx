"use client";

import { useState, useEffect } from "react";
import { getActivities } from "@/lib/api";
import ChunkDetailPanel from "./ChunkDetailPanel";

interface Activity {
  id: string;
  workspace_id: string;
  category: string;
  status: number;
  title: string;
  message: string;
  created_at: string;
}

interface WorkspaceRightPanelProps {
  workspaceId: string | null;
  selectedChunk?: any | null;
  onCloseChunk?: () => void;
}

export default function WorkspaceRightPanel({ workspaceId, selectedChunk, onCloseChunk }: WorkspaceRightPanelProps) {
  const [showActivity, setShowActivity] = useState(false);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (showActivity && workspaceId) {
      loadActivities();
    }
  }, [showActivity, workspaceId]);

  const loadActivities = async () => {
    if (!workspaceId) return;

    try {
      setLoading(true);
      const response = await getActivities(workspaceId);
      setActivities(response.response || []);
    } catch (error) {
      console.error("Failed to load activities:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return "just now";
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: date.getFullYear() !== now.getFullYear() ? "numeric" : undefined,
    });
  };

  // Show chunk detail panel if a chunk is selected
  if (selectedChunk && workspaceId) {
    return (
      <ChunkDetailPanel
        chunk={selectedChunk}
        workspaceId={workspaceId}
        onClose={onCloseChunk || (() => {})}
      />
    );
  }

  // Otherwise show activity panel
  return (
    <div className="h-full flex flex-col">
      <div className="flex-1"></div>

      <div className="border-t border-border">
        <button
          onClick={() => setShowActivity(!showActivity)}
          className="w-full px-6 py-4 text-left text-sm text-text-secondary hover:bg-background-secondary transition-colors"
        >
          Activity
        </button>

        {showActivity && (
          <div className="max-h-96 overflow-y-auto bg-background-secondary">
            {loading ? (
              <div className="p-6 text-center text-text-secondary text-sm">
                Loading activities...
              </div>
            ) : activities.length === 0 ? (
              <div className="p-6 text-center text-text-secondary text-sm">
                No activities yet
              </div>
            ) : (
              <div className="p-6 space-y-4">
                {activities.map((activity, index) => (
                  <div key={activity.id} className="flex gap-3">
                    <div className="flex flex-col items-center">
                      <div
                        className={`w-2 h-2 rounded-full mt-1.5 ${
                          activity.status >= 200 && activity.status < 300
                            ? "bg-green-500"
                            : activity.status >= 400
                            ? "bg-red-500"
                            : "bg-text-secondary"
                        }`}
                      />
                      {index < activities.length - 1 && (
                        <div className="w-px h-full bg-border mt-1"></div>
                      )}
                    </div>
                    <div className="flex-1 pb-4">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="text-sm font-medium text-text-primary">
                            {activity.title}
                          </div>
                          <div className="text-xs text-text-secondary mt-1">
                            {activity.message}
                          </div>
                        </div>
                        <div className="text-xs text-text-secondary whitespace-nowrap">
                          {formatDate(activity.created_at)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
