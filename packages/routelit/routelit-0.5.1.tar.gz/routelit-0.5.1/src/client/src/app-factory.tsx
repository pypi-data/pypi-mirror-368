import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

export function renderApp(rootId: string = "root") {
  createRoot(document.getElementById(rootId)!).render(
    <StrictMode>
      <App />
    </StrictMode>
  );
}
