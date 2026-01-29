import assert from 'assert';
import path from 'path';
import fs from 'fs/promises';
import { convertToAvif } from '../src/converter.js';
import { batchConvert } from '../src/batch.js';
import { isFormatSupported } from '../src/formats.js';

async function runTests() {
  console.log('開始運行測試...\n');

  // 創建測試目錄
  const testDir = path.join(process.cwd(), 'test-data');
  const outputDir = path.join(testDir, 'output');
  
  await fs.mkdir(testDir, { recursive: true });
  await fs.mkdir(outputDir, { recursive: true });

  // 測試1: 格式支持檢查
  console.log('測試1: 格式支持檢查');
  assert.strictEqual(isFormatSupported('test.jpg'), true);
  assert.strictEqual(isFormatSupported('test.png'), true);
  assert.strictEqual(isFormatSupported('test.avif'), false);
  console.log('✓ 通過\n');

  // 測試2: 單文件轉換 (需要一個測試圖片)
  console.log('測試2: 單文件轉換');
  try {
    // 創建一個簡單的測試圖片 (1x1像素的PNG)
    const testImagePath = path.join(testDir, 'test.png');
    const testOutputPath = path.join(outputDir, 'test.avif');
    
    // 使用sharp創建測試圖片
    const sharp = (await import('sharp')).default;
    await sharp({
      create: {
        width: 1,
        height: 1,
        channels: 3,
        background: { r: 255, g: 0, b: 0 }
      }
    }).png().toFile(testImagePath);

    const result = await convertToAvif(testImagePath, testOutputPath, { quality: 80 });
    
    assert.strictEqual(result.inputPath, testImagePath);
    assert.strictEqual(result.outputPath, testOutputPath);
    assert(result.convertedSize > 0);
    
    console.log('✓ 單文件轉換通過');
    console.log(`  原始大小: ${result.originalSize} bytes`);
    console.log(`  轉換後大小: ${result.convertedSize} bytes`);
    console.log(`  壓縮率: ${result.compressionRatio}%\n`);
  } catch (error) {
    console.log('✗ 單文件轉換失敗:', error.message);
  }

  // 測試3: 批量轉換
  console.log('測試3: 批量轉換');
  try {
    const batchInputDir = path.join(testDir, 'batch-input');
    const batchOutputDir = path.join(testDir, 'batch-output');
    
    await fs.mkdir(batchInputDir, { recursive: true });
    await fs.mkdir(batchOutputDir, { recursive: true });

    // 創建多個測試圖片
    const sharp = (await import('sharp')).default;
    for (let i = 1; i <= 3; i++) {
      await sharp({
        create: {
          width: 10,
          height: 10,
          channels: 3,
          background: { r: i * 50, g: 100, b: 200 }
        }
      }).png().toFile(path.join(batchInputDir, `test${i}.png`));
    }

    const result = await batchConvert(batchInputDir, batchOutputDir, {
      quality: 80,
      concurrent: 2
    });

    assert.strictEqual(result.total, 3);
    assert.strictEqual(result.success, 3);
    assert.strictEqual(result.failed, 0);
    
    console.log('✓ 批量轉換通過');
    console.log(`  總文件數: ${result.total}`);
    console.log(`  成功: ${result.success}`);
    console.log(`  失敗: ${result.failed}\n`);
  } catch (error) {
    console.log('✗ 批量轉換失敗:', error.message);
  }

  console.log('所有測試完成！');
}

// 運行測試
runTests().catch(console.error);