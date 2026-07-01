import React, { useMemo } from 'react';

export interface LensStage {
  id: string;
  label: string;
  owner: string;
  whatHappens: string;
  risk?: string;
}

export interface LensEvent {
  stageId: string;
  status: 'waiting' | 'running' | 'success' | 'warning' | 'error';
  at: number | string;
  summary: string;
  meta?: Record<string, string | number | boolean>;
}

export function ProductLensPanel({
  product,
  workflow,
  stages,
  events,
}: {
  product: string;
  workflow: string;
  stages: LensStage[];
  events: LensEvent[];
}) {
  const latestByStage = useMemo(() => {
    const map = new Map<string, LensEvent>();
    for (const event of events) map.set(event.stageId, event);
    return map;
  }, [events]);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <header className="mb-5">
        <p className="text-xs font-bold uppercase tracking-wide text-slate-500">Product Lens</p>
        <h2 className="text-xl font-bold text-slate-950">{product}</h2>
        <p className="mt-1 text-sm text-slate-600">{workflow}</p>
      </header>

      <ol className="space-y-3">
        {stages.map((stage, index) => {
          const event = latestByStage.get(stage.id);
          const status = event?.status ?? 'waiting';

          return (
            <li key={stage.id} className="rounded-xl border border-slate-200 p-4">
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-950 text-sm font-bold text-white">
                  {index + 1}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold text-slate-950">{stage.label}</h3>
                    <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">{stage.owner}</span>
                    <span data-status={status} className="rounded-full bg-blue-50 px-2 py-1 text-xs text-blue-700">
                      {status}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-slate-600">{event?.summary || stage.whatHappens}</p>
                  {event?.meta && (
                    <dl className="mt-3 flex flex-wrap gap-2">
                      {Object.entries(event.meta).map(([key, value]) => (
                        <div key={key} className="rounded-lg bg-slate-50 px-2 py-1 text-xs text-slate-500">
                          <dt className="inline font-semibold">{key}: </dt>
                          <dd className="inline">{String(value)}</dd>
                        </div>
                      ))}
                    </dl>
                  )}
                </div>
              </div>
            </li>
          );
        })}
      </ol>

      <p className="mt-4 text-xs text-slate-500">
        Product Lens shows safe workflow summaries only. It should not display secrets, raw prompts, tokens, or private payloads.
      </p>
    </section>
  );
}
