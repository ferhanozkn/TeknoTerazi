export function Footer() {
  return (
    <footer className="border-t border-border bg-surface py-8 text-center text-sm text-text-muted">
      <p>TeknoTerazi — teknoloji ürünleri hakkında topluluğun fikrini al.</p>
      <p className="mt-1">Oy verirken tarayıcına anonim bir kimlik çerezi kaydedebiliriz.</p>
      <p className="mt-1">&copy; {new Date().getFullYear()} TeknoTerazi</p>
    </footer>
  );
}
