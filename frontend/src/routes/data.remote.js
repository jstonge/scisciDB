// frontend/src/routes/data.remote.js
import { query } from '$app/server';
import { db } from '$lib/server/db/index.js'; 
import { venue } from '$lib/server/db/schema.js'; 
import { desc } from 'drizzle-orm';

// Query to get all venue data
export const getCounts = query(async () => {
	const result = await db.select().from(venue).orderBy(desc(venue.year));
	return result;
});