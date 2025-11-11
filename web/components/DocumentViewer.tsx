"use client";

import { useState, useEffect, useRef, useMemo } from "react";
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

interface DocumentViewerProps {
  document: Document | null;
  onClose: () => void;
}

export default function DocumentViewer({ document, onClose }: DocumentViewerProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [content, setContent] = useState<string | null>(null);
  const [fileType, setFileType] = useState<"pdf" | "text" | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!document) {
      setContent(null);
      setPdfUrl(null);
      setFileType(null);
      return;
    }

    loadDocument();
  }, [document]);

  const loadDocument = async () => {
    if (!document) return;

    try {
      setLoading(true);
      setError(null);

      const blob = await downloadDocument(document.id);
      const filename = document.file_path.split("/").pop() || "";
      const ext = filename.split(".").pop()?.toLowerCase();

      if (ext === "pdf") {
        setFileType("pdf");
        const url = URL.createObjectURL(blob);
        setPdfUrl(url);
      } else if (ext === "txt" || !ext || ext === "text") {
        setFileType("text");
        const text = await blob.text();
        setContent(text);
      } else {
        setError("Unsupported file type. Only PDF and text files are supported.");
      }

      setLoading(false);
    } catch (err: any) {
      setError(err.message || "Failed to load document");
      setLoading(false);
    }
  };

  useEffect(() => {
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl]);

  if (!document) {
    return (
      <div className="h-full flex items-center justify-center p-8 bg-background-secondary">
        <div className="text-text-secondary text-center">
          Double-click a document to view it
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center p-8 bg-background-secondary">
        <div className="text-text-secondary">Loading document...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex flex-col bg-background-secondary">
        <div className="border-b border-border p-4 flex justify-between items-center">
          <h2 className="font-medium text-text-primary">Error</h2>
          <button
            onClick={onClose}
            className="text-text-secondary hover:text-text-primary"
          >
            ✕
          </button>
        </div>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-red-600">{error}</div>
        </div>
      </div>
    );
  }

  const filename = document.file_path.split("/").pop() || "Document";

  return (
    <div className="h-full flex flex-col bg-background-secondary">
      <div className="border-b border-border p-4 flex justify-between items-center">
        <div>
          <h2 className="font-medium text-text-primary">{filename}</h2>
          {document.filing_date && (
            <div className="text-sm text-text-secondary mt-1">
              Filed: {document.filing_date}
            </div>
          )}
        </div>
        <button
          onClick={onClose}
          className="text-text-secondary hover:text-text-primary"
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-hidden">
        {fileType === "pdf" && pdfUrl ? (
          <PDFViewer pdfUrl={pdfUrl} />
        ) : fileType === "text" && content ? (
          <TextViewer content={content} />
        ) : null}
      </div>
    </div>
  );
}

function PDFViewer({ pdfUrl }: { pdfUrl: string }) {
  return (
    <iframe
      src={pdfUrl}
      className="w-full h-full border-0"
      title="PDF Viewer"
    />
  );
}

function TextViewer({ content }: { content: string }) {
  const containerRef = useRef<HTMLDivElement>(null);

  const isHTML = content.trim().startsWith("<") || content.includes("<table") || content.includes("<a id=");

  if (isHTML) {
    return (
      <div ref={containerRef} className="h-full overflow-auto bg-background-primary">
        <div
          className="text-sm text-text-primary p-6 prose prose-sm max-w-none"
          dangerouslySetInnerHTML={{ __html: content }}
          style={{
            lineHeight: "1.6",
          }}
        />
      </div>
    );
  }

  return (
    <div ref={containerRef} className="h-full overflow-auto bg-background-primary">
      <pre className="text-sm text-text-primary p-6 font-mono whitespace-pre-wrap break-words">
        {content}
      </pre>
    </div>
  );
}
