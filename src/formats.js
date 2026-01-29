export function listSupportedFormats() {
  return {
    input: [
      'JPEG', 'JPG', 'PNG', 'WebP', 'GIF', 'SVG', 'TIFF', 'BMP'
    ],
    output: [
      'AVIF'
    ]
  };
}

export function getSupportedExtensions() {
  return [
    '.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.tiff', '.bmp'
  ];
}

export function isFormatSupported(filename) {
  const ext = filename.toLowerCase();
  const supportedExts = getSupportedExtensions();
  return supportedExts.some(supportedExt => ext.endsWith(supportedExt));
}