const Queue = require('bull');
const { setupDatabase } = require('./config/database');
const NaverBlogScraper = require('./scrapers/NaverBlogScraper');
const TistoryScraper = require('./scrapers/TistoryScraper');
const WordPressScraper = require('./scrapers/WordPressScraper');
const MediumScraper = require('./scrapers/MediumScraper');
const VelogScraper = require('./scrapers/VelogScraper');

require('dotenv').config();

// Redis 큐 설정
const scrapingQueue = new Queue('blog scraping', process.env.REDIS_URL);

// 스크래퍼 인스턴스
const scrapers = {
  naver: new NaverBlogScraper(),
  tistory: new TistoryScraper(),
  wordpress: new WordPressScraper(),
  medium: new MediumScraper(),
  velog: new VelogScraper()
};

// 큐 작업 처리
scrapingQueue.process('scrape-blog', async (job) => {
  const { platform, url, options } = job.data;
  
  console.log(`Starting scraping job for ${platform}: ${url}`);
  
  try {
    const scraper = scrapers[platform];
    if (!scraper) {
      throw new Error(`Unsupported platform: ${platform}`);
    }
    
    const result = await scraper.scrape(url, options);
    console.log(`Scraping completed for ${platform}: ${url}`);
    
    return result;
  } catch (error) {
    console.error(`Scraping failed for ${platform}: ${url}`, error);
    throw error;
  }
});

// 스케줄링된 작업
scrapingQueue.add('scrape-blog', {
  platform: 'naver',
  url: 'https://blog.naver.com',
  options: { maxPages: 10 }
}, {
  repeat: { cron: '0 */6 * * *' }, // 6시간마다 실행
  removeOnComplete: 10,
  removeOnFail: 5
});

console.log('Blog scraper service started');
console.log('Waiting for scraping jobs...');