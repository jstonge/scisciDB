// frontend/src/routes/data.remote.js
import { prerender } from '$app/server';
import * as v from 'valibot';
import { db } from "$lib/server/db/index.js"

// Get all unique venues
export const getVenues = prerender(async () => {
  
  const { papers } = await import('$lib/server/db/schema.js');
  const result = await db.selectDistinct({venue: papers.venue}).from(papers);
  
  return result.map(r => r.venue);
});

// // Get papers with min year and venue filters
// export const getFilteredPapers = prerender(
//   v.object({
//     venue: v.string(),
//     minYear: v.number()
//   }),
//   async ({ venue, minYear }) => {
//     const { db } = await import('$lib/server/db/index.js');
//     const { papers } = await import('$lib/server/db/schema.js');
//     const { eq, asc, and, gte } = await import('drizzle-orm');
    
//     const result = await db.select({
//       year: papers.year,
//       count: papers.count
//     })
//     .from(papers)
//     .where(and(
//       eq(papers.venue, venue),
//       gte(papers.year, minYear)
//     ))
//     .orderBy(asc(papers.year));
    
//     return result;
//   }
// );

export const getAllPapers = prerender(async () => {
  const { papers } = await import('$lib/server/db/schema.js');
  const { eq, asc, and, gte } = await import('drizzle-orm');
  return await db.select().from(papers).orderBy(asc(papers.year));
});