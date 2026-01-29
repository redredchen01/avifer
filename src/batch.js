import path from 'path';
import fs from 'fs/promises';
import { glob } from 'glob';
import ora from 'ora';
import chalk from 'chalk';
import { convertToAvif } from './converter.js';

export async function batchConvert(inputDir, outputDir, options = {}) {
  const {
    quality = 80,
    speed = 6,
    pattern = '**/*.{jpg,jpeg,png,webp,gif}',
    concurrent = 4
  } = options;

  // 檢查輸入目錄是否存在
  try {
    await fs.access(inputDir);
  } catch (error) {
    throw new Error(`輸入目錄不存在: ${inputDir}`);
  }

  // 創建輸出目錄
  await fs.mkdir(outputDir, { recursive: true });

  // 查找所有匹配的圖片文件
  const searchPattern = path.join(inputDir, pattern);
  const files = await glob(searchPattern, { nodir: true });

  if (files.length === 0) {
    console.log(chalk.yellow('未找到匹配的圖片文件'));
    return;
  }

  console.log(chalk.blue(`找到 ${files.length} 個圖片文件`));

  // 初始化進度條
  const spinner = ora({
    text: '正在轉換圖片...',
    color: 'blue'
  }).start();

  let completed = 0;
  let totalOriginalSize = 0;
  let totalConvertedSize = 0;
  const errors = [];

  // 並發處理文件
  const chunks = [];
  for (let i = 0; i < files.length; i += concurrent) {
    chunks.push(files.slice(i, i + concurrent));
  }

  for (const chunk of chunks) {
    const promises = chunk.map(async (file) => {
      try {
        // 計算相對路徑以保持目錄結構
        const relativePath = path.relative(inputDir, file);
        const outputFile = path.join(outputDir, relativePath.replace(/\.[^/.]+$/, '.avif'));

        // 確保輸出子目錄存在
        const outputSubDir = path.dirname(outputFile);
        await fs.mkdir(outputSubDir, { recursive: true });

        const result = await convertToAvif(file, outputFile, { quality, speed });
        
        completed++;
        totalOriginalSize += result.originalSize;
        totalConvertedSize += result.convertedSize;

        spinner.text = `正在轉換圖片... (${completed}/${files.length})`;
        
        return result;
      } catch (error) {
        errors.push({ file, error: error.message });
        completed++;
        spinner.text = `正在轉換圖片... (${completed}/${files.length})`;
        return null;
      }
    });

    await Promise.all(promises);
  }

  spinner.succeed('轉換完成');

  // 顯示結果統計
  console.log(chalk.green('\n=== 轉換結果 ==='));
  console.log(`成功轉換: ${files.length - errors.length} 個文件`);
  console.log(`失敗: ${errors.length} 個文件`);
  
  if (totalOriginalSize > 0) {
    const totalCompressionRatio = ((totalOriginalSize - totalConvertedSize) / totalOriginalSize * 100).toFixed(2);
    console.log(`原始大小: ${(totalOriginalSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`轉換後大小: ${(totalConvertedSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`總壓縮率: ${totalCompressionRatio}%`);
  }

  // 顯示錯誤信息
  if (errors.length > 0) {
    console.log(chalk.red('\n=== 錯誤信息 ==='));
    errors.forEach(({ file, error }) => {
      console.log(chalk.red(`${file}: ${error}`));
    });
  }

  return {
    total: files.length,
    success: files.length - errors.length,
    failed: errors.length,
    totalOriginalSize,
    totalConvertedSize,
    errors
  };
}