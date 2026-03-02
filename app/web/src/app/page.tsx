import { JobsSummary } from "@/modules/jobs/summary";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-50">
      <div className="mx-auto max-w-5xl px-6 py-12">
        <header className="mb-10">
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900">
            Exobrain
          </h1>
          <p className="mt-1 text-zinc-500">
            Personal tools and dashboards
          </p>
        </header>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <JobsSummary />

          <div className="flex items-center justify-center rounded-lg border-2 border-dashed border-zinc-300 bg-white p-6">
            <p className="text-sm text-zinc-400">
              More modules coming soon
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
