import { UserRepository } from '../../repositories/UserRepository.js';
import { AppError } from '../../utils/AppError.js';
import bcrypt from 'bcrypt';
import { NewUser } from '../../models/schema.js';

export class RegisterService {
  constructor(private userRepository: UserRepository) {}

  async execute(data: NewUser) {
    const existingUser = await this.userRepository.findByEmail(data.email);
    if (existingUser) {
      throw new AppError('Email already in use', 400);
    }

    const hashedPassword = await bcrypt.hash(data.password, 10);

    return await this.userRepository.create({
      name: data.name,
      email: data.email,
      password: hashedPassword,
    });
  }
}
