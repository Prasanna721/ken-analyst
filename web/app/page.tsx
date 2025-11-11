import Layout from "@/components/Layout";
import SearchBox from "@/components/SearchBox";
import WorkspaceList from "@/components/WorkspaceList";
import CreateWorkspaceCard from "@/components/CreateWorkspaceCard";

export default function Home() {
  return (
    <Layout>
      <div className="h-full flex">
        <div className="w-1/2 border-r border-border p-8 flex flex-col">
          <div className="mb-8">
            <CreateWorkspaceCard />
          </div>

          <div className="flex-1 overflow-hidden">
            <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wide">
              Workspaces
            </h3>
            <WorkspaceList />
          </div>
        </div>

        <div className="w-1/2 p-8">
          <h3 className="text-sm font-medium text-text-secondary mb-6 uppercase tracking-wide">
            Create Workspace
          </h3>
          <SearchBox />
        </div>
      </div>
    </Layout>
  );
}
