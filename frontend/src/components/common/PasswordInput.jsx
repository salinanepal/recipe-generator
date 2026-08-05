import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

export default function PasswordInput({ label, name, value, onChange, minLength }) {
  const [visible, setVisible] = useState(false);

  return (
    <div>
      <label className="form-label">{label}</label>
      <div className="relative mt-1">
        <input
          type={visible ? "text" : "password"}
          name={name}
          value={value}
          onChange={onChange}
          required
          minLength={minLength}
          className="input-field mt-0 pr-10"
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? "Hide password" : "Show password"}
          className="absolute inset-y-0 right-0 flex items-center pr-3 text-ink/40 hover:text-ink"
        >
          {visible ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
    </div>
  );
}