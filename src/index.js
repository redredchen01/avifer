#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { convertToAvif } from './converter.js';
import { batchConvert } from './batch.js';
import { listSupportedFormats } from './formats.js';

const program = new Command();

program
  .name('avif-converter')
  .description('本地批量AVIF圖片轉換工具')
  .version('1.0.0');

program
  .command('convert')
  .description('轉換單個圖片到AVIF格式')
  .argument('<input>', '輸入圖片路徑')
  .argument('<output>', '輸出AVIF圖片路徑')
  .option('-q, --quality <number>', '壓縮質量 (1-100)', '80')
  .option('-s, --speed <number>', '編碼速度 (1-10)', '6')
  .action(async (input, output, options) => {
    try {
      console.log(chalk.blue('開始轉換...'));
      await convertToAvif(input, output, options);
      console.log(chalk.green('✓ 轉換完成'));
    } catch (error) {
      console.error(chalk.red('✗ 轉換失敗:'), error.message);
      process.exit(1);
    }
  });

program
  .command('batch')
  .description('批量轉換圖片到AVIF格式')
  .argument('<input-dir>', '輸入目錄路徑')
  .argument('<output-dir>', '輸出目錄路徑')
  .option('-q, --quality <number>', '壓縮質量 (1-100)', '80')
  .option('-s, --speed <number>', '編碼速度 (1-10)', '6')
  .option('-p, --pattern <pattern>', '文件匹配模式', '**/*.{jpg,jpeg,png,webp,gif}')
  .option('-c, --concurrent <number>', '並發處理數量', '4')
  .action(async (inputDir, outputDir, options) => {
    try {
      console.log(chalk.blue('開始批量轉換...'));
      await batchConvert(inputDir, outputDir, options);
      console.log(chalk.green('✓ 批量轉換完成'));
    } catch (error) {
      console.error(chalk.red('✗ 批量轉換失敗:'), error.message);
      process.exit(1);
    }
  });

program
  .command('formats')
  .description('列出支持的圖片格式')
  .action(() => {
    const formats = listSupportedFormats();
    console.log(chalk.yellow('支持的輸入格式:'));
    formats.input.forEach(format => console.log(`  • ${format}`));
    console.log(chalk.yellow('支持的輸出格式:'));
    formats.output.forEach(format => console.log(`  • ${format}`));
  });

program.parse();