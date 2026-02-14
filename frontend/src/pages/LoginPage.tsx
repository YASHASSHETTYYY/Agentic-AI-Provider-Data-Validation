import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

type Mode = "login" | "register";

export function LoginPage(): JSX.Element {
  const navigate = useNavigate();
  const { login, registerAndLogin } = useAuth();

  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("admin@providerops.local");
  const [password, setPassword] = useState("ChangeMe123!");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      if (mode === "register") {
        await registerAndLogin(email, password);
      } else {
        await login(email, password);
      }
      navigate("/", { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unexpected error.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-layout">
      <section className="auth-panel">
        <div className="auth-copy">
          <p className="eyebrow">Provider Ops Platform</p>
          <h1>Industrial Validation Control Room</h1>
          <p>
            Secure operations console for provider ingestion, risk scoring, and review queues.
          </p>
        </div>
        <form className="auth-form" onSubmit={onSubmit}>
          <label>
            Work Email
            <input
              autoComplete="email"
              onChange={(e) => setEmail(e.target.value)}
              required
              type="email"
              value={email}
            />
          </label>
          <label>
            Password
            <input
              autoComplete="current-password"
              minLength={8}
              onChange={(e) => setPassword(e.target.value)}
              required
              type="password"
              value={password}
            />
          </label>
          {error ? <p className="form-error">{error}</p> : null}
          <button className="btn btn-primary" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Please wait..." : mode === "register" ? "Create Account" : "Sign In"}
          </button>
          <button
            className="btn btn-ghost"
            onClick={() => setMode((current) => (current === "login" ? "register" : "login"))}
            type="button"
          >
            {mode === "login" ? "Need an account? Register" : "Already have an account? Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}
