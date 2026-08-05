import Link from "next/link";
import { listProjects } from "@/lib/projects/list-projects";
import { NewProjectForm } from "./NewProjectForm";

export default function HomePage() {
  const projects = listProjects();

  return (
    <main className="page">
      <header className="page-header">
        <h1>Alpha Studio</h1>
        <p className="subtitle">
          Projetos em <code>C:\Ai-Project\Criaturas</code> e{" "}
          <code>\Animes</code>
        </p>
      </header>

      <section className="card">
        <h2>Novo projeto</h2>
        <NewProjectForm />
      </section>

      <h2>Projetos ({projects.length})</h2>
      <ul className="project-list">
        {projects.map((project) => (
          <li key={project.id}>
            <Link href={`/projects/${project.id}`}>
              <div className="project-item">
                <div className="name">{project.creatureName}</div>
                <div className="meta">
                  {project.clipCount} clipe(s) ·{" "}
                  {project.hasAudio ? "áudio ok" : "sem áudio"} ·{" "}
                  {project.hasEditPlan ? "plano gerado" : "sem plano"}
                </div>
              </div>
            </Link>
          </li>
        ))}
        {projects.length === 0 && (
          <li className="hint">Nenhum projeto encontrado ainda.</li>
        )}
      </ul>
    </main>
  );
}
