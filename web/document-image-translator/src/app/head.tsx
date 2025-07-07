// This file customizes the <head> for the Next.js app, including favicons and logo metadata.
export default function Head() {
  return (
    <>
      <title>Document Image Translator</title>
      <meta name="description" content="Translate document images to your target language and visualize the result." />
      <link rel="icon" href="/favicon.ico" />
      <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
      <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
      <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      <link rel="manifest" href="/site.webmanifest" />
      <meta property="og:image" content="/logo.svg" />
    </>
  );
}
