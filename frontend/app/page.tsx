async function getDigest() {
  const res = await fetch("http://127.0.0.1:8000/api/digest", {
    cache: "no-store",
  });
  return res.json();
}

export default async function Home() {
  const articles = await getDigest();

  return (
    <main className="p-8">
      <h1 className="font-heading text-3xl mb-4">Digest Test</h1>
      <p className="mb-4">Total articles: {articles.length}</p>
      <pre className="text-xs bg-white p-4 rounded overflow-auto max-h-96">
        {JSON.stringify(articles.slice(0, 3), null, 2)}
      </pre>
    </main>
  );
}