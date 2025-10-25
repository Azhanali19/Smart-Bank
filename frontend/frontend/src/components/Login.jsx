import { useState } from "react";
import api from "../api";

export default function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ email: "", password: "", name: "" });
  const [error, setError] = useState("");

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const endpoint = isRegister ? "/auth/register" : "/auth/login";
      const res = await api.post(endpoint, form);
      const token = res.data.access_token || res.data.token;
      if (token) {
        localStorage.setItem("token", token);
        onLogin();
      } else {
        setError("Login failed");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Error");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow-lg w-80">
        <h1 className="text-2xl font-bold mb-4 text-center">
          {isRegister ? "Register" : "Login"}
        </h1>
        <form onSubmit={handleSubmit} className="space-y-3">
          {isRegister && (
            <input
              name="name"
              placeholder="Name"
              className="border p-2 w-full rounded"
              value={form.name}
              onChange={handleChange}
              required
            />
          )}
          <input
            name="email"
            type="email"
            placeholder="Email"
            className="border p-2 w-full rounded"
            value={form.email}
            onChange={handleChange}
            required
          />
          <input
            name="password"
            type="password"
            placeholder="Password"
            className="border p-2 w-full rounded"
            value={form.password}
            onChange={handleChange}
            required
          />
          <button
            type="submit"
            className="bg-blue-600 text-white w-full py-2 rounded hover:bg-blue-700"
          >
            {isRegister ? "Register" : "Login"}
          </button>
        </form>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        <button
          className="text-blue-600 text-sm mt-3 underline"
          onClick={() => setIsRegister(!isRegister)}
        >
          {isRegister ? "Already have an account?" : "Create account"}
        </button>
      </div>
    </div>
  );
}
