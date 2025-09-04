import type { Config } from 'drizzle-kit';

export default {
  schema: './schema.ts',
  out: './migrations', 
  dialect: 'postgresql',
  dbCredentials: {
    host: 'localhost',
    port: 5434,
    user: 'postgres',
    password: 'password',
    database: 'urban_infra',
  },
  verbose: true,
  strict: true,
} satisfies Config;