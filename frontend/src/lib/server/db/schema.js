// frontend/src/lib/server/db/schema.js
import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core';

export const papers = sqliteTable('papers', {
  venue: text('venue').notNull(),
  year: integer('year').notNull(),
  count: integer('count').notNull()
});

export const fields = sqliteTable('fields', {
  field: text('field').notNull(),
  year: integer('year').notNull(),
  count: integer('count').notNull()
});

export const top_venue_google_scholar = sqliteTable('top_venue_google_scholar', {
  venue: text('venue').notNull(),
  field: text('field').notNull()
});