"use client";

import { useState, useMemo, useEffect, useRef } from "react";
import { getFileIcon } from "@/lib/utils";
import { downloadDocument } from "@/lib/api";

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

interface WorkspaceLeftPanelProps {
  status: "idle" | "creating" | "success" | "error";
  error: string | null;
  workspace: Workspace | null;
  documents: Document[];
}

type TabType = "finder" | "ai-agents";
type FilterType = "all" | "10-K" | "10-Q" | "other";
type ViewMode = "grid" | "viewer";

export default function WorkspaceLeftPanel({
  status,
  error,
  workspace,
  documents,
}: WorkspaceLeftPanelProps) {
  const [activeTab, setActiveTab] = useState<TabType>("finder");
  const [activeFilter, setActiveFilter] = useState<FilterType>("all");
  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [documentContent, setDocumentContent] = useState<string | null>(null);
  const [fileType, setFileType] = useState<"pdf" | "text" | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const getFileName = (filePath: string) => {
    return filePath.split("/").pop() || filePath;
  };

  const filteredDocuments = useMemo(() => {
    if (activeFilter === "all") return documents;
    if (activeFilter === "10-K") return documents.filter((doc) => doc.doc_type === "10_K");
    if (activeFilter === "10-Q") return documents.filter((doc) => doc.doc_type === "10_Q");
    return documents.filter((doc) => doc.doc_type === "other");
  }, [documents, activeFilter]);

  const filterButtons: { label: string; value: FilterType }[] = [
    { label: "All", value: "all" },
    { label: "10-K", value: "10-K" },
    { label: "10-Q", value: "10-Q" },
    { label: "Other", value: "other" },
  ];

  const handleDocumentSelect = async (doc: Document) => {
    setSelectedDocument(doc);
    setViewMode("viewer");
    setLoading(true);
    setLoadError(null);
    setDocumentContent(null);
    setPdfUrl(null);

    try {
      const blob = await downloadDocument(doc.id);
      const filename = doc.file_path.split("/").pop() || "";
      const ext = filename.split(".").pop()?.toLowerCase();

      if (ext === "pdf") {
        setFileType("pdf");
        const url = URL.createObjectURL(blob);
        setPdfUrl(url);
      } else if (ext === "txt" || !ext || ext === "text") {
        setFileType("text");
        const text = await blob.text();
        setDocumentContent(text);
      } else {
        setLoadError("Unsupported file type. Only PDF and text files are supported.");
      }

      setLoading(false);
    } catch (err: any) {
      setLoadError(err.message || "Failed to load document");
      setLoading(false);
    }
  };

  const handleBackToGrid = () => {
    setViewMode("grid");
    setSelectedDocument(null);
    setDocumentContent(null);
    setFileType(null);
    if (pdfUrl) {
      URL.revokeObjectURL(pdfUrl);
    }
    setPdfUrl(null);
    setLoadError(null);
  };

  useEffect(() => {
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl]);

  if (status === "idle" || status === "creating") {
    return (
      <div className="h-full flex items-center justify-center p-8 bg-background-primary">
        <div className="text-center">
          <div className="text-2xl font-heading text-text-primary mb-4">
            {status === "idle" ? "Initializing..." : "Creating workspace..."}
          </div>
          {status === "creating" && (
            <div className="text-text-secondary">
              Please wait while we set up your workspace
            </div>
          )}
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="h-full flex items-center justify-center p-8 bg-background-primary">
        <div className="text-center">
          <div className="text-2xl font-heading text-red-600 mb-4">Error</div>
          <div className="text-text-secondary">{error}</div>
        </div>
      </div>
    );
  }

  if (viewMode === "viewer" && selectedDocument) {
    return (
      <div className="h-full flex flex-col bg-background-primary">
        <div className="border-b border-border p-4 flex items-center gap-3">
          <button
            onClick={handleBackToGrid}
            className="text-text-secondary hover:text-text-primary text-xl"
          >
            ←
          </button>
          <div className="flex-1">
            <h2 className="font-medium text-text-primary text-sm">
              {getFileName(selectedDocument.file_path)}
            </h2>
            {selectedDocument.filing_date && (
              <div className="text-xs text-text-secondary mt-1">
                Filed: {selectedDocument.filing_date}
              </div>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          {loading ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-text-secondary">Loading document...</div>
            </div>
          ) : loadError ? (
            <div className="h-full flex items-center justify-center p-8">
              <div className="text-red-600 text-center">{loadError}</div>
            </div>
          ) : fileType === "pdf" && pdfUrl ? (
            <iframe
              src={pdfUrl}
              className="w-full h-full border-0"
              title="PDF Viewer"
            />
          ) : fileType === "text" && documentContent ? (
            <TextViewer content={documentContent} />
          ) : null}
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-background-primary">
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

      {activeTab === "finder" && (
        <div className="border-b border-border p-4">
          <div className="flex gap-2">
            {filterButtons.map((btn) => (
              <button
                key={btn.value}
                onClick={() => setActiveFilter(btn.value)}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  activeFilter === btn.value
                    ? "bg-golden-light text-text-primary"
                    : "bg-background-secondary text-text-secondary hover:bg-golden-light"
                }`}
              >
                {btn.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === "finder" ? (
          <div>
            {filteredDocuments.length === 0 ? (
              <div className="text-text-secondary text-center py-8">
                No documents found
                {activeFilter !== "all" && (
                  <span> for filter "{activeFilter}"</span>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-4">
                {filteredDocuments.map((doc) => {
                  const fileName = getFileName(doc.file_path);
                  return (
                    <div
                      key={doc.id}
                      onDoubleClick={() => handleDocumentSelect(doc)}
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
                      {doc.filing_date && (
                        <div className="text-[10px] text-text-secondary">
                          {doc.filing_date}
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

function TextViewer({ content }: { content: string }) {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 5000 });
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  const lines = content.split("\n");
  const totalHeight = lines.length * 20;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const scrollTop = container.scrollTop;
      const viewportHeight = container.clientHeight;

      const startLine = Math.max(0, Math.floor(scrollTop / 20) - 100);
      const endLine = Math.min(lines.length, Math.ceil((scrollTop + viewportHeight) / 20) + 100);

      const startChar = lines.slice(0, startLine).reduce((acc, line) => acc + line.length + 1, 0);
      const endChar = lines.slice(0, endLine).reduce((acc, line) => acc + line.length + 1, 0);

      setVisibleRange({ start: startChar, end: endChar });
    };

    container.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();

    return () => {
      container.removeEventListener("scroll", handleScroll);
    };
  }, [lines]);

  const visibleContent = content.substring(visibleRange.start, visibleRange.end);
  const topPadding = visibleRange.start > 0 ? Math.floor(content.substring(0, visibleRange.start).split("\n").length * 20) : 0;
  const bottomPadding = Math.max(0, totalHeight - topPadding - (visibleContent.split("\n").length * 20));

  return (
    <div ref={containerRef} className="h-full overflow-auto bg-background-primary">
      <div style={{ height: `${totalHeight}px`, position: "relative" }}>
        <div style={{ height: `${topPadding}px` }} />
        <pre
          ref={contentRef}
          className="text-sm text-text-primary p-6 font-mono whitespace-pre-wrap break-words"
        >
          {visibleContent}
        </pre>
        <div style={{ height: `${bottomPadding}px` }} />
      </div>
    </div>
  );
}
