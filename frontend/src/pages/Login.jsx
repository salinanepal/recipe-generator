import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import AuthLayout from "../components/layouts/AuthLayout";
import PasswordInput from "../components/common/PasswordInput";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/");
    }
    catch (err) {
      console.log(err.response?.data);
    
      const detail = err.response?.data?.detail;
    
      if (typeof detail === "string") {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail.map(e => e.msg).join(", "));
      } else {
        setError("Login failed");
      }
    }
    finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <h1 className="font-display text-2xl text-ink">Welcome back</h1>
          <p className="mt-1 text-sm text-ink/60">Log in to generate recipes from your ingredients.</p>
        </div>

        {error && (
          <p className="rounded-md bg-category-protein/10 px-3 py-2 text-sm text-category-protein">
            {error}
          </p>
        )}

        <div>
          <label className="form-label">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="input-field"
          />
        </div>

        <PasswordInput
          label="Password"
          name="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? "Logging in..." : "Log in"}
        </button>

        <p className="text-center text-sm text-ink/60">
          No account? <Link to="/register" className="font-medium text-basil hover:text-basil-dark">Register</Link>
        </p>
      </form>
    </AuthLayout>
  );
}