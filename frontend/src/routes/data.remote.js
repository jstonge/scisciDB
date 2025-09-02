// frontend/src/routes/data.remote.js
import { prerender } from '$app/server';
import { db } from "$lib/server/db/index.js"
import { asc, gte, sum, eq, and, or, lte } from 'drizzle-orm'
import { papers, fields } from '$lib/server/db/schema.js'

// Get all unique venues
export const getVenues = prerender(async () => {
  const result = await db.selectDistinct({venue: papers.venue}).from(papers);
  return result.map(r => r.venue);
});

export const getAllPapers = prerender(async () => {
  return await db.select().from(papers).orderBy(asc(papers.year));
});

export const getFieldsStem = prerender(async () => {
  return await db
  .select()
  .from(fields)
  .where(
    and(
      gte(fields.year, 1950),
      lte(fields.year, 2024),
      or(
        eq(fields.field, "Computer Science"),
        eq(fields.field, "Medicine"),
        eq(fields.field, "Chemistry"),
        eq(fields.field, "Materials Science"),
        eq(fields.field, "Physics"),
        eq(fields.field, "Biology"),
        eq(fields.field, "Geology"),
        eq(fields.field, "Engineering"),
        eq(fields.field, "Environmental Science"),
        eq(fields.field, "Agricultural and Food Sciences"),
        eq(fields.field, "Mathematics"),
      )
    )
  )
  .orderBy(asc(fields.year));
});

export const getFieldsSocSci = prerender(async () => {
  return await db
        .select()
        .from(fields)
        .where(
          and(
            gte(fields.year, 1950),
            lte(fields.year, 2024),
            or(
              eq(fields.field, "History"),
              eq(fields.field, "Linguistics"),
              eq(fields.field, "Geography"),
              eq(fields.field, "Political Science"),
              eq(fields.field, "Economics"),
              eq(fields.field, "Sociology"),
              eq(fields.field, "Philosophy"),
              eq(fields.field, "Art"),
              eq(fields.field, "Education"),
              eq(fields.field, "Psychology"),
              eq(fields.field, "Business"),
              eq(fields.field, "Law")
            )
          )
        )
        .orderBy(asc(fields.year));
});

export const getAllFieldsAgg = prerender(async () => {
  return await db
    .select({
      field: fields.field,
      total_count: sum(fields.count)
    })
    .from(fields)
    .where(gte(fields.year, 1950))
    .groupBy(fields.field);
});