import type { ProviderRecord } from "../types";

type ProviderTableProps = {
  providers: ProviderRecord[];
  isLoading: boolean;
  onValidate: (providerId: string) => void;
};

export function ProviderTable({
  providers,
  isLoading,
  onValidate
}: ProviderTableProps): JSX.Element {
  if (isLoading) {
    return (
      <div className="table-shell">
        <div className="table-loading">Loading providers...</div>
      </div>
    );
  }

  if (providers.length === 0) {
    return (
      <div className="table-shell">
        <div className="table-empty">
          No providers found. Import a CSV file to start validation workflows.
        </div>
      </div>
    );
  }

  return (
    <div className="table-shell">
      <table className="provider-table">
        <thead>
          <tr>
            <th>Provider</th>
            <th>Specialty</th>
            <th>Risk</th>
            <th>Confidence</th>
            <th>Issue</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {providers.map((provider) => (
            <tr key={provider.id}>
              <td>
                <div className="provider-name">{provider.provider_name}</div>
                <div className="provider-meta">{provider.npi ?? "NPI unavailable"}</div>
              </td>
              <td>{provider.specialty ?? "Unknown"}</td>
              <td>
                <span className={`risk-pill risk-${provider.risk_level.toLowerCase()}`}>
                  {provider.risk_level}
                </span>
              </td>
              <td>
                <div className="confidence-wrap">
                  <div className="confidence-track">
                    <div
                      className="confidence-fill"
                      style={{ width: `${Math.round(provider.confidence_score * 100)}%` }}
                    />
                  </div>
                  <span>{Math.round(provider.confidence_score * 100)}%</span>
                </div>
              </td>
              <td>{provider.primary_issue ?? "No blocking issues"}</td>
              <td>
                <button
                  className="btn btn-inline"
                  onClick={() => onValidate(provider.id)}
                  type="button"
                >
                  Revalidate
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
