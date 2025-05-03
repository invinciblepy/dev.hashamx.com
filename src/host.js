// src/api.js
// Decide the API host once, then reuse it everywhere.
const API_HOST =
  window.location.hostname === "localhost"
    ? "http://localhost:5000"          // <-- local Flask (or 127.0.0.1)
    : "https://api.hashamx.com";       // <-- production sub-domain

export function host() {
  return API_HOST;
}
