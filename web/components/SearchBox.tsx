"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { searchCompanies } from "@/lib/api";
import { useWorkspaceStore } from "@/store/workspaceStore";
import { generateWorkspaceId } from "@/lib/utils";

interface SearchResult {
  symbol: string;
  name: string;
}

export default function SearchBox() {
  const router = useRouter();
  const addPendingWorkspace = useWorkspaceStore((state) => state.addPendingWorkspace);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    const performSearch = async () => {
      if (!query.trim()) {
        setResults([]);
        setLoading(false);
        return;
      }

      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();
      setLoading(true);

      try {
        const data = await searchCompanies(query, abortControllerRef.current.signal);
        setResults(data.response || []);
      } catch (error: any) {
        if (error.name !== "AbortError") {
          console.error("Search failed:", error);
          setResults([]);
        }
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(performSearch, 300);

    return () => {
      clearTimeout(timeoutId);
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [query]);

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search companies..."
          className="w-full px-4 py-3 border border-border bg-background-primary text-text-primary placeholder-text-secondary focus:outline-none focus:border-golden transition-colors"
        />
        {loading && (
          <div className="text-sm text-text-secondary mt-2">Searching...</div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {results.length > 0 && (
          <div className="grid grid-cols-3 gap-3">
            {results.map((result, index) => (
              <div
                key={index}
                onClick={() => {
                  const workspaceId = generateWorkspaceId();
                  addPendingWorkspace({ workspaceId, ticker: result.symbol });
                  router.push(`/workspace/${workspaceId}`);
                }}
                className="p-4 border border-border hover:bg-golden-light transition-colors cursor-pointer"
              >
                <div className="font-medium text-text-primary">{result.symbol}</div>
                <div className="text-sm text-text-secondary truncate">{result.name}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
