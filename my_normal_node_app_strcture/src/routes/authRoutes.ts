import { Router } from 'express';
import { UserRepository } from '../repositories/UserRepository.js';
import { RegisterService } from '../services/auth/RegisterService.js';
import { RegisterController } from '../controllers/auth/RegisterController.js';
import { validateRequest } from '../middlewares/validation.middleware.js';
import { registerSchema } from '../validations/auth.validation.js';

const authRouter = Router();

const userRepository = new UserRepository();
const registerService = new RegisterService(userRepository);
const registerController = new RegisterController(registerService);

authRouter.post('/register', validateRequest(registerSchema), registerController.handle);

export default authRouter;
