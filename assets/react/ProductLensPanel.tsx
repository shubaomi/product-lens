import React, { useMemo, useState } from 'react';

type LensStatus = 'waiting' | 'running' | 'success' | 'warning' | 'error';

export interface LensStage {
  id: string;
  label: string;
  owner: string;
  whatHappens: string;
  risk?: string;
}

export interface LensWorkflow {
  id: string;
  label: string;
  description: string;
  stages: LensStage[];
}

export interface ProductLensManifest {
  product: string;
  audience?: string;
  workflows: LensWorkflow[];
}

export interface LensEvent {
  workflowId: string;
  runId: string;
  stageId: string;
  status: LensStatus;
  at: number | string;
  summary: string;
  meta?: Record<string, string | number | boolean>;
}

export interface ProductLensClassNames {
  root?: string;
  header?: string;
  eyebrow?: string;
  title?: string;
  description?: string;
  controls?: string;
  control?: string;
  label?: string;
  select?: string;
  timeline?: string;
  stage?: string;
  stageWaiting?: string;
  stageRunning?: string;
  stageSuccess?: string;
  stageWarning?: string;
  stageError?: string;
  stageIndex?: string;
  stageBody?: string;
  stageHeader?: string;
  stageTitle?: string;
  badge?: string;
  status?: string;
  summary?: string;
  metaList?: string;
  metaItem?: string;
  footer?: string;
  empty?: string;
}

export interface ProductLensLabels {
  eyebrow?: string;
  workflow?: string;
  run?: string;
  noRuns?: string;
  empty?: string;
  safetyNote?: string;
}

const defaultClassNames: ProductLensClassNames = {
  root: 'product-lens',
  header: 'product-lens__header',
  eyebrow: 'product-lens__eyebrow',
  title: 'product-lens__title',
  description: 'product-lens__description',
  controls: 'product-lens__controls',
  control: 'product-lens__control',
  label: 'product-lens__label',
  select: 'product-lens__select',
  timeline: 'product-lens__timeline',
  stage: 'product-lens__stage',
  stageWaiting: 'product-lens__stage--waiting',
  stageRunning: 'product-lens__stage--running',
  stageSuccess: 'product-lens__stage--success',
  stageWarning: 'product-lens__stage--warning',
  stageError: 'product-lens__stage--error',
  stageIndex: 'product-lens__stage-index',
  stageBody: 'product-lens__stage-body',
  stageHeader: 'product-lens__stage-header',
  stageTitle: 'product-lens__stage-title',
  badge: 'product-lens__badge',
  status: 'product-lens__status',
  summary: 'product-lens__summary',
  metaList: 'product-lens__meta-list',
  metaItem: 'product-lens__meta-item',
  footer: 'product-lens__footer',
  empty: 'product-lens__empty',
};

const defaultLabels: Required<ProductLensLabels> = {
  eyebrow: 'Product Lens',
  workflow: 'Workflow',
  run: 'Run',
  noRuns: 'No runs yet',
  empty: 'No Product Lens workflows are configured.',
  safetyNote:
    'Product Lens shows safe workflow summaries only. It should not display secrets, raw prompts, tokens, or private payloads.',
};

const statusClassKey: Record<LensStatus, keyof ProductLensClassNames> = {
  waiting: 'stageWaiting',
  running: 'stageRunning',
  success: 'stageSuccess',
  warning: 'stageWarning',
  error: 'stageError',
};

function cx(...values: Array<string | undefined | false>): string {
  return values.filter(Boolean).join(' ');
}

export function isProductLensEnabled(value: boolean | string | null | undefined): boolean {
  return value === true || value === 'true' || value === '1' || value === 'yes';
}

