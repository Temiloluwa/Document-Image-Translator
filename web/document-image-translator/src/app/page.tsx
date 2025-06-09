import Link from "next/link";

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 gap-8 bg-gray-50">
      <h1 className="text-4xl font-bold mb-4 text-blue-900">Document Image Translator</h1>
      <p className="text-lg text-gray-700 mb-8 text-center max-w-xl">
        Effortlessly translate document images to your target language and visualize the result as HTML.
      </p>
      <div className="flex gap-6">
        <Link href="/upload" className="bg-blue-600 text-white rounded px-6 py-3 font-semibold hover:bg-blue-700 transition">
          Upload & Translate
        </Link>
        <Link href="/status" className="bg-gray-200 text-blue-900 rounded px-6 py-3 font-semibold hover:bg-gray-300 transition">
          Check Status
        </Link>
      </div>
    </main>
  );
}
