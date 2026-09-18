import Link from "next/link";

export function Pagination({
  currentPage,
  numPages,
  hasPrevious,
  hasNext,
  querystringPrefix,
}: {
  currentPage: number;
  numPages: number;
  hasPrevious: boolean;
  hasNext: boolean;
  querystringPrefix: string;
}) {
  if (numPages <= 1) return null;

  const pageHref = (page: number) => `?${querystringPrefix}sayfa=${page}`;

  return (
    <nav aria-label="Sayfalama" className="flex flex-wrap items-center gap-2 text-sm">
      {hasPrevious && (
        <Link href={pageHref(currentPage - 1)} className="rounded-full px-3 py-1.5 text-text-muted hover:text-primary">
          ‹ Önceki
        </Link>
      )}
      {Array.from({ length: numPages }, (_, i) => i + 1).map((page) =>
        page === currentPage ? (
          <span key={page} className="rounded-full bg-primary px-3 py-1.5 font-medium text-white">
            {page}
          </span>
        ) : (
          <Link
            key={page}
            href={pageHref(page)}
            className="rounded-full px-3 py-1.5 text-text-muted hover:text-primary"
          >
            {page}
          </Link>
        ),
      )}
      {hasNext && (
        <Link href={pageHref(currentPage + 1)} className="rounded-full px-3 py-1.5 text-text-muted hover:text-primary">
          Sonraki ›
        </Link>
      )}
    </nav>
  );
}
