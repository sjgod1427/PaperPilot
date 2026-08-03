import type { MDXComponents } from "mdx/types";

// Global MDX component overrides. Required by @next/mdx for the App Router --
// see node_modules/@next/mdx's README. This is where the docs content (ported
// from INSTALL.md) picks up the PaperPilot design tokens instead of rendering
// as unstyled default markdown.
const components: MDXComponents = {
  h1: ({ children }) => (
    <h1 className="mb-6 font-pp-mono text-2xl font-semibold text-pp-ink">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="mt-10 mb-4 font-pp-mono text-lg font-semibold text-pp-ink first:mt-0">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="mt-8 mb-3 font-pp-mono text-base font-semibold text-pp-ink">
      {children}
    </h3>
  ),
  p: ({ children }) => (
    <p className="mb-4 text-sm leading-relaxed text-pp-muted">{children}</p>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      className="text-pp-accent underline underline-offset-2 hover:text-pp-ink"
    >
      {children}
    </a>
  ),
  ul: ({ children }) => (
    <ul className="mb-4 list-disc space-y-2 pl-5 text-sm leading-relaxed text-pp-muted">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-4 list-decimal space-y-2 pl-5 text-sm leading-relaxed text-pp-muted">
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="marker:text-pp-muted-2">{children}</li>,
  strong: ({ children }) => (
    <strong className="font-semibold text-pp-ink">{children}</strong>
  ),
  blockquote: ({ children }) => (
    <blockquote className="mb-4 border-l-2 border-pp-accent/60 pl-4 text-sm italic text-pp-muted">
      {children}
    </blockquote>
  ),
  code: ({ children }) => (
    <code className="rounded bg-pp-surface-2 px-1.5 py-0.5 font-pp-mono text-[0.85em] text-pp-accent">
      {children}
    </code>
  ),
  pre: ({ children }) => (
    <pre className="mb-4 overflow-x-auto rounded-lg border border-pp-border bg-pp-surface p-4 font-pp-mono text-xs leading-relaxed text-pp-ink [&>code]:bg-transparent [&>code]:p-0 [&>code]:text-pp-ink">
      {children}
    </pre>
  ),
};

export function useMDXComponents(existingComponents: MDXComponents): MDXComponents {
  return {
    ...existingComponents,
    ...components,
  };
}
