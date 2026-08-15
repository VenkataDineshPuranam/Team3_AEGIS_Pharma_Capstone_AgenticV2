import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emits .next/standalone -- a self-contained server with only the modules actually
  // imported, which is what deploy/containers/Dockerfile.web copies into its runtime
  // stage. Without this the image has to ship the entire node_modules tree, and the
  // build toolchain along with it.
  output: "standalone",
  // The repo root, not apps/web: `next build` otherwise infers the workspace root from
  // the nearest lockfile and warns, and the standalone trace comes out rooted in the
  // wrong place inside the container.
  outputFileTracingRoot: path.join(import.meta.dirname, "../../"),
};

export default nextConfig;