export function ProductLensPanel({
  manifest,
  events,
  enabled = true,
  initialWorkflowId,
  initialRunId,
  classNames,
  labels,
}: {
  manifest: ProductLensManifest;
  events: LensEvent[];
  enabled?: boolean;
  initialWorkflowId?: string;
  initialRunId?: string;
  classNames?: ProductLensClassNames;
  labels?: ProductLensLabels;
}) {
  const cn = { ...defaultClassNames, ...classNames };
  const text = { ...defaultLabels, ...labels };
  const [selectedWorkflowId, setSelectedWorkflowId] = useState(
    initialWorkflowId || manifest.workflows[0]?.id || ''
  );
  const [selectedRunId, setSelectedRunId] = useState(initialRunId || '');

  const selectedWorkflow =
    manifest.workflows.find((workflow) => workflow.id === selectedWorkflowId) || manifest.workflows[0];

  const workflowEvents = useMemo(
    () => events.filter((event) => event.workflowId === selectedWorkflow?.id),
    [events, selectedWorkflow?.id]
  );

  const runIds = useMemo(() => {
    const ids = Array.from(new Set(workflowEvents.map((event) => event.runId)));
    return ids.sort();
  }, [workflowEvents]);

  const activeRunId = runIds.includes(selectedRunId) ? selectedRunId : runIds[0] || '';

  const runEvents = useMemo(
    () => workflowEvents.filter((event) => !activeRunId || event.runId === activeRunId),
    [workflowEvents, activeRunId]
  );

  const latestByStage = useMemo(() => {
    const map = new Map<string, LensEvent>();
    for (const event of runEvents) map.set(event.stageId, event);
    return map;
  }, [runEvents]);

  if (!enabled) return null;

  if (!selectedWorkflow) {
    return (
      <section className={cn.empty} data-product-lens>
        <p>{text.empty}</p>
      </section>
    );
  }

  return (
    <section
      className={cn.root}
      data-product-lens
      data-workflow-id={selectedWorkflow.id}
      data-run-id={activeRunId || undefined}
    >
      <header className={cn.header}>
        <p className={cn.eyebrow}>{text.eyebrow}</p>
        <h2 className={cn.title}>{manifest.product}</h2>
        <p className={cn.description}>{selectedWorkflow.description}</p>
      </header>

      <div className={cn.controls}>
        <label className={cn.control}>
          <span className={cn.label}>{text.workflow}</span>
          <select
            className={cn.select}
            value={selectedWorkflow.id}
            onChange={(event) => {
              setSelectedWorkflowId(event.target.value);
              setSelectedRunId('');
            }}
          >
            {manifest.workflows.map((workflow) => (
              <option key={workflow.id} value={workflow.id}>
                {workflow.label}
              </option>
            ))}
          </select>
        </label>

        <label className={cn.control}>
          <span className={cn.label}>{text.run}</span>
          <select
            className={cn.select}
            value={activeRunId}
            onChange={(event) => setSelectedRunId(event.target.value)}
            disabled={!runIds.length}
          >
            {runIds.length ? (
              runIds.map((runId) => (
                <option key={runId} value={runId}>
                  {runId}
                </option>
              ))
            ) : (
              <option value="">{text.noRuns}</option>
            )}
          </select>
        </label>
      </div>

      <ol className={cn.timeline}>
        {selectedWorkflow.stages.map((stage, index) => {
          const event = latestByStage.get(stage.id);
          const status = event?.status ?? 'waiting';

          return (
            <li
              key={stage.id}
              className={cx(cn.stage, cn[statusClassKey[status]])}
              data-stage-id={stage.id}
              data-status={status}
            >
              <div className={cn.stageIndex} aria-hidden="true">
                {index + 1}
              </div>
              <div className={cn.stageBody}>
                <div className={cn.stageHeader}>
                  <h3 className={cn.stageTitle}>{stage.label}</h3>
                  <span className={cn.badge}>{stage.owner}</span>
                  <span className={cn.status}>{status}</span>
                </div>
                <p className={cn.summary}>{event?.summary || stage.whatHappens}</p>
                {event?.meta && (
                  <dl className={cn.metaList}>
                    {Object.entries(event.meta).map(([key, value]) => (
                      <div key={key} className={cn.metaItem}>
                        <dt>{key}</dt>
                        <dd>{String(value)}</dd>
                      </div>
                    ))}
                  </dl>
                )}
              </div>
            </li>
          );
        })}
      </ol>

      <p className={cn.footer}>{text.safetyNote}</p>
    </section>
  );
}
