// frontend/src/lib/server/db/seed.js
import { db } from './index.js';
import { papers } from './schema.js';
import fs from 'fs/promises';

// Create table if it doesn't exist
db.run(`
  CREATE TABLE IF NOT EXISTS papers (
    venue TEXT NOT NULL,
    year INTEGER NOT NULL,
    count INTEGER NOT NULL
  )
`);

// Clear existing data (only if table exists and has data)
try {
  await db.delete(papers);
} catch (error) {
  // Table might be empty or not exist, that's fine
  console.log('Table was empty or didn\'t exist');
}

// Read and insert data
const jsonData = JSON.parse(await fs.readFile('static/data/nature_papers_by_year.json', 'utf8'));

await db.insert(papers).values(
  jsonData.data.map(item => ({
    venue: 'Nature',
    year: item.year,
    count: item.count
  }))
);

console.log(`✅ Imported ${jsonData.data.length} records`);