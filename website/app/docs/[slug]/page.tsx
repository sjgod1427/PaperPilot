import fs from "fs";
import path from "path";
import { notFound } from "next/navigation";

const DOCS_DIR = path.join(process.cwd(), "content", "docs");

function getSlugs(): string[] {
  return fs
    .readdirSync(DOCS_DIR)
    .filter((file) => file.endsWith(".mdx"))
    .map((file) => file.replace(/\.mdx$/, ""));
}

export function generateStaticParams() {
  return getSlugs().map((slug) => ({ slug }));
}

export const dynamicParams = false;

export default async function DocPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  if (!getSlugs().includes(slug)) {
    notFound();
  }

  const { default: Doc } = await import(`@/content/docs/${slug}.mdx`);

  return (
    <article className="pb-16">
      <Doc />
    </article>
  );
}
