/*
Registration Page - Gen-Z Inspired Design
Implements REQ-18: Sign-up with profile creation requirement
*/
import React, { useState } from 'react'
import { useRouter } from 'next/router'
import { useForm } from 'react-hook-form'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card } from '@/components/ui/Card'
import { toast } from 'react-hot-toast'
import { authAPI } from '@/services/api'

interface RegisterForm {
  email: string
  username: string
  password: string
  password_confirm: string
}

export default function RegisterPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState(1) // 1: Register, 2: Verify
  const [verificationCode, setVerificationCode] = useState('')
  const [userEmail, setUserEmail] = useState('')

  const { register, handleSubmit, formState: { errors }, watch } = useForm<RegisterForm>()
  const password = watch('password')

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true)
    try {
      await authAPI.register(data)
      setUserEmail(data.email)
      setStep(2)
      toast.success('Registration successful! Check your email for verification code.')
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerification = async () => {
    setIsLoading(true)
    try {
      const response = await authAPI.verify(userEmail, verificationCode)
      localStorage.setItem('token', response.data.token)
      toast.success('Account verified! Welcome to the creator community!')
      router.push('/profile/create')
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Verification failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-yellow-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md"
      >
        <Card className="p-8 backdrop-blur-lg bg-white/10 border-white/20">
          {step === 1 ? (
            <>
              {/* Header */}
              <div className="text-center mb-8">
                <motion.h1 
                  className="text-4xl font-bold text-white mb-2"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  Join the Vibe ✨
                </motion.h1>
                <motion.p 
                  className="text-purple-200"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  Connect with creators, build amazing projects
                </motion.p>
              </div>

              {/* Registration Form */}
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <div>
                  <Input
                    type="email"
                    placeholder="Your email ✉️"
                    {...register('email', { 
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address'
                      }
                    })}
                    error={errors.email?.message}
                    className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                  />
                </div>

                <div>
                  <Input
                    type="text"
                    placeholder="Username 🎭"
                    {...register('username', { 
                      required: 'Username is required',
                      minLength: {
                        value: 3,
                        message: 'Username must be at least 3 characters'
                      }
                    })}
                    error={errors.username?.message}
                    className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                  />
                </div>

                <div>
                  <Input
                    type="password"
                    placeholder="Password 🔒"
                    {...register('password', { 
                      required: 'Password is required',
                      minLength: {
                        value: 8,
                        message: 'Password must be at least 8 characters'
                      }
                    })}
                    error={errors.password?.message}
                    className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                  />
                </div>

                <div>
                  <Input
                    type="password"
                    placeholder="Confirm password 🔒"
                    {...register('password_confirm', { 
                      required: 'Please confirm your password',
                      validate: value => value === password || 'Passwords do not match'
                    })}
                    error={errors.password_confirm?.message}
                    className="bg-white/10 border-white/20 text-white placeholder-purple-200"
                  />
                </div>

                <Button
                  type="submit"
                  variant="gradient"
                  size="lg"
                  fullWidth
                  isLoading={isLoading}
                  className="mt-8"
                >
                  Create Account 🚀
                </Button>
              </form>

              {/* Login Link */}
              <div className="text-center mt-6">
                <p className="text-purple-200">
                  Already have an account?{' '}
                  <button
                    onClick={() => router.push('/auth/login')}
                    className="text-yellow-400 hover:text-yellow-300 font-semibold transition-colors"
                  >
                    Sign in here
                  </button>
                </p>
              </div>
            </>
          ) : (
            <>
              {/* Verification Step */}
              <div className="text-center mb-8">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-16 h-16 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4"
                >
                  <span className="text-2xl">📧</span>
                </motion.div>
                <h1 className="text-3xl font-bold text-white mb-2">Check Your Email</h1>
                <p className="text-purple-200">
                  We sent a verification code to<br />
                  <span className="text-yellow-400 font-semibold">{userEmail}</span>
                </p>
              </div>

              <div className="space-y-6">
                <Input
                  type="text"
                  placeholder="Enter 6-digit code"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  maxLength={6}
                  className="bg-white/10 border-white/20 text-white placeholder-purple-200 text-center text-2xl tracking-widest"
                />

                <Button
                  onClick={handleVerification}
                  variant="gradient"
                  size="lg"
                  fullWidth
                  isLoading={isLoading}
                  disabled={verificationCode.length !== 6}
                >
                  Verify Account ✅
                </Button>

                <button
                  onClick={() => setStep(1)}
                  className="w-full text-purple-200 hover:text-white transition-colors"
                >
                  ← Back to registration
                </button>
              </div>
            </>
          )}
        </Card>

        {/* Fun footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center mt-8 text-purple-200"
        >
          <p className="text-sm">
            Ready to turn your creative dreams into reality? 🌟
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}
