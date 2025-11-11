"use client";

import { useState } from "react";
import { getFileIcon } from "@/lib/utils";

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

interface WorkplaceLeftPanelProps {
  workspace: Workspace | null;
  documents: Document[];
  loading: boolean;
  error: string | null;
}

type TabType = "finder" | "ai-agents";

export default function WorkplaceLeftPanel({
  workspace,
  documents,
  loading,
  error,
}: WorkplaceLeftPanelProps) {
  const [activeTab, setActiveTab] = useState<TabType>("finder");

  const getFileName = (filePath: string) => {
    return filePath.split("/").pop() || filePath;
  };

  return (
    <div className="w-96 border-r border-border flex flex-col bg-background-primary">
      <div className="border-b border-border flex">
        <button
          onClick={() => setActiveTab("finder")}
          className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
            activeTab === "finder"
              ? "bg-background-secondary text-text-primary border-b-2 border-golden"
              : "text-text-secondary hover:bg-background-secondary"
          }`}
        >
          Finder
        </button>
        <button
          onClick={() => setActiveTab("ai-agents")}
          className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
            activeTab === "ai-agents"
              ? "bg-background-secondary text-text-primary border-b-2 border-golden"
              : "text-text-secondary hover:bg-background-secondary"
          }`}
        >
          AI Agents
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-full text-text-secondary">
            Loading...
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full text-text-secondary">
            {error}
          </div>
        ) : activeTab === "finder" ? (
          <div>
            {documents.length === 0 ? (
              <div className="text-text-secondary text-center py-8">
                No documents found
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-4">
                {documents.map((doc) => {
                  const fileName = getFileName(doc.file_path);
                  return (
                    <div
                      key={doc.id}
                      className="flex flex-col items-center p-3 hover:bg-golden-light transition-colors cursor-pointer border border-transparent hover:border-border"
                    >
                      <div className="text-4xl mb-2">{getFileIcon(fileName)}</div>
                      <div className="text-xs text-text-primary text-center break-words w-full">
                        {fileName}
                      </div>
                      {doc.doc_type !== "other" && (
                        <div className="text-[10px] text-text-secondary mt-1">
                          {doc.doc_type.replace("_", "-")}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          <div className="text-text-secondary">
            <p className="mb-4">AI Agents will help you build financial models automatically.</p>
            <div className="p-4 border border-border bg-golden-light">
              <p className="text-sm text-text-primary">Coming soon...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
