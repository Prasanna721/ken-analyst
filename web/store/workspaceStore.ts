import { create } from "zustand";

interface WorkspaceCreation {
  workspaceId: string;
  ticker?: string;
  file?: File;
}

interface WorkspaceStore {
  pendingWorkspaces: Map<string, WorkspaceCreation>;
  addPendingWorkspace: (data: WorkspaceCreation) => void;
  getPendingWorkspace: (workspaceId: string) => WorkspaceCreation | undefined;
  removePendingWorkspace: (workspaceId: string) => void;
}

export const useWorkspaceStore = create<WorkspaceStore>((set, get) => ({
  pendingWorkspaces: new Map(),

  addPendingWorkspace: (data) =>
    set((state) => {
      const newMap = new Map(state.pendingWorkspaces);
      newMap.set(data.workspaceId, data);
      return { pendingWorkspaces: newMap };
    }),

  getPendingWorkspace: (workspaceId) => {
    return get().pendingWorkspaces.get(workspaceId);
  },

  removePendingWorkspace: (workspaceId) =>
    set((state) => {
      const newMap = new Map(state.pendingWorkspaces);
      newMap.delete(workspaceId);
      return { pendingWorkspaces: newMap };
    }),
}));
