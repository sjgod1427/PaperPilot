import fs from "fs";
import path from "path";
import Link from "next/link";
import matter from "gray-matter";

const DOCS_DIR = path.join(process.cwd(), "content", "docs");

interface DocEntry {
  slug: string;
  title: string;
  order: number;
}

function getDocEntries(): DocEntry[] {
  const files = fs.readdirSync(DOCS_DIR).filter((file) => file.endsWith(".mdx"));

  const entries = files.map((file) => {
    const raw = fs.readFileSync(path.join(DOCS_DIR, file), "utf8");
    const { data } = matter(raw);
    const slug = file.replace(/\.mdx$/, "");

    return {
      slug,
      title: typeof data.title === "string" ? data.title : slug,
      order: typeof data.order === "number" ? data.order : 0,
    };
  });

  return entries.sort((a, b) => a.order - b.order);
}

export default function DocsLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const entries = getDocEntries();

  return (
    <div className="min-h-full bg-pp-bg">
      <div className="mx-auto flex max-w-5xl flex-col gap-10 px-6 py-16 md:flex-row">
        <aside className="shrink-0 md:w-48">
          <div className="mb-4 font-pp-mono text-xs font-semibold uppercase tracking-wide text-pp-muted-2">
            Docs
          </div>
          <nav className="flex flex-col gap-1 border-l border-pp-border pl-4">
            {entries.map((entry) => (
              <Link
                key={entry.slug}
                href={`/docs/${entry.slug}`}
                className="font-pp-mono text-sm text-pp-muted hover:text-pp-ink"
              >
                {entry.title}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}
