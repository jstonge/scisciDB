// frontend/src/routes/data.remote.js
import { prerender } from '$app/server';
import { db } from "$lib/server/db/index.js"
import { asc } from 'drizzle-orm'
import { papers } from '$lib/server/db/schema.js'

// Get all unique venues
export const getVenues = prerender(async () => {
  const result = await db.selectDistinct({venue: papers.venue}).from(papers);
  return result.map(r => r.venue);
});

export const getAllPapers = prerender(async () => {
  return await db.select().from(papers).orderBy(asc(papers.year));
});