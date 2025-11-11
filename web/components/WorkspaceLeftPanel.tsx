interface WorkspaceLeftPanelProps {
  status: "idle" | "creating" | "success" | "error";
  error: string | null;
  workspaceData: any;
}

export default function WorkspaceLeftPanel({
  status,
  error,
  workspaceData,
}: WorkspaceLeftPanelProps) {
  if (status === "idle") {
    return (
      <div className="h-full flex items-center justify-center p-8">
        <div className="text-text-secondary">Initializing...</div>
      </div>
    );
  }

  if (status === "creating") {
    return (
      <div className="h-full flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-2xl font-heading text-text-primary mb-4">
            Creating workspace...
          </div>
          <div className="text-text-secondary">
            Please wait while we set up your workspace
          </div>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="h-full flex items-center justify-center p-8">
        <div className="text-center">
          <div className="text-2xl font-heading text-red-600 mb-4">
            Error creating workspace
          </div>
          <div className="text-text-secondary">{error}</div>
        </div>
      </div>
    );
  }

  if (status === "success" && workspaceData) {
    return (
      <div className="h-full p-8">
        <div className="mb-8">
          <h1 className="font-heading text-4xl text-text-primary mb-2">
            {workspaceData.workspace.name}
          </h1>
          <div className="text-text-secondary">
            {workspaceData.workspace.ticker} • Created{" "}
            {new Date(workspaceData.workspace.created_at).toLocaleDateString()}
          </div>
        </div>

        {workspaceData.documents && workspaceData.documents.length > 0 && (
          <div>
            <h2 className="text-xl font-medium text-text-primary mb-4">
              Documents ({workspaceData.documents.length})
            </h2>
            <div className="space-y-2">
              {workspaceData.documents.map((doc: any, index: number) => (
                <div
                  key={index}
                  className="p-4 border border-border hover:bg-golden-light/30 transition-colors cursor-pointer"
                >
                  <div className="font-medium text-text-primary">
                    {doc.doc_type}
                  </div>
                  <div className="text-sm text-text-secondary truncate">
                    {doc.file_path}
                  </div>
                  {doc.filing_date && (
                    <div className="text-xs text-text-secondary mt-1">
                      Filed: {doc.filing_date}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return null;
}
