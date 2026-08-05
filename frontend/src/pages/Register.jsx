import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import AuthLayout from "../layouts/AuthLayout";
import PasswordInput from "../components/common/PasswordInput";

export default function Register() {
  const [form, setForm] = useState({ username: "", full_name: "", email: "", password: "" });
  const [confirmPassword, setConfirmPassword] = useState("");
  const [confirmError, setConfirmError] = useState("");
  const [serverError, setServerError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleConfirmChange = (e) => {
    const value = e.target.value;
    setConfirmPassword(value);
    if (confirmError && value === form.password) setConfirmError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setServerError("");

    if (form.password !== confirmPassword) {
      setConfirmError("Passwords don't match");
      return;
    }
    setConfirmError("");

    setSubmitting(true);
    try {
      await register(form);
      navigate("/");
    } catch (err) {
      setServerError(err.response?.data?.detail || "Registration failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <h1 className="font-display text-2xl text-ink">Create an account</h1>
          <p className="mt-1 text-sm text-ink/60">Start turning your pantry into recipes.</p>
        </div>

        {serverError && (
          <p className="rounded-md bg-category-protein/10 px-3 py-2 text-sm text-category-protein">
            {serverError}
          </p>
        )}

        <div>
          <label className="form-label">Username</label>
          <input type="text" name="username" value={form.username} onChange={handleChange}
            required className="input-field" />
        </div>

        <div>
          <label className="form-label">Full name</label>
          <input type="text" name="full_name" value={form.full_name} onChange={handleChange}
            required className="input-field" />
        </div>

        <div>
          <label className="form-label">Email</label>
          <input type="email" name="email" value={form.email} onChange={handleChange}
            required className="input-field" />
        </div>

        <PasswordInput
          label="Password"
          name="password"
          value={form.password}
          onChange={handleChange}
          minLength={8}
        />

        <div>
          <PasswordInput
            label="Confirm password"
            name="confirmPassword"
            value={confirmPassword}
            onChange={handleConfirmChange}
            minLength={8}
          />
          {confirmError && (
            <p className="mt-1 text-sm text-category-protein">{confirmError}</p>
          )}
        </div>

        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? "Creating account..." : "Register"}
        </button>

        <p className="text-center text-sm text-ink/60">
          Already have an account? <Link to="/login" className="font-medium text-basil hover:text-basil-dark">Log in</Link>
        </p>
      </form>
    </AuthLayout>
  );
}