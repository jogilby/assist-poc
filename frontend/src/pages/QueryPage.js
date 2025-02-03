import { useState, useEffect } from "react";
import { Button, Input, Select } from "@/components/ui";
import queryAPI from "@/api/query";
import fetchProjects from "@/api/projects";

export default function QueryPage() {
  const [query, setQuery] = useState("");
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState("all");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadProjects() {
      const data = await fetchProjects();
      setProjects(data);
    }
    loadProjects();
  }, []);

  async function handleQuery() {
    setLoading(true);
    setResponse("");
    const data = await queryAPI(selectedProject === "all" ? null : selectedProject, query);
    setResponse(data.response);
    setLoading(false);
  }

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">Query Your Documents</h1>
      <div className="my-4">
        <Select value={selectedProject} onChange={(e) => setSelectedProject(e.target.value)}>
          <option value="all">All Projects</option>
          {projects.map((project) => (
            <option key={project.id} value={project.id}>{project.folder_name}</option>
          ))}
        </Select>
      </div>
      <Input 
        type="text" 
        placeholder="Enter your query..." 
        value={query} 
        onChange={(e) => setQuery(e.target.value)} 
      />
      <Button onClick={handleQuery} disabled={loading} className="mt-2">
        {loading ? "Processing..." : "Search"}
      </Button>
      {response && <div className="mt-4 p-2 border rounded bg-gray-100">{response}</div>}
    </div>
  );
}