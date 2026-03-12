import React from "react";
import { createRoot, type Root } from "react-dom/client";

import { App } from "./App";
import "./index.css";
import type { StreamlitComponentLike } from "./types";

const mountedRoots = new WeakMap<HTMLElement, Root>();

export default function mountOutlierSearchForm(component: StreamlitComponentLike) {
  const parent = component.parentElement;
  let mountNode = parent.querySelector<HTMLElement>('[data-of-search-form="true"]');

  if (!mountNode) {
    mountNode = document.createElement("div");
    mountNode.dataset.ofSearchForm = "true";
    mountNode.className = "of-root";
    parent.innerHTML = "";
    parent.appendChild(mountNode);
  }

  let root = mountedRoots.get(mountNode);
  if (!root) {
    root = createRoot(mountNode);
    mountedRoots.set(mountNode, root);
  }

  root.render(
    <React.StrictMode>
      <App component={component} />
    </React.StrictMode>,
  );

  return () => {
    const mounted = mountedRoots.get(mountNode!);
    mounted?.unmount();
    mountedRoots.delete(mountNode!);
  };
}
