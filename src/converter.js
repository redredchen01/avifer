import sharp from 'sharp';
import path from 'path';
import fs from 'fs/promises';

export async function convertToAvif(inputPath, outputPath, options = {}) {
  const {
    quality = 80,
    speed = 6
  } = options;

  // 檢查輸入文件是否存在
  try {
    await fs.access(inputPath);
  } catch (error) {
    throw new Error(`輸入文件不存在: ${inputPath}`);
  }

  // 確保輸出目錄存在
  const outputDir = path.dirname(outputPath);
  await fs.mkdir(outputDir, { recursive: true });

  // 使用sharp進行轉換
  const converter = sharp(inputPath);
  
  // 獲取圖片信息
  const metadata = await converter.metadata();
  
  // 配置AVIF輸出
  const avifOptions = {
    quality: quality,
    speed: speed,
    chromaSubsampling: '4:2:0'
  };

  // 處理帶透明度的圖片
  if (metadata.hasAlpha) {
    avifOptions.chromaSubsampling = '4:4:4';
  }

  await converter
    .avif(avifOptions)
    .toFile(outputPath);

  // 返回轉換信息
  const stats = await fs.stat(outputPath);
  const originalStats = await fs.stat(inputPath);
  
  return {
    inputPath,
    outputPath,
    originalSize: originalStats.size,
    convertedSize: stats.size,
    compressionRatio: ((originalStats.size - stats.size) / originalStats.size * 100).toFixed(2),
    metadata
  };
}