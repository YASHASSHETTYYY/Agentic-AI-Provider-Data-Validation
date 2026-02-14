import { Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { useAuth } from "./hooks/useAuth";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";

export default function App(): JSX.Element {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        element={isAuthenticated ? <Navigate replace to="/" /> : <LoginPage />}
        path="/login"
      />
      <Route
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
        path="/"
      />
      <Route element={<Navigate replace to={isAuthenticated ? "/" : "/login"} />} path="*" />
    </Routes>
  );
}
