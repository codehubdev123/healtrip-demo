import { Request, Response } from 'express';
import { RegisterService } from '../../services/auth/RegisterService.js';
import { catchAsync } from '../../utils/catchAsync.js';

export class RegisterController {
  constructor(private registerService: RegisterService) {}

  public handle = catchAsync(async (req: Request, res: Response): Promise<void> => {
    const { name, email, password } = req.body;

    const newUser = await this.registerService.execute({ name, email, password });

    res.status(201).json({
      success: true,
      data: {
        id: newUser.id,
        name: newUser.name,
        email: newUser.email,
      },
    });
  });
}
