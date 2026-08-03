import type { NextConfig } from "next";
import createMDX from "@next/mdx";

const nextConfig: NextConfig = {
  output: "export",
  images: {
    unoptimized: true,
  },
  pageExtensions: ["js", "jsx", "md", "mdx", "ts", "tsx"],
  // GitHub Pages serves this as a project site under /PaperPilot/, not at
  // the domain root, so every internal link and static asset needs this
  // prefix -- otherwise they'd resolve against the wrong root and 404.
  basePath: "/PaperPilot",
  assetPrefix: "/PaperPilot/",
  // GitHub Pages has no server to rewrite extensionless URLs to their
  // matching .html file, so pages must export as out/docs/setup/index.html
  // (resolved by requesting the folder) rather than out/docs/setup.html.
  trailingSlash: true,
};

const withMDX = createMDX({});

export default withMDX(nextConfig);
