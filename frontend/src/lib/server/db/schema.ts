import { sqliteTable, integer, text, primaryKey } from 'drizzle-orm/sqlite-core';

export const venue = sqliteTable('venue', {
	venue: text('venue').notNull(),
	year: integer('year').notNull(),
	count: integer('count')
}, (table) => {
	return {
		pk: primaryKey({ columns: [table.venue, table.year] })
	};
});