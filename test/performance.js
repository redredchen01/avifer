import { performance } from 'perf_hooks';
import fs from 'fs/promises';
import path from 'path';
import { convertToAvif } from '../src/converter.js';
import { batchConvert } from '../src/batch.js';

async function performanceTest() {
  console.log('開始性能測試...\n');

  const testDir = path.join(process.cwd(), 'perf-test');
  const outputDir = path.join(testDir, 'output');
  
  await fs.mkdir(testDir, { recursive: true });
  await fs.mkdir(outputDir, { recursive: true });

  // 測試不同質量設置的性能
  console.log('=== 質量設置性能測試 ===');
  const qualities = [50, 70, 80, 90];
  
  for (const quality of qualities) {
    const startTime = performance.now();
    
    try {
      const sharp = (await import('sharp')).default;
      const testImage = path.join(testDir, `test-${quality}.png`);
      const outputImage = path.join(outputDir, `test-${quality}.avif`);
      
      // 創建測試圖片
      await sharp({
        create: {
          width: 1920,
          height: 1080,
          channels: 3,
          background: { r: 255, g: 100, b: 50 }
        }
      }).png().toFile(testImage);

      const result = await convertToAvif(testImage, outputImage, { quality });
      
      const endTime = performance.now();
      const duration = (endTime - startTime).toFixed(2);
      
      console.log(`質量 ${quality}: ${duration}ms, 壓縮率: ${result.compressionRatio}%`);
      
      // 清理文件
      await fs.unlink(testImage);
      await fs.unlink(outputImage);
    } catch (error) {
      console.log(`質量 ${quality}: 測試失敗 - ${error.message}`);
    }
  }

  // 測試並發處理性能
  console.log('\n=== 並發處理性能測試 ===');
  const concurrentLevels = [1, 2, 4, 8];
  
  for (const concurrent of concurrentLevels) {
    const startTime = performance.now();
    
    try {
      const batchInputDir = path.join(testDir, `batch-${concurrent}`);
      const batchOutputDir = path.join(testDir, `output-${concurrent}`);
      
      await fs.mkdir(batchInputDir, { recursive: true });
      await fs.mkdir(batchOutputDir, { recursive: true });

      // 創建10個測試圖片
      const sharp = (await import('sharp')).default;
      for (let i = 1; i <= 10; i++) {
        await sharp({
          create: {
            width: 800,
            height: 600,
            channels: 3,
            background: { r: i * 25, g: 100, b: 200 }
          }
        }).png().toFile(path.join(batchInputDir, `test${i}.png`));
      }

      const result = await batchConvert(batchInputDir, batchOutputDir, {
        quality: 80,
        concurrent
      });
      
      const endTime = performance.now();
      const duration = (endTime - startTime).toFixed(2);
      
      console.log(`並發 ${concurrent}: ${duration}ms, 成功: ${result.success}/${result.total}`);
      
      // 清理目錄
      await fs.rm(batchInputDir, { recursive: true });
      await fs.rm(batchOutputDir, { recursive: true });
    } catch (error) {
      console.log(`並發 ${concurrent}: 測試失敗 - ${error.message}`);
    }
  }

  // 內存使用測試
  console.log('\n=== 內存使用測試 ===');
  const memBefore = process.memoryUsage();
  console.log('測試前內存使用:', {
    rss: `${(memBefore.rss / 1024 / 1024).toFixed(2)} MB`,
    heapUsed: `${(memBefore.heapUsed / 1024 / 1024).toFixed(2)} MB`
  });

  try {
    const largeInputDir = path.join(testDir, 'large-batch');
    const largeOutputDir = path.join(testDir, 'large-output');
    
    await fs.mkdir(largeInputDir, { recursive: true });
    await fs.mkdir(largeOutputDir, { recursive: true });

    // 創建50個較大的測試圖片
    const sharp = (await import('sharp')).default;
    for (let i = 1; i <= 50; i++) {
      await sharp({
        create: {
          width: 1200,
          height: 800,
          channels: 3,
          background: { r: Math.random() * 255, g: Math.random() * 255, b: Math.random() * 255 }
        }
      }).png().toFile(path.join(largeInputDir, `large${i}.png`));
    }

    await batchConvert(largeInputDir, largeOutputDir, {
      quality: 80,
      concurrent: 4
    });
    
    const memAfter = process.memoryUsage();
    console.log('測試後內存使用:', {
      rss: `${(memAfter.rss / 1024 / 1024).toFixed(2)} MB`,
      heapUsed: `${(memAfter.heapUsed / 1024 / 1024).toFixed(2)} MB`
    });
    
    console.log('內存增長:', {
      rss: `${((memAfter.rss - memBefore.rss) / 1024 / 1024).toFixed(2)} MB`,
      heapUsed: `${((memAfter.heapUsed - memBefore.heapUsed) / 1024 / 1024).toFixed(2)} MB`
    });

    // 清理目錄
    await fs.rm(largeInputDir, { recursive: true });
    await fs.rm(largeOutputDir, { recursive: true });
  } catch (error) {
    console.log('內存測試失敗:', error.message);
  }

  console.log('\n性能測試完成！');
}

// 運行性能測試
performanceTest().catch(console.error);