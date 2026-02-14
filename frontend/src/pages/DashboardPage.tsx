import { useMemo, useState, type ChangeEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { KpiCard } from "../components/KpiCard";
import { ProviderTable } from "../components/ProviderTable";
import { useAuth } from "../hooks/useAuth";
import {
  downloadProvidersCsv,
  fetchProviderSummary,
  fetchProviders,
  importProviders,
  validateAllProviders,
  validateProvider
} from "../lib/api";
import type { RiskLevel } from "../types";

const PAGE_SIZE = 20;

export function DashboardPage(): JSX.Element {
  const { token, user, logout } = useAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState<RiskLevel | "All">("All");
  const [page, setPage] = useState(1);
  const [flash, setFlash] = useState<string | null>(null);

  const summaryQuery = useQuery({
    queryKey: ["summary", token],
    queryFn: () => fetchProviderSummary(token!),
    enabled: Boolean(token)
  });

  const providerQuery = useQuery({
    queryKey: ["providers", token, page, search, riskFilter],
    queryFn: () =>
      fetchProviders(token!, {
        page,
        pageSize: PAGE_SIZE,
        search,
        riskLevel: riskFilter
      }),
    enabled: Boolean(token)
  });

  const refreshData = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["summary", token] }),
      queryClient.invalidateQueries({ queryKey: ["providers", token] })
    ]);
  };

  const importMutation = useMutation({
    mutationFn: (file: File) => importProviders(token!, file),
    onSuccess: async (data) => {
      setFlash(`Imported ${data.imported} provider records from ${data.source_file}.`);
      await refreshData();
    },
    onError: (error) => {
      setFlash(error instanceof Error ? error.message : "Import failed.");
    }
  });

  const validateAllMutation = useMutation({
    mutationFn: () => validateAllProviders(token!),
    onSuccess: async (data) => {
      setFlash(`Validation completed for ${data.processed} providers.`);
      await refreshData();
    },
    onError: (error) => {
      setFlash(error instanceof Error ? error.message : "Validation failed.");
    }
  });

  const validateSingleMutation = useMutation({
    mutationFn: (providerId: string) => validateProvider(token!, providerId),
    onSuccess: async () => {
      setFlash("Provider revalidated successfully.");
      await refreshData();
    },
    onError: (error) => {
      setFlash(error instanceof Error ? error.message : "Revalidation failed.");
    }
  });

  const totalPages = useMemo(() => {
    const total = providerQuery.data?.total ?? 0;
    return Math.max(1, Math.ceil(total / PAGE_SIZE));
  }, [providerQuery.data?.total]);

  const onImportSelected = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    importMutation.mutate(file);
    event.target.value = "";
  };

  const onExport = async () => {
    if (!token) {
      return;
    }
    try {
      const blob = await downloadProvidersCsv(token);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "validated_providers.csv";
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      setFlash(error instanceof Error ? error.message : "Export failed.");
    }
  };

  return (
    <main className="dashboard-layout">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Operations Console</p>
          <h1>Provider Validation Pipeline</h1>
          <p className="muted">Signed in as {user?.email}</p>
        </div>
        <div className="header-actions">
          <label className="btn btn-ghost file-upload">
            Import CSV
            <input accept=".csv" onChange={onImportSelected} type="file" />
          </label>
          <button
            className="btn btn-primary"
            disabled={validateAllMutation.isPending}
            onClick={() => validateAllMutation.mutate()}
            type="button"
          >
            {validateAllMutation.isPending ? "Validating..." : "Validate All"}
          </button>
          <button className="btn btn-ghost" onClick={onExport} type="button">
            Export CSV
          </button>
          <button className="btn btn-outline" onClick={logout} type="button">
            Logout
          </button>
        </div>
      </header>

      {flash ? <p className="flash">{flash}</p> : null}

      <section className="kpi-grid">
        <KpiCard
          label="Providers"
          value={String(summaryQuery.data?.total_providers ?? 0)}
          hint="Current records in your workspace"
        />
        <KpiCard
          label="High Risk"
          value={String(summaryQuery.data?.high_risk_count ?? 0)}
          hint="Immediate manual review required"
        />
        <KpiCard
          label="Needs Review"
          value={String(summaryQuery.data?.requires_review ?? 0)}
          hint="Medium and high risk combined"
        />
        <KpiCard
          label="Avg Confidence"
          value={`${Math.round((summaryQuery.data?.avg_confidence ?? 0) * 100)}%`}
          hint="Automated validation reliability"
        />
      </section>

      <section className="filter-bar">
        <input
          onChange={(event) => {
            setSearch(event.target.value);
            setPage(1);
          }}
          placeholder="Search provider, specialty, or NPI"
          value={search}
        />
        <select
          onChange={(event) => {
            setRiskFilter(event.target.value as RiskLevel | "All");
            setPage(1);
          }}
          value={riskFilter}
        >
          <option value="All">All Risk Levels</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
      </section>

      <ProviderTable
        isLoading={providerQuery.isLoading}
        onValidate={(providerId) => validateSingleMutation.mutate(providerId)}
        providers={providerQuery.data?.items ?? []}
      />

      <footer className="pager">
        <button
          className="btn btn-inline"
          disabled={page <= 1}
          onClick={() => setPage((current) => Math.max(1, current - 1))}
          type="button"
        >
          Previous
        </button>
        <span>
          Page {page} of {totalPages}
        </span>
        <button
          className="btn btn-inline"
          disabled={page >= totalPages}
          onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
          type="button"
        >
          Next
        </button>
      </footer>
    </main>
  );
}
