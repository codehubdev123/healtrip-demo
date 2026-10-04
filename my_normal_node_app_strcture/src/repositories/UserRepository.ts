import { db } from '../config/db.js';
import { users, NewUser, User } from '../models/schema.js';
import { eq } from 'drizzle-orm';

export class UserRepository {
  async findByEmail(email: string): Promise<User | undefined> {
    const result = await db.select().from(users).where(eq(users.email, email)).limit(1);
    return result[0];
  }

  async create(userData: NewUser): Promise<User> {
    const [newUser] = await db.insert(users).values(userData).returning();
    return newUser;
  }
}
